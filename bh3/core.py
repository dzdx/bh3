#!/usr/bin/env python
# coding: utf-8

import profile
import datetime
import locale
import os
import sys
import re
import random
import struct
import traceback
import argparse
import subprocess as sp
import unicodedata

from os.path import dirname, join

from bh3 import wow
import time
from bh3 import lines

AVATOR_DIR = join(dirname(__file__), 'ascii_imgs')

AVATORS = os.listdir(AVATOR_DIR)


class Valkyrie(object):
    def __init__(self, tty, ns):
        self.tty = tty
        self.ns = ns

        self.select_avator(ns.avator, ns.no)
        self.pic_path = join(AVATOR_DIR, self.avator_name, str(self.avator_no) + '.txt')
        words = lines.linesGetter.get_lines(self.avator_name)
        words = self.filter_words(words, min_length=ns.min_length)
        self.words = wow.DogeDeque(*words)


    def select_avator(self, avator_name, avator_no):
        if avator_name is None:
            if len(AVATORS) == 0:
                sys.stderr.write('avator error: no avator to be choice\n')
                os.exit(1)
            avator_name = random.choice(AVATORS)
        else:
            if avator_name not in AVATORS:
                sys.stderr.write('avator error: no such avator name\n')
                os.exit(1)

        if avator_no is None:
            resources = [os.path.splitext(name)[0]
                         for name in os.listdir(join(AVATOR_DIR, avator_name))
                         if name.endswith('.txt')
                        ]
            if len(resources) == 0:
                sys.stderr.write('avator error: %s has no resource\n' % avator_name)
                os.exit(1)
            avator_no = random.choice(resources)
        self.avator_name = avator_name
        self.avator_no = avator_no


    def setup(self):

        if self.tty.pretty:
            # stdout is a tty, load Shibe and calculate how wide he is
            doge = self.load_doge()
            max_doge = max(map(clean_len, doge)) + 15
        else:
            # stdout is being piped and we should not load Shibe
            doge = []
            max_doge = 15

        if self.tty.width < max_doge:
            # Shibe won't fit, so abort.
            sys.stderr.write('wow, such small terminal\n')
            sys.stderr.write('no doge under {0} column\n'.format(max_doge))
            sys.exit(1)

        # Check for prompt height so that we can fill the screen minus how high
        # the prompt will be when done.
        prompt = os.environ.get('PS1', '').split('\n')
        line_count = len(prompt) + 1

        # Create a list filled with empty lines and Shibe at the bottom.
        fill = range(self.tty.height - len(doge) - line_count)
        self.lines = ['\n' for x in fill]
        self.lines += doge

        # Try to fetch data fed thru stdin
        had_stdin = self.get_stdin_data()


        # Apply the text around Shibe
        self.apply_text()

    def apply_text(self):
        """
        Apply text around doge

        """

        # Calculate a random sampling of lines that are to have text applied
        # onto them. Return value is a sorted list of line index integers.
        linelen = len(self.lines)
        affected = sorted(random.sample(range(linelen), int(linelen / 3.5)))

        for i, target in enumerate(affected, start=1):
            line = self.lines[target]
            line = re.sub('\n', ' ', line)

            word = self.words.get()


            # Generate a new Message, possibly based on a word.
            self.lines[target] = Message(self, line, word).generate()

    def load_doge(self):
        """
        Return pretty ASCII Shibe.

        wow

        """

        with open(self.pic_path) as f:
            if sys.version_info < (3, 0):
                if locale.getpreferredencoding() == 'UTF-8':
                    doge_lines = [l.decode('utf-8') for l in f.xreadlines()]
                else:
                    # encode to printable characters, leaving a space in place
                    # of untranslatable characters, resulting in a slightly
                    # blockier doge on non-UTF8 terminals
                    doge_lines = [
                        l.decode('utf-8')
                        .encode(locale.getpreferredencoding(), 'replace')
                        .replace('?', ' ')
                        for l in f.xreadlines()
                    ]
            else:
                doge_lines = [l for l in f.readlines()]
            return doge_lines


    def filter_words(self, words, min_length):
        return [word for word in words if len(word) >= min_length]

    def get_stdin_data(self):
        """
        Get words from stdin.

        """

        if self.tty.in_is_tty:
            # No pipez found
            return False

        if sys.version_info < (3, 0):
            stdin_lines = (l.decode('utf-8') for l in sys.stdin.xreadlines())
        else:
            stdin_lines = (l for l in sys.stdin.readlines())

        rx_word = re.compile("\w+", re.UNICODE)

        # If we have stdin data, we should remove everything else!
        self.words.clear()
        word_list = [match.group(0)
                     for line in stdin_lines
                     for match in rx_word.finditer(line.lower())]
        word_list = self.filter_words(
            word_list,
            min_length=self.ns.min_length)

        self.words.extend(word_list)

        return True

    def print_avator(self):
        for line in self.lines:
            if sys.version_info < (3, 0):
                line = line.encode('utf8')
            sys.stdout.write(line)
        sys.stdout.flush()


