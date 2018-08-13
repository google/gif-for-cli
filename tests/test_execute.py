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
from unittest.mock import patch

from gif_for_cli.execute import execute


@patch('gif_for_cli.execute.process_input_source')
@patch('gif_for_cli.execute.os.makedirs')
@patch('gif_for_cli.execute.generate')
@patch('gif_for_cli.execute.display')
@patch('gif_for_cli.execute.export')
class TestExecute(unittest.TestCase):
    def test_new(self, mock_export, mock_display, mock_generate,
            mock_makedirs, mock_process_input_source):
        mock_process_input_source.side_effect = lambda input_source, api_key: input_source

        environ = {}
        argv = []
        stdout = io.StringIO()

        input_source = ''
        cols = 160
        rows = 40
        cell_width = 3
        cell_height = 6
        num_frames = 11
        seconds = 1.1

        with patch('gif_for_cli.execute.open') as mocked_open:
            mocked_open.return_value = io.StringIO(json.dumps({
                'input_source': input_source,
                'input_source_file': input_source,
                'cols': cols,
                'rows': rows,
                'cell_width': cell_width,
                'cell_height': cell_height,
                'num_frames': num_frames,
                'seconds': seconds,
            }))

            with patch('gif_for_cli.execute.os.path.exists') as mock_exists:
                mock_exists.return_value = False

                execute(environ, argv, stdout)

        self.assertEqual(mock_process_input_source.call_count, 1)
        # for some reaosn, this intercepts some locale laoding
        paths = sorted([
            call[0][0]
            for call in mock_exists.call_args_list[-6:]
        ])

        self.assertTrue(paths[0].endswith(
            '/d41d8cd98f00b204e9800998ecf8427e-160cols-40rows-cw3px-ch6px'
        ))
        self.assertTrue(paths[1].endswith(
            '/d41d8cd98f00b204e9800998ecf8427e-160cols-40rows-cw3px-ch6px/256'
        ))
        self.assertTrue(paths[2].endswith(
            '/d41d8cd98f00b204e9800998ecf8427e-160cols-40rows-cw3px-ch6px/256fgbg'
        ))
        self.assertTrue(paths[3].endswith(
            '/d41d8cd98f00b204e9800998ecf8427e-160cols-40rows-cw3px-ch6px/jpg'
        ))
        self.assertTrue(paths[4].endswith(
            '/d41d8cd98f00b204e9800998ecf8427e-160cols-40rows-cw3px-ch6px/nocolor'
        ))
        self.assertTrue(paths[5].endswith(
            '/d41d8cd98f00b204e9800998ecf8427e-160cols-40rows-cw3px-ch6px/truecolor'
        ))
        self.assertEqual(mock_makedirs.call_count, 6)
        self.assertEqual(mock_generate.call_count, 1)
        self.assertEqual(mocked_open.call_count, 1)
        self.assertEqual(mock_display.call_count, 1)
        self.assertEqual(mock_export.call_count, 0)

    def test_new_no_display(self, mock_export, mock_display, mock_generate,
            mock_makedirs, mock_process_input_source):
        mock_process_input_source.side_effect = lambda input_source, api_key: input_source

        environ = {}
        argv = ['--no-display']
        stdout = io.StringIO()

        input_source = ''
        cols = 160
        rows = 40
        cell_width = 3
        cell_height = 6
        num_frames = 11
        seconds = 1.1

        with patch('gif_for_cli.execute.open') as mocked_open:
            mocked_open.return_value = io.StringIO(json.dumps({
                'input_source': input_source,
                'input_source_file': input_source,
                'cols': cols,
                'rows': rows,
                'cell_width': cell_width,
                'cell_height': cell_height,
                'num_frames': num_frames,
                'seconds': seconds,
            }))

            with patch('gif_for_cli.execute.os.path.exists') as mock_exists:
                mock_exists.return_value = False

                execute(environ, argv, stdout)

        self.assertEqual(mock_process_input_source.call_count, 1)
        # for some reaosn, this intercepts some locale laoding
        paths = sorted([
            call[0][0]
            for call in mock_exists.call_args_list[-6:]
        ])

        self.assertTrue(paths[0].endswith(
            '/d41d8cd98f00b204e9800998ecf8427e-160cols-40rows-cw3px-ch6px'
        ))
        self.assertTrue(paths[1].endswith(
            '/d41d8cd98f00b204e9800998ecf8427e-160cols-40rows-cw3px-ch6px/256'
        ))
        self.assertTrue(paths[2].endswith(
            '/d41d8cd98f00b204e9800998ecf8427e-160cols-40rows-cw3px-ch6px/256fgbg'
        ))
        self.assertTrue(paths[3].endswith(
            '/d41d8cd98f00b204e9800998ecf8427e-160cols-40rows-cw3px-ch6px/jpg'
        ))
        self.assertTrue(paths[4].endswith(
            '/d41d8cd98f00b204e9800998ecf8427e-160cols-40rows-cw3px-ch6px/nocolor'
        ))
        self.assertTrue(paths[5].endswith(
            '/d41d8cd98f00b204e9800998ecf8427e-160cols-40rows-cw3px-ch6px/truecolor'
        ))
        self.assertEqual(mock_makedirs.call_count, 6)
        self.assertEqual(mock_generate.call_count, 1)
        self.assertEqual(mocked_open.call_count, 1)
        self.assertEqual(mock_display.call_count, 0)
        self.assertEqual(mock_export.call_count, 0)

    def test_cached(self, mock_export, mock_display, mock_generate,
            mock_makedirs, mock_process_input_source):
        mock_process_input_source.side_effect = lambda input_source, api_key: input_source

        environ = {}
        argv = []
        stdout = io.StringIO()

        input_source = ''
        cols = 160
        rows = 40
        cell_width = 3
        cell_height = 6
        num_frames = 11
        seconds = 1.1

        with patch('gif_for_cli.execute.open') as mocked_open:
            mocked_open.return_value = io.StringIO(json.dumps({
                'input_source': input_source,
                'input_source_file': input_source,
                'cols': cols,
                'rows': rows,
                'cell_width': cell_width,
                'cell_height': cell_height,
                'num_frames': num_frames,
                'seconds': seconds,
            }))

            with patch('gif_for_cli.execute.os.path.exists') as mock_exists:
                mock_exists.return_value = True

                execute(environ, argv, stdout)

        self.assertEqual(mock_process_input_source.call_count, 1)
        # for some reaosn, this intercepts some locale laoding
        paths = sorted([
            call[0][0]
            for call in mock_exists.call_args_list[-6:]
        ])
        self.assertTrue(paths[0].endswith(
            '/d41d8cd98f00b204e9800998ecf8427e-160cols-40rows-cw3px-ch6px'
        ))
        self.assertEqual(mock_makedirs.call_count, 0)
        self.assertEqual(mock_generate.call_count, 0)
        self.assertEqual(mocked_open.call_count, 1)
        self.assertEqual(mock_display.call_count, 1)
        self.assertEqual(mock_display.call_args[1]['seconds_per_frame'], 0.1)
        self.assertEqual(mock_export.call_count, 0)

    def test_export(self, mock_export, mock_display, mock_generate,
            mock_makedirs, mock_process_input_source):
        mock_process_input_source.side_effect = lambda input_source, api_key: input_source

        environ = {}
        argv = ['--export=foo.gif']
        stdout = io.StringIO()

        input_source = ''
        cols = 160
        rows = 40
        cell_width = 3
        cell_height = 6
        num_frames = 11
        seconds = 1.1

        with patch('gif_for_cli.execute.open') as mocked_open:
            mocked_open.return_value = io.StringIO(json.dumps({
                'input_source': input_source,
                'input_source_file': input_source,
                'cols': cols,
                'rows': rows,
                'cell_width': cell_width,
                'cell_height': cell_height,
                'num_frames': num_frames,
                'seconds': seconds,
            }))

            with patch('gif_for_cli.execute.os.path.exists') as mock_exists:
                mock_exists.return_value = True

                execute(environ, argv, stdout)

        self.assertEqual(mock_process_input_source.call_count, 1)
        # for some reaosn, this intercepts some locale laoding
        paths = sorted([
            call[0][0]
            for call in mock_exists.call_args_list[-6:]
        ])
        self.assertTrue(paths[0].endswith(
            '/d41d8cd98f00b204e9800998ecf8427e-160cols-40rows-cw3px-ch6px'
        ))
        self.assertEqual(mock_makedirs.call_count, 0)
        self.assertEqual(mock_generate.call_count, 0)
        self.assertEqual(mocked_open.call_count, 1)
        self.assertEqual(mock_display.call_count, 0)
        self.assertEqual(mock_export.call_count, 1)
