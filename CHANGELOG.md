# CHANGELOG:

- v2.0.0: Added a separate GIMP 3 plug-in using the current Python API. It exports matching guide rectangles from all top-level layers, including hidden layers, and preserves the skip layer and skip color options. The GIMP 2 plug-in remains available.
- v1.2.2: Using a more robust file counting method in target folder. It was not possible to count files in some folders with the old method.
- v1.2.1: Setting default folder parameter to None since that way we ensure the user selects a desired folder. Otherwise it could be saving images to the home directory and that's not good UX.
- v1.2.0: Skipping cards given a specific color and color distance value
- v1.1.0: Skipping odd or even layers if specified.
- v1.0.1: Fixed overwriting existing files.
- v1.0.0: Initial version.
