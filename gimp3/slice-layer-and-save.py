#!/usr/bin/env python3
"""Export guide-sized rectangles from every top-level layer as PNG files.

Port of Irian's GIMP 2.10 ``slice-layer-and-save.py`` for GIMP 3.2.
Install as ``plug-ins/slice-layer-and-save/slice-layer-and-save.py``.
"""

import math
import os
import sys

import gi

gi.require_version("Gimp", "3.0")
gi.require_version("GimpUi", "3.0")
gi.require_version("Gegl", "0.4")
from gi.repository import Gegl, Gio, GLib, Gimp, GimpUi, GObject


PROCEDURE_NAME = "python-fu-slice-layer-and-save"


def _guide_boundaries(image):
    """Return sorted image-space boundaries, without altering the image."""
    width, height = image.get_width(), image.get_height()
    horizontal, vertical = set(), set()
    guide_id = 0

    while True:
        guide_id = image.find_next_guide(guide_id)
        if guide_id == 0:
            break
        position = image.get_guide_position(guide_id)
        orientation = image.get_guide_orientation(guide_id)
        if orientation == Gimp.OrientationType.HORIZONTAL and 0 < position < height:
            horizontal.add(position)
        elif orientation == Gimp.OrientationType.VERTICAL and 0 < position < width:
            vertical.add(position)

    if not horizontal and not vertical:
        raise ValueError("No guides found. Add at least one guide before slicing.")

    return [0, *sorted(horizontal), height], [0, *sorted(vertical), width]


def _matching_rectangles(image, card_height, card_width, tolerance):
    horizontal, vertical = _guide_boundaries(image)
    minimum_area = max(0, card_height - tolerance) * max(0, card_width - tolerance)
    maximum_area = (card_height + tolerance) * (card_width + tolerance)
    rectangles = []

    for y1, y2 in zip(horizontal, horizontal[1:]):
        for x1, x2 in zip(vertical, vertical[1:]):
            area = (x2 - x1) * (y2 - y1)
            if minimum_area <= area <= maximum_area:
                rectangles.append((x1, y1, x2 - x1, y2 - y1))

    return rectangles


def _matches_skip_color(image, layer, rectangle, target_color, tolerance):
    x, y, width, height = rectangle
    center_x = x + width // 2
    center_y = y + height // 2
    radius = min(width, height) // 4
    success, sampled_color = image.pick_color(
        [layer], center_x, center_y, False, True, radius
    )
    if not success or sampled_color is None:
        return False

    sampled = sampled_color.get_rgba()
    target = target_color.get_rgba()
    distance = math.dist(
        (sampled.red, sampled.green, sampled.blue),
        (target.red, target.green, target.blue),
    )
    return distance <= tolerance


def _export_png(source_layer, source_image, rectangle, path):
    x, y, width, height = rectangle
    # Copy into a full-size image first. A smaller destination clips pixels
    # before the layer can be moved to the requested guide rectangle.
    image = Gimp.Image.new(
        source_image.get_width(), source_image.get_height(),
        source_image.get_base_type(),
    )
    if image is None:
        raise RuntimeError("Could not create a temporary image for export.")

    try:
        layer = Gimp.Layer.new_from_drawable(source_layer, image)
        if layer is None or not image.insert_layer(layer, None, 0):
            raise RuntimeError("Could not copy the layer into a temporary image.")
        # Export every page even when its source layer is hidden in the document.
        layer.set_visible(True)
        if not image.crop(width, height, x, y):
            raise RuntimeError("Could not crop the image to the guide rectangle.")

        exporter = Gimp.get_pdb().lookup_procedure("file-png-export")
        if exporter is None:
            raise RuntimeError("GIMP's PNG exporter is unavailable.")
        export_config = exporter.create_config()
        export_config.set_property("run-mode", Gimp.RunMode.NONINTERACTIVE)
        export_config.set_property("image", image)
        export_config.set_property("file", Gio.File.new_for_path(path))
        result = exporter.run(export_config)
        if result.index(0) != Gimp.PDBStatusType.SUCCESS:
            raise RuntimeError("PNG export failed for {}.".format(path))
    finally:
        image.delete()


def _next_filename(folder, number):
    while True:
        path = os.path.join(folder, "rect-{:03d}.png".format(number))
        if not os.path.exists(path):
            return path, number + 1
        number += 1


