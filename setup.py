"""Setup script.

Run "python3 setup --help-commands" to list all available commands and their
descriptions.
"""
import os
import sys
from abc import abstractmethod
from subprocess import CalledProcessError, call, check_call

from pip.req import parse_requirements
from setuptools import Command, find_packages, setup
from setuptools.command.test import test as TestCommand

from kyco import __version__

if 'bdist_wheel' in sys.argv:
    raise RuntimeError("This setup.py does not support wheels")

if 'VIRTUAL_ENV' in os.environ:
    BASE_ENV = os.environ['VIRTUAL_ENV']
else:
    BASE_ENV = '/'


class SimpleCommand(Command):
    """Make Command implementation simpler."""

    user_options = []

    @abstractmethod
    def run(self):
        """Run when command is invoked.

        Use *call* instead of *check_call* to ignore failures.
        """
        pass

    def initialize_options(self):
        """Set defa ult values for options."""
        pass

    def finalize_options(self):
        """Post-process options."""
        pass


class Linter(SimpleCommand):
    """Code linters."""

    description = 'run Pylama on Python files'

    def run(self):
        """Run linter."""
        self.lint()

    @staticmethod
    def lint():
        """Run pylama and radon."""
        files = 'setup.py tests kyco'
        print('Pylama is running. It may take several seconds...')
        cmd = 'pylama {}'.format(files)
        try:
            check_call(cmd, shell=True)
        except CalledProcessError as e:
            print('FAILED: please, fix the error(s) above.')
            sys.exit(e.returncode)


class Test(TestCommand):
    """Run doctest and linter besides tests/*."""

    def run(self):
        """First, tests/*."""
        super().run()
        print('Running examples in documentation')
        check_call('make doctest -C docs/', shell=True)
        Linter.lint()


class Cleaner(SimpleCommand):
    """Custom clean command to tidy up the project root."""

    description = 'clean build, dist, pyc and egg from package and docs'

    def run(self):
        """Clean build, dist, pyc and egg from package and docs."""
        call('rm -vrf ./build ./dist ./*.pyc ./*.egg-info', shell=True)
        call('make -C docs clean', shell=True)


# parse_requirements() returns generator of pip.req.InstallRequirement objects
requirements = parse_requirements('requirements.txt', session=False)

setup(name='kyco',
      version=__version__,
      description='Controller for OpenFlow Protocol from the Kytos project',
      url='http://github.com/kytos/kyco',
      author='Kytos Team',
      author_email='of-ng-dev@ncc.unesp.br',
      license='MIT',
      test_suite='tests',
      scripts=['bin/kyco'],
      data_files=[(os.path.join(BASE_ENV, 'etc/kyco'),
                   ['etc/kyco.conf', 'etc/logging.ini'])],
      packages=find_packages(exclude=['tests']),
      install_requires=[str(ir.req) for ir in requirements],
      cmdclass={
          'lint': Linter,
          'clean': Cleaner,
          'test': Test
      },
      zip_safe=False)
