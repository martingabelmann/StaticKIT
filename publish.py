#!/usr/bin/python3

from jinja import template
import yaml
import os
from shutil import copy2, copystat
import argparse
import time
import re
import sys


"""
parse arguments and print help file
"""

parser = argparse.ArgumentParser(description='build static htmls from jinja templates that fake the KIT layout')

parser.add_argument('--verbose',
                    '-v',
                    action='count',
                    help='more output (use multiple times to increase verbosity level)',
                    default=0)

parser.add_argument('--dryrun',
                    '-d',
                    action='store_true',
                    help='Don\'t write anything to files')

parser.add_argument('--force',
                    '-f',
                    action='store_true',
                    help='Don\'t ask to override existing files')

parser.add_argument('--inputdir',
    		    '-i',
                    default='.',
                    help='directory containing the jinja pages and a config.yml (defaults to the working directory)')

parser.add_argument('--outputdir',
    		    '-o',
                    default=os.path.expanduser('~') + '/.public_html',
                    help='destination directory for static html website (defaults to ~/.public_html)')


"""
variable substitions in yaml files
you can reuse variables with {{variablename}} within other objects
"""
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



"""
anotherversion of copytree
src:    source directory 
dst:    destination directory
ignore: list of ignored files/dirs
"""
def copytree(src, dst, ignore=[], force=False):
    names = os.listdir(src)
    for name in names:
        if name in ignore:
            continue
        srcname = os.path.join(src, name)
        dstname = os.path.join(dst, name)
        if os.path.isdir(srcname):
            if not os.path.exists(dstname):
                os.makedirs(dstname)
            copytree(srcname, dstname, ignore, force)
        else:
            if os.path.exists(dstname):
                srclastedit = os.path.getmtime(srcname)
                dstlastedit = os.path.getmtime(dstname)
                if srclastedit != dstlastedit:
                    override = input(dstname + " was edited, override? (y/n): ") if not force else 'y'
                    if override == "y": 
                        os.remove(dstname)
                    else:
                        continue
                else:
                    continue
            copy2(srcname, dstname)
    copystat(src, dst)

def main():
    args       = parser.parse_args()
    inputdir   = args.inputdir
    outputdir   = args.outputdir
    configfile = inputdir + '/config.yml'
    sourcesdir = os.path.dirname(os.path.abspath(__file__)) + '/sources'
    
    copytree(sourcesdir, outputdir, ['index.html'], args.force)

    try: 
        stream = open(configfile, 'r')
    except FileNotFoundError:
        print('could not open ' + configfile)
        parser.print_help()
        exit(1)

    try:
        rules = yaml.load(stream)
        rules = parse_vars(rules)
    except:
        print('config.yml seems not to be a valid yaml file.')
        exit(1)
        
    rules.update({'date':time.strftime("%d/%m/%Y")})    
    
    html  = template(inputdir + '/pages')
    html.add_subst(rules)
    html.save(outputdir + '/pages')
    html.clear()

if __name__ == "__main__":
    main()
