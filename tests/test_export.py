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
import os
import unittest
from unittest.mock import patch, Mock

from gif_for_cli.constants import ANSI_RESET, STORED_CELL_CHAR
from gif_for_cli.export import _export_txt_frames, _get_txt_frames, _run_ffmpeg,\
    export, export_txt_frame


@patch('gif_for_cli.export.Image')
@patch('gif_for_cli.export.open')
class TestExportTxtFrame(unittest.TestCase):
    def setUp(self):
        super(TestExportTxtFrame, self).setUp()
        self.rows = 40
        self.cols = 160
        self.actual_rows = 2
        self.row_ratio = self.rows / self.actual_rows

    def test_nocolor(self, mock_open, mock_Image):
        mock_im = Mock()
        mock_im_cropped = Mock()
        mock_im.crop.return_value = mock_im_cropped
        mock_Image.new.return_value = mock_im

        txt_filename = '/home/foo/.cache/gif-for-cli/0.0.0/abcdef/nocolor/0001.txt'
        cell_char = STORED_CELL_CHAR

        frame = '\n'.join([u'#' * self.cols] * self.actual_rows)
        mock_open.return_value = io.StringIO(frame)

        export_txt_frame(txt_filename, cell_char, self.rows, self.cols)

        self.assertEqual(mock_Image.new.call_count, 1)

        width = mock_Image.new.call_args[0][1][0]
        height = mock_Image.new.call_args[0][1][1]

        self.assertEqual(mock_im.crop.call_count, 1)
        self.assertEqual(mock_im.crop.call_args[0][0][2], width)
        self.assertEqual(mock_im.crop.call_args[0][0][3], height / self.row_ratio)
        self.assertEqual(mock_im.save.call_count, 0)
        self.assertEqual(mock_im_cropped.save.call_count, 1)

    def test_256(self, mock_open, mock_Image):
        mock_im = Mock()
        mock_im_cropped = Mock()
        mock_im.crop.return_value = mock_im_cropped
        mock_Image.new.return_value = mock_im

        txt_filename = '/home/foo/.cache/gif-for-cli/0.0.0/abcdef/256/0001.txt'
        cell_char = '$'

        frame = '\n'.join([u'\u001b[38;5;1m#' * self.cols] * self.actual_rows)
        mock_open.return_value = io.StringIO(frame)

        export_txt_frame(txt_filename, cell_char, self.rows, self.cols)

        self.assertEqual(mock_Image.new.call_count, 1)

        width = mock_Image.new.call_args[0][1][0]
        height = mock_Image.new.call_args[0][1][1]

        self.assertEqual(mock_im.crop.call_count, 1)
        self.assertEqual(mock_im.crop.call_args[0][0][2], width)
        self.assertEqual(mock_im.crop.call_args[0][0][3], height / self.row_ratio)
        self.assertEqual(mock_im.save.call_count, 0)
        self.assertEqual(mock_im_cropped.save.call_count, 1)

    def test_256fgbg(self, mock_open, mock_Image):
        mock_im = Mock()
        mock_im_cropped = Mock()
        mock_im.crop.return_value = mock_im_cropped
        mock_Image.new.return_value = mock_im

        txt_filename = '/home/foo/.cache/gif-for-cli/0.0.0/abcdef/256fgbg/0001.txt'
        cell_char = '$'

        frame = '\n{}'.format(ANSI_RESET).join(
            [u'\u001b[48;5;10m\u001b[38;5;1m#' * self.cols] * self.actual_rows
        )
        mock_open.return_value = io.StringIO(frame)

        export_txt_frame(txt_filename, cell_char, self.rows, self.cols)

        self.assertEqual(mock_Image.new.call_count, 1)

        width = mock_Image.new.call_args[0][1][0]
        height = mock_Image.new.call_args[0][1][1]

        self.assertEqual(mock_im.crop.call_count, 1)
        self.assertEqual(mock_im.crop.call_args[0][0][2], width)
        self.assertEqual(mock_im.crop.call_args[0][0][3], height / self.row_ratio)
        self.assertEqual(mock_im.save.call_count, 0)
        self.assertEqual(mock_im_cropped.save.call_count, 1)

    def test_truecolor(self, mock_open, mock_Image):
        mock_im = Mock()
        mock_im_cropped = Mock()
        mock_im.crop.return_value = mock_im_cropped
        mock_Image.new.return_value = mock_im

        txt_filename = '/home/foo/.cache/gif-for-cli/0.0.0/abcdef/truecolor/0001.txt'
        cell_char = '$'

        frame = '\n'.join([u'\u001b[38;2;255;255;255m#' * self.cols] * self.actual_rows)
        mock_open.return_value = io.StringIO(frame)

        export_txt_frame(txt_filename, cell_char, self.rows, self.cols)

        self.assertEqual(mock_Image.new.call_count, 1)

        width = mock_Image.new.call_args[0][1][0]
        height = mock_Image.new.call_args[0][1][1]

        self.assertEqual(mock_im.crop.call_count, 1)
        self.assertEqual(mock_im.crop.call_args[0][0][2], width)
        self.assertEqual(mock_im.crop.call_args[0][0][3], height / self.row_ratio)
        self.assertEqual(mock_im.save.call_count, 0)
        self.assertEqual(mock_im_cropped.save.call_count, 1)