class Message(object):
    """
    A randomly placed and randomly colored message

    """

    def __init__(self, valkyrie, occupied, word):
        self.valkyrie = valkyrie
        self.tty =  valkyrie.tty
        self.occupied = occupied
        self.word = word

    def generate(self):
        msg = self.word

        # Calculate the maximum possible spacer
        interval = self.tty.width - onscreen_len(msg)
        interval -= clean_len(self.occupied)

        if interval < 1:
            # The interval is too low, so the message can not be shown without
            # spilling over to the subsequent line, borking the setup.
            # Return the doge slice that was in this row if there was one,
            # and a line break, effectively disabling the row.
            return self.occupied + "\n"

        # Apply spacing
        msg = u'{0}{1}'.format(' ' * random.choice(range(interval)), msg)

        if self.tty.pretty:
            # Apply pretty ANSI color coding.
            msg = u'\x1b[1m\x1b[38;5;{0}m{1}\x1b[39m\x1b[0m'.format(
                wow.COLORS.get(), msg
            )

        # Line ends are pretty cool guys, add one of those.
        return u'{0}{1}\n'.format(self.occupied, msg)


class TTYHandler(object):
    def setup(self):
        self.height, self.width = self.get_tty_size()
        self.in_is_tty = sys.stdin.isatty()
        self.out_is_tty = sys.stdout.isatty()

        self.pretty = self.out_is_tty
        if sys.platform == 'win32' and os.getenv('TERM') == 'xterm':
            self.pretty = True

    def _tty_size_windows(self, handle):
        try:
            from ctypes import windll, create_string_buffer

            h = windll.kernel32.GetStdHandle(handle)
            buf = create_string_buffer(22)

            if windll.kernel32.GetConsoleScreenBufferInfo(h, buf):
                left, top, right, bottom = struct.unpack('4H', buf.raw[10:18])
                return right - left + 1, bottom - top + 1
        except:
            pass

    def _tty_size_linux(self, fd):
        try:
            import fcntl
            import termios

            return struct.unpack(
                'hh',
                fcntl.ioctl(
                    fd, termios.TIOCGWINSZ, struct.pack('hh', 0, 0)
                )
            )
        except:
            return

    def get_tty_size(self):
        """
        Get the current terminal size without using a subprocess

        http://stackoverflow.com/questions/566746
        I have no clue what-so-fucking ever over how this works or why it
        returns the size of the terminal in both cells and pixels. But hey, it
        does.

        """
        if sys.platform == 'win32':
            # stdin, stdout, stderr = -10, -11, -12
            ret = self._tty_size_windows(-10)
            ret = ret or self._tty_size_windows(-11)
            ret = ret or self._tty_size_windows(-12)
        else:
            # stdin, stdout, stderr = 0, 1, 2
            ret = self._tty_size_linux(0)
            ret = ret or self._tty_size_linux(1)
            ret = ret or self._tty_size_linux(2)

        return ret or (25, 80)


def clean_len(s):
    """
    Calculate the length of a string without it's color codes

    """

    s = re.sub(r'\x1b\[[0-9;]*m', '', s)

    return len(s)


def onscreen_len(s):
    """
    Calculate the length of a unicode string on screen,
    accounting for double-width characters

    """

    if sys.version_info < (3, 0) and isinstance(s, str):
        return len(s)

    length = 0
    for ch in s:
        length += 2 if unicodedata.east_asian_width(ch) == 'W' else 1

    return length


def setup_arguments():
    parser = argparse.ArgumentParser('bh3')

    parser.add_argument(
        '--avator',
        help='which bh3 avator',
        dest='avator',
        choices=AVATORS
    )

    parser.add_argument(
        '--no',
        type=int
    )

    parser.add_argument(
        '--min_length',
        help='pretty minimum',  # minimum length of a word
        type=int,
        default=1,
    )

    parser.add_argument(
        '-mh', '--max-height',
        help='such max height',
        type=int,
    )

    parser.add_argument(
        '-mw', '--max-width',
        help='such max width',
        type=int,
    )
    return parser


def main():
    tty = TTYHandler()
    tty.setup()

    parser = setup_arguments()
    ns = parser.parse_args()
    if ns.max_height:
        tty.height = ns.max_height
    if ns.max_width:
        tty.width = ns.max_width

    try:
        v = Valkyrie(tty, ns)
        v.setup()
        v.print_avator()

    except (UnicodeEncodeError, UnicodeDecodeError):
        # Some kind of unicode error happened. This is usually because the
        # users system does not have a proper locale set up. Try to be helpful
        # and figure out what could have gone wrong.
        traceback.print_exc()
        print()

        lang = os.environ.get('LANG')
        if not lang:
            print('wow error: broken $LANG, so fail')
            return 3

        if not lang.endswith('UTF-8'):
            print(
                "wow error: locale '{0}' is not UTF-8.  ".format(lang) +
                "doge needs UTF-8 to print Shibe.  Please set your system to "
                "use a UTF-8 locale."
            )
            return 2

        print(
            "wow error: Unknown unicode error.  Please report at "
            "https://github.com/dzdx/bh3/issues and include output from "
            "/usr/bin/locale"
        )
        return 1


# wow very main
if __name__ == "__main__":
    sys.exit(main())
