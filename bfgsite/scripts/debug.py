""" Run an interactive debugging session  """

from code import interact
import os
import sys

from repoze.bfg.registry import registry_manager
from repoze.bfg.interfaces import IRootFactory

from paste.deploy import loadapp

def main(argv=sys.argv):
    config = None
    if len(argv) > 1:
        config = sys.argv[1]
    if not config:
        # we assume that the console script lives in the 'bin' dir of a
        # sandbox or buildout, and that the .ini file lives in the 'etc'
        # directory of the sandbox or buildout
        me = sys.argv[0]
        me = os.path.abspath(me)
        sandbox = os.path.dirname(os.path.dirname(me))
        config = os.path.join(sandbox, 'website.ini')

    config = os.path.abspath(os.path.normpath(config))

    app = loadapp('config:%s' % config, name='website')
    registry_manager.push(app.registry)
    root_factory = app.registry.getUtility(IRootFactory)
    environ = {}
    root = root_factory(environ)
    cprt = ('Type "help" for more information. "root" is the bfgsite '
            'root object.')
    banner = "Python %s on %s\n%s" % (sys.version, sys.platform, cprt)
    interact(banner, local={'root':root})

if __name__ == '__main__':
    main()
