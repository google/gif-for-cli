from collections import OrderedDict
import itertools
import math
from multiprocessing import Pool
import os
import urllib.parse

import ffmpeg
from PIL import Image
import requests
from x256 import x256

from .constants import NOCOLOR_CHARS, STORED_CELL_CHAR


def avg(it):
    l = len(it)
    return sum(it) / float(l)


def get_avg_for_em(px, x, y, cell_height, cell_width):
    pixels = [
        px[sx, sy]
        for sy in range(y, y + cell_height)
        for sx in range(x, x + cell_width)
    ]
    return [round(n) for n in map(avg, zip(*pixels))]


def get_gray(*rgb):
    return avg(rgb)


def get_256_cell(r, g, b):
    return u'\u001b[38;5;{}m{}'.format(x256.from_rgb(r, g, b), STORED_CELL_CHAR)


def get_truecolor_cell(r, g, b):
    return u'\u001b[38;2;{};{};{}m{}'.format(r, g, b, STORED_CELL_CHAR)


def process_input_source(input_source):
    if not os.path.exists(input_source) and not input_source.startswith('http://') and not input_source.startswith('https://'):
        apikey = 'TQ7VXFHXBJQ5'

        # get from Tenor GIF API
        if input_source.isdigit():
            endpoint = 'gifs'
            query = 'ids={}'.format(urllib.parse.quote_plus(input_source))
        elif input_source == '':
            endpoint = 'trending'
            query = 'limit=1'
        else:
            endpoint = 'search'
            query = 'limit=1&q={}'.format(urllib.parse.quote_plus(input_source))

        resp = requests.get('https://api.tenor.com/v1/{}?key={}&{}'.format(endpoint, apikey, query))
        results = resp.json()['results']
        if not results:
            sys.stderr.write('Could not find GIF.')
            sys.exit(1)

        input_source = results[0]['media'][0]['mp4']['url']
    return input_source


def _run_ffmpeg(input_source_file, output_dirnames, cols, cell_width, **options):
    scale_width = cols * cell_width

    stream = ffmpeg.input(input_source_file)
    stream = stream.output(
        '{}/%04d.jpg'.format(output_dirnames['jpg']),
        vf='scale={}:-1'.format(scale_width)
    )
    ffmpeg.run(stream)


def convert_frame(frame_name, **options):
    cell_height = options['cell_height']
    cell_width = options['cell_width']
    output_dirnames = options['output_dirnames']

    # for each frame, generate text file with ANSI colors
    img = Image.open('{}/{}.jpg'.format(output_dirnames['jpg'], frame_name))
    px = img.load()
    width, height = img.size
    width = width - (width % cell_width)
    height = height - (height % cell_height)
    cols = math.floor(width / cell_width)

    chars_nocolor = []
    lines_256 = []
    lines_truecolor = []

    for y in range(0, height, cell_height):
        line_256 = []
        line_truecolor = []
        for x in range(0, width, cell_width):
            rgb = get_avg_for_em(px, x, y, cell_height, cell_width)

            chars_nocolor.append(get_gray(*rgb))
            line_256.append(get_256_cell(*rgb))
            line_truecolor.append(get_truecolor_cell(*rgb))

        lines_256.append(''.join(line_256))
        lines_truecolor.append(''.join(line_truecolor))

    # We need to divide up the gray colors into roughly equal buckets,
    # without adding numpy as a dependency just for the histogram function.
    num_cells_per_char = len(chars_nocolor) / len(NOCOLOR_CHARS)
    char_counts = OrderedDict()
    for cell in sorted(chars_nocolor):
        char_counts[cell] = char_counts.get(cell, 0) + 1
    cur_count = 0
    cur_char_idx = 0
    char_idxs = {}
    for cell, cell_num in char_counts.items():
        if cur_count > num_cells_per_char:
            cur_count = 0
            cur_char_idx += 1
        char_idxs[cell] = cur_char_idx
        cur_count += cell_num


    with open('{}/{}.txt'.format(output_dirnames['nocolor'], frame_name), 'w') as f:
        for i, gray in enumerate(chars_nocolor):
            if i and i % cols == 0:
                f.write('\n')
            f.write(NOCOLOR_CHARS[char_idxs[gray]])

    with open('{}/{}.txt'.format(output_dirnames['256'], frame_name), 'w') as f:
        f.write('\n'.join(lines_256))
    
    with open('{}/{}.txt'.format(output_dirnames['truecolor'], frame_name), 'w') as f:
        f.write('\n'.join(lines_truecolor))


def _log_frame_progress(total, results, stdout):
    for count, result in enumerate(itertools.chain([None], results)):
        if count:
            stdout.write(u'\u001b[2K\u001b[1000D')
        stdout.write('Processed {}/{} frames...'.format(count, total))
        stdout.flush()
    stdout.write('\n')


def _convert_frames(cpu_pool_size, stdout, **options):
    output_dirnames = options['output_dirnames']

    frame_names = [
        de.name.split('.')[0]
        for de in sorted(os.scandir(output_dirnames['jpg']), key=lambda de: de.name)
        if de.is_file()
    ]

    total = len(frame_names)

    if cpu_pool_size == 1:
        results = (
            convert_frame(frame_name, **options)
            for frame_name in frame_names
        )
        _log_frame_progress(total, results, stdout)
    else:
        with Pool(cpu_pool_size) as pool:
            # we need this consumed instantly in order for the tasks to begin
            # execution in parallel.
            results = [
                pool.apply_async(convert_frame, [frame_name], options)
                for frame_name in frame_names
            ]
            results = (r.get() for r in results)
            _log_frame_progress(total, results, stdout)


def generate(**options):
    # extract frames to files
    _run_ffmpeg(**options)

    _convert_frames(**options)
