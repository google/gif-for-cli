"""
Copyright 2018 Google LLC

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

    https://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
"""
import argparse
import os


def _get_default_display_mode(environ):
    TERM = environ.get('TERM', '').lower()
    # FIXME: COLORTERM may not be accepted by sshd
    COLORTERM = environ.get('COLORTERM', '').lower()
    if 'truecolor' in TERM or 'truecolor' in COLORTERM:
        return 'truecolor'
    elif '256' in TERM or '256' in COLORTERM:
        return '256'
    return 'nocolor'


def _pool_type(val):
    if val is None:
        return val
    val = int(val)
    if val <= 0:
        raise argparse.ArgumentTypeError('Minimum cpu_pool_size is 1')
    return val


def get_parser(environ):
    default_display_mode = _get_default_display_mode(environ)

    parser = argparse.ArgumentParser(
        prog='gif_for_cli',
        description="""Convert .gif/.mp4 to animated ASCII art with or wihtout ANSI colors
    and view it in your terminal. Supports querying Tenor GIF API.
    """,
        formatter_class=argparse.RawTextHelpFormatter
    )
    parser.add_argument(
        'input_source',
        type=str,
        nargs='?',
        default='',
        help="""An input source. Can be a filename, url, or a query to the Tenor GIF API.

    e.g.
    foo.gif - a local file.
    https://example.com/media.mp4 - a remote file.
    'happy birthday' - searches Tenor for "happy birthday" and gets the first result.
    12345 - gets the GIF with ID 12345 from Tenor.
    [none provided] - gets the first GIF from the Tenor trending endpoint.
    """
    )
    # display related options.
    parser.add_argument(
        '--display-mode',
        dest='display_mode',
        type=str,
        default=default_display_mode,
        choices=['nocolor', '256', 'truecolor'],
        help='Override the auto-detected color support.'
    )
    parser.add_argument(
        '-c',
        dest='cell_char',
        type=str,
        default='#',
        help='Character to use for each colorized cell/block. e.g. #, \u2588, etc.'
    )
    parser.add_argument(
        '-l',
        dest='num_loops',
        type=int,
        default=3,
        help='Number of times to repeat animation. 0 will repeat forever.'
    )
    # generation related options.
    parser.add_argument(
        '--cols',
        dest='cols',
        type=int,
        default=160
    )
    parser.add_argument(
        '-cw',
        dest='cell_width',
        type=int,
        default=3
    )
    parser.add_argument(
        '-ch',
        dest='cell_height',
        type=int,
        default=6
    )

    # generation related options, but doens't affect generated output.
    parser.add_argument(
        '--pool-size',
        dest='cpu_pool_size',
        type=_pool_type,
        default=None
    )

    return parser


def get_output_dirnames(home_dir, version, input_source_hash, cols, cell_width, cell_height):
    # include generator options in path
    output_dirnames = {
        '.': '{}/.cache/gif-for-cli/{}/{}-{}cols-cw{}px-ch{}px'.format(
            home_dir,
            version,
            input_source_hash,
            cols,
            cell_width,
            cell_height
        ),
    }
    output_dirnames['jpg'] = '{}/jpg'.format(output_dirnames['.'])
    output_dirnames['nocolor'] = '{}/nocolor'.format(output_dirnames['.'])
    output_dirnames['256'] = '{}/256'.format(output_dirnames['.'])
    output_dirnames['truecolor'] = '{}/truecolor'.format(output_dirnames['.'])
    return output_dirnames


def get_sorted_filenames(dirname, ext):
    return (
        de.name
        for de in sorted(os.scandir(dirname), key=lambda de: de.name)
        if de.is_file() and de.name.endswith('.' + ext)
    )
