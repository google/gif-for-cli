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

import third_party
from .constants import STORED_CELL_CHAR
from .utils import get_sorted_filenames, pool_abstraction, memoize


@memoize
def to_rgb(s):
    return tuple(x256.to_rgb(int(s)))


class ColorSelector:
    def __init__(self):
        self.seq = ""
        self.collecting = False
        self.bg = (0, 0, 0,)
        self.fg = (255, 255, 255,)

    def add_char(self, char):
        if(char == u'\u001b'):
            self.collecting = True
            return True
        elif(char == "m" and self.collecting):
            self.finalize()
            self.collecting = False
            return True
        elif(self.collecting):
            self.collect(char)
            return True
        return False

    def collect(self,char):
        self.seq += char

    def finalize(self):
        if self.seq == '[0':
            # reset
            self.bg = (0, 0, 0,)
            self.fg = (255, 255, 255,)
        elif self.seq.startswith('[48;5;'):
            # 256 BG
            self.bg = to_rgb(self.seq[6:])
        elif self.seq.startswith('[38;5;'):
            # 256 FG
            self.fg = to_rgb(self.seq[6:])
        elif self.seq.startswith('[38;2;'):
            # truecolor FG
            self.fg = tuple([int(c) for c in self.seq[6:].split(';')])
        self.seq = ""

    def get_colors(self):
        return (self.bg,self.fg)


class Drawer:
    def __init__(self,cols,rows):
        self.font = ImageFont.truetype(
            os.path.join(third_party.__path__[0], 'Roboto_Mono/RobotoMono-Regular.ttf'),
            size=24,
        )
        cell = self.font.getsize('M')
        self.cell_width = cell[0]
        self.cell_height = int(cell[1] * 1.25)
        self.image_size = (cols * self.cell_width, rows * self.cell_height)
        self.image = Image.new('RGB', self.image_size)
        self.draw = ImageDraw.Draw(self.image)

    def draw_ascii_char(self,xy,char,colors):
        xy = (xy[0] * self.cell_width,xy[1] * self.cell_height)
        self.draw.rectangle(
            [
                xy,
                (xy[0] + self.cell_width, xy[1] + self.cell_height),
            ],
            fill=colors[0],
        )
        self.draw.text(
            xy,
            char,
            fill=colors[1],
            font=self.font,
        )

    def crop(self,cols,rows):
        self.image = self.image.crop((0, 0, cols * self.cell_width, rows * self.cell_height))

    def save(self,filename):
        self.image.save(filename)


def export_txt_frame(txt_filename, cell_char, rows, cols):
    # PNG is used because JPG looked a little desaturated.
    img_filename = '{}.png'.format(txt_filename)
    txt = open(txt_filename).read().replace(STORED_CELL_CHAR, cell_char)
    drawer = Drawer(cols,rows)
    cs = ColorSelector()

    for row, line in enumerate(txt.split('\n')):
        col = 0
        for char in line:
            added = cs.add_char(char)
            if(added):
                pass
            else:
                # draw char on background
                drawer.draw_ascii_char((col,row),char,cs.get_colors())
                col += 1
    # Chances are there's fewer rows.
    drawer.crop(col,row + 1)
    drawer.save(img_filename)


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
    _, err = p.communicate()

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
