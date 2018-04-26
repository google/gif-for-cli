# gif-for-cli

Takes in a GIF, short video, or a query to the Tenor GIF API and converts it to animated ASCII art. Animation and color support are performed using ANSI escape sequences.

Recommened use case: put one of the example commands in your `.bashrc` or `.profile` to get an animated ASCII art image as your MOTD!

This script will automatically detect how many colors the current terminal uses and display the correct version:

| Original GIF  | No Colors Supported | 256 Colors Supported | Truecolor Supported |
| ------------- |:-------------------:| --------------------:| -------------------:|
| [![Original GIF][original-gif]][original-gif-url] | [![No Color Animated ASCII Art][no-color]][no-color-url] | [![256 Colors Animated ASCII Art][256-colors]][256-colors-url] | [![Truecolor Animated ASCII Art][truecolor]][truecolor-url] |

[original-gif]: https://media1.tenor.com/images/18b80cf2409fc038638c564c6f07d3b5/tenor.gif?itemid=5437241
[no-color]: https://media1.tenor.com/images/7785f624c29e1a212ace715942ef5b82/tenor.gif?itemid=11713984
[256-colors]: https://media1.tenor.com/images/04d6327fb30fc6b1eb0a5cf6824b4ae7/tenor.gif?itemid=11713983
[truecolor]: https://media1.tenor.com/images/336f10e1717e60e33d9e1911d5beda77/tenor.gif?itemid=11713985

[original-gif-url]: https://tenor.com/view/the-matrix-gif-5437241
[no-color-url]: https://tenor.com/view/the-matrix-ascii-gif-11713984
[256-colors-url]: https://tenor.com/view/the-matrix-ascii-gif-11713983
[truecolor-url]: https://tenor.com/view/the-matrix-ascii-gif-11713985

## Installation

Requires Python 3 and ffmpeg, other depencies are installed by `setup.py`.

Download this repo and run:

    python3 setup.py install

Or install from PyPI:

    pip3 install gif-for-cli

## Usage

### File/URL

    gif-for-cli path/to/some.gif
    gif-for-cli http://example.com/foo.gif
    gif-for-cli http://example.com/foo.mp4

Executing as a Python module is also supported:

    python3 -m gif_for_cli path/to/some.gif

### Query Tenor's API

Queries to Tenor's GIF API can also be performed:

    # get current top trending GIF
    gif-for-cli

    # get top GIF for "Happy Birthday"
    gif-for-cli "Happy Birthday"

    # get GIF with ID #5437241
    # browse https://tenor.com/ for more!
    gif-for-cli 5437241
    gif-for-cli https://tenor.com/view/the-matrix-gif-5437241

### Help

See more generation/display options:

    gif-for-cli --help

### Troubleshooting

If you get an error like the following:

    -bash: gif-for-cli: command not found

Chances are gif-for-cli was installed in a location not on your `PATH`. This can happen if running `gif-for-cli` in your `.bashrc`, but it was installed into `~/.local/bin`, and that directory hasn't been added to your `PATH`.

## About Tenor

Tenor is the API that delivers the most relevant GIFs for any application, anywhere in the world. We are the preferred choice for communication products of all types and the fastest growing GIF service on the market.

Check out our API Docs: [https://tenor.com/gifapi]

## Testing

    python3 -m unittest discover

With coverage:

    coverage run --source gif_for_cli -m unittest discover
    coverage report -m

## Disclaimer

This is not an officially supported Google product.
