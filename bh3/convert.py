# coding=utf-8


import os
import subprocess
import StringIO

import sys

IMGS_DIR = 'bh3/imgs'
ASCII_IMGS_DIR = 'bh3/ascii_imgs'



class AvatorImageConverter(object):
    def __init__(self, imgs_dir, dest_dir):
        self.imgs_dir = imgs_dir
        self.dest_dir = dest_dir

    def iter_avator_img(self):
        for name in os.listdir(self.imgs_dir):
            avator_dir = os.path.join(IMGS_DIR, name)
            if os.path.isdir(avator_dir):
                for img_name in os.listdir(avator_dir):
                    no, ext = os.path.splitext(img_name)
                    if ext != '.png':
                        continue
                    yield name, no, os.path.join(avator_dir, img_name)

    def convert_avator_img(self, name, no, img_path):
        ascii_img_dir = os.path.join(self.dest_dir, name)
        if not os.path.exists(ascii_img_dir):
            os.makedirs(ascii_img_dir)
        dest_path = os.path.join(self.dest_dir, name, no + '.txt')
        subprocess.check_call(['img2xterm', '-yw', '2', img_path, dest_path])


    def convert(self):
        for name, no, img_path in self.iter_avator_img():
            self.convert_avator_img(name, no, img_path)


if __name__ == '__main__':
    converter = AvatorImageConverter(IMGS_DIR, ASCII_IMGS_DIR)
    converter.convert()
