from napari_ome_zarr_roi_loader.roi_loader_widget import RoiLoader


def test_example_magic_widget(make_napari_viewer, capsys):
    # TODO: Actually write the test
    viewer = make_napari_viewer()
    _ = RoiLoader(viewer)
    # layer = viewer.add_image(np.random.random((100, 100)))
    # my_widget = load_intensity_roi()

    # TODO: Figure out how to test OME-Zarr ROI loading here
    # At the moment, this just initializes the widget

    # # if we "call" this object, it'll execute our function
    # my_widget(viewer.layers[0])

    # # read captured output and check that it's as we expected
    # captured = capsys.readouterr()
    # assert captured.out == f"you have selected {layer}\n"
