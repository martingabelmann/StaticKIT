#!/usr/bin/python3

from jinja import template
import yaml
import os
from shutil import copy2, copystat
import argparse
import logging
import time
import re
import sys


"""
parse arguments and print help file
"""

parser = argparse.ArgumentParser(description='Build static htmls from Jinja2 templates that fake the KIT layout')

parser.add_argument('--verbose',
                    '-v',
                    action='count',
                    help='more output (use multiple times to increase verbosity level)',
                    default=0)

parser.add_argument('--dryrun',
                    '-d',
                    action='store_true',
                    help='don\'t write anything to files')

parser.add_argument('--force',
                    '-f',
                    action='store_true',
                    help='don\'t ask to override existing files')

parser.add_argument('--inputdir',
    		        '-i',
                    default='.',
                    help='directory containing the jinja pages and a config.yml (defaults to the working directory)')

parser.add_argument('--outputdir',
    		        '-o',
                    default=os.path.expanduser('~') + '/.public_html',
                    help='destination directory for static html website (defaults to ~/.public_html)')

parser.add_argument('--init',
    		        '-ii',
                    help='initialize a new project at directory INIT')

parser.add_argument('--diff',
    		        '-dd',
                    action='store_true',
                    help='show a simple diff between edited files')

"""
variable substitions in yaml files
reuse variables with {{variablename}} within other objects
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
def copytree(src, dst, ignore=[], verbose=0, force=False):
    names = os.listdir(src)
    for name in names:
        if name in ignore:
            continue
        srcname = os.path.join(src, name)
        dstname = os.path.join(dst, name)
        if os.path.isdir(srcname):
            if not os.path.exists(dstname):
                os.makedirs(dstname)
            copytree(srcname, dstname, ignore, verbose, force)
        else:
            if os.path.exists(dstname):
                srclastedit = os.path.getmtime(srcname)
                dstlastedit = os.path.getmtime(dstname)
                if srclastedit != dstlastedit:
                    override = input(dstname + " was edited, override? (y/n): ") if not force else 'y'
                    if override == "y": 
                        if verbose > 0:
                            print('removing ' + dstname)
                        os.remove(dstname)
                    else:
                        continue
                else:
                    continue
            if verbose > 0:
                print('copying ' + srcname + ' to ' + dstname)
            copy2(srcname, dstname)
    copystat(src, dst)


"""
initialize a new project
dest: destination where the project is initialized
"""
def init(dest, dryrun=False, force=False):
    if os.path.isdir(dest) and os.listdir!="" and not force:
        logging.error('directory ' + dest + ' already exists and is not empty!')
        exit(1)
    if not dryrun:
        print("copying example project to " + dest)
        copytree(os.path.dirname(os.path.abspath(__file__)) + '/example', dest, [], force)


"""
load YAML rules from file
and build htmls wih jinja2

inputdir:   dir containing jinja templates
outputdir:  where to place the resulting files
configfile: yaml that is used for the templates 
"""
def publish(inputdir, outputdir, configfile, dryrun=False, diff=False, force=False):
    logging.debug("input location: " + inputdir)
    logging.debug("output location: " + outputdir) 
    logging.debug("using config file from: " + configfile)

    try:
        logging.info("opening config file "  + configfile)
        stream = open(configfile, 'r')
    except FileNotFoundError:
        logging.error("could not open config file")
        logging.error("file not found:" + configfile)
        exit(1)

    try:
        logging.info("parsing config.yml for YAML")
        rules = yaml.load(stream)
        rules = parse_vars(rules)
    except:
        # TODO raise typical yaml exceptions
        logging.error("config.yml seems not to be a valid yaml file.")
        exit(1)
    
    
    logging.debug("setting additional template variables")
    rules.update({'date':time.strftime("%d/%m/%Y")})    
   
    logging.debug("using YAML structure:\n+++++\n" + yaml.dump(rules) + "+++++")

    logging.info("loading template(s) " + inputdir)
    html  = template(inputdir)
    
    logging.info("applying template rules from YAML")
    html.add_subst(rules)
    
    mode = 'r' if dryrun else 'w'
    logging.info("saving resulting documents to " + outputdir)
    html.save(outputdir, mode, diff)
    html.clear()

"""
set loglevel, run argparser and init/publish
"""
def main():
    args       = parser.parse_args()

    logging.basicConfig(format='%(levelname)s:%(message)s')
    if args.verbose == 0:
        logging.getLogger().setLevel(logging.ERROR) 
    elif args.verbose == 1:
        logging.getLogger().setLevel(logging.INFO) 
    elif args.verbose >= 2:
        logging.getLogger().setLevel(logging.DEBUG)
        logging.debug("running in debug mode")
    else:
        logging.getLogger().setLevel(logging.DEBUG)

    inputdir=os.path.abspath(args.inputdir)
    outputdir=os.path.abspath(args.outputdir)
    configfile=os.path.abspath(args.inputdir + '/config.yml')
    sourcesdir=os.path.dirname(os.path.abspath(__file__)) + '/sources'

    if args.init:
        init(args.init, args.dryrun, args.force)
    else:
        print('running publish for ' + inputdir)
        publish(inputdir + '/pages', 
                outputdir + '/pages', 
                configfile, 
                dryrun=args.dryrun,
                diff=args.diff,
                force=args.force)
                
 
        print('running publish for ' + sourcesdir + '/index.html')
        publish(sourcesdir + '/index.html', 
                outputdir + '/index.html', 
                configfile, 
                dryrun=args.dryrun,
                diff=args.diff,
                force=args.force)
               
        if not args.dryrun:
            copytree(sourcesdir,
                     outputdir, 
                     ['index.html'],
                     args.verbose,
                     args.force)


"""
run main if this file is executed
"""
if __name__ == "__main__":
    main()
