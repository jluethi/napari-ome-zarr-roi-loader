# napari-ome-zarr-roi-loader

[![License BSD-3](https://img.shields.io/pypi/l/napari-ome-zarr-roi-loader.svg?color=green)](https://github.com/jluethi/napari-ome-zarr-roi-loader/raw/main/LICENSE)
[![PyPI](https://img.shields.io/pypi/v/napari-ome-zarr-roi-loader.svg?color=green)](https://pypi.org/project/napari-ome-zarr-roi-loader)
[![Python Version](https://img.shields.io/pypi/pyversions/napari-ome-zarr-roi-loader.svg?color=green)](https://python.org)
[![tests](https://github.com/jluethi/napari-ome-zarr-roi-loader/workflows/tests/badge.svg)](https://github.com/jluethi/napari-ome-zarr-roi-loader/actions)
[![codecov](https://codecov.io/gh/jluethi/napari-ome-zarr-roi-loader/branch/main/graph/badge.svg)](https://codecov.io/gh/jluethi/napari-ome-zarr-roi-loader)
[![napari hub](https://img.shields.io/endpoint?url=https://api.napari-hub.org/shields/napari-ome-zarr-roi-loader)](https://napari-hub.org/plugins/napari-ome-zarr-roi-loader)

Loads ROIs stored in OME-Zarr tables

![ROI_loader_example](https://user-images.githubusercontent.com/18033446/214337778-48cc48d6-7149-4db7-823c-c5196ee3fd32.jpg)


This plugin is designed to load regions of interest from OME-Zarr files, as produced by [Fractal](https://fractal-analytics-platform.github.io).

It works with individual OME-Zarr files. If you have an HCS OME-Zarr plate, select an image within a well (i.e. select `/path/to/plate.ome.zarr/B/03/0`) as the Zarr URL.

----------------------------------

## Installation

To install latest development version :

    pip install git+https://github.com/jluethi/napari-ome-zarr-roi-loader.git


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
