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
import io
import json
import unittest
from unittest.mock import patch, MagicMock, Mock

from PIL import Image

from gif_for_cli.generate import (
    _run_ffmpeg,
    _save_config,
    convert_frame,
    _convert_frames,
    generate,
)


@patch('gif_for_cli.generate.open')
class TestSaveConfig(unittest.TestCase):
    def test(self, mocked_open):
        num_frames = 10
        seconds = 1.5
        options = {
            'input_source': 'happy birthday',
            'input_source_file': 'foo.jpg',
            'cols': 160,
            'cell_width': 3,
            'cell_height': 6,
            'output_dirnames': {'.': 'foo'},
        }

        f = io.StringIO()
        # we need close() to noop so we can verify the value later
        f.close = lambda *args, **kwargs: None
        mocked_open.return_value = f

        _save_config(num_frames, seconds, **options)

        content = json.loads(f.getvalue())

        self.assertNotIn('output_dirnames', content)
        self.assertEqual(content, {
            'input_source': options['input_source'],
            'input_source_file': options['input_source_file'],
            'cols': options['cols'],
            'cell_width': options['cell_width'],
            'cell_height': options['cell_height'],
            'num_frames': num_frames,
            'seconds': seconds,
        })


@patch('gif_for_cli.generate.subprocess.Popen')
class TestRunFfmpeg(unittest.TestCase):
    def test(self, mock_Popen):
        out = b''
        err = b"""Output #0, image2, to '/home/foo/.cache/gif-for-cli/0.0.0/2094cb18c10ddb47dbe239ddbd702cc0-160cols-cw3px-ch6px/jpg/%04d.jpg':
  Metadata:
    major_brand     : isom
    minor_version   : 512
    compatible_brands: isomiso2avc1mp41
    encoder         : Lavf57.83.100
    Stream #0:0(und): Video: mjpeg, yuvj420p(pc), 480x257, q=2-31, 200 kb/s, 10 fps, 10 tbn, 10 tbc (default)
    Metadata:
      handler_name    : VideoHandler
      encoder         : Lavc57.107.100 mjpeg
    Side data:
      cpb: bitrate max/min/avg: 0/0/200000 buffer size: 0 vbv_delay: -1
frame=   11 fps=0.0 q=20.2 Lsize=N/A time=00:00:01.10 bitrate=N/A speed=3.21x
video:258kB audio:0kB subtitle:0kB other streams:0kB global headers:0kB muxing overhead: unknown"""  # noqa: E501

        mock_process = Mock()
        mock_process.returncode = 0
        mock_process.communicate.return_value = (out, err,)
        mock_Popen.return_value = mock_process

        options = {
            'input_source_file': 'foo.gif',
            'output_dirnames': {'jpg': 'foo/jpg'},
            'cols': 160,
            'rows': 160,
            'cell_width': 3,
            'cell_height': 6,
            'ignoreme': None,
        }

        num_frames, seconds = _run_ffmpeg(**options)

        self.assertEqual(num_frames, 11)
        self.assertEqual(seconds, 1.1)


@patch('gif_for_cli.generate.Image')
class TestConvertFrame(unittest.TestCase):
    def test(self, mock_Image):
        im = Image.new('RGB', (100, 100,))
        # this exercises some code branches that handle multiple colors
        for i in range(0, 10):
            im.putpixel((i, 0,), (255, 255, 5 * i,))

        mock_Image.open.return_value = im

        frame_name = '0001'
        options = {
            'cell_height': 6,
            'cell_width': 3,
            'output_dirnames': {
                'jpg': 'foo/jpg',
                'nocolor': 'foo/nocolor',
                '256': 'foo/256',
                '256fgbg': 'foo/256fgbg',
                'truecolor': 'foo/truecolor',
            },
        }

        with patch('gif_for_cli.generate.open') as mocked_open:
            convert_frame(frame_name, **options)

        self.assertEqual(mock_Image.open.call_count, 1)
        self.assertEqual(mocked_open.call_count, 4)


@patch('gif_for_cli.generate.get_sorted_filenames')
@patch('gif_for_cli.generate.convert_frame')
@patch('gif_for_cli.utils.Pool')
class TestConvertFrames(unittest.TestCase):
    def test_1_cpu(self, mock_Pool, mock_convert_frame, mock_get_sorted_filenames):
        mock_get_sorted_filenames.return_value = ['0001.jpg', '0002.jpg']

        options = {
            'cpu_pool_size': 1,
            'stdout': io.StringIO(),
            'output_dirnames': {
                'jpg': 'foo/jpg',
            },
        }

        _convert_frames(**options)

        self.assertEqual(mock_get_sorted_filenames.call_count, 1)
        self.assertEqual(mock_convert_frame.call_count, 2)
        self.assertEqual(mock_Pool.call_count, 0)

        output = options['stdout'].getvalue()

        self.assertEqual(output[-1], '\n')

        output = output[:-1].split(u'\u001b[2K\u001b[1000D')

        self.assertEqual(output, [
            'Processed 0/2 frames...',
            'Processed 1/2 frames...',
            'Processed 2/2 frames...',
        ])

    def test_2_cpus(self, mock_Pool, mock_convert_frame, mock_get_sorted_filenames):
        mock_get_sorted_filenames.return_value = ['0001.jpg', '0002.jpg']
        mock_pool = MagicMock()
        mock_pool.__enter__.return_value = mock_pool

        def mock_result(f, args, kwargs):
            m = Mock()
            m.get.return_value = f(*args, **kwargs)
            return m
        mock_pool.apply_async = mock_result
        mock_Pool.return_value = mock_pool

        options = {
            'cpu_pool_size': 2,
            'stdout': io.StringIO(),
            'output_dirnames': {
                'jpg': 'foo/jpg',
            },
        }

        _convert_frames(**options)

        self.assertEqual(mock_get_sorted_filenames.call_count, 1)
        self.assertEqual(mock_convert_frame.call_count, 2)
        self.assertEqual(mock_Pool.call_count, 1)

        output = options['stdout'].getvalue()

        self.assertEqual(output[-1], '\n')

        output = output[:-1].split(u'\u001b[2K\u001b[1000D')

        self.assertEqual(output, [
            'Processed 0/2 frames...',
            'Processed 1/2 frames...',
            'Processed 2/2 frames...',
        ])


@patch('gif_for_cli.generate._run_ffmpeg')
@patch('gif_for_cli.generate._save_config')
@patch('gif_for_cli.generate._convert_frames')
class TestGenerate(unittest.TestCase):
    def test(self, mock_convert_frames, mock_save_config, mock_run_ffmpeg):
        mock_run_ffmpeg.return_value = (11, 1.1,)

        options = {}

        generate(**options)

        self.assertEqual(mock_convert_frames.call_count, 1)
        self.assertEqual(mock_save_config.call_count, 1)
        self.assertEqual(mock_save_config.call_args[0][0], 11)
        self.assertEqual(mock_save_config.call_args[0][1], 1.1)
        self.assertEqual(mock_run_ffmpeg.call_count, 1)
