#!/usr/bin/python3
# -*- coding: utf-8 -*-

import os
import codecs
from jinja2 import Environment, FileSystemLoader
from difflib import unified_diff

class template:

    def __init__(self):
        self.env           = Environment(loader=FileSystemLoader("/"),trim_blocks=True)
        self.substitutions = {}

    def add_subst(self, new):
        self.substitutions.update(new)

    def add_glob(self, new):
        self.env.globals.update(new)

    def clear(self):
        self.substitutions.clear()
        self.env.globals.clear()

    def save(self, filein, fileout, mode='w', diff=False):
        if os.path.isdir(filein):
            if not os.path.isdir(fileout):
                os.makedirs(fileout)
            for file in os.listdir(filein):
                next_fileout = fileout + '/' + file
                next_filein  = filein + '/'  + file
                self.save(next_filein, next_fileout, mode, diff)
        else:
            content = self.env.get_template(filein).render(self.substitutions)
            if diff:
                if os.path.isfile(fileout):
                    before=open(fileout).read().splitlines()
                    after=content.splitlines()
                    print('\n'.join(unified_diff(before, after, fromfile=fileout, tofile=fileout))) 
                else:
                    print("created: " + fileout)

            if mode == "w":
                f = codecs.open(fileout, mode, encoding='utf-8')
                f.write(content)
