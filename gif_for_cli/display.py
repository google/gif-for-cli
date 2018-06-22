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
import time

from .constants import STORED_CELL_CHAR, ANSI_RESET, ANSI_CURSOR_UP
from .utils import get_sorted_filenames


def display_txt_frames(txt_frames, stdout, num_loops, seconds_per_frame):
    previous_line_count = 0
    remaining_loops = num_loops or None

    try:
        while remaining_loops is None or remaining_loops > 0:
            for txt_frame in txt_frames:
                stdout.write(ANSI_CURSOR_UP * previous_line_count)
                stdout.write(txt_frame)
                stdout.write('\n')
                stdout.flush()
                previous_line_count = len(txt_frames[0].split('\n'))
                time.sleep(seconds_per_frame)

            if remaining_loops is not None:
                remaining_loops -= 1
        stdout.write(ANSI_RESET)
    except KeyboardInterrupt:
        # ensure styling is reset
        stdout.write(ANSI_RESET)
        # we'll want an extra new line if CTRL+C was pressed
        stdout.write('\n')

    stdout.flush()


def get_txt_frames(display_dirname, cell_char):
    return [
        open('{}/{}'.format(display_dirname, filename)).read().replace(STORED_CELL_CHAR, cell_char)
        for filename in get_sorted_filenames(display_dirname, 'txt')
    ]


def display(display_dirname, stdout, num_loops, cell_char, seconds_per_frame):
    txt_frames = get_txt_frames(display_dirname, cell_char)

    display_txt_frames(txt_frames, stdout, num_loops, seconds_per_frame)
