import os
import time

from .constants import STORED_CELL_CHAR


def display(display_dirname, stdout, num_loops, cell_char, seconds_per_frame):
    txt_frames = [
        open('{}/{}'.format(display_dirname, de.name)).read().replace(STORED_CELL_CHAR, cell_char)
        for de in sorted(os.scandir(display_dirname), key=lambda de: de.name)
        if de.is_file()
    ]


    previous_line_count = 0
    remaining_loops = num_loops or None

    last_line = u'\u001b[0m'

    try:
        while remaining_loops is None or remaining_loops > 0:
            for txt_frame in txt_frames:
                stdout.write(u'\u001b[A' * previous_line_count)
                stdout.write(txt_frame)
                stdout.write('\n')
                stdout.flush()
                previous_line_count = len(txt_frames[0].split('\n'))
                time.sleep(seconds_per_frame)

            if remaining_loops is not None:
                remaining_loops -= 1
        stdout.write(u'\u001b[0m')
    except KeyboardInterrupt:
        last_line = last_line + '\n'
    finally:
        stdout.write(last_line)

    stdout.flush()
