# GIMP Script: Slice layer and save (with constraints)

This script is intended to be used with PDFs but can be used with any file with one or more layers. It saves one image inside the zone defined by guides and within specified dimensions.

Use cases:

- Extracting individual board game cards from PDFs shared by people
- Save an image in different parts.

## Installation

Check your GIMP plugins folder [like this](https://www.gimp-forum.net/Thread-Where-is-PLUGINS-in-GIMP). Then copy and paste `slice-layer-and-save.py` into that folder.

## How to use

1. Open a PDF in GIMP, importing all the pages.
1. Set your guides where you want to slice the PDF.
1. Run the script and configure it.
1. The script will save each zone in its own image in the specified folder.
1. Select another layer you want to slice and repeat from step 3 until you have all your cards.

## Parameters

1. **Card height/width in pixels**: self-explanatory, measure it before running the script with the 'Measure' tool.
1. **Margin of error**: This is a tolerance in case you don't exactly position the guide correctly but you still want the image to come out. Put 0 if you want exact measurements.
1. **Skip layers**: Skip each odd or even layer entirely. Useful for when you don't want to extract the back side of a PDF with cards.
1. **Skip color**: Intended to allow skipping blank card spots on PDFs. This way you only save images with content. Usually you'll pick white (or the background color of the sheet in case it has a different one). It reads the average color of the middle of each zone divided by the guides.
1. **Skip color tolerance**: In case the script doesn't detect well the colors to skip you can play with this value to try to fix it. Example: A value of 0.1 means the color must be almost exactly the one you picked for the card spot to be skipped. Useful in situations where the valid cards are also light in color.
1. **Save folder**: Pick a folder to save images, otherwise it will give you an error.

## Testing platform

Tested with GIMP 2.10.34 running Python 2.7.18 on Windows 11
