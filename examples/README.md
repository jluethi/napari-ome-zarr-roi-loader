# 2D to 3D workflow
I'm creating a 2D to 3D workflow. It will consist of 2 tasks.


### Installing the tasks manually
1. Use the existing fractal-tasks-core environment
    The new conversion tasks also need ome-zarr-py => install it manually in that environment (see instructions on FMI wiki for manual installation of packages in a Fractal-collected environemnt)

    ```
    pip install ome-zarr
    ```

2. Manually add the task via the web interface:
Task name: Convert 2D Segmentation to 3D
Command: /Path/to/venv/python /path/to/python/file.py
Input/Output Type: zarr
source: joel:convert_2d_segmentation_to_3D==0.0.1

3. Edit the meta default args:
```
fractal task edit $ID --meta-file /path/to/custom_fractal_tasks/meta_conversion.json
```
(With ID being the actual task ID)
TBD: Do we need a specific memory default?
