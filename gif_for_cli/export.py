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
import os
import subprocess

from PIL import Image, ImageDraw, ImageFont
from x256 import x256

from . import third_party
from .constants import STORED_CELL_CHAR
from .utils import get_sorted_filenames, pool_abstraction, memoize


@memoize
def to_rgb(s):
    return tuple(x256.to_rgb(int(s)))


def export_txt_frame(txt_filename, cell_char, rows, cols, **options):
    # PNG is used because JPG looked a little desaturated.
    img_filename = '{}.png'.format(txt_filename)

    font = ImageFont.truetype(
        os.path.join(third_party.__path__[0], 'Roboto_Mono/RobotoMono-Regular.ttf'),
        size=24,
    )
    em_size = font.getsize('M')

    img_cell_width = em_size[0]
    img_cell_height = int(em_size[1] * 1.25)

    im = Image.new('RGB', (cols * img_cell_width, rows * img_cell_height,))
    draw = ImageDraw.Draw(im)

    txt = open(txt_filename).read().replace(STORED_CELL_CHAR, cell_char)

    bg = (0, 0, 0,)
    fg = (255, 255, 255,)
    escaped = False
    escape_seq = []

    for row, line in enumerate(txt.split('\n')):
        col = 0
        for char in line:
            if char == u'\u001b':
                escaped = True
            elif escaped:
                if char == 'm':
                    # act on escape_seq
                    escape_seq = ''.join(escape_seq)

                    if escape_seq == '[0':
                        # reset
                        bg = (0, 0, 0,)
                        fg = (255, 255, 255,)
                    elif escape_seq.startswith('[48;5;'):
                        # 256 BG
                        bg = to_rgb(escape_seq[6:])
                    elif escape_seq.startswith('[38;5;'):
                        # 256 FG
                        fg = to_rgb(escape_seq[6:])
                    elif escape_seq.startswith('[38;2;'):
                        # truecolor FG
                        fg = tuple([int(c) for c in escape_seq[6:].split(';')])

                    escaped = False
                    escape_seq = []
                else:
                    escape_seq.append(char)
            else:
                # draw char on background
                x = col * img_cell_width
                y = row * img_cell_height

                draw.rectangle(
                    [
                        (x, y,),
                        (x + img_cell_width, y + img_cell_height,),
                    ],
                    fill=bg,
                )
                draw.text(
                    (x, y,),
                    char,
                    fill=fg,
                    font=font,
                )

                col += 1

    actual_rows = row + 1
    actual_cols = col

    # Chances are there's fewer rows.
    im = im.crop((0, 0, actual_cols * img_cell_width, actual_rows * img_cell_height))
    im.save(img_filename)


def _get_txt_frames(display_dirname):
    return [
        '{}/{}'.format(display_dirname, filename)
        for filename in get_sorted_filenames(display_dirname, 'txt')
    ]


def _run_ffmpeg(export_filename, display_dirname, stdout, seconds_per_frame):
    if not os.path.isabs(export_filename):
        export_filename = '{}/{}'.format(os.getcwd(), export_filename)

    # convert pngs to .gif using ffmpeg
    cmd = [
        'ffmpeg',
        '-y',
        '-framerate', str(1.0 / seconds_per_frame),
        '-i', '{}/%04d.txt.png'.format(display_dirname),
        export_filename,
    ]
    p = subprocess.Popen(cmd,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )
    out, err = p.communicate()

    if p.returncode == 0:
        stdout.write('Exported to:\n{}\n'.format(export_filename))
    else:
        stdout.write('ffmpeg encountered an error: {}\n'.format(err))


def _export_txt_frames(txt_frames, cpu_pool_size, stdout, **options):
    pool_abstraction(export_txt_frame, txt_frames, cpu_pool_size, stdout, **options)


def export(export_filename, display_dirname, stdout, seconds_per_frame,
        cpu_pool_size, output_dirnames, **options):
    txt_frames = _get_txt_frames(display_dirname)

    _export_txt_frames(txt_frames, cpu_pool_size, stdout, **options)

    _run_ffmpeg(export_filename, display_dirname, stdout, seconds_per_frame)
