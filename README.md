# napari-ome-zarr-roi-loader

[![License BSD-3](https://img.shields.io/pypi/l/napari-ome-zarr-roi-loader.svg?color=green)](https://github.com/jluethi/napari-ome-zarr-roi-loader/raw/main/LICENSE)
[![PyPI](https://img.shields.io/pypi/v/napari-ome-zarr-roi-loader.svg?color=green)](https://pypi.org/project/napari-ome-zarr-roi-loader)
[![Python Version](https://img.shields.io/pypi/pyversions/napari-ome-zarr-roi-loader.svg?color=green)](https://python.org)
[![tests](https://github.com/jluethi/napari-ome-zarr-roi-loader/workflows/tests/badge.svg)](https://github.com/jluethi/napari-ome-zarr-roi-loader/actions)
[![codecov](https://codecov.io/gh/jluethi/napari-ome-zarr-roi-loader/branch/main/graph/badge.svg)](https://codecov.io/gh/jluethi/napari-ome-zarr-roi-loader)
[![napari hub](https://img.shields.io/endpoint?url=https://api.napari-hub.org/shields/napari-ome-zarr-roi-loader)](https://napari-hub.org/plugins/napari-ome-zarr-roi-loader)

Loads ROIs stored in OME-Zarr tables


![ROI_loader_example](https://user-images.githubusercontent.com/18033446/234389807-c2af9214-9742-4acb-91c1-bfb9c27f6fa2.jpg)


----------------------------------

## Installation

To install latest development version :

    pip install git+https://github.com/jluethi/napari-ome-zarr-roi-loader.git


## Usage

This plugin is designed to load regions of interest from OME-Zarr files, as produced by [Fractal](https://fractal-analytics-platform.github.io).

### Using the plugin
1. **Zarr URL:** Select an OME-Zarr file. If it's a HCS plate, select an image in a well, i.e. `/path/to/plate.ome.zarr/B/03/0`
2. **ROI Table:** Select which ROI table to use to load the regions of interest. Only Fractal ROI tables are valid choices
3. **ROI:** Select the region of interest you want to load from the dropdown
4. **Channels:**: Select which channels should be loaded. You can select multiple channels to load at the same time.
5. **Image Level:** Pick the resolution level at which the image data is loaded. The higher the number, the lower the resolution of the image will be (and the quicker it will load)
6. **Labels:** Pick the label layers to load. They will be loaded at the same resolution as the image layer (or whichever resolution is closest to it) and scaled according to their metadata to fit the image layer.
7. **Features:** Select which feature tables to load and to append to the label layer. It loads the features for the OME-Zarr image and appends the features for the labels that are present in the label image selected to the label_layer.features dataframe. Currently only loading a single feature table is supported and it's always appened to the label layer that is selected. Loading features when multiple label layers are selected is not supported.
8. **Load ROI:** Click to load all the selected channels, labels & features of the selected region of interest. The plugin loads the whole data into memory. Thus, loading large amounts of image data (large ROIs at high resolution or 3D data) on a slow connection can make the napari viewer freeze for a while. Normally, it loads the data eventually.

![ROI_Loader_with_Labels](https://user-images.githubusercontent.com/18033446/234390387-e9880009-ee33-4ef3-9b10-7ebd29713fa5.jpg)


### Exporting ROI image
You can use napari's built-in image export to save an image that was loaded to disk, e.g. as a TIF:
1. Open the region of interest you're looking for (using the instructions above)
2. Select the layer you're interested in.
3. Go to the `File` menu and click `Save selected Layer(s)`
![SaveSelectedLayer](https://user-images.githubusercontent.com/18033446/234390405-a2d6be02-d78e-414d-8376-46846d7828f3.jpg)

4. Choose a location and a name to save the image
![SaveDialogue](https://user-images.githubusercontent.com/18033446/234390414-2bf950a3-8c13-452f-b18e-a9f5acc0f6b9.jpg)

----------------------------------

## Contributing

Contributions are very welcome. Tests can be run with [tox], please ensure
the coverage at least stays the same before you submit a pull request.

## License

Distributed under the terms of the [BSD-3] license,
"napari-ome-zarr-roi-loader" is free and open source software

## Issues

If you encounter any problems, please [file an issue] along with a detailed description.

[napari]: https://github.com/napari/napari
[Cookiecutter]: https://github.com/audreyr/cookiecutter
[@napari]: https://github.com/napari
[MIT]: http://opensource.org/licenses/MIT
[BSD-3]: http://opensource.org/licenses/BSD-3-Clause
[GNU GPL v3.0]: http://www.gnu.org/licenses/gpl-3.0.txt
[GNU LGPL v3.0]: http://www.gnu.org/licenses/lgpl-3.0.txt
[Apache Software License 2.0]: http://www.apache.org/licenses/LICENSE-2.0
[Mozilla Public License 2.0]: https://www.mozilla.org/media/MPL/2.0/index.txt
[cookiecutter-napari-plugin]: https://github.com/napari/cookiecutter-napari-plugin

[file an issue]: https://github.com/jluethi/napari-ome-zarr-roi-loader/issues

[napari]: https://github.com/napari/napari
[tox]: https://tox.readthedocs.io/en/latest/
[pip]: https://pypi.org/project/pip/
[PyPI]: https://pypi.org/
