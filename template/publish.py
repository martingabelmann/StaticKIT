#!/usr/bin/python3

from jinja import template
import yaml


try: 
    stream = open('config.yml', 'r')
except:
    print('could not open config.yml')


try:
    rules = yaml.load(stream)
except:
    print('config.tml seems not to be a valid yaml file.')



html  = template("index.html")
html.add_subst(rules)
html.save('../index.html')
html.clear()
