"""
This widget allows users to load individual ROIs from an OME-Zarr file

Written by:
Joel Luethi, joel.luethi@fmi.ch
"""
import os

import napari
from magicgui.widgets import ComboBox, Container, FileEdit, PushButton
from napari.utils.notifications import show_info

from napari_ome_zarr_roi_loader.utils import load_intensity_roi


class RoiLoader(Container):
    def __init__(self, viewer: napari.viewer.Viewer):
        self._viewer = viewer
        self._zarr_url_picker = FileEdit(label="Zarr URL")
        self._roi_table_picker = ComboBox(
            label="ROI Table", choices=self._get_roi_table_choices()
        )
        self._roi_picker = ComboBox(
            label="ROI", choices=self._get_roi_choices()
        )
        # TODO: Make channel selection multi-select
        self._channel_picker = ComboBox(
            label="Channels", choices=self._get_channel_choices()
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
        selected_value = self._roi_table_picker.value
        img_roi, scale_img = load_intensity_roi(
            zarr_url=self._zarr_url_picker.value,
            roi_of_interest=self._roi_picker.value,
            channel_index=self._channel_picker.value,
            level=self._level_picker.value,
            roi_table=self._roi_table_picker.value,
        )
        self._viewer.add_image(img_roi, scale=scale_img)

        # FIXME: For some reason, running currently resets the
        # self._roi_table_picker choices to an empty list. This works around
        # that. No idea why this reset is happening though.
        self.update_roi_tables()
        self._roi_table_picker.value = selected_value

    def update_roi_tables(self):
        """
        Handles updating the list of available ROI tables
        """
        self._roi_table_picker.choices = self._get_roi_table_choices()

    def update_roi_selection(self):
        print("ROI table picker has changed")
        # TODO: Trigger update of level, channels & ROI choices

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
        # FIXME: Add actual inference for choices
        return ["FOV_36"]

    def _get_channel_choices(self):
        # FIXME: Add actual inference for choices
        return [0]

    def _get_level_choices(self):
        # FIXME: Add actual inference for choices
        return [0, 1, 2, 3, 4]
