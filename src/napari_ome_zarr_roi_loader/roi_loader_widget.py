"""
This widget allows users to load individual ROIs from an OME-Zarr file

Written by:
Joel Luethi, joel.luethi@fmi.ch
"""
import os
from pathlib import Path
from typing import TYPE_CHECKING, List

import napari
from magicgui import magic_factory
from magicgui.widgets import ComboBox, Container, FileEdit, PushButton
from napari.utils.notifications import show_info

from napari_ome_zarr_roi_loader.utils import load_intensity_roi

if TYPE_CHECKING:
    pass


def _init_loading_widget(widget):
    """
    ROI loader widget initialization

    Parameters
    ----------
    widget: napari widget
    """

    def get_roi_table_choices(*args):
        try:
            # FIXME: How to make this work also with remote urls like AWS?
            tables = [
                f
                for f in os.listdir(widget.zarr_url.value / "tables")
                if not f.startswith(".")
            ]
            if len(tables) == 0:
                show_info("No tables found")
                return [""]
            else:
                # widget.roi_table.choices = tables
                return tables
        except FileNotFoundError:
            return [""]
        except Exception as e:
            print(
                f"An {type(e)} Exception occured: \n{e}\n"
                "No ROI table choices were loaded"
            )
            return [""]

    # def get_roi_list(*args):
    #     pass

    # @widget.roi_table.changed.connect
    # def update_roi_list_choices():
    #     pass

    widget.roi_table._default_choices = get_roi_table_choices

    @widget.zarr_url.changed.connect
    def update_roi_tables():
        """
        Handles updating the list of available ROI tables
        """
        widget.roi_table.reset_choices()


@magic_factory(
    zarr_url={"label": "OME Zarr File", "mode": "d"},
    roi_table={"choices": [""], "label": "Name of ROI table:"},
    widget_init=_init_loading_widget,
)
def load_roi_widget(
    viewer: napari.Viewer,
    zarr_url: Path,
    roi_table: List[str],
    roi_of_interest: str,
    channel_index: int,
    level: int = 0,
):
    # TODO: Init for channel selection
    # Allow channel selection by name via dropdown instead of channel_index

    # TODO: Allow for label selection? Not in initial scope for first version

    # TODO: Refactor roi_index_of_interest to be selectors
    # Write a table loader that is cached.
    # Use it here and for the actual loading in the utils
    # => allows to do a check of the table here to list available ROIs &
    # to run a check that the table corresponds to expectations, without
    # loading it multiple time or overloading the
    # `convert_ROI_table_to_indices` function

    # TODO: Change level selection to a dropdown (similar to channels),
    # but simpler

    # Current selection: Just for individual OME-Zarr images, not HCS plates

    # TODO: Check that the ROI table contains relevant columns,
    # throw an informative error otherwise
    print(roi_table)
    img_roi, scale_img = load_intensity_roi(
        zarr_url,
        roi_of_interest,
        channel_index,
        level=level,
        roi_table=roi_table,
    )
    viewer.add_image(img_roi, scale=scale_img)


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
