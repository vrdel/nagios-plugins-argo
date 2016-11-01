from distutils.core import setup
import glob, sys

NAME='nagios-plugins-argo'
DIR='/usr/lib/nagios/plugins/argo/'

def get_ver():
    try:
        for line in open(NAME+'.spec'):
            if "Version:" in line:
                return line.split()[1]
    except IOError:
        print "Make sure that %s is in directory"  % (NAME+'.spec')
        sys.exit(1)


setup(name=NAME,
      version=get_ver(),
      author='SRCE, GRNET',
      author_email='dvrcic@srce.hr, themis@grnet.gr',
      description='''
        This package includes probes for ARGO components.
        Currently it supports the following components:
            - ARGO Web API
            - POEM''',
      url='http://argoeu.github.io/',
      data_files=[(DIR, glob.glob('src/*'))],
      packages=['nagios_plugins_argo'],
      package_dir={'nagios_plugins_argo': 'modules/'},
      )
