from functools import lru_cache
from pathlib import Path
from typing import Iterable, List

import anndata as ad
import dask.array as da

# import matplotlib.pyplot as plt
import numpy as np
import zarr


def convert_ROI_table_to_indices(
    ROI: ad.AnnData,
    level: int = 0,
    pxl_sizes_zyx: Iterable[float] = None,
    cols_xyz_pos: Iterable[str] = [
        "x_micrometer",
        "y_micrometer",
        "z_micrometer",
    ],
    cols_xyz_len: Iterable[str] = [
        "len_x_micrometer",
        "len_y_micrometer",
        "len_z_micrometer",
    ],
) -> List[List[int]]:
    # Function based on
    # https://github.com/fractal-analytics-platform/fractal-tasks-core/blob/main/fractal_tasks_core/lib_regions_of_interest.py
    # Modified to directly use the pixel sizes loaded from the metadata
    # Written by @tcompa (Tommaso Comparin)

    # Set pyramid-level pixel sizes
    pxl_size_z, pxl_size_y, pxl_size_x = pxl_sizes_zyx

    x_pos, y_pos, z_pos = cols_xyz_pos[:]
    x_len, y_len, z_len = cols_xyz_len[:]

    origin_x = min(ROI[:, x_pos].X[:, 0])
    origin_y = min(ROI[:, y_pos].X[:, 0])
    origin_z = min(ROI[:, z_pos].X[:, 0])

    # list_indices = []
    indices_dict = {}
    for FOV in ROI.obs_names:

        # Extract data from anndata table
        x_micrometer = ROI[FOV, x_pos].X[0, 0] - origin_x
        y_micrometer = ROI[FOV, y_pos].X[0, 0] - origin_y
        z_micrometer = ROI[FOV, z_pos].X[0, 0] - origin_z
        len_x_micrometer = ROI[FOV, x_len].X[0, 0]
        len_y_micrometer = ROI[FOV, y_len].X[0, 0]
        len_z_micrometer = ROI[FOV, z_len].X[0, 0]

        # Identify indices along the three dimensions
        start_x = x_micrometer / pxl_size_x
        end_x = (x_micrometer + len_x_micrometer) / pxl_size_x
        start_y = y_micrometer / pxl_size_y
        end_y = (y_micrometer + len_y_micrometer) / pxl_size_y
        start_z = z_micrometer / pxl_size_z
        end_z = (z_micrometer + len_z_micrometer) / pxl_size_z
        indices = [start_z, end_z, start_y, end_y, start_x, end_x]

        # Round indices to lower integer
        indices = list(map(round, indices))

        # Append ROI indices to to list
        # ist_indices.append(indices[:])
        indices_dict[FOV] = indices[:]

    return indices_dict


# def load_label_roi_plate(
#     zarr_url,
#     well,
#     roi_index_of_interest,
#     labels_name,
#     level=0,
#     image_index=0,
#     roi_table="FOV_ROI_table",
# ):
#     # Loads the label image of a given ROI in a well
#     # returns the image as a numpy array + a list of the image scale

#     # image_index defaults to 0 (Change if you have more
#     # than one image per well) => FIXME for multiplexing

#     # Get the ROI table
#     roi_an = ad.read_zarr(
#         zarr_url / f"{well}/{image_index}/tables/{roi_table}"
#     )

#     # Load the pixel sizes from the OME-Zarr file
#     attrs_path = zarr_url / f"{well}/{image_index}/labels/{labels_name}"
#     dataset = 0  # FIXME, hard coded in case multiple multiscale
#     # datasets would be present & multiscales is a list
#     with zarr.open(attrs_path) as metadata:
#         scale_labels = metadata.attrs["multiscales"][dataset]["datasets"][
#             level
#         ]["coordinateTransformations"][0]["scale"]

#     # Get ROI indices for labels
#     list_indices = convert_ROI_table_to_indices(
#         roi_an,
#         level=level,
#         full_res_pxl_sizes_zyx=scale_labels,
#     )

#     # Get the indices for a given roi
#     indices = list_indices[roi_index_of_interest]
#     s_z, e_z, s_y, e_y, s_x, e_x = indices[:]

#     # Load labels
#     label_data_zyx = da.from_zarr(
#         zarr_url / f"{well}/{image_index}/labels/{labels_name}/{level}"
#     )
#     label_roi = label_data_zyx[s_z:e_z, s_y:e_y, s_x:e_x]
#     return np.array(label_roi), scale_labels


@lru_cache(maxsize=16)
def get_metadata(zarr_url):
    with zarr.open(zarr_url) as metadata:
        return metadata


