"""
Copyright 2022 (C)
    Friedrich Miescher Institute for Biomedical Research and
    University of Zurich

    Original authors:
    Tommaso Comparin <tommaso.comparin@exact-lab.it>

    This file is part of Fractal and was originally developed by eXact lab
    S.r.l.  <exact-lab.it> under contract with Liberali Lab from the Friedrich
    Miescher Institute for Biomedical Research and Pelkmans Lab from the
    University of Zurich.


Script to generate JSON schemas for task arguments afresh, and write them
to the package manifest.
"""
import json
import logging

from pathlib import Path

from fractal_tasks_core.dev.lib_args_schemas import (
    create_schema_for_single_task,
)
from fractal_tasks_core.dev.lib_task_docs import create_docs_info
from fractal_tasks_core.dev.lib_task_docs import create_docs_link

PACKAGE = "napari_ome_zarr_roi_loader"

if __name__ == "__main__":
    # To use this function, 2 workarounds are required:
    # 1. Need to copy the task files into the src folder of the package
    # for this to work
    # 2. Need to have lib_channels.py & lib_input_models.py in the source
    # folder as well (it doesn't use the provided INNER_PYDANTIC_MODELS), see
    # https://github.com/fractal-analytics-platform/fractal-tasks-core/issues/444

    INNER_PYDANTIC_MODELS = {}
    task_executable_list = [
        "convert_2D_segmentation_to_3D.py",
        "convert_metadata_components_2D_to_3D.py",
    ]
    for ind, executable in enumerate(task_executable_list):
        logging.info(f"[{executable}] START")
        schema = create_schema_for_single_task(
            executable,
            package="napari_ome_zarr_roi_loader",
        )
        task_schema_path = Path(executable[:-3] + ".json")
        with task_schema_path.open("w") as f:
            json.dump(schema, f, indent=2)
            f.write("\n")
