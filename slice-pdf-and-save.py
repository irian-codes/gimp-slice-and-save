#!/usr/bin/env python

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


def slice_layer_and_save(image, drawable, skipPages):
    # Set up an undo group, so the operation will be undone in one step.
    pdb.gimp_undo_push_group_start(image)

    # MAIN SCRIPT START

    guides = []
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

        guides.append(Guide(guideIndex, guideOrientation, guidePosition))

    pdb.gimp_message("heeey 1.3: " + ", ".join([guide.to_json() for guide in guides]))
    # MAIN SCRIPT END

    # Close the undo group.
    pdb.gimp_undo_push_group_end(image)


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
        (
            PF_OPTION,
            "skipPages",
            "Skip layers? (pages in a PDF)",
            2,
            ("Even", "Odd", "None"),
        ),
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