@lru_cache(maxsize=16)
def read_roi_table(zarr_url: Path, roi_table):
    # FIXME: Make this work for cloud-based files => different paths
    table_url = zarr_url / f"tables/{roi_table}"
    return ad.read_zarr(table_url)


def get_channel_dict(zarr_url):
    metadata = get_metadata(zarr_url)
    channel_dict = {}
    try:
        for i, channel in enumerate(metadata.attrs["omero"]["channels"]):
            channel_dict[i] = channel
    except KeyError:
        pass

    return channel_dict


def get_label_dict(label_zarr_url):
    # Based on the label_zarr_url, load the available labels
    # params: label_zarr_url: Path to the label folder in the OME-Zarr file

    # Check that the label folder exists
    if not label_zarr_url.exists():
        return {}

    metadata = get_metadata(label_zarr_url)
    label_dict = {}
    try:
        for i, label in enumerate(metadata.attrs["labels"]):
            label_dict[i] = label
    except KeyError:
        pass

    return label_dict


def load_intensity_roi(
    zarr_url,
    roi_of_interest,
    channel_index,
    level=0,
    roi_table="FOV_ROI_table",
):
    # Loads the intensity image of a given ROI in a well
    # returns the image as a numpy array + a list of the image scale

    # image_index defaults to 0 (Change if you have more than one
    # image per well) => FIXME for multiplexing

    # Get the ROI table
    roi_an = read_roi_table(zarr_url, roi_table)

    # Load the pixel sizes from the OME-Zarr file
    dataset = 0  # FIXME, hard coded in case multiple multiscale
    # datasets would be present & multiscales is a list
    metadata = get_metadata(zarr_url)
    scale_img = metadata.attrs["multiscales"][dataset]["datasets"][level][
        "coordinateTransformations"
    ][0]["scale"]

    # Get ROI indices for labels
    indices_dict = convert_ROI_table_to_indices(
        roi_an,
        level=level,
        pxl_sizes_zyx=scale_img,
    )

    # Get the indices for a given roi
    indices = indices_dict[roi_of_interest]
    s_z, e_z, s_y, e_y, s_x, e_x = indices[:]

    # Load data
    img_data_zyx = da.from_zarr(f"{zarr_url}/{level}")[channel_index]
    img_roi = img_data_zyx[s_z:e_z, s_y:e_y, s_x:e_x]

    return np.array(img_roi), scale_img


def load_label_roi(
    zarr_url,
    roi_of_interest,
    label_name,
    target_scale=None,
    roi_table="FOV_ROI_table",
):
    # Loads the label image of a given ROI in a well
    # returns the image as a numpy array + a list of the image scale

    # Get the ROI table
    roi_an = read_roi_table(zarr_url, roi_table)

    # Load the pixel sizes from the OME-Zarr file
    scales = get_available_scales(zarr_url / "labels" / label_name)
    if target_scale:
        level = get_closest_scale(target_scale, scales)
        scale_lbls = scales[level]
    else:
        level = "0"
        scale_lbls = scales[level]

    # Get ROI indices for labels
    indices_dict = convert_ROI_table_to_indices(
        roi_an,
        level=level,
        pxl_sizes_zyx=scale_lbls,
    )

    # Get the indices for a given roi
    indices = indices_dict[roi_of_interest]
    s_z, e_z, s_y, e_y, s_x, e_x = indices[:]

    # Load data
    lbl_data_zyx = da.from_zarr(zarr_url / "labels" / label_name / level)
    lbl_roi = lbl_data_zyx[s_z:e_z, s_y:e_y, s_x:e_x]

    return np.array(lbl_roi), scale_lbls


def get_available_scales(zarr_url):
    metadata = get_metadata(zarr_url)
    dataset = 0  # FIXME, hard coded in case multiple multiscale
    # datasets would be present & multiscales is a list
    available_scales = {}
    levels = metadata.attrs["multiscales"][dataset]["datasets"]
    for level in levels:
        for transformation in level["coordinateTransformations"]:
            if transformation["type"] == "scale":
                available_scales[level["path"]] = transformation["scale"]
            else:
                pass
                # Ignore other transformations
    return available_scales


def get_closest_scale(target_scale, scales):
    """
    Should mostly provide either the highest resolution or the one exactly
    matching the target scale, given that label images are usually downsampled.
    But would need to generalize to handle arbitrary target_scales better.

    params: target_scale: list of floats
            scales: dict of scales. Keys are the names of the folders in the
                    OME-Zarr, values are the scales (list of floats)
    """
    closest_scale = list(scales.keys())[0]
    for key, val in scales.items():
        if np.linalg.norm(
            np.array(val) - np.array(target_scale)
        ) < np.linalg.norm(
            np.array(scales[closest_scale]) - np.array(target_scale)
        ):
            closest_scale = key

    return closest_scale
