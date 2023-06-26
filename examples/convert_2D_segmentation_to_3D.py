"""Fractal task to convert 2D segmentations into 3D segmentations"""
import logging
from pathlib import Path

import anndata as ad
import dask.array as da
import numpy as np
import zarr
from anndata._io.specs import write_elem
from ome_zarr.writer import write_labels
from pydantic.decorator import validate_arguments

logger = logging.getLogger(__name__)


def read_table(zarr_url: Path, roi_table):
    table_url = zarr_url / f"tables/{roi_table}"
    return ad.read_zarr(table_url)


def update_table_metadata(group_tables, table_name):
    if "tables" not in group_tables.attrs:
        group_tables.attrs["tables"] = [table_name]
    elif table_name not in group_tables.attrs["tables"]:
        group_tables.attrs["tables"] = group_tables.attrs["tables"] + [
            table_name
        ]


@validate_arguments
def convert_2D_segmentation_to_3D(
    input_paths,
    output_path,
    component,
    metadata,
    label_name: str,
    ROI_tables_to_copy: list[str],
    new_label_name: str = None,
    new_table_names: list = None,
    level: int = 0,
    suffix: str = "mip",
):
    """
    This task loads the 2D segmentation, replicates it along the Z slice and
    stores it back into the 3D OME-Zarr image.

    This is a temporary workaround task, as long as we store 2D data in
    a separate OME-Zarr file from the 3D data. Also, some assumptions are made
    on the metadata structure, generalization to be tested.

    :param input_paths: List of paths to the input files (Fractal managed)
    :param output_path: Path to the output file (Fractal managed)
    :param component: Component name, e.g. "plate_name.zarr/B/03/0"
                      (Fractal managed)
    :param metadata: Metadata dictionary (Fractal managed)
    :param label_name: Name of the label to copy from 2D OME-Zarr to
                       3D OME-Zarr
    :param ROI_tables_to_copy: List of ROI table names to copy from 2D OME-Zarr
                               to 3D OME-Zarr
    :param new_label_name: Optionally overwriting the name of the label in
                           the 3D OME-Zarr
    :param new_table_names: Optionally overwriting the names of the ROI tables
                            in the 3D OME-Zarr
    :param level: Level of the 2D OME-Zarr label to copy from
    :param suffix: Suffix of the 2D OME-Zarr to copy from
    """
    # TODO: Not using output_path atm, but hard-coded to expect the output
    # component in the input path

    if level != 0:
        raise NotImplementedError("Only level 0 is supported at the moment")
    zarr_url = Path(input_paths[0]) / component
    zarr_3D_url = Path(input_paths[0]) / component.replace(
        f"_{suffix}.zarr", ".zarr"
    )
    if new_label_name is None:
        new_label_name = label_name
    if new_table_names is None:
        new_table_names = ROI_tables_to_copy
    # TODO: Check that new table names are unique and match in length to
    # ROI_tables_to_copy

    # 1a) Load a 2D label image
    label_img = da.from_zarr(f"{zarr_url}/labels/{label_name}/{level}")
    chunks = label_img.chunksize
    with zarr.open(
        f"{zarr_url}/labels/{label_name}", mode="rw+"
    ) as zarr_label_img:
        coordinate_transforms_label_img = zarr_label_img.attrs["multiscales"][
            0
        ]["datasets"]

    # 1b) Get number z planes & Z spacing from 3D OME-Zarr file
    with zarr.open(zarr_3D_url, mode="rw+") as zarr_img:
        zarr_3D = da.from_zarr(zarr_img[0])
        new_z_planes = zarr_3D.shape[-3]
        z_pixel_size = zarr_img.attrs["multiscales"][0]["datasets"][0][
            "coordinateTransformations"
        ][0]["scale"][0]

    # 2) Create the 3D stack of the label image
    label_img_3D = da.stack([label_img.squeeze()] * new_z_planes)
    label_img_3D

    # 3) Save changed label image to OME-Zarr
    with zarr.open(zarr_3D_url, mode="rw+") as zarr_img:
        write_labels(
            label_img_3D,
            zarr_img,
            name=new_label_name,
            axes="zyx",
            chunks=chunks,
            storage_options={"dimension_separator": "/"},
        )

        # Hacky way of ensuring we have the correct metadata, because the
        # writer doesn't get the metadata right yet.
        axes = zarr_img.attrs["multiscales"][0]["axes"]
        labels_zarr = zarr_img[f"labels/{new_label_name}"]
        multiscales = labels_zarr.attrs["multiscales"]
        multiscales[0]["datasets"] = coordinate_transforms_label_img
        # Skip the channels axis, because this image contains no channels
        multiscales[0]["axes"] = axes[1:]
        labels_zarr.attrs["multiscales"] = multiscales

        # Update ROI tables
        for i, ROI_table in enumerate(ROI_tables_to_copy):
            new_table_name = new_table_names[i]
            roi_an = read_table(Path(zarr_url), ROI_table)
            nb_rois = len(roi_an.X)
            # Set the new Z values to span the whole ROI
            roi_an.X[:, 5] = np.array([z_pixel_size * new_z_planes] * nb_rois)

            # TODO: Check that the table doesn't exist yet.
            # Otherwise make an overwrite check?

            # Save the ROI table to the 3D OME-Zarr file
            group_tables = zarr_img.require_group("tables/")
            write_elem(group_tables, new_table_name, roi_an)

            # Update the tables .zattrs for the new table
            update_table_metadata(group_tables, new_table_name)

    return {}


if __name__ == "__main__":
    from fractal_tasks_core._utils import run_fractal_task

    run_fractal_task(
        task_function=convert_2D_segmentation_to_3D,
        logger_name=logger.name,
    )
