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
import unittest
from unittest.mock import patch

from gif_for_cli.constants import ANSI_CURSOR_UP, ANSI_RESET, STORED_CELL_CHAR
from gif_for_cli.display import display_txt_frames, get_txt_frames, display


class TestDisplayTxtFrames(unittest.TestCase):
    def setUp(self):
        self.num_frames = 5
        self.width = 10
        self.height = 5
        self.txt_frames = [
            '\n'.join([str(i) * self.width] * self.height)
            for i in range(self.num_frames)
        ]
        self.seconds_per_frame = 200

    def test_3_loops(self):
        stdout = io.StringIO()

        txt_frames = self.txt_frames
        num_loops = 3

        with patch('time.sleep') as mock_sleep:
            display_txt_frames(txt_frames, stdout, num_loops, self.seconds_per_frame)

        self.assertEqual(mock_sleep.call_count, num_loops * len(txt_frames))
        for call in mock_sleep.call_args_list:
            self.assertEqual(call[0][0], self.seconds_per_frame)

        output_ending = '\n' + ANSI_RESET
        output = stdout.getvalue()

        self.assertEqual(output[-len(output_ending):], output_ending)

        output = output[:-len(output_ending)]
        output = output.split('\n' + (ANSI_CURSOR_UP * self.height))

        self.assertEqual(output, self.txt_frames * num_loops)

    def test_0_loops(self):
        stdout = io.StringIO()

        txt_frames = self.txt_frames
        num_loops = 0
        error_after_num_loops = 5
        error_after_num_sleep_calls = error_after_num_loops * len(txt_frames)

        with patch('time.sleep') as mock_sleep:
            num_sleep_calls = 0

            def sleep_side_effect(s):
                nonlocal num_sleep_calls
                num_sleep_calls += 1
                if num_sleep_calls >= error_after_num_sleep_calls:
                    raise KeyboardInterrupt()
                return
            mock_sleep.side_effect = sleep_side_effect

            display_txt_frames(txt_frames, stdout, num_loops, self.seconds_per_frame)

        self.assertEqual(mock_sleep.call_count, error_after_num_loops * len(txt_frames))
        for call in mock_sleep.call_args_list:
            self.assertEqual(call[0][0], self.seconds_per_frame)

        output_ending = '\n' + ANSI_RESET + '\n'
        output = stdout.getvalue()

        self.assertEqual(output[-len(output_ending):], output_ending)

        output = output[:-len(output_ending)]
        output = output.split('\n' + (ANSI_CURSOR_UP * self.height))

        self.assertEqual(output, self.txt_frames * error_after_num_loops)


@patch('gif_for_cli.display.open')
@patch('gif_for_cli.display.get_sorted_filenames')
class TestGetTxtFrames(unittest.TestCase):
    def test(self, mock_get_sorted_filenames, mock_open):
        display_dirname = 'some-dir'
        cell_char = '$'

        mock_get_sorted_filenames.return_value = ['0001.txt', '0002.txt']
        mock_open.side_effect = lambda *args, **kwargs: io.StringIO(STORED_CELL_CHAR * 10)

        txt_frames = get_txt_frames(display_dirname, cell_char)

        self.assertEqual(len(txt_frames), 2)
        self.assertEqual(txt_frames[0], cell_char * 10)
        self.assertEqual(txt_frames[1], cell_char * 10)

        self.assertEqual(mock_get_sorted_filenames.call_count, 1)
        self.assertEqual(mock_get_sorted_filenames.call_args[0][0], display_dirname)
        self.assertEqual(mock_open.call_count, 2)
        self.assertEqual(mock_open.call_args_list[0][0][0], display_dirname + '/' + '0001.txt')
        self.assertEqual(mock_open.call_args_list[1][0][0], display_dirname + '/' + '0002.txt')


@patch('gif_for_cli.display.get_txt_frames')
@patch('gif_for_cli.display.display_txt_frames')
class TestDisplay(unittest.TestCase):
    def test(self, mock_display_txt_frames, mock_get_txt_frames):
        display_dirname = 'some-dir'
        stdout = io.StringIO()
        num_loops = 3
        cell_char = '$'
        seconds_per_frame = 0.1

        display(display_dirname, stdout, num_loops, cell_char, seconds_per_frame)

        self.assertEqual(mock_get_txt_frames.call_count, 1)
        self.assertEqual(mock_get_txt_frames.call_args[0][0], display_dirname)
        self.assertEqual(mock_get_txt_frames.call_args[0][1], cell_char)

        self.assertEqual(mock_display_txt_frames.call_count, 1)
        self.assertEqual(mock_display_txt_frames.call_args[0][0], mock_get_txt_frames.return_value)
        self.assertEqual(mock_display_txt_frames.call_args[0][1], stdout)
        self.assertEqual(mock_display_txt_frames.call_args[0][2], num_loops)
        self.assertEqual(mock_display_txt_frames.call_args[0][3], seconds_per_frame)
