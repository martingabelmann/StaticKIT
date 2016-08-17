#!/usr/bin/python3

from jinja import template
import yaml
import time
import re
import sys

# allow/support basic variable substitions in yaml file
# you can reuse variables with {{variablename}} within other objects
def parse_vars(yamlin):
    # save the initial object
    if 'global_yaml' not in globals():
        global global_yaml
        global_yaml = yamlin

    # recursively go through the object
    if isinstance(yamlin, list):
        yamlout=[]
        for sub in yamlin:
            yamlout.append(parse_vars(sub))
    elif isinstance(yamlin, dict):
        yamlout={}
        for sub in yamlin:
            yamlout[sub] = parse_vars(yamlin[sub])

    # replace {{vars}} in strings with their values
    elif isinstance(yamlin, str):
        foundvars=re.findall('{{(.*?)}}', yamlin)
        if len(foundvars)>0:
            yamlout=''
            for var in foundvars:
                inline_var = '{{' + var + '}}'
                if var in global_yaml:
                    yamlin = yamlin.replace(inline_var, str(global_yaml[var]))
                else:
                    print('{{' + var + '}} is not defined')
                    sys.exit(0)
            yamlout = yamlin
        else:
            yamlout = yamlin

    # be sure nothing gets lost
    else:
        yamlout = yamlin

    return yamlout



try: 
    stream = open('config.yml', 'r')
except:
    print('could not open config.yml')

try:
    rules = yaml.load(stream)
    rules = parse_vars(rules)
except:
    print('config.yml seems not to be a valid yaml file.')

rules.update({'date':time.strftime("%d/%m/%Y")})

html  = template("./www/")
html.add_subst(rules)
html.save('../')
html.clear()
