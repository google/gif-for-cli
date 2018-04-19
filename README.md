# gif-for-cli

Takes in a GIF, short video, or a query to the Tenor GIF API and converts it to animated ASCII art. Animation and color support are performed using ANSI escape sequences.

Recommened use case: put one of the example commands in your `.bashrc` to get an animated ASCII art image as your MOTD!

## Installation

Requires Python 3 and ffmpeg.

    python3 setup.py install
    pip3 install gif-for-cli

## Usage

    python3 -m gif_for_cli path/to/some.gif
    python3 -m gif_for_cli http://example.com/foo.gif
    python3 -m gif_for_cli http://example.com/foo.mp4

Queries to Tenor's GIF API can also be performed:

    # get currently top trending GIF
    python3 -m gif_for_cli

    # get top GIF for "Happy Birthday"
    python3 -m gif_for_cli "Happy Birthday"

    # get GIF with ID #5437241
    # browse https://tenor.com/ for more!
    python3 -m gif_for_cli 5437241
    python3 -m gif_for_cli https://tenor.com/view/the-matrix-gif-5437241

See more generation/display options:

    python3 -m gif_for_cli --help

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
