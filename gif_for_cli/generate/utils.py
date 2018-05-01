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
import os
import urllib.parse

import requests
from x256 import x256

from ..constants import STORED_CELL_CHAR


def avg(it):
    l = len(it)
    return sum(it) / float(l)


def get_gray(*rgb):
    return avg(rgb)


def get_256_cell(r, g, b):
    return u'\u001b[38;5;{}m{}'.format(x256.from_rgb(r, g, b), STORED_CELL_CHAR)


def get_truecolor_cell(r, g, b):
    return u'\u001b[38;2;{};{};{}m{}'.format(r, g, b, STORED_CELL_CHAR)


def get_avg_for_em(px, x, y, cell_height, cell_width):
    pixels = [
        px[sx, sy]
        for sy in range(y, y + cell_height)
        for sx in range(x, x + cell_width)
    ]
    return [round(n) for n in map(avg, zip(*pixels))]


def process_input_source(input_source):
    if input_source.strip().startswith('https://tenor.com/view/'):
        gif_id = input_source.rsplit('-', 1)[-1]
        if gif_id.isdigit():
            input_source = gif_id
        else:
            raise Exception('Bad GIF URL.')

    is_url = input_source.startswith('http://') or input_source.startswith('https://')

    if not os.path.exists(input_source) and not is_url:
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
