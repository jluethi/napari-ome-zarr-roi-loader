"""Convert metdata components from 2D to 3D Fractal task"""
import logging

from pydantic.decorator import validate_arguments

logger = logging.getLogger(__name__)


@validate_arguments
def convert_metadata_components_2D_to_3D(
    input_paths,
    output_path,
    metadata,
    from_2d_to_3d: bool = True,
    suffix: str = "mip",
):
    """
    Workaround task to manually change the hard-coded metadata components
    A fractal workflow sets them to the mip.zarr components after running the
    maximum intensity projection task. This resets them to the 3D components.

    :param input_paths: List of paths to the input files (Fractal managed)
    :param output_path: Path to the output file (Fractal managed)
    :param component: Component name, e.g. "plate_name.zarr/B/03/0"
                      (Fractal managed)
    :param metadata: Metadata dictionary (Fractal managed)
    :param from_2d_to_3d: If True, removes the suffix. If False,
                          adds the suffix to the metadata
    :param suffix: Suffix of the 2D OME-Zarr
    """
    old_image_list = metadata["image"]
    old_well_list = metadata["well"]
    old_plate_list = metadata["plate"]
    new_image_list = []
    new_well_list = []
    new_plate_list = []
    if from_2d_to_3d:
        old_value = f"_{suffix}.zarr"
        new_value = ".zarr"
    else:
        old_value = ".zarr"
        new_value = f"_{suffix}.zarr"
    for image in old_image_list:
        new_image_list.append(image.replace(old_value, new_value))
    for well in old_well_list:
        new_well_list.append(well.replace(old_value, new_value))
    for plate in old_plate_list:
        new_plate_list.append(plate.replace(old_value, new_value))
    metadata["image"] = new_image_list
    metadata["well"] = new_well_list
    metadata["plate"] = new_plate_list

    return metadata


if __name__ == "__main__":
    from fractal_tasks_core.tasks._utils import run_fractal_task

    run_fractal_task(
        task_function=convert_metadata_components_2D_to_3D,
        logger_name=logger.name,
    )
