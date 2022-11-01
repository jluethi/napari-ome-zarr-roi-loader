"""
This widget allows users to load individual ROIs from an OME-Zarr file

Written by:
Joel Luethi, joel.luethi@fmi.ch
"""
from pathlib import Path
from typing import TYPE_CHECKING

from magicgui import magic_factory
from napari import Viewer  # pylint: disable-msg=E0611

from napari_ome_zarr_roi_loader.utils import load_intensity_roi

if TYPE_CHECKING:
    pass


# TODO: Init for ROI tables (drop down with relevant selection)
# TODO: Init for channel/label selection
# (separate the two or have them in one list?)
@magic_factory(zarr_url={"label": "OME Zarr File", "mode": "d"})
def load_roi_widget(
    viewer: Viewer,
    zarr_url: Path,
    roi_table: str,
    roi_index_of_interest: int,
    channel_index: int,
    level: int = 0,
):
    # TODO: Refactor roi_index_of_interest & channel_index to be selectors
    # Current selection: Just for individual OME-Zarr images, not HCS plates

    img_roi, scale_img = load_intensity_roi(
        zarr_url, roi_index_of_interest, channel_index, level=0
    )
    viewer.add_image(img_roi, scale=scale_img)
