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
import io
import unittest
from unittest.mock import patch, Mock

from gif_for_cli.utils import (
    _get_default_display_mode,
    _log_frame_progress,
    _pool_type,
    get_parser,
    get_output_dirnames,
    get_sorted_filenames,
)


class TestGetDefaultDisplayMode(unittest.TestCase):
    def test_empty_env(self):
        self.assertEqual(_get_default_display_mode({}), 'nocolor')

    def test_256(self):
        self.assertEqual(_get_default_display_mode({
            'TERM': 'xterm-256color',
        }), '256fgbg')

    def test_truecolor(self):
        self.assertEqual(_get_default_display_mode({
            'TERM': 'xterm-256color',
            'COLORTERM': 'truecolor',
        }), 'truecolor')


class TestLogFrameProgress(unittest.TestCase):
    def test(self):
        total = 5
        results = range(0, total)
        stdout = io.StringIO()

        _log_frame_progress(total, results, stdout)

        output = stdout.getvalue()

        self.assertEqual(output[-1], '\n')

        output = output[:-1].split(u'\u001b[2K\u001b[1000D')

        self.assertEqual(output, [
            'Processed 0/5 frames...',
            'Processed 1/5 frames...',
            'Processed 2/5 frames...',
            'Processed 3/5 frames...',
            'Processed 4/5 frames...',
            'Processed 5/5 frames...',
        ])


class TestPoolType(unittest.TestCase):
    def test_none(self):
        self.assertIsNone(_pool_type(None))

    def test_int_string(self):
        self.assertEqual(_pool_type('2'), 2)

    def test_int_string_0(self):
        with self.assertRaises(argparse.ArgumentTypeError):
            _pool_type('0')


class TestGetParser(unittest.TestCase):
    def test(self):
        parser = get_parser({})

        self.assertIsNotNone(parser)


class TestGetOutputDirnames(unittest.TestCase):
    def test(self):
        output_dirnames = get_output_dirnames(
            '/home/foo',
            '0.0.0',
            '2094cb18c10ddb47dbe239ddbd702cc0',
            160,
            140,
            3,
            6
        )

        dirname = '/home/foo/.cache/gif-for-cli/0.0.0/2094cb18c10ddb47dbe239ddbd702cc0-160cols-140rows-cw3px-ch6px'  # noqa: E501

        self.assertEqual(output_dirnames['.'], dirname)
        self.assertEqual(output_dirnames['jpg'], dirname + '/jpg')
        self.assertEqual(output_dirnames['nocolor'], dirname + '/nocolor')
        self.assertEqual(output_dirnames['256'], dirname + '/256')
        self.assertEqual(output_dirnames['truecolor'], dirname + '/truecolor')


@patch('os.scandir')
class TestGetSortedFilenames(unittest.TestCase):
    def test(self, mock_scandir):
        display_dirname = 'some-dir'

        def mock_entry(name, is_file):
            m = Mock()
            m.name = name
            m.is_file.return_value = is_file
            return m

        mock_scandir.return_value = [
            mock_entry('.', False),
            mock_entry('..', False),
            mock_entry('sike.txt', False),
            mock_entry('.DS_Store', True),
            mock_entry('0001.txt', True),
            mock_entry('0002.txt', True),
        ]

        sorted_filenames = get_sorted_filenames(display_dirname, 'txt')

        self.assertEqual(mock_scandir.call_count, 1)
        self.assertEqual(mock_scandir.call_args[0][0], display_dirname)
        self.assertEqual(list(sorted_filenames), [
            '0001.txt',
            '0002.txt',
        ])
