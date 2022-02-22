# wai-annotations-imgaug
Stream processors for the wai.annotations conversion library for image augmentation.

## Plugins
### HSL-GRAYSCALE
Turns RGB images into fake grayscale ones by converting them to HSL and then using the L channel for all channels.

#### Domain(s):
- **Image Domains**

#### Options:

```
    HSL-GRAYSCALE:
      Turns RGB images into fake grayscale ones by converting them to HSL and then using the L channel for all channels.

      Domain(s): Image Object-Detection Domain, Image Segmentation Domain, Image Classification Domain

      usage: hsl-grayscale [-f FACTOR]

      optional arguments:
        -f FACTOR, --factor FACTOR
                        the factor to apply to the L channel to darken or lighten the image (<1: darker, >1: lighter)
```


### ROTATE
Rotates images randomly within a range of degrees or by a specified degree. Specify seed value and force augmentation to be seeded to generate repeatable augmentations.

#### Domain(s):
- **Image Domains**

#### Options:

```
    ROTATE:
      Rotates images randomly within a range of degrees or by a specified degree. Specify seed value and force augmentation to be seeded to generate repeatable augmentations.

      Domain(s): Image Object-Detection Domain, Image Classification Domain, Image Segmentation Domain

      usage: rotate-image [-f FROM_DEGREE] [-s SEED] [-a] [-T THRESHOLD] [-t TO_DEGREE]

      optional arguments:
        -f FROM_DEGREE, --from-degree FROM_DEGREE
                        the start degree to use for rotating the images
        -s SEED, --seed SEED
                        the seed value to use for the random number generator; randomly seeded if not provided
        -a, --seed-augmentation
                        whether to seed the augmentation; if specified, uses the seeded random generator to produce a seed value from 0 to 1000 for the augmentation.
        -T THRESHOLD, --threshold THRESHOLD
                        the threshold to use for Random.rand(): if equal or above, rotation gets applied; range: 0-1; default: 0 (= always)
        -t TO_DEGREE, --to-degree TO_DEGREE
                        the end degree to use for rotating the images
```