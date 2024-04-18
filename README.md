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
1. **Save folder**: Pick a folder to save images, otherwise it defaults to the user home directory.

## Testing platform

Tested with GIMP 2.10.34 running Python 2.7.18 on Windows 11
