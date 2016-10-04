#!/usr/bin/python3

from jinja import template
import yaml
import os
from shutil import copy2, copystat
import argparse
import logging
from datetime import datetime
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
            try:
                copy2(srcname, dstname)
            except FileNotFoundError:
                logging.error(srcname + ' not found')
    try:
        copystat(src, dst)
    except FileNotFoundError:
        logging.error(srcname + ' not found')

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
ckeck if a path exists
"""
def ispath(path):
    path = os.path.abspath(path)
    if os.path.exists(path):
        return path
    else:
        logging.error(path + ' does not exists')
        return False

"""
load YAML rules from file
and build htmls wih jinja2
"""
def main():
    args = parser.parse_args()

    logging.basicConfig(format='%(levelname)s: %(message)s')
    if args.verbose == 0:
        logging.getLogger().setLevel(logging.ERROR) 
    elif args.verbose == 1:
        logging.getLogger().setLevel(logging.INFO) 
    elif args.verbose >= 2:
        logging.getLogger().setLevel(logging.DEBUG)
        logging.debug("running in debug mode")
    else:
        logging.getLogger().setLevel(logging.DEBUG)

    inputdir   = ispath(args.inputdir)
    pagesdir   = ispath(args.inputdir + '/pages')
    outputdir  = os.path.abspath(args.outputdir)
    configfile = ispath(args.inputdir + '/config.yml')
    sourcesdir = ispath(os.path.dirname(os.path.abspath(__file__)) + '/sources')



    if args.init:
        init(args.init, args.dryrun, args.force)
    else:
        logging.debug("input location: " + inputdir)
        logging.debug("output location: " + outputdir) 
        logging.debug("using config file from: " + configfile)
        logging.debug("using sources from: " + sourcesdir)

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
        except Exception as e:
            # TODO raise typical yaml exceptions
            logging.error("config.yml seems not to be a valid yaml file.")
            logging.error(e)
            exit(1)
        
        logging.debug("setting additional template variables")
        rules.update({'date': datetime.now() })    
   
        logging.debug("using YAML structure:\n+++++\n" + yaml.dump(rules) + "+++++")

        logging.info("applying template rules from YAML")
        html  = template()
        html.add_subst(rules)
        
        mode = 'r' if args.dryrun else 'w'
        
        if pagesdir:
            logging.info("saving resulting documents to " + outputdir)
            print('building html pages from ' + inputdir)
            html.save(pagesdir, outputdir + '/pages', mode, args.diff)
        
        if sourcesdir and ispath(sourcesdir + '/index.html'):
            print('building homepage from ' + sourcesdir + '/index.html')
            html.save(sourcesdir + '/index.html', outputdir + '/index.html', mode, args.diff)
        else: 
            logging.error('cannot create an index.html')
            exit(1)

        if 'root_templates' in rules and  isinstance(rules['root_templates'], list):
            print('building extra template files in document root.')
            for tpl in rules['root_templates']:
                if not os.path.isfile(inputdir + '/' + tpl):
                    logging.error('file not found: ' + inputdir + '/' + tpl)
                    continue
                if not args.dryrun:
                    html.save(inputdir + '/' + tpl, outputdir + '/' + tpl, mode, args.diff)

        html.clear()

        if 'copy_files' in rules and  isinstance(rules['copy_files'], list):
            print('copying extra files')
            for f in rules['copy_files']:
                i = inputdir + '/' + f
                o = outputdir + '/' + f
                if os.path.isdir(i) and not args.dryrun:
                    copytree(i, o, [],  args.verbose, args.force)
                elif os.path.isfile(i) and not args.dryrun:
                    copy2(i, o)


        if not args.dryrun and sourcesdir:
            copytree(sourcesdir,
                     outputdir, 
                     ['index.html'],
                     args.verbose,
                     args.force)

        print('done!')

"""
run main if this file is executed
"""
if __name__ == "__main__":
    main()
