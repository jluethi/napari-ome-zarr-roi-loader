"""
This widget allows users to load individual ROIs from an OME-Zarr file

Written by:
Joel Luethi, joel.luethi@fmi.ch
"""
import os
from pathlib import Path

import napari
import zarr
from magicgui.widgets import ComboBox, Container, FileEdit, PushButton, Select
from napari.utils.notifications import show_info

from napari_ome_zarr_roi_loader.utils import (
    get_channel_dict,
    get_label_dict,
    get_metadata,
    load_intensity_roi,
    read_roi_table,
)


class RoiLoader(Container):
    def __init__(self, viewer: napari.viewer.Viewer):
        self._viewer = viewer
        self.channel_dict = {}
        self.channel_names_dict = {}
        self.labels_dict = {}
        self._zarr_url_picker = FileEdit(label="Zarr URL", mode="d")
        self._roi_table_picker = ComboBox(label="ROI Table")
        self._roi_picker = ComboBox(label="ROI")
        self._channel_picker = Select(
            label="Channels",
        )
        self._level_picker = ComboBox(label="Level")
        self._label_picker = Select(
            label="Labels",
        )
        self._run_button = PushButton(value=False, text="Load ROI")

        # Initialize possible choices
        self.update_roi_tables()
        self.update_roi_selection()

        # Update selections & bind buttons
        self._zarr_url_picker.changed.connect(self.update_roi_tables)
        self._run_button.clicked.connect(self.run)
        self._roi_table_picker.changed.connect(self.update_roi_selection)

        super().__init__(
            widgets=[
                self._zarr_url_picker,
                self._roi_table_picker,
                self._roi_picker,
                self._channel_picker,
                self._level_picker,
                self._label_picker,
                self._run_button,
            ]
        )

    def run(self):
        roi_table = self._roi_table_picker.value
        roi_name = self._roi_picker.value
        level = self._level_picker.value
        channels = self._channel_picker.value
        if len(channels) < 1:
            show_info(
                "No channel selected. Select the channels you want to load"
            )
            return
        blending = None
        for channel in channels:
            img_roi, scale_img = load_intensity_roi(
                zarr_url=self._zarr_url_picker.value,
                roi_of_interest=roi_name,
                channel_index=self.channel_names_dict[channel],
                level=level,
                roi_table=roi_table,
            )
            channel_meta = self.channel_dict[self.channel_names_dict[channel]]
            # TODO: Figure out how to use the colormaps from the metadata
            # colormap = channel_meta["color"]
            # TODO: Make rescaling optional?
            rescaling = (
                channel_meta["window"]["start"],
                channel_meta["window"]["end"],
            )
            self._viewer.add_image(
                img_roi,
                scale=scale_img,
                blending=blending,
                contrast_limits=rescaling,
            )
            blending = "additive"

    def update_roi_tables(self):
        """
        Handles updating the list of available ROI tables
        """
        # Uses the `_default_choices` to avoid having choices reset.
        # See https://github.com/pyapp-kit/magicgui/issues/306
        roi_table = self._get_roi_table_choices()
        self._roi_table_picker.choices = roi_table
        self._roi_table_picker._default_choices = roi_table

    def update_roi_selection(self):
        # Uses the `_default_choices` to avoid having choices reset.
        # See https://github.com/pyapp-kit/magicgui/issues/306
        new_rois = self._get_roi_choices()
        self._roi_picker.choices = new_rois
        self._roi_picker._default_choices = new_rois
        channels = self._get_channel_choices()
        self._channel_picker.choices = channels
        self._channel_picker._default_choices = channels
        levels = self._get_level_choices()
        self._level_picker.choices = levels
        self._level_picker._default_choices = levels

        # Initialize available label images
        labels = self._get_label_choices()
        self._label_picker.choices = labels
        self._label_picker._default_choices = labels

    def _get_roi_table_choices(self):
        try:
            # FIXME: How to make this work also with remote urls like AWS?
            tables = [
                f
                for f in os.listdir(self._zarr_url_picker.value / "tables")
                if not f.startswith(".")
            ]
            if len(tables) == 0:
                show_info("No tables found")
                return [""]
            else:
                return sorted(tables)
        except FileNotFoundError:
            return [""]
        except Exception as e:
            print(
                f"An {type(e)} Exception occured: \n{e}\n"
                "No ROI table choices were loaded"
            )
            return [""]

    def _get_roi_choices(self):
        if not self._roi_table_picker.value:
            # When no roi table is provided.
            # E.g. during bug with self._roi_table_picker reset
            return [""]
        try:
            roi_table = read_roi_table(
                self._zarr_url_picker.value, self._roi_table_picker.value
            )
            new_choices = list(roi_table.obs_names)
            return new_choices
        except zarr.errors.PathNotFoundError:
            new_choices = [""]
            return new_choices

    def _get_channel_choices(self):
        self.channel_dict = get_channel_dict(self._zarr_url_picker.value)
        self.channel_names_dict = {}
        for channel_index in self.channel_dict.keys():
            channel_name = self.channel_dict[channel_index]["label"]
            self.channel_names_dict[channel_name] = channel_index
        return list(self.channel_names_dict.keys())

    def _get_label_choices(self):
        self.label_dict = get_label_dict(
            Path(self._zarr_url_picker.value) / "labels"
        )
        return list(self.label_dict.values())
        # self.labels_names_dict = {}
        # for label_index in self.label_dict.keys():
        #     label_name = self.label_dict[label_index]
        #     self.labels_names_dict[label_name] = label_index
        # return list(self.labels_names_dict.keys())

    def _get_level_choices(self):
        try:
            metadata = get_metadata(self._zarr_url_picker.value)
            dataset = 0  # FIXME, hard coded in case multiple multiscale
            # datasets would be present & multiscales is a list
            nb_levels = len(metadata.attrs["multiscales"][dataset]["datasets"])
            return list(range(nb_levels))
        except KeyError:
            # This happens when no valid OME-Zarr file is selected, thus no
            # metadata file is found & no levels can be set
            return [""]
