#!/usr/bin/python3
# -*- coding: utf-8 -*-

import os
import codecs
import shutil
from jinja2 import Environment, FileSystemLoader
from difflib import unified_diff

class template:

    def __init__(self, template):
        self.template      = template
        self.templatedir   = os.path.abspath(template) if os.path.isdir(template) else os.path.abspath(os.path.dirname(template))
        self.env           = Environment(loader=FileSystemLoader(self.templatedir),trim_blocks=True)
        self.substitutions = {}

    def add_subst(self, new):
        self.substitutions.update(new)

    def add_glob(self, new):
        self.env.globals.update(new)

    def clear(self):
        self.substitutions.clear()
        self.env.globals.clear()

    def __savefile(self, filein, fileout, mode, diff):
        if os.path.isdir(filein):
            if not os.path.isdir(fileout):
                os.makedirs(fileout)
            for file in os.listdir(filein):
                sfileout = fileout + '/' + os.path.basename(file)
                self.__savefile(filein + '/' + file, sfileout, mode, diff)
        else:
            content = self.env.get_template(os.path.relpath(filein, self.templatedir)).render(self.substitutions)
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

    def save(self, fileout, mode='w', diff=False):
        self.__savefile(self.template, os.path.abspath(fileout), mode, diff)

