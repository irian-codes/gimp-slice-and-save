#!/usr/bin/env python
# v1.0.0

import os
import json
from gimpfu import *


class Guide:
    """
    Represents a guide in a GIMP Image.

    Attributes:
        index (int): The index of the guide.
        orientation (int): The orientation of the guide (0 is horizontal, 1 is vertical).
        position (int): The position of the guide in pixels from the top or left, depending on the orientation.
    """

    def __init__(self, index, orientation, position):
        self.index = index
        self.orientation = orientation
        self.position = position

    def to_json(self):
        """
        Converts the Guide object to a JSON-valid string.

        Returns:
            str: A JSON-valid string representing the Guide object.
        """
        guide_dict = {
            "index": self.index,
            "orientation": self.orientation,
            "position": self.position,
        }

        return json.dumps(guide_dict)
    
class Rectangle:
    """
    Represents a rectangular shape.

    Attributes:
        x1 (int): The x-coordinate of the top-left corner of the rectangle.
        y1 (int): The y-coordinate of the top-left corner of the rectangle.
        x2 (int): The x-coordinate of the bottom-right corner of the rectangle.
        y2 (int): The y-coordinate of the bottom-right corner of the rectangle.
    """
    def __init__(self, x1, y1, x2, y2):
        self.x1 = x1
        self.y1 = y1
        self.x2 = x2
        self.y2 = y2
    
    @property
    def area(self):
        """
        Calculates the area of the rectangle.

        Returns:
            int: The area of the rectangle.
        """
        return (self.x2 - self.x1) * (self.y2 - self.y1)
    
    @property
    def width(self):
        return self.x2 - self.x1
    
    @property
    def height(self):
        return self.y2 - self.y1
    
    def to_json(self):
        """
        Converts the Rectangle object to a JSON-valid string.

        Returns:
            str: A JSON-valid string representing the Rectangle object.
        """
        rect_dict = {
            "x1": self.x1,
            "y1": self.y1,
            "x2": self.x2,
            "y2": self.y2,
            "height": self.height,
            "width": self.width,
            "area": self.area,
        }

        return json.dumps(rect_dict)

def slice_layer_and_save(image, drawable, cardHeight, cardWidth, tolerance, skipPages, saveFolder):
    # Set up an undo group, so the operation will be undone in one step.
    pdb.gimp_undo_push_group_start(image)

    inputValidationResult = inputValidation(image, saveFolder=saveFolder)
    
    if inputValidationResult[0] == False:
        exit_script(image, inputValidationResult[1])
        return

    # MAIN SCRIPT START

    (guidesH, guidesV) = getGuides(image)
    tryInsertHelperGuides(image, drawable, guidesH, guidesV)

    rectangles = getRectangles(guidesH, guidesV, cardHeight, cardWidth, tolerance)
    saveRectanglesAsImage(image, drawable, rectangles, saveFolder)
    # MAIN SCRIPT END

    exit_script(image, "Done! Images saved in:\n" + saveFolder)

def exit_script(image, message):
    pdb.gimp_message(message)
    pdb.gimp_undo_push_group_end(image)

def tryInsertHelperGuide(image, drawable, guides, orientation):
   guideFound = False
   if orientation == 1:
       targetPosition = pdb.gimp_image_width(image)
   else:
       targetPosition = pdb.gimp_image_height(image)

   for guide in reversed(guides):
       if guide.position == targetPosition:
        guideFound = True
        break
    
   if guideFound == False:
        pdb.script_fu_guide_new_percent(image, drawable, orientation, 100)

def tryInsertHelperGuides(image, drawable, guidesH, guidesV):
   """	
   Tries to insert a guide to the right side of the image.
   This eases the process of creating rectangles from guides.
   """
   tryInsertHelperGuide(image, drawable, guidesH, 0)
   tryInsertHelperGuide(image, drawable, guidesV, 1)

