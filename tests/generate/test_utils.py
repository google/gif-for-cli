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
import json
import unittest
from unittest.mock import patch, Mock

from PIL import Image

from gif_for_cli.generate.utils import (
    get_gray,
    get_256_cell,
    get_truecolor_cell,
    get_avg_for_em,
    process_input_source,
)
from ..fixtures import empty_gif_response, gif_response

api_key = 'TQ7VXFHXBJQ5'


class TestGetGray(unittest.TestCase):
    def test(self):
        self.assertAlmostEqual(
            get_gray(0, 128, 255),
            127.66666666
        )


class TestGet256Cell(unittest.TestCase):
    def test(self):
        self.assertEqual(
            get_256_cell(0, 128, 255),
            u'\u001b[38;5;33m#'
        )


class TestGetTruecolorCell(unittest.TestCase):
    def test(self):
        self.assertEqual(
            get_truecolor_cell(0, 128, 255),
            u'\u001b[38;2;0;128;255m#'
        )


class TestGetAvgForEm(unittest.TestCase):
    def setUp(self):
        self.im = Image.new('RGB', (100, 100,))
        self.px = self.im.load()
        self.black = [0, 0, 0,]
        self.white = [255, 255, 255,]
        self.gray = [128, 128, 128,]

    def assertColor(self, out, color):
        self.assertEqual(out, color)

        for v in out:
            self.assertEqual(type(v), int)

    def test_default_black_block(self):
        out = get_avg_for_em(self.px, 0, 0, 2, 2)

        self.assertColor(out, self.black)

        out = get_avg_for_em(self.px, 2, 0, 2, 2)

        self.assertColor(out, self.black)

        out = get_avg_for_em(self.px, 0, 2, 2, 2)

        self.assertColor(out, self.black)

        out = get_avg_for_em(self.px, 2, 2, 2, 2)

        self.assertColor(out, self.black)

    def test_white_block(self):
        self.im.putpixel((0, 0,), tuple(self.white))
        self.im.putpixel((1, 0,), tuple(self.white))
        self.im.putpixel((0, 1,), tuple(self.white))
        self.im.putpixel((1, 1,), tuple(self.white))

        out = get_avg_for_em(self.px, 0, 0, 2, 2)

        self.assertColor(out, self.white)

        out = get_avg_for_em(self.px, 2, 0, 2, 2)

        self.assertColor(out, self.black)

        out = get_avg_for_em(self.px, 0, 2, 2, 2)

        self.assertColor(out, self.black)

        out = get_avg_for_em(self.px, 2, 2, 2, 2)

        self.assertColor(out, self.black)

    def test_gray_block(self):
        self.im.putpixel((0, 0,), tuple(self.white))
        self.im.putpixel((0, 1,), tuple(self.white))

        out = get_avg_for_em(self.px, 0, 0, 2, 2)

        self.assertColor(out, self.gray)

        out = get_avg_for_em(self.px, 2, 0, 2, 2)

        self.assertColor(out, self.black)

        out = get_avg_for_em(self.px, 0, 2, 2, 2)

        self.assertColor(out, self.black)

        out = get_avg_for_em(self.px, 2, 2, 2, 2)

        self.assertColor(out, self.black)

    def test_separate_color_channels(self):
        color1 = (0, 128, 255,)
        color2 = (255, 128, 0,)

        self.im.putpixel((0, 0,), color1)
        self.im.putpixel((1, 0,), color1)
        self.im.putpixel((0, 1,), color1)
        self.im.putpixel((1, 1,), color1)

        self.im.putpixel((2, 0,), color1)
        self.im.putpixel((3, 0,), color1)
        self.im.putpixel((2, 1,), color2)
        self.im.putpixel((3, 1,), color2)

        out = get_avg_for_em(self.px, 0, 0, 2, 2)

        self.assertColor(out, list(color1))

        out = get_avg_for_em(self.px, 2, 0, 2, 2)

        self.assertColor(out, self.gray)

        out = get_avg_for_em(self.px, 0, 2, 2, 2)

        self.assertColor(out, self.black)

        out = get_avg_for_em(self.px, 2, 2, 2, 2)

        self.assertColor(out, self.black)


