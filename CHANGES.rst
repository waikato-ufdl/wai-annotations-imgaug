Changelog
=========

1.0.6 (2022-09-05)
------------------

- `sub-images` plugin now has a `--verbose` flag; only initializes the regions now once


1.0.5 (2022-06-13)
------------------

- Added `sub-images` plugin for extracting regions (including their annotations) based on
  one or more bounding box definitions from the images coming through and only forwarding
  these sub-images


1.0.4 (2022-05-12)
------------------

- Fixed error message of AnnotationOverlay in case data of wrong domain is coming through
- Moved AnnotationOverlay into wai.annotations.imgvis module


1.0.3 (2022-05-05)
------------------

- `--labels` option of the `add-annotation-overlay-od` plugin gets respected now,
  also using correct label for text now (when varying the colors)


1.0.2 (2022-05-05)
------------------

- added `add-annotation-overlay-od` plugin to overlay the object detections on the images


1.0.1 (2022-03-01)
------------------

- added more typing hints to parameters
- added ability to add augmented images rather than replace original ones, using
  the `-m/--mode add` option (`--suffix` overrides the default suffix)
- added `scale` ISP for scaling images


1.0.0 (2022-02-23)
------------------

- Initial release: crop, flip, gaussian-blur, hsl-grayscale, linear-contrast, rotate
