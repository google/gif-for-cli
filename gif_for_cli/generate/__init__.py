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
from collections import OrderedDict
import json
import math
from multiprocessing import Pool
import os
import re
import subprocess

from PIL import Image

from ..constants import NOCOLOR_CHARS
from ..utils import get_sorted_filenames

from .utils import (
    avg,
    get_gray,
    get_256_cell,
    get_truecolor_cell,
    get_avg_for_em,
    _log_frame_progress,
)


def _save_config(num_frames, seconds, **options):
    d = {
        key: options.get(key)
        for key in [
            'input_source',
            'input_source_file',
            'cols',
            'cell_width',
            'cell_height',
        ]
    }
    d['num_frames'] = num_frames
    d['seconds'] = seconds

    with open('{}/config.json'.format(options['output_dirnames']['.']), 'w') as f:
        json.dump(d, f)


def _run_ffmpeg(input_source_file, output_dirnames, cols, rows, cell_width, cell_height, **options):
    scale_width = cols * cell_width
    scale_height = rows * cell_height

    cmd = [
        'ffmpeg',
        '-i', input_source_file,
        '-vf', 'scale=w={}:h={}:force_original_aspect_ratio=decrease'.format(scale_width, scale_height),
        '{}/%04d.jpg'.format(output_dirnames['jpg'])
    ]
    p = subprocess.Popen(cmd,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE
    )
    out, err = p.communicate()
    err = err.decode('utf8')

    num_frames = int(re.search(r'frame=\s*(\d+)', err).group(1))
    hours, minutes, seconds = re.search(r'time=(\d{2}):(\d{2}):(\d{2}.\d{2})', err).groups()
    seconds = float(seconds) + (int(minutes) * 60) + (int(hours) * 3600)
    return num_frames, seconds


def convert_frame(frame_name, **options):
    cell_height = options['cell_height']
    cell_width = options['cell_width']
    output_dirnames = options['output_dirnames']

    # for each frame, generate text file with ANSI colors
    img = Image.open('{}/{}.jpg'.format(output_dirnames['jpg'], frame_name))
    px = img.load()
    width, height = img.size
    # trim image if needed.
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

    lines_nocolor = []
    line_nocolor = None
    for i, gray in enumerate(chars_nocolor):
        if not line_nocolor:
            line_nocolor = []

        line_nocolor.append(NOCOLOR_CHARS[char_idxs[gray]])

        if (i + 1) % cols == 0:
            lines_nocolor.append(''.join(line_nocolor))
            line_nocolor = None


    with open('{}/{}.txt'.format(output_dirnames['nocolor'], frame_name), 'w') as f:
        f.write('\n'.join(lines_nocolor))

    with open('{}/{}.txt'.format(output_dirnames['256'], frame_name), 'w') as f:
        f.write('\n'.join(lines_256))
    
    with open('{}/{}.txt'.format(output_dirnames['truecolor'], frame_name), 'w') as f:
        f.write('\n'.join(lines_truecolor))


def _convert_frames(cpu_pool_size, stdout, **options):
    output_dirnames = options['output_dirnames']

    frame_names = [
        filename.split('.')[0]
        for filename in get_sorted_filenames(output_dirnames['jpg'], 'jpg')
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
            # then use a generator to iterate as they execute.
            results = (r.get() for r in results)
            _log_frame_progress(total, results, stdout)


def generate(**options):
    # extract frames to files
    num_frames, seconds = _run_ffmpeg(**options)

    _save_config(num_frames, seconds, **options)

    _convert_frames(**options)