@patch('os.path.exists')
@patch('gif_for_cli.generate.utils.requests')
class TestProcessInputSource(unittest.TestCase):
    def set_mock_response(self, mock_requests, data, side_effect=False):
        mock_response = Mock()
        if side_effect:
            mock_response.json.side_effect = data
        else:
            mock_response.json.return_value = data
        mock_requests.get.return_value = mock_response

    def test_file(self, mock_requests, mock_exists):
        mock_exists.return_value = True

        input_source = 'foo.gif'

        processed_input_source = process_input_source(input_source, api_key)

        self.assertEqual(processed_input_source, input_source)
        self.assertEqual(mock_exists.call_count, 1)
        self.assertEqual(mock_requests.get.call_count, 0)

    def test_http_url(self, mock_requests, mock_exists):
        mock_exists.return_value = False

        input_source = 'http://example.com/foo.gif'

        processed_input_source = process_input_source(input_source, api_key)

        self.assertEqual(processed_input_source, input_source)
        self.assertEqual(mock_exists.call_count, 1)
        self.assertEqual(mock_requests.get.call_count, 0)

    def test_https_url(self, mock_requests, mock_exists):
        mock_exists.return_value = False

        input_source = 'https://example.com/foo.gif'

        processed_input_source = process_input_source(input_source, api_key)

        self.assertEqual(processed_input_source, input_source)
        self.assertEqual(mock_exists.call_count, 1)
        self.assertEqual(mock_requests.get.call_count, 0)

    def test_tenor_trending(self, mock_requests, mock_exists):
        mock_exists.return_value = False

        self.set_mock_response(mock_requests, gif_response)

        input_source = ''

        processed_input_source = process_input_source(input_source, api_key)

        mpr_url = gif_response['results'][0]['media'][0]['mp4']['url']
        self.assertEqual(processed_input_source, mpr_url)
        self.assertEqual(mock_exists.call_count, 1)
        self.assertEqual(mock_requests.get.call_count, 1)

    def test_tenor_search(self, mock_requests, mock_exists):
        mock_exists.return_value = False

        self.set_mock_response(mock_requests, gif_response)

        input_source = 'happy birthday'

        processed_input_source = process_input_source(input_source, api_key)

        mpr_url = gif_response['results'][0]['media'][0]['mp4']['url']
        self.assertEqual(processed_input_source, mpr_url)
        self.assertEqual(mock_exists.call_count, 1)
        self.assertEqual(mock_requests.get.call_count, 1)

    def test_tenor_search_empty_results(self, mock_requests, mock_exists):
        mock_exists.return_value = False

        self.set_mock_response(mock_requests, empty_gif_response)

        input_source = 'happy birthday'

        with self.assertRaises(Exception) as cm:
            process_input_source(input_source, api_key)

        self.assertEqual(cm.exception.args[0], 'Could not find GIF.')
        self.assertEqual(mock_exists.call_count, 1)
        self.assertEqual(mock_requests.get.call_count, 1)

    def test_tenor_gif_id(self, mock_requests, mock_exists):
        mock_exists.return_value = False

        self.set_mock_response(mock_requests, gif_response)

        input_source = '11313704'

        processed_input_source = process_input_source(input_source, api_key)

        mpr_url = gif_response['results'][0]['media'][0]['mp4']['url']
        self.assertEqual(processed_input_source, mpr_url)
        self.assertEqual(mock_exists.call_count, 1)
        self.assertEqual(mock_requests.get.call_count, 1)

    def test_tenor_gif_id_error_occurred(self, mock_requests, mock_exists):
        mock_exists.return_value = False

        self.set_mock_response(mock_requests, {'error': 'some error'})

        input_source = '11313704'

        with self.assertRaises(Exception) as cm:
            process_input_source(input_source, api_key)

        self.assertEqual(cm.exception.args[0], 'An error occurred: some error')
        self.assertEqual(mock_exists.call_count, 1)
        self.assertEqual(mock_requests.get.call_count, 1)

    def test_tenor_gif_id_empty_json(self, mock_requests, mock_exists):
        mock_exists.return_value = False

        self.set_mock_response(mock_requests, {})

        input_source = '11313704'

        with self.assertRaises(Exception) as cm:
            process_input_source(input_source, api_key)

        self.assertEqual(cm.exception.args[0], 'Could not find GIF.')
        self.assertEqual(mock_exists.call_count, 1)
        self.assertEqual(mock_requests.get.call_count, 1)

    def test_tenor_gif_id_exception_when_getting_json(self, mock_requests, mock_exists):
        mock_exists.return_value = False

        self.set_mock_response(mock_requests, Exception('some error'), side_effect=True)

        input_source = '11313704'

        with self.assertRaises(Exception) as cm:
            process_input_source(input_source, api_key)

        self.assertEqual(cm.exception.args[0], 'some error')
        self.assertEqual(mock_exists.call_count, 1)
        self.assertEqual(mock_requests.get.call_count, 1)

    def test_tenor_gif_id_json_decode_error(self, mock_requests, mock_exists):
        mock_exists.return_value = False

        self.set_mock_response(mock_requests, lambda *args: json.loads('<'), side_effect=True)

        input_source = '11313704'

        with self.assertRaises(Exception) as cm:
            process_input_source(input_source, api_key)

        self.assertEqual(cm.exception.args[0], 'A server error occurred.')
        self.assertEqual(mock_exists.call_count, 1)
        self.assertEqual(mock_requests.get.call_count, 1)

    def test_tenor_gif_url(self, mock_requests, mock_exists):
        mock_exists.return_value = False

        self.set_mock_response(mock_requests, gif_response)

        input_source = 'https://tenor.com/view/the-matrix-gif-5437241'

        processed_input_source = process_input_source(input_source, api_key)

        mpr_url = gif_response['results'][0]['media'][0]['mp4']['url']
        self.assertEqual(processed_input_source, mpr_url)
        self.assertEqual(mock_exists.call_count, 1)
        self.assertEqual(mock_requests.get.call_count, 1)

    def test_tenor_broken_gif_url(self, mock_requests, mock_exists):
        mock_exists.return_value = False

        self.set_mock_response(mock_requests, gif_response)

        input_source = 'https://tenor.com/view/the-matrix-gif'

        with self.assertRaises(Exception) as cm:
            process_input_source(input_source, api_key)

        self.assertEqual(cm.exception.args[0], 'Bad GIF URL.')
        self.assertEqual(mock_exists.call_count, 0)
        self.assertEqual(mock_requests.get.call_count, 0)
