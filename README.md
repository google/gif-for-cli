<h1 align="center">
    <img src="docs/gif-for-cli-logo.png" alt="gif-for-cli logo" width="256" height="198"/>
</h1>

Takes in a GIF, short video, or a query to the [Tenor][tenor-home] GIF API and converts it to animated ASCII art. Animation and color support are performed using ANSI escape sequences.

Example use cases:

* run `gif-for-cli` in your `.bashrc` or `.profile` to get an animated ASCII art image as your MOTD!
* git hooks [;)](git-hooks/pre-push)

This script will automatically detect how many colors the current terminal uses and display the correct version:

| Original GIF  | No Colors Supported | 256 Colors Supported | 256 Colors Supported (with foreground and background colors) | Truecolor Supported |
| ------------- |:-------------------:| --------------------:| ------------------------------------------------------------:| -------------------:|
| [![Original GIF][original-gif]][original-gif-url] | [![No Color Animated ASCII Art][no-color]][no-color-url] | [![256 Colors Animated ASCII Art][256-colors]][256-colors-url] | [![256 FG/BG Colors Animated ASCII Art][256fgbg-colors]][256fgbg-colors-url] | [![Truecolor Animated ASCII Art][truecolor]][truecolor-url] |

[original-gif]: https://media1.tenor.com/images/eac7f7d8534f0843ebd707101b8ef7fd/tenor.gif?itemid=11699608
[no-color]: https://media1.tenor.com/images/95e9551fb69b5c2f67cdc48f04c75bc7/tenor.gif?itemid=11997403
[256-colors]: https://media1.tenor.com/images/d354ee0840d9376e2baacdbee59b6c06/tenor.gif?itemid=11997429
[256fgbg-colors]: https://media1.tenor.com/images/f8d461c1a6e06f0b3dd6c7aff474117b/tenor.gif?itemid=12000378
[truecolor]: https://media1.tenor.com/images/30196efdd05d816d4aab6179e41318ac/tenor.gif?itemid=11997399

[original-gif-url]: https://tenor.com/view/rob-delaney-peter-deadpool-deadpool2-untitled-deadpool-sequel-gif-11699608
[no-color-url]: https://tenor.com/view/peter-deadpool2-ascii-giffor-cli-gif-11997403
[256-colors-url]: https://tenor.com/view/peter-deadpool2-ascii-giffor-cli-ready-gif-11997429
[256fgbg-colors-url]: https://tenor.com/view/peter-deadpool2-ascii-giffor-cli-ready-gif-12000378
[truecolor-url]: https://tenor.com/view/peter-deadpool2-ascii-giffor-cli-ready-gif-11997399

## Installation

Requires Python 3 (with setuptools and pip), zlib, libjpeg, and ffmpeg, other dependencies are installed by `setup.py`.

### Install dependencies:

    # Debian based distros
    sudo apt-get install ffmpeg zlib* libjpeg* python3-setuptools
    # Mac
    brew install ffmpeg zlib libjpeg python

Your Python environment may need these installation tools:

    sudo easy_install3 pip
    # This should enable a pre-built Pillow wheel to be installed, otherwise
    # you may need to install Python, zlib, and libjpeg development libraries
    # so Pillow can compile from source.
    pip3 install --user wheel

### Install gif-for-cli:

Install from PyPI:

    pip3 install --user gif-for-cli

Or download this repo and run:

    python3 setup.py install --user

The `gif-for-cli` command will likely be installed into `~/.local/bin` or similar, you may need to put that directory in your $PATH by adding this to your `.profile`:

    # Linux
    if [ -d "$HOME/.local/bin" ] ; then
        PATH="$HOME/.local/bin:$PATH"
    fi
    # Mac, adjust for Python version
    if [ -d "$HOME/Library/Python/3.6/bin/" ] ; then
        PATH="$HOME/Library/Python/3.6/bin/:$PATH"
    fi

## Usage

### File/URL

    gif-for-cli path/to/some.gif
    gif-for-cli http://example.com/foo.gif
    gif-for-cli http://example.com/foo.mp4

Executing as a Python module is also supported:

    python3 -m gif_for_cli path/to/some.gif

### Query [Tenor's GIF API][tenor-gif-api]

Queries to Tenor's GIF API can also be performed:

    # get current top trending GIF
    gif-for-cli

    # get top GIF for "Happy Birthday"
    gif-for-cli "Happy Birthday"

    # get GIF with ID #11699608
    # browse https://tenor.com/ for more!
    gif-for-cli 11699608
    gif-for-cli https://tenor.com/view/rob-delaney-peter-deadpool-deadpool2-untitled-deadpool-sequel-gif-11699608

### Override display mode

    gif-for-cli --display-mode=nocolor 11699608
    gif-for-cli --display-mode=256 11699608
    gif-for-cli --display-mode=256fgbg 11699608
    gif-for-cli --display-mode=truecolor 11699608

### Change max width/height

The default number of rows and columns may be too large and result in line wrapping. If you know your terminal size, you can control the output size with the following options:

    gif-for-cli --rows 10 --cols 100 11699608

Set to current terminal size:

    gif-for-cli --rows `tput lines` --cols `tput cols` 11699608

Note: Generated ASCII art is cached based on the number of rows and columns, so running that command after resizing your terminal window will likely result in the ASCII Art being regenerated.

### Loop forever

    gif-for-cli -l 0 11699608

Use <kbd>CTRL</kbd> + <kbd>c</kbd> to exit.

### Export/Share

Want to share your generated ASCII Art outside a CLI env (e.g. social media)?

    gif-for-cli 11699608 --export=foo.gif

### Help

See more generation/display options:

    gif-for-cli --help

## About Tenor

Tenor is the API that delivers the most relevant GIFs for any application, anywhere in the world. We are the preferred choice for communication products of all types and the fastest growing GIF service on the market.

Check out our API Docs: [https://tenor.com/gifapi][tenor-gif-api]

## Testing

    python3 -m unittest discover

With coverage:

    coverage run --source gif_for_cli -m unittest discover
    coverage report -m

## Development

To reuse the shared Git hooks in this repo, run:

    git config core.hooksPath git-hooks

## Troubleshooting

If you get an error like the following:

    -bash: gif-for-cli: command not found

Chances are gif-for-cli was installed in a location not on your `PATH`. This can happen if running `gif-for-cli` in your `.bashrc`, but it was installed into `~/.local/bin`, and that directory hasn't been added to your `PATH`. You can either specify the full path to gif-for-cli to run it, or add its location to your $PATH.

## Some of our Favorites

    gif-for-cli 10988977
    gif-for-cli 5863633
    gif-for-cli 5437241

## Module Usage

To add gifs to your cli tool include `gif-for-cli` import and call execute.

```python
import os
import sys

from gif_for_cli.execute import execute

execute(os.environ,
    ["https://tenor.com/view/yay-pokemon-pikachu-gif-8081211"],
    sys.stdout)
```

## Disclaimer

This is not an officially supported Google product.

[tenor-home]: https://tenor.com/
[tenor-gif-api]: https://tenor.com/gifapi
