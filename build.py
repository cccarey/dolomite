#!/usr/bin/env python
import os, sys, tarfile, shutil
import subprocess as proc
import warnings

warnings.filterwarnings('ignore','.*apt API not stable yet.*')
import apt

def create_dir(name):
    if not os.path.exists(name):
        #os.mkdir(name)
        os.makedirs(name)
        
def dependenciesMet(packages):
    met = True
    cache = apt.Cache()
    for package in packages:
        pkg = cache[package]
        if not pkg.isInstalled:
            print("%s package is not installed." % package)
            met = False
    return met

def usage():
    print("Usage: %s component_name" % sys.argv[0])
    
def get_config(component):
    config_file = open("%s-conf" % component)
    config = { }
    for setting in config_file:
        if len(setting.split('=',1)) > 1:
            if (len(setting.split(' '))) > 1:
                config[setting.split('=',1)[0]] = setting.rstrip('\n').split('=',1)[1].split(' ')
            else:
                config[setting.split('=',1)[0]] = setting.rstrip('\n').split('=',1)[1]
    return config

def main():
    if len(sys.argv) != 2:
        usage()
        sys.exit(1)
    component = sys.argv[1]
    
    print("building %s" % component)

    config = get_config(component)
    
    create_dir('tmp')

    basedir = os.getcwd()
    os.chdir('tmp')
    buildPrefix = "/".join([os.getcwd(), 'tar/dolomite-env'])

    if 'BUILDDEP' in config:
        print("checking build depedencies...")
        if not dependenciesMet(config['BUILDDEP']):
            print("install dependencies using the following command and try again")
            print("sudo apt-get install %s" % " ".join(config['BUILDDEP']))
            sys.exit(1)
        
    print("downloading source...")
    if 'SOURCEPATH' in config:
        try:
            proc.check_call(['wget','-c', '%s/%s' % (config['SOURCEPATH'], config['SOURCETARFILE'])])
        except proc.CalledProcessError:
            sys.exit(1)
    elif 'SOURCEPKG' in config:
        try:
            proc.check_call(['apt-get','source',config['SOURCEPKG']])
        except proc.CalledProcessError:
            sys.exit(1)

    if 'SOURCETARFILE' in config:
        print("extracting tar ball...")    
        memcached = tarfile.open(name=config['SOURCETARFILE'], mode='r:gz')
        memcached.extractall()
    
    print("configuring...")
    os.chdir(config['BUILDDIR'])
    configcmd = './configure'
    if 'CONFIGOVERRIDE' in config:
        configcmd = config['CONFIGOVERRIDE']
    cmdline = [configcmd,'--prefix=%s' % buildPrefix,'--mandir=/tmp/dump']
    if 'CONFIGEXTRA' in config:
        if type(config['CONFIGEXTRA']) is list:
            cmdline.extend(config['CONFIGEXTRA'])
        else:
            cmdline.append(config['CONFIGEXTRA'])
    try:
        proc.check_call(cmdline)
    except proc.CalledProcessError:
        sys.exit(1)
        
    print("building...")
    try:
        proc.check_call(['make'])
    except proc.CalledProcessError:
        sys.exit(1)

    print("installing files...")
    try:
        proc.check_call(['make','install'])
    except proc.CalledProcessError:
        sys.exit(1)
    
    os.chdir(basedir)
    if 'POSTBUILDCLEANUP' in config:
        print("running post build cleanup command")
        proc.check_call([config['POSTBUILDCLEANUP']])
        
if __name__ == "__main__":
    main()
