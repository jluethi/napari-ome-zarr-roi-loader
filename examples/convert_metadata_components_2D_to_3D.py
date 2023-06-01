"""Convert metdata components from 2D to 3D Fractal task"""
import logging
from typing import Any, Dict, Sequence

logger = logging.getLogger(__name__)


def convert_metadata_components_2D_to_3D(
    input_paths,
    output_path,
    metadata,
):
    """
    Workaround task to manually change the hard-coded metadata components
    A fractal workflow sets them to the mip.zarr components after running the
    maximum intensity projection task. This resets them to the 3D components.

    """
    old_image_list = metadata["image"]
    new_image_list = []
    for image in old_image_list:
        new_image_list.append(image.replace("_mip.zarr", ".zarr"))
    metadata["image"] = new_image_list
    return metadata


if __name__ == "__main__":
    from fractal_tasks_core._utils import run_fractal_task
    from pydantic import BaseModel, Extra

    class TaskArguments(BaseModel, extra=Extra.forbid):
        input_paths: Sequence[str]
        output_path: str
        metadata: Dict[str, Any]

    run_fractal_task(
        task_function=convert_metadata_components_2D_to_3D,
        TaskArgsModel=TaskArguments,
        logger_name=logger.name,
    )
