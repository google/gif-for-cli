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
import itertools
from json.decoder import JSONDecodeError
import math
import os
import urllib.parse

import requests
from x256 import x256

from ..constants import X256FGBG_CHARS, STORED_CELL_CHAR

from .x256fgbg_utils import top_2_colors


def avg(it):
    l = len(it)
    return sum(it) / float(l)


def get_gray(*rgb):
    return avg(rgb)


def get_256_cell(r, g, b):
    return u'\u001b[38;5;{}m{}'.format(x256.from_rgb(r, g, b), STORED_CELL_CHAR)


def get_256fgbg_cell(r, g, b):
    best, second = top_2_colors(r, g, b)
    # if the best color is an exact match, use a blank space for the FG color.
    char = ' '
    if best['distance'] != 0:
        # The bigger the distance of the best color, the more we want the FG
        # color to show up.
        # Cases:
        # best and second are equal - 50BG/50FG - largest X256FGBG_CHARS
        # best is close, second is far away - 90BG/10FG - smaller X256FGBG_CHARS
        ratio = best['distance'] / second['distance']
        char = X256FGBG_CHARS[math.floor(ratio * (len(X256FGBG_CHARS) - 1))]

    return u'\u001b[48;5;{}m\u001b[38;5;{}m{}'.format(
        best['index'],
        second['index'],
        char,
    )


def get_truecolor_cell(r, g, b):
    return u'\u001b[38;2;{};{};{}m{}'.format(r, g, b, STORED_CELL_CHAR)


def get_avg_for_em(px, x, y, cell_height, cell_width):
    pixels = [
        px[sx, sy]
        for sy in range(y, y + cell_height)
        for sx in range(x, x + cell_width)
    ]
    return [round(n) for n in map(avg, zip(*pixels))]


def process_input_source(input_source, api_key):
    if input_source.strip().startswith('https://tenor.com/view/'):
        gif_id = input_source.rsplit('-', 1)[-1]
        if gif_id.isdigit():
            input_source = gif_id
        else:
            raise Exception('Bad GIF URL.')

    is_url = input_source.startswith('http://') or input_source.startswith('https://')

    if not os.path.exists(input_source) and not is_url:
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

        resp = requests.get('https://api.tenor.com/v1/{}?key={}&{}'.format(endpoint, api_key, query))

        try:
            resp_json = resp.json()
        except JSONDecodeError:
            raise Exception('A server error occurred.')

        if 'error' in resp_json:
            raise Exception('An error occurred: {}'.format(resp_json['error']))

        results = resp_json.get('results')

        if not results:
            raise Exception('Could not find GIF.')

        input_source = results[0]['media'][0]['mp4']['url']
    return input_source


def _log_frame_progress(total, results, stdout):
    for count, result in enumerate(itertools.chain([None], results)):
        if count:
            stdout.write(u'\u001b[2K\u001b[1000D')
        stdout.write('Processed {}/{} frames...'.format(count, total))
        stdout.flush()
    stdout.write('\n')
