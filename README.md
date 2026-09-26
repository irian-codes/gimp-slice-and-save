# GIMP Script: Slice layer and save (with constraints)

This plug-in is intended for PDFs but works with any image containing one or more layers. It exports each guide-bounded rectangle matching the specified card dimensions as a separate PNG from each selected layer.

Use cases:

- Extracting individual board game cards from PDFs shared by people
- Save an image in different parts.

## Instructional video

- [Spanish](https://1drv.ms/u/s!At9UtWURDSwlic8ivmoBwWBo_pGkjw?e=Lrhypf)
- [English](https://1drv.ms/u/s!At9UtWURDSwlic8kEIiBThGfEEqdxg?e=QbOSSK)

## Installation

The GIMP 2 and GIMP 3 versions are separate. You can install both when the two GIMP versions are installed side by side.

### GIMP 3.2

1. In GIMP, open **Edit > Preferences > Folders > Plug-ins** to locate your user plug-ins folder. On Windows with GIMP 3.2, this is usually `%APPDATA%\GIMP\3.2\plug-ins`.
2. Create a `slice-layer-and-save` folder inside that plug-ins folder, then copy [`gimp3/slice-layer-and-save.py`](gimp3/slice-layer-and-save.py) into it. GIMP 3 expects the plug-in file in a folder with the same name, so the installed path should end in `plug-ins/slice-layer-and-save/slice-layer-and-save.py`.
3. Restart GIMP. Open an image and select **Tools > Slice each layer using guides...**.

### GIMP 2.10

Copy [`gimp2/slice-layer-and-save.py`](gimp2/slice-layer-and-save.py) into your GIMP 2.10 plug-ins folder and restart GIMP. The original Python 2 script is unchanged apart from its location in this repository.

## How to use

1. Open a PDF in GIMP, importing its pages as layers, or open another layered image.
2. Set guides to divide the image into the regions you want to export. The image edges act as boundaries too.
3. Select **Tools > Slice each layer using guides...** and enter the card dimensions and destination folder.
4. The plug-in checks every top-level layer and saves each matching region as a numbered PNG. Hidden layers are included unless skipped by the layer or color options.

## Parameters

1. **Card height/width in pixels**: self-explanatory, measure it before running the script with the 'Measure' tool.
1. **Margin of error**: This is a tolerance in case you don't exactly position the guide correctly but you still want the image to come out. Put 0 if you want exact measurements.
1. **Skip layers**: Skip even or odd layer positions, counted from 0 at the top of the layer stack. Useful when you don't want to extract the back side of a PDF with cards.
1. **Skip color**: Intended to allow skipping blank card spots on PDFs. This way you only save images with content. Usually you'll pick white (or the background color of the sheet in case it has a different one). It reads the average color of the middle of each zone divided by the guides.
1. **Skip color tolerance**: In case the script doesn't detect well the colors to skip you can play with this value to try to fix it. Example: A value of 0.1 means the color must be almost exactly the one you picked for the card spot to be skipped. Useful in situations where the valid cards are also light in color.
1. **Save folder**: Pick a folder to save images, otherwise it will give you an error.

## Testing platform

- GIMP 3 plug-in: tested with GIMP 3.2.6 on Windows 11. A headless integration check confirmed two guide regions, hidden layer export, skip color, and skip even layers; exported PNG dimensions and pixel colors were inspected.
- GIMP 2 plug-in: previously tested with GIMP 2.10.34 running Python 2.7.18 on Windows 11.
