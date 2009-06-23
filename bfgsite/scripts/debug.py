""" Run an interactive debugging session  """

import os
import sys

from repoze.bfg.paster import BFGShellCommand

def main(argv=sys.argv):
    config = None
    if len(argv) > 1:
        config = sys.argv[1]
    if not config:
        # we assume that the console script lives in the 'bin' dir of a
        # sandbox or buildout, and that the .ini file lives in the 'etc'
        # directory of the sandbox or buildout
        exe = sys.executable
        sandbox = os.path.dirname(os.path.dirname(os.path.abspath(exe)))
        config = os.path.join(sandbox, 'bfgsite.ini')
    shell = BFGShellCommand('bfg')
    shell.args = (config, 'website')
    shell.command()

if __name__ == '__main__':
    main()
