import imgaug.augmenters as iaa

from wai.common.cli.options import TypedOption
from wai.annotations.imgaug.isp.base.component import BaseImageAugmentation


class Rotate(BaseImageAugmentation):
    """
    Stream processor which rotates images, either randomly within a range of degrees
    (negative/positive) or with a specific degree when the to/from degrees are the same.
    """

    from_degree = TypedOption(
        "-f", "--from-degree",
        type=float,
        help="the start of the degree range to use for rotating the images"
    )

    to_degree = TypedOption(
        "-t", "--to-degree",
        type=float,
        help="the end of the degree range to use for rotating the images"
    )

    def _can_augment(self):
        """
        Checks whether augmentation can take place.

        :return: whether can augment
        :rtype: bool
        """
        return (self.from_degree is not None) and (self.to_degree is not None)

    def _create_pipeline(self, aug_seed):
        """
        Creates and returns the augmentation pipeline.

        :param aug_seed: the seed value to use, can be None
        :type aug_seed: int
        :return: the pipeline
        :rtype: iaa.Sequential
        """
        if self.from_degree == self.to_degree:
            return iaa.Sequential([
                iaa.Affine(
                    rotate=self.from_degree,
                    seed=aug_seed,
                )
            ])
        else:
            return iaa.Sequential([
                iaa.Affine(
                    rotate=(self.from_degree, self.to_degree),
                    seed=aug_seed,
                )
            ])
