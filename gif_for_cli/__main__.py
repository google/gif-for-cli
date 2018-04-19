import argparse
import hashlib
import os
from os.path import expanduser
import sys

from . import __version__
from .constants import STORED_CELL_CHAR
from .display import display
from .generate import process_input_source, generate


default_display_mode = 'nocolor'

TERM = os.environ.get('TERM', '').lower()
# FIXME: COLORTERM may not be accepted by sshd
COLORTERM = os.environ.get('COLORTERM', '').lower()
if 'truecolor' in TERM or 'truecolor' in COLORTERM:
    default_display_mode = 'truecolor'
elif '256' in TERM or '256' in COLORTERM:
    default_display_mode = '256'


parser = argparse.ArgumentParser(
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
parser.add_argument(
    '-s',
    dest='seconds_per_frame',
    type=float,
    default=0.2
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
def pool_type(val):
    if val is None:
        return val
    val = int(val)
    if val <= 0:
        raise argparse.ArgumentTypeError('Minimum cpu_pool_size is 1')
    return val

parser.add_argument(
    '--pool-size',
    dest='cpu_pool_size',
    type=pool_type,
    default=None
)

args = parser.parse_args()


input_source = args.input_source

input_source_file = process_input_source(input_source)


home_dir = expanduser('~')

m = hashlib.md5()
m.update(input_source_file.encode('utf8'))
input_source_hash = m.hexdigest()

# include generator options in path
output_dirnames = {
    '.': '{}/.cache/gif-for-cli/{}/{}-{}cols-cw{}px-ch{}px'.format(
        home_dir,
        __version__,
        input_source_hash,
        args.cols,
        args.cell_width,
        args.cell_height
    ),
}
output_dirnames['jpg'] = '{}/jpg'.format(output_dirnames['.'])
output_dirnames['nocolor'] = '{}/nocolor'.format(output_dirnames['.'])
output_dirnames['256'] = '{}/256'.format(output_dirnames['.'])
output_dirnames['truecolor'] = '{}/truecolor'.format(output_dirnames['.'])


if not os.path.exists(output_dirnames['.']):
    for output_dirname in output_dirnames.values():
        if not os.path.exists(output_dirname):
            os.makedirs(output_dirname)

    generate(
        stdout=sys.stdout,
        input_source=input_source,
        input_source_file=input_source_file,
        cpu_pool_size=args.cpu_pool_size,
        cols=args.cols,
        cell_width=args.cell_width,
        cell_height=args.cell_height,
        output_dirnames=output_dirnames,
    )


display(
    display_dirname=output_dirnames[args.display_mode],
    stdout=sys.stdout,
    num_loops=args.num_loops,
    cell_char=args.cell_char,
    seconds_per_frame=args.seconds_per_frame
)
