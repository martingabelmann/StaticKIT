#!/usr/bin/python3
# -*- coding: utf-8 -*-

import sys
import os
import codecs
import shutil
from jinja2 import Environment, FileSystemLoader

class template:

    def __init__(self, template):
        self.template     = template
        self.templatedir  = os.path.dirname(os.path.abspath(__file__))
        self.env          = Environment(loader=FileSystemLoader(self.templatedir),
                                       trim_blocks=True
                                      )
        self.substitutions = {}

    def add_subst(self, new):
        self.substitutions.update(new)

    def add_glob(self, new):
        self.env.globals.update(new)

    def clear(self):
        self.substitutions.clear()
        self.env.globals.clear()

    def save(self, fileout, mode='w'):
        content = self.env.get_template(self.template).render(self.substitutions)
        dirname = os.path.dirname(fileout)
        if not os.path.exists(dirname) and dirname != '':
            os.makedirs(dirname)

        f = codecs.open(fileout, mode, encoding='utf-8')
        f.write(content) 