def getGuides(image):
    guidesH = []
    guidesV = []
    # Init at +inf to allow entering the while loop first time.
    guideIndex = float("inf")

    while guideIndex > 0:
        # After we pass the last guide index it returns 0 indicating there are no more guides.
        # But if we pass 0 it returns the first guide again, so it's a circular linked list.
        # Thus we set it to 0 and when it returns to 0 it means we've cycled over all guides.
        if guideIndex == float("inf"):
            guideIndex = 0

        guideIndex = pdb.gimp_image_find_next_guide(image, guideIndex)

        # To avoid any crashes
        if guideIndex == 0:
            break

        guideOrientation = pdb.gimp_image_get_guide_orientation(image, guideIndex)
        guidePosition = pdb.gimp_image_get_guide_position(image, guideIndex)

        if guideOrientation == 0:
            guidesH.append(Guide(guideIndex, guideOrientation, guidePosition))
        else:
            guidesV.append(Guide(guideIndex, guideOrientation, guidePosition))

    if len(guidesH) == 0 and len(guidesV) == 0:
        exit_script(image, "No guides found. Please add at least one guide.")
        return

    # I want the guides sorted first by Horizontal and then their position to group them.
    guidesH.sort(key=lambda guide: guide.position)
    guidesV.sort(key=lambda guide: guide.position)

    return (guidesH, guidesV)

def getRectangles(guidesH, guidesV, cardHeight, cardWidth, tolerance):
    rectangles = []
    # For each horizontal guide loop through all vertical guides
    previousHPos = 0
    for h_guide in guidesH:
        previousVPos = 0

        for v_guide in guidesV:
            x1 = previousVPos
            y1 = previousHPos
            x2 = v_guide.position
            y2 = h_guide.position
            minArea = (cardHeight - tolerance) * (cardWidth - tolerance)
            maxArea =  (cardHeight + tolerance) * (cardWidth + tolerance)

            rect = Rectangle(x1, y1, x2, y2)

            if minArea <= rect.area <= maxArea:
                rectangles.append(rect)

            previousVPos = v_guide.position
        
        previousHPos = h_guide.position

    return rectangles

def saveRectanglesAsImage(image, drawable,rectangles, saveFolder):
    for i, rect in enumerate(rectangles):
        filePath = os.path.join(saveFolder, "rect-{0:03d}.png".format(i+1))

        newImage = gimp.Image(rect.width, rect.height, image.base_type)
        layerCopy = pdb.gimp_layer_new_from_drawable(drawable, newImage)
        newImage.add_layer(layerCopy, 0)
        
        pdb.gimp_layer_resize(layerCopy, rect.width, rect.height, -rect.x1, -rect.y1)

        pdb.gimp_file_save(newImage, layerCopy, filePath, filePath)
        gimp.delete(newImage)

def inputValidation(image, saveFolder):
    errorMessage = ""

    if not os.path.exists(saveFolder):
        errorMessage = "Folder {0} does not exist.".format(saveFolder)
        return (False, errorMessage)
    
    return (True, "")

register(
    "python_fu_slice_layer_and_save",
    "Slices a layer according to guides and saves each zone as a separate image",
    "When guides have been set up, the script gets the guides zones from them. Then it gets each zone that matches the configuration criteria and saves them as an image file.",
    "irian-codes",
    "MIT",
    "2024",
    "Slice each layer using guides",  # Label of the script inside the menu.
    "*",  # type of image it works on (*, RGB, RGB*, RGBA, GRAY etc...)
    [
        # PARAMETERS TO CREATE AN UI TO GET USER INPUT.
        # basic parameters are: (UI_ELEMENT, "variable", "label", Default)
        # PF_IMAGE and PF_DRAWABLE are mandatory in <Image> scripts but careful because if the path it's only <Image> without nothing elste they get autoadded and if you specify them you'll get an error.
        (PF_IMAGE, "image", "Active image", None),
        (PF_DRAWABLE, "drawable", "Input layer", None),
        (PF_INT, "cardHeight", "Card height (in pixels)", 0),
        (PF_INT, "cardWidth", "Card width (in pixels)", 0),
        (PF_INT, "tolerance", "Margin of error (in pixels)", 10),
        (
            PF_OPTION,
            "skipPages",
            "Skip layers? (pages in a PDF)",
            2,
            ("Even", "Odd", "None"),
        ),
        (PF_DIRNAME, 'saveFolder', 'Save folder', '.')
        # PF_SLIDER, SPINNER have an extra tuple (min, max, step)
        # PF_RADIO has an extra tuples within a tuple:
        # eg. (("radio_label", "radio_value), ...) for as many radio buttons
        # PF_OPTION has an extra tuple containing options in drop-down list
        # eg. ("opt1", "opt2", ...) for as many options
        # see ui_examples_1.py and ui_examples_2.py for live examples
    ],
    [],
    slice_layer_and_save,
    menu="<Image>/Tools",  # Menu path, f.e. <Image>/Tools/StandeesFiller.  Needs root image.
)
main()

# CHANGELOG:
# v1.0.0: Initial version.
