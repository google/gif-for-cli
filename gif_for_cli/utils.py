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
from multiprocessing import Pool
import itertools
import os


def memoize(f):
    """
    Caveat: Presumes each arg is hashable, and therefore a valid dict key.
    """
    d = {}

    def wrapper(*args):
        if args in d:
            return d[args]

        res = f(*args)
        d[args] = res
        return res

    return wrapper


def _get_default_display_mode(environ):
    TERM = environ.get('TERM', '').lower()
    # FIXME: COLORTERM may not be accepted by sshd
    COLORTERM = environ.get('COLORTERM', '').lower()
    if 'truecolor' in TERM or 'truecolor' in COLORTERM:
        return 'truecolor'
    elif '256' in TERM or '256' in COLORTERM:
        return '256fgbg'
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
        formatter_class=argparse.RawTextHelpFormatter,
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
    """,
    )
    parser.add_argument(
        '--api-key',
        dest='api_key',
        type=str,
        default='TQ7VXFHXBJQ5',
        help='Tenor API key to perform queries with.',
    )
    # display related options.
    parser.add_argument(
        '--display-mode',
        '-m',
        dest='display_mode',
        type=str,
        default=default_display_mode,
        choices=['nocolor', '256', '256fgbg', 'truecolor'],
        help='Override the auto-detected color support.',
    )
    parser.add_argument(
        '-c',
        dest='cell_char',
        type=str,
        default='#',
        help='Character to use for each colorized cell/block. e.g. #, \u2588, etc.',
    )
    parser.add_argument(
        '-l',
        dest='num_loops',
        type=int,
        default=3,
        help='Number of times to repeat animation. 0 will repeat forever.',
    )
    # generation related options.
    parser.add_argument(
        '--cols',
        dest='cols',
        type=int,
        default=160,
        help='Maximum number of columns.',
    )
    parser.add_argument(
        '--rows',
        dest='rows',
        type=int,
        default=40,
        help='Maximum number of rows.',
    )
    parser.add_argument(
        '-cw',
        dest='cell_width',
        type=int,
        default=3,
        help='Number of pixels in width you want mapped to a single character.',
    )
    parser.add_argument(
        '-ch',
        dest='cell_height',
        type=int,
        default=6,
        help='Number of pixels in height you want mapped to a single character.',
    )

    # generation related options, but doens't affect generated output.
    parser.add_argument(
        '--pool-size',
        dest='cpu_pool_size',
        type=_pool_type,
        default=None,
    )
    parser.add_argument(
        '--no-display',
        dest='no_display',
        action='store_true',
        help='Skip displaying ASCII in terminal, useful for pre-caching output.',
    )

    # export related options, doens't affect generated output.
    parser.add_argument(
        '--export',
        dest='export_filename',
        type=str,
        default='',
        help="""Specify a filename (.gif, .mp4, etc.) for ffmpeg to export to.
    Useful for sharing animated ASCII art outside a CLI environment. ASCII is
    not output to the terminal.""",
    )

    return parser


def get_output_dirnames(home_dir, version, input_source_hash, cols, rows, cell_width, cell_height):
    # include generator options in path
    output_dirnames = {
        '.': '{}/.cache/gif-for-cli/{}/{}-{}cols-{}rows-cw{}px-ch{}px'.format(
            home_dir,
            version,
            input_source_hash,
            cols,
            rows,
            cell_width,
            cell_height
        ),
    }
    output_dirnames['jpg'] = '{}/jpg'.format(output_dirnames['.'])
    output_dirnames['nocolor'] = '{}/nocolor'.format(output_dirnames['.'])
    output_dirnames['256'] = '{}/256'.format(output_dirnames['.'])
    output_dirnames['256fgbg'] = '{}/256fgbg'.format(output_dirnames['.'])
    output_dirnames['truecolor'] = '{}/truecolor'.format(output_dirnames['.'])
    return output_dirnames


def get_sorted_filenames(dirname, ext):
    return (
        de.name
        for de in sorted(os.scandir(dirname), key=lambda de: de.name)
        if de.is_file() and de.name.endswith('.' + ext)
    )


def _log_frame_progress(total, results, stdout):
    for count, result in enumerate(itertools.chain([None], results)):
        if count:
            stdout.write(u'\u001b[2K\u001b[1000D')
        stdout.write('Processed {}/{} frames...'.format(count, total))
        stdout.flush()
    stdout.write('\n')


def pool_abstraction(callable, items, pool_size, stdout, **options):
    total = len(items)

    if pool_size == 1:
        results = (
            callable(item, **options)
            for item in items
        )
        _log_frame_progress(total, results, stdout)
    else:
        with Pool(pool_size) as pool:
            # we need this consumed instantly in order for the tasks to begin
            # execution in parallel.
            results = [
                pool.apply_async(callable, [item], options)
                for item in items
            ]
            # then use a generator to iterate as they execute.
            results = (r.get() for r in results)
            _log_frame_progress(total, results, stdout)
