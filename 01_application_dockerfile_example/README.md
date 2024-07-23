# PyMUSAS Docker Example Application

This application expects to be given data to process, and an output directory to send that data to.

To run this application, first build the image with:

`podman build -t pymusas-docker .`

Then once you have a working image, this can be run with:

`podman run --rm -v './input/The Adventures of Sherlock Holmes.txt:/input:ro' -v './output:/output:rw' pymusas-docker`

Replace 'input/InputFileHere.txt'' with your own file :)

See `podman run --help` for details on the `-v` and `--rm` arguments