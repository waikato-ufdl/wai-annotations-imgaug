from typing import Type, Tuple

from wai.annotations.core.component import ProcessorComponent
from wai.annotations.core.domain import DomainSpecifier
from wai.annotations.core.specifier import ProcessorStageSpecifier


class SubImagesISPSpecifier(ProcessorStageSpecifier):
    """
    Specifies the sub-images ISP.
    """
    @classmethod
    def description(cls) -> str:
        return "Extracts sub-images (incl their annotations) from the images coming through, using the defined regions."

    @classmethod
    def domain_transfer_function(
            cls,
            input_domain: Type[DomainSpecifier]
    ) -> Type[DomainSpecifier]:
        from wai.annotations.domain.image.classification import ImageClassificationDomainSpecifier
        from wai.annotations.domain.image.object_detection import ImageObjectDetectionDomainSpecifier
        if input_domain is ImageClassificationDomainSpecifier:
            return input_domain
        elif input_domain is ImageObjectDetectionDomainSpecifier:
            return input_domain
        else:
            raise Exception(
                f"SubImages only handles the following domains: "
                f"{ImageClassificationDomainSpecifier.name()}, "
                f"{ImageObjectDetectionDomainSpecifier.name()}"
            )

    @classmethod
    def components(cls) -> Tuple[Type[ProcessorComponent]]:
        from wai.annotations.imgaug.isp.sub_images.component import SubImages
        return SubImages,