@patch('gif_for_cli.export.export_txt_frame')
@patch('gif_for_cli.export.pool_abstraction')
class TestExportTxtFrames(unittest.TestCase):
    def setUp(self):
        super(TestExportTxtFrames, self).setUp()
        self.txt_frames = [
            'some-dir/000{}.txt'.format(i)
            for i in range(5)
        ]

    def test(self, mock_pool_abstraction, mock_export_txt_frame):
        txt_frames = self.txt_frames
        cpu_pool_size = 1
        stdout = io.StringIO()

        _export_txt_frames(txt_frames, cpu_pool_size, stdout)

        self.assertEqual(mock_pool_abstraction.call_count, 1)
        self.assertEqual(mock_pool_abstraction.call_args[0][0], mock_export_txt_frame)
        self.assertEqual(mock_pool_abstraction.call_args[0][1], txt_frames)
        self.assertEqual(mock_pool_abstraction.call_args[0][2], cpu_pool_size)
        self.assertEqual(mock_pool_abstraction.call_args[0][3], stdout)


@patch('gif_for_cli.export.get_sorted_filenames')
class TestGetTxtFrames(unittest.TestCase):
    def test(self, mock_get_sorted_filenames):
        display_dirname = 'some-dir'

        mock_get_sorted_filenames.return_value = ['0001.txt', '0002.txt']

        txt_frames = _get_txt_frames(display_dirname)

        self.assertEqual(len(txt_frames), 2)
        self.assertEqual(txt_frames[0], 'some-dir/0001.txt')
        self.assertEqual(txt_frames[1], 'some-dir/0002.txt')

        self.assertEqual(mock_get_sorted_filenames.call_count, 1)
        self.assertEqual(mock_get_sorted_filenames.call_args[0][0], display_dirname)


@patch('gif_for_cli.export.subprocess.Popen')
class TestRunFfmpeg(unittest.TestCase):
    def setUp(self):
        super(TestRunFfmpeg, self).setUp()
        self.options = {
            'export_filename': 'foo.gif',
            'display_dirname': 'some-dir',
            'stdout': io.StringIO(),
            'seconds_per_frame': 0.1,
        }
        self.out = b''
        self.err = b"""Output #0, image2, to '/home/foo/.cache/gif-for-cli/0.0.0/2094cb18c10ddb47dbe239ddbd702cc0-160cols-cw3px-ch6px/jpg/%04d.jpg':
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

    def test_ffmpeg_success(self, mock_Popen):
        mock_process = Mock()
        mock_process.returncode = 0
        mock_process.communicate.return_value = (self.out, self.err,)
        mock_Popen.return_value = mock_process

        _run_ffmpeg(**self.options)

        self.assertEqual(
            self.options['stdout'].getvalue(),
            'Exported to:\n{cwd}/{export_filename}\n'.format(cwd=os.getcwd(), **self.options),
        )

    def test_ffmpeg_success_abs_filepath(self, mock_Popen):
        mock_process = Mock()
        mock_process.returncode = 0
        mock_process.communicate.return_value = (self.out, self.err,)
        mock_Popen.return_value = mock_process

        self.options['export_filename'] = '/tmp/foo.gif'

        _run_ffmpeg(**self.options)

        self.assertEqual(
            self.options['stdout'].getvalue(),
            'Exported to:\n{export_filename}\n'.format(**self.options),
        )

    def test_ffmpeg_failure(self, mock_Popen):
        mock_process = Mock()
        mock_process.returncode = 1
        mock_process.communicate.return_value = (self.out, self.err,)
        mock_Popen.return_value = mock_process

        _run_ffmpeg(**self.options)

        self.assertEqual(
            self.options['stdout'].getvalue(),
            'ffmpeg encountered an error: {}\n'.format(self.err),
        )


@patch('gif_for_cli.export._get_txt_frames')
@patch('gif_for_cli.export._export_txt_frames')
@patch('gif_for_cli.export._run_ffmpeg')
class TestExport(unittest.TestCase):
    def test(self, mock_run_ffmpeg, mock_export_txt_frames, mock_get_txt_frames):
        export_filename = 'foo.gif'
        display_dirname = 'some-dir'
        stdout = io.StringIO()
        seconds_per_frame = 0.1
        cpu_pool_size = 2
        output_dirnames = {
            'jpg': 'foo/jpg',
        }

        mock_get_txt_frames.return_value = ['some-dir/0001.txt']

        export(
            export_filename,
            display_dirname,
            stdout,
            seconds_per_frame,
            cpu_pool_size,
            output_dirnames,
        )

        self.assertEqual(mock_get_txt_frames.call_count, 1)
        self.assertEqual(mock_get_txt_frames.call_args[0][0], display_dirname)

        self.assertEqual(mock_export_txt_frames.call_count, 1)
        self.assertEqual(mock_export_txt_frames.call_args[0][0], mock_get_txt_frames.return_value)
        self.assertEqual(mock_export_txt_frames.call_args[0][1], cpu_pool_size)
        self.assertEqual(mock_export_txt_frames.call_args[0][2], stdout)

        self.assertEqual(mock_run_ffmpeg.call_count, 1)
        self.assertEqual(mock_run_ffmpeg.call_args[0][0], export_filename)
        self.assertEqual(mock_run_ffmpeg.call_args[0][1], display_dirname)
        self.assertEqual(mock_run_ffmpeg.call_args[0][2], stdout)
        self.assertEqual(mock_run_ffmpeg.call_args[0][3], seconds_per_frame)
