# wai-annotations-imgaug
Image augmentation stream processors for the wai.annotations conversion library.

## Plugins
### HSL-GRAYSCALE
Turns RGB images into fake grayscale ones by converting them to HSL and then using the L channel for all channels. The brightness can be influenced and varied even.

#### Domain(s):
- **Image Domains**

#### Options:

```
    HSL-GRAYSCALE:
      Turns RGB images into fake grayscale ones by converting them to HSL and then using the L channel for all channels. The brightness can be influenced and varied even.

      Domain(s): Image Object-Detection Domain, Image Classification Domain

      usage: hsl-grayscale [-f FACTOR_FROM] [-t FACTOR_TO] [-s SEED] [-a] [-T THRESHOLD]

      optional arguments:
        -f FACTOR_FROM, --from-factor FACTOR_FROM
                        the start of the factor range to apply to the L channel to darken or lighten the image (<1: darker, >1: lighter)
        -t FACTOR_TO, --to-factor FACTOR_TO
                        the end of the factor range to apply to the L channel to darken or lighten the image (<1: darker, >1: lighter)
        -s SEED, --seed SEED
                        the seed value to use for the random number generator; randomly seeded if not provided
        -a, --seed-augmentation
                        whether to seed the augmentation; if specified, uses the seeded random generator to produce a seed value from 0 to 1000 for the augmentation.
        -T THRESHOLD, --threshold THRESHOLD
                        the threshold to use for Random.rand(): if equal or above, augmentation gets applied; range: 0-1; default: 0 (= always)
```


### ROTATE
Rotates images randomly within a range of degrees or by a specified degree. Specify seed value and force augmentation to be seeded to generate repeatable augmentations.

#### Domain(s):
- **Image Domains**

#### Options:

```
    ROTATE:
      Rotates images randomly within a range of degrees or by a specified degree. Specify seed value and force augmentation to be seeded to generate repeatable augmentations.

      Domain(s): Image Object-Detection Domain, Image Classification Domain

      usage: rotate [-f DEGREE_FROM] [-t DEGREE_TO] [-s SEED] [-a] [-T THRESHOLD]

      optional arguments:
        -f DEGREE_FROM, --from-degree DEGREE_FROM
                        the start of the degree range to use for rotating the images
        -t DEGREE_TO, --to-degree DEGREE_TO
                        the end of the degree range to use for rotating the images
        -s SEED, --seed SEED
                        the seed value to use for the random number generator; randomly seeded if not provided
        -a, --seed-augmentation
                        whether to seed the augmentation; if specified, uses the seeded random generator to produce a seed value from 0 to 1000 for the augmentation.
        -T THRESHOLD, --threshold THRESHOLD
                        the threshold to use for Random.rand(): if equal or above, augmentation gets applied; range: 0-1; default: 0 (= always)
```