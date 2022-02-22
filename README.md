# wai-annotations-processors
Stream processors for the wai.annotations conversion library.

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
