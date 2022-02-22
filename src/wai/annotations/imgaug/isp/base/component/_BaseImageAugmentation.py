import io
import imageio
import imgaug.augmenters as iaa
from imgaug.augmentables.bbs import BoundingBox, BoundingBoxesOnImage
from imgaug.augmentables.polys import Polygon, PolygonsOnImage
import numpy as np
import PIL

from random import Random
from wai.common.cli.options import TypedOption, FlagOption
from wai.common.adams.imaging.locateobjects import LocatedObjects
from wai.common.geometry import Polygon as WaiPolygon
from wai.common.geometry import Point as WaiPoint
from wai.annotations.core.component import ProcessorComponent
from wai.annotations.core.stream import ThenFunction, DoneFunction
from wai.annotations.core.stream.util import RequiresNoFinalisation
from wai.annotations.domain.image import ImageInstance, Image

MIN_RAND = 0
MAX_RAND = 1000


class BaseImageAugmentation(
    RequiresNoFinalisation,
    ProcessorComponent[ImageInstance, ImageInstance]
):
    """
    Base class for stream processors that augment images.
    """

    seed = TypedOption(
        "-s", "--seed",
        type=int,
        help="the seed value to use for the random number generator; randomly seeded if not provided"
    )

    seed_augmentation = FlagOption(
        "-a", "--seed-augmentation",
        help="whether to seed the augmentation; if specified, uses the seeded random generator to produce a seed value from %d to %d for the augmentation." % (MIN_RAND, MAX_RAND)
    )

    threshold = TypedOption(
        "-T", "--threshold",
        type=float,
        help="the threshold to use for Random.rand(): if equal or above, augmentation gets applied; range: 0-1; default: 0 (= always)"
    )

    def _create_pipeline(self, aug_seed):
        """
        Creates and returns the augmentation pipeline.

        :param aug_seed: the seed value to use, can be None
        :type aug_seed: int
        :return: the pipeline
        :rtype: iaa.Sequential
        """
        raise NotImplementedError()

    def process_element(
            self,
            element: ImageInstance,
            then: ThenFunction[ImageInstance],
            done: DoneFunction
    ):
        # no rotation?
        if (self.from_degree is None) or (self.to_degree is None):
            then(element)
            return

        threshold = 0.0 if self.threshold is None else self.threshold
        if (threshold < 0) or (threshold > 1):
            raise Exception("Threshold must satisfy x >= 0 and x <= 1, supplied: %f" % threshold)

        if not hasattr(self, "_random"):
            self._random = Random(self.seed)

        if self._random.random() < threshold:
            then(element)
            return

        # configure pipeline
        if self.seed_augmentation:
            aug_seed = self._random.randint(MIN_RAND, MAX_RAND)
        else:
            aug_seed = None
        seq = self._create_pipeline(aug_seed)

        img_in = element.data
        image = imageio.imread(element.data.data)

        # convert annotations
        bboxesoi = None
        polys = None
        if element.annotations_type() == LocatedObjects:
            has_polys = False
            for obj in element.annotations:
                if obj.has_polygon():
                    has_polys = True
                    break
            if has_polys:
                polys = []
                for obj in element.annotations:
                    x = obj.get_polygon_x()
                    y = obj.get_polygon_y()
                    points = []
                    for i in range(len(x)):
                        points.append((x[i], y[i]))
                    poly = Polygon(points)
                    polys.append(poly)
                    polysoi = PolygonsOnImage(polys, shape=image.shape)
                    # TODO use polysoi instead polys?
            else:
                bboxes = []
                for obj in element.annotations:
                    bbox = BoundingBox(x1=obj.x, y1=obj.y, x2=obj.x + obj.width - 1, y2=obj.y + obj.height - 1)
                    bboxes.append(bbox)
                bboxesoi = BoundingBoxesOnImage(bboxes, shape=image.shape)

        # augment
        bbs_aug = None
        polys_aug = None
        if bboxesoi is not None:
            image_aug, bbs_aug = seq(image=image, bounding_boxes=bboxesoi)
        elif polys is not None:
            image_aug, polys_aug = seq(image=image, polygons=polys)
        else:
            image_aug = seq(image=image)

        # update annotations
        annotations_new = element.annotations
        if bbs_aug is not None:
            objs_aug = []
            for i, bbox in enumerate(bbs_aug):
                # skip ones outside image
                if bbox.is_out_of_image(image_aug):
                    continue
                # clip bboxes to fit into image
                bbox = bbox.clip_out_of_image(image_aug)
                # update located object
                obj_aug = element.annotations[i].get_clone()
                obj_aug.x = bbox.x1
                obj_aug.y = bbox.y1
                obj_aug.width = bbox.x2 - bbox.x1 + 1
                obj_aug.height = bbox.y2 - bbox.y1 + 1
                objs_aug.append(obj_aug)
                annotations_new = LocatedObjects(objs_aug)
        elif polys_aug is not None:
            objs_aug = []
            for i, poly in enumerate(polys_aug):
                # skip ones outside image
                if poly.is_out_of_image(image_aug):
                    continue
                # clip bboxes to fit into image
                polys = poly.clip_out_of_image(image_aug)
                if len(polys) == 0:
                    continue
                for p in polys:
                    # update located object
                    obj_aug = element.annotations[i].get_clone()
                    bbox = p.to_bounding_box()
                    obj_aug.x = bbox.x1
                    obj_aug.y = bbox.y1
                    obj_aug.width = bbox.x2 - bbox.x1 + 1
                    obj_aug.height = bbox.y2 - bbox.y1 + 1
                    points = []
                    for row in p.coords:
                        points.append(WaiPoint((int(row[0])), int(row[1])))
                    obj_aug.set_polygon(WaiPolygon(*points))
                    objs_aug.append(obj_aug)
            annotations_new = LocatedObjects(objs_aug)

        img_pil = PIL.Image.fromarray(np.uint8(image_aug))
        pil_img_bytes = io.BytesIO()
        img_pil.save(pil_img_bytes, format=img_in.format.pil_format_string)
        img_out = Image(img_in.filename, pil_img_bytes.getvalue(), img_in.format, img_in.size)

        # new element
        element_out = element.__class__(img_out, annotations_new)
        then(element_out)
