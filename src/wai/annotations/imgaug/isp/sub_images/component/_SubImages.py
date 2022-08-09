import io
import os

from shapely.geometry import Polygon, GeometryCollection, MultiPolygon
from typing import List

from wai.common.cli.options import TypedOption, FlagOption
from wai.common.geometry import Polygon as WaiPolygon
from wai.common.geometry import Point as WaiPoint
from wai.common.adams.imaging.locateobjects import LocatedObjects, LocatedObject
from wai.annotations.domain.image import Image
from wai.annotations.domain.image import ImageInstance
from wai.annotations.domain.classification import Classification
from wai.annotations.domain.image.classification import ImageClassificationInstance
from wai.annotations.domain.image.object_detection import ImageObjectDetectionInstance
from wai.annotations.core.component import ProcessorComponent
from wai.annotations.core.stream import ThenFunction, DoneFunction
from wai.annotations.core.stream.util import RequiresNoFinalisation


REGION_SORTING_NONE = "none"
REGION_SORTING_XY = "x-then-y"
REGION_SORTING_YX = "y-then-x"
REGION_SORTING = [
    REGION_SORTING_NONE,
    REGION_SORTING_XY,
    REGION_SORTING_YX,
]


class SubImages(
    RequiresNoFinalisation,
    ProcessorComponent[ImageInstance, ImageInstance]
):
    """
    Stream processor which turns RGB images into fake grayscale ones.
    """

    regions: List[str] = TypedOption(
        "-r", "--regions",
        type=str,
        nargs="+",
        help="the regions (X,Y,WIDTH,HEIGHT) to crop and forward with their annotations"
    )

    region_sorting: str = TypedOption(
        "-s", "--region-sorting",
        type=str,
        default=REGION_SORTING_NONE,
        help="how to sort the supplied region definitions: %s" % "|".join(REGION_SORTING)
    )

    include_partial: bool = FlagOption(
        "-p", "--include-partial",
        help="whether to include only annotations that fit fully into a region or also partial ones"
    )

    skip_empty: bool = FlagOption(
        "-e", "--suppress-empty",
        help="suppresses sub-images that have no annotations (object detection)"
    )

    verbose: bool = FlagOption(
        "--verbose",
        help="for outputting debugging information"
    )

    def _initialize(self):
        """
        Parses options.
        """
        self._regions_xyxy = []
        self._region_lobjs = []
        for region in self.regions:
            coords = [int(x) for x in region.split(",")]
            if len(coords) == 4:
                x, y, w, h = coords
                self._region_lobjs.append(LocatedObject(x=x, y=y, width=w, height=h))

        if self.verbose:
            self.logger.info("unsorted regions: %s" % str([str(x) for x in self._region_lobjs]))

        if self.region_sorting is not REGION_SORTING_NONE:
            if self.region_sorting == REGION_SORTING_XY:
                def sorting(obj: LocatedObject):
                    return "%06d %06d" % (obj.x, obj.y)
            elif self.region_sorting == REGION_SORTING_YX:
                def sorting(obj: LocatedObject):
                    return "%06d %06d" % (obj.y, obj.x)
            else:
                raise Exception("Unhandled region sorting: %s" % self.region_sorting)
            self._region_lobjs.sort(key=sorting)
            if self.verbose:
                self.logger.info("sorted regions: %s" % str([str(x) for x in self._region_lobjs]))

        for lobj in self._region_lobjs:
            self._regions_xyxy.append((lobj.x, lobj.y, lobj.x + lobj.width - 1, lobj.y + lobj.height - 1))
        if self.verbose:
            self.logger.info("sorted xyxy: %s" % str(self._regions_xyxy))

    def _new_filename(self, filename, index):
        """
        Generates a new filename based on the original and the index of the region.

        :param filename: the base filename
        :type filename: str
        :param index: the region index
        :type index: int
        :return: the generated filename
        :rtype: str
        """
        parts = os.path.splitext(filename)
        pattern = "-%0" + str(len(str(len(self._region_lobjs)))) + "d"
        return parts[0] + pattern % index + parts[1]

    def _bbox_to_shapely(self, lobj: LocatedObject) -> Polygon:
        """
        Converts the located object rectangle into a shapely Polygon.

        :param lobj: the bbox to convert
        :return: the Polygon
        """
        coords = [
            (lobj.x, lobj.y),
            (lobj.x + lobj.width - 1, lobj.y),
            (lobj.x + lobj.width - 1, lobj.y + lobj.height - 1),
            (lobj.x, lobj.y + lobj.height - 1),
            (lobj.x, lobj.y),
        ]
        return Polygon(coords)

    def _polygon_to_shapely(self, lobj: LocatedObject) -> Polygon:
        """
        Converts the located object polygon into a shapely Polygon.

        :param lobj: the polygon to convert
        :return: the Polygon
        """
        if not lobj.has_polygon():
            return self._bbox_to_shapely(lobj)
        x_list = lobj.get_polygon_x()
        y_list = lobj.get_polygon_y()
        coords = []
        for x, y in zip(x_list, y_list):
            coords.append((x, y))
        coords.append((x_list[0], y_list[0]))
        return Polygon(coords)

    def _fit_annotation(self, index: int, region: LocatedObject, annotation: LocatedObject) -> LocatedObject:
        """
        Fits the annotation into the specified region, adjusts size if necessary.

        :param index: the index of the region
        :param region: the region to fit the annotation in
        :param annotation: the annotation to fit
        :return: the adjust annotation
        """
        sregion = self._bbox_to_shapely(region)
        sbbox = self._bbox_to_shapely(annotation)
        sintersect = sbbox.intersection(sregion)
        minx, miny, maxx, maxy = [int(x) for x in sintersect.bounds]
        result = LocatedObject(x=minx-region.x, y=miny-region.y, width=maxx-minx+1, height=maxy-miny+1, **annotation.metadata)
        result.metadata["region_index"] = index
        result.metadata["region_xywh"] = "%d,%d,%d,%d" % (region.x, region.y, region.width, region.height)

        if annotation.has_polygon():
            spolygon = self._polygon_to_shapely(annotation)
        else:
            spolygon = self._bbox_to_shapely(annotation)

        try:
            sintersect = spolygon.intersection(sregion)
        except:
            self.logger.warning("Failed to compute intersection!")
            sintersect = None

        if isinstance(sintersect, GeometryCollection):
            for x in sintersect.geoms:
                if isinstance(x, Polygon):
                    sintersect = x
                    break
        elif isinstance(sintersect, MultiPolygon):
            for x in sintersect.geoms:
                if isinstance(x, Polygon):
                    sintersect = x
                    break

        if isinstance(sintersect, Polygon):
            x_list, y_list = sintersect.exterior.coords.xy
            points = []
            for i in range(len(x_list)):
                points.append(WaiPoint(x=x_list[i]-region.x, y=y_list[i]-region.y))
            result.set_polygon(WaiPolygon(*points))
        else:
            self.logger.warning("Unhandled geometry type returned from intersection, skipping: %s" % str(type(sintersect)))

        return result

    def process_element(
            self,
            element: ImageInstance,
            then: ThenFunction[ImageInstance],
            done: DoneFunction
    ):
        if not hasattr(self, "_regions_xyxy"):
            self._initialize()

        img_in = element.data

        pil_image = img_in.pil_image
        for region_index, region_xyxy in enumerate(self._regions_xyxy):
            if self.verbose:
                self.logger.info("Applying region %d :%s" % (region_index, str(region_xyxy)))
            # crop image
            sub_image = pil_image.crop(region_xyxy)
            pil_img_bytes = io.BytesIO()
            sub_image.save(pil_img_bytes, format=img_in.format.pil_format_string)
            img_out = Image(self._new_filename(img_in.filename, region_index), pil_img_bytes.getvalue(), img_in.format, img_in.size)
            # crop annotations and forward
            region_lobj = self._region_lobjs[region_index]
            if isinstance(element, ImageClassificationInstance):
                annotations = Classification(label=element.annotations.label)
                new_element = ImageClassificationInstance(data=img_out, annotations=annotations)
                then(new_element)
            elif isinstance(element, ImageObjectDetectionInstance):
                new_objects = []
                for ann_lobj in element.annotations:
                    ratio = region_lobj.overlap_ratio(ann_lobj)
                    if ((ratio > 0) and self.include_partial) or (ratio >= 1):
                        new_objects.append(self._fit_annotation(region_index, region_lobj, ann_lobj))
                if not self.skip_empty or (len(new_objects) > 0):
                    new_element = ImageObjectDetectionInstance(data=img_out, annotations=LocatedObjects(new_objects))
                    then(new_element)
            else:
                self.logger.warning("Unhandled data (%s), skipping!" % str(type(element)))
                then(element)
                return
