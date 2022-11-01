"""
This widget allows users to load individual ROIs from an OME-Zarr file

Written by:
Joel Luethi, joel.luethi@fmi.ch
"""
import os
from pathlib import Path
from typing import TYPE_CHECKING, List

from magicgui import magic_factory
from napari import Viewer  # pylint: disable-msg=E0611
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

    widget.roi_table._default_choices = get_roi_table_choices

    @widget.zarr_url.changed.connect
    def update_roi_tables():
        """
        Handles updating the list of available ROI tables
        """
        widget.roi_table.reset_choices()


# TODO: Init for ROI tables (drop down with relevant selection)
# TODO: Init for channel/label selection
# (separate the two or have them in one list?)
@magic_factory(
    zarr_url={"label": "OME Zarr File", "mode": "d"},
    roi_table={"choices": [""], "label": "Name of ROI table:"},
    widget_init=_init_loading_widget,
)
def load_roi_widget(
    viewer: Viewer,
    zarr_url: Path,
    roi_table: List[str],
    roi_index_of_interest: int,
    channel_index: int,
    level: int = 0,
):
    # TODO: Refactor roi_index_of_interest & channel_index to be selectors
    # Current selection: Just for individual OME-Zarr images, not HCS plates
    print(roi_table)
    img_roi, scale_img = load_intensity_roi(
        zarr_url,
        roi_index_of_interest,
        channel_index,
        level=level,
        roi_table=roi_table,
    )
    viewer.add_image(img_roi, scale=scale_img)
