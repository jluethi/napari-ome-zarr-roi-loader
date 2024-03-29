# 2D to 3D workflow
I'm creating a 2D to 3D workflow. It will consist of 2 tasks.


### Installing the tasks manually
1. Create an environment for the tasks

```
conda create --name fractal_2d_to_3D_tasks python=3.10 -y
```

2. Activate this conda environment: `conda activate fractal_2d_to_3D_tasks`


3. Install the dependencies

```
pip install fractal-tasks-core==0.12.2
```

4. Add the task via CLI client
```
fractal task new --input-type zarr --output-type zarr --version 0.1.0 --meta-file /path/to/meta_conversion.json --args-schema /path/to/convert_2D_segmentation_to_3D.json --args-schema-version pydantic_v1 "Convert 2D Segmentation to 3D" "/path/to/python /path/to/convert_2D_segmentation_to_3D.py" convert_2D_segmentation_to_3D_0.1.0

fractal task new --input-type zarr --output-type zarr --version 0.1.0 --meta-file /path/to/meta_convert_metadata.json --args-schema /path/to/convert_metadata_components_2D_to_3D.json --args-schema-version pydantic_v1 "Convert Metadata Components from 2D to 3D" "/path/to/python /path/to/convert_metadata_components_2D_to_3D.py" convert_metadata_components_2D_to_3D_0.1.0
```

-----


### Old instructions

3. Manually add the task via the web interface:
Task name: Convert 2D Segmentation to 3D
Task name: Convert Metadata Components from 2D to 3D
Command: /Path/to/venv/python /path/to/python/file.py
Input/Output Type: zarr
source: joel:convert_2d_segmentation_to_3D==0.0.1
source: joel:convert_metadata_components_2D_to_3D==0.0.1

4. Edit the meta default args:
```
fractal task edit $ID --meta-file /path/to/custom_fractal_tasks/meta_conversion.json
```
(With ID being the actual task ID)

It's important that the parallelization level is set correctly (to image for the `Convert 2D Segmentation to 3D` and not set for the `Convert Metadata Components from 2D to 3D` task)
