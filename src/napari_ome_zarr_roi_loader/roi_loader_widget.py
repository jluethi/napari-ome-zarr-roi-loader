"""
This widget allows users to load individual ROIs from an OME-Zarr file

Written by:
Joel Luethi, joel.luethi@fmi.ch
"""
import os

import napari
import zarr
from magicgui.widgets import ComboBox, Container, FileEdit, PushButton, Select
from napari.utils.notifications import show_info

from napari_ome_zarr_roi_loader.utils import (
    get_channel_dict,
    get_metadata,
    load_intensity_roi,
    read_roi_table,
)


class RoiLoader(Container):
    def __init__(self, viewer: napari.viewer.Viewer):
        self._viewer = viewer
        self.channel_dict = {}
        self.channel_names_dict = {}
        self._zarr_url_picker = FileEdit(label="Zarr URL", mode="d")
        self._roi_table_picker = ComboBox(
            label="ROI Table", choices=self._get_roi_table_choices()
        )
        self._roi_picker = ComboBox(
            label="ROI", choices=self._get_roi_choices()
        )
        # TODO: Make channel selection multi-select
        self._channel_picker = Select(
            label="Channels",
            choices=self._get_channel_choices(),
        )
        self._level_picker = ComboBox(
            label="Level", choices=self._get_level_choices()
        )
        self._run_button = PushButton(value=False, text="Load ROI")

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

        # FIXME: For some reason, running currently resets the
        # self._roi_table_picker choices to an empty list. This works around
        # that. No idea why this reset is happening though. See
        # https://github.com/jluethi/napari-ome-zarr-roi-loader/issues/3
        self.update_roi_tables()
        self._roi_table_picker.value = roi_table
        self._roi_picker.value = roi_name
        self._level_picker.value = level
        self._channel_picker.value = channels

    def update_roi_tables(self):
        """
        Handles updating the list of available ROI tables
        """
        self._roi_table_picker.choices = self._get_roi_table_choices()

    def update_roi_selection(self):
        self._roi_picker.choices = self._get_roi_choices()
        self._channel_picker.choices = self._get_channel_choices()
        self._level_picker.choices = self._get_level_choices()

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
                return tables
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
            return list(roi_table.obs_names)
        except zarr.errors.PathNotFoundError:
            return [""]

    def _get_channel_choices(self):
        self.channel_dict = get_channel_dict(self._zarr_url_picker.value)
        self.channel_names_dict = {}
        for channel_index in self.channel_dict.keys():
            channel_name = self.channel_dict[channel_index]["label"]
            self.channel_names_dict[channel_name] = channel_index
        return list(self.channel_names_dict.keys())

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