def run(procedure, run_mode, image, drawables, config, run_data):
    if run_mode == Gimp.RunMode.INTERACTIVE:
        GimpUi.init(PROCEDURE_NAME)
        dialog = GimpUi.ProcedureDialog.new(procedure, config)
        dialog.fill(None)
        accepted = dialog.run()
        dialog.destroy()
        if not accepted:
            return procedure.new_return_values(Gimp.PDBStatusType.CANCEL, GLib.Error())

    try:
        card_height = config.get_property("card-height")
        card_width = config.get_property("card-width")
        tolerance = config.get_property("tolerance")
        skip_layers = config.get_property("skip-layers")
        skip_color = config.get_property("skip-color")
        skip_color_tolerance = config.get_property("skip-color-tolerance")
        folder_file = config.get_property("save-folder")
        folder = folder_file.get_path() if folder_file is not None else None

        if card_height <= 0 or card_width <= 0:
            raise ValueError("Card height and width must be greater than zero.")
        if tolerance < 0 or skip_color_tolerance < 0:
            raise ValueError("Tolerances cannot be negative.")
        if not folder or not os.path.isdir(folder):
            raise ValueError("Choose an existing local save folder.")

        rectangles = _matching_rectangles(image, card_height, card_width, tolerance)
        if not rectangles:
            raise ValueError("No guide rectangles match the card dimensions and tolerance.")

        layers = image.get_layers()
        number = sum(
            os.path.isfile(os.path.join(folder, name)) for name in os.listdir(folder)
        ) + 1
        saved = 0

        for index, layer in enumerate(layers):
            if (skip_layers == "even" and index % 2 == 0) or (
                skip_layers == "odd" and index % 2 == 1
            ):
                continue
            for rectangle in rectangles:
                if _matches_skip_color(
                    image, layer, rectangle, skip_color, skip_color_tolerance
                ):
                    continue
                path, number = _next_filename(folder, number)
                _export_png(layer, image, rectangle, path)
                saved += 1

        Gimp.message("Saved {} image(s) in:\n{}".format(saved, folder))
        return procedure.new_return_values(Gimp.PDBStatusType.SUCCESS, GLib.Error())
    except Exception as error:
        Gimp.message("Slice each layer using guides: {}".format(error))
        return procedure.new_return_values(Gimp.PDBStatusType.EXECUTION_ERROR, GLib.Error())


class SliceLayerAndSave(Gimp.PlugIn):
    def do_set_i18n(self, procname):
        return False, None, None

    def do_query_procedures(self):
        return [PROCEDURE_NAME]

    def do_create_procedure(self, name):
        if name != PROCEDURE_NAME:
            return None

        procedure = Gimp.ImageProcedure.new(
            self, name, Gimp.PDBProcType.PLUGIN, run, None
        )
        procedure.set_image_types("*")
        procedure.set_documentation(
            "Slice each layer using guides",
            "Export guide rectangles matching the card area as numbered PNGs.",
            name,
        )
        procedure.set_menu_label("Slice each layer using guides...")
        procedure.set_attribution("irian-codes", "MIT", "2024-2026")
        procedure.add_menu_path("<Image>/Tools")

        flags = GObject.ParamFlags.READWRITE
        procedure.add_int_argument(
            "card-height", "Card height (pixels)", "Expected card height",
            1, 1000000, 1, flags
        )
        procedure.add_int_argument(
            "card-width", "Card width (pixels)", "Expected card width",
            1, 1000000, 1, flags
        )
        procedure.add_int_argument(
            "tolerance", "Margin of error (pixels)", "Allowed size difference",
            0, 1000000, 10, flags
        )

        choices = Gimp.Choice.new()
        choices.add("even", 0, "Even", "Skip layers 0, 2, 4, ...")
        choices.add("odd", 1, "Odd", "Skip layers 1, 3, 5, ...")
        choices.add("none", 2, "None", "Export every top-level layer")
        procedure.add_choice_argument(
            "skip-layers", "Skip layers? (pages in a PDF)",
            "Which layer positions to skip", choices, "none", flags
        )

        white = Gegl.Color.new("white")
        procedure.add_color_argument(
            "skip-color", "Color to skip", "Ignore cells matching this colour",
            True, white, flags
        )
        procedure.add_double_argument(
            "skip-color-tolerance", "Margin of error (color distance)",
            "RGB distance from the skip color", 0.0, 2.0, 0.1, flags
        )
        procedure.add_file_argument(
            "save-folder", "Save folder", "Folder for numbered PNGs",
            Gimp.FileChooserAction.SELECT_FOLDER, False, None, flags
        )
        return procedure


Gimp.main(SliceLayerAndSave.__gtype__, sys.argv)
