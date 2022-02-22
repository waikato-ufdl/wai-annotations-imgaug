import cv2
import io
import numpy as np
import PIL

from wai.common.cli.options import TypedOption, FlagOption

from wai.annotations.core.component import ProcessorComponent
from wai.annotations.core.stream import ThenFunction, DoneFunction
from wai.annotations.core.stream.util import RequiresNoFinalisation
from wai.annotations.domain.image import ImageInstance, Image


class HSLGrayScale(
    RequiresNoFinalisation,
    ProcessorComponent[ImageInstance, ImageInstance]
):
    """
    Stream processor which turns RGB images into fake grayscale ones.
    """
    factor = TypedOption(
        "-f", "--factor",
        type=float,
        help="the factor to apply to the L channel to darken or lighten the image (<1: darker, >1: lighter)"
    )

    def process_element(
            self,
            element: ImageInstance,
            then: ThenFunction[ImageInstance],
            done: DoneFunction
    ):
        img_in = element.data

        # convert to HSL
        img_pil = img_in.pil_image
        img_rgb = np.array(img_pil)
        img_hls = cv2.cvtColor(img_rgb, cv2.COLOR_BGR2HLS)
        img_l = img_hls[:, :, 1]

        # adjust brightness?
        if self.factor is not None:
            img_l = img_l * self.factor
            img_l = img_l.astype(np.uint8)

        # convert back to PIL bytes
        img_pil = PIL.Image.fromarray(np.uint8(img_l))
        pil_img_bytes = io.BytesIO()
        img_pil.save(pil_img_bytes, format=img_in.format.pil_format_string)
        img_out = Image(img_in.filename, pil_img_bytes.getvalue(), img_in.format, img_in.size)

        # new element
        element_out = element.__class__(img_out, element.annotations)
        then(element_out)
