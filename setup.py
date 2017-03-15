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
from setuptools.command.develop import develop
from setuptools.command.test import test as TestCommand

from kytos import __version__

if 'bdist_wheel' in sys.argv:
    raise RuntimeError("This setup.py does not support wheels")

if 'VIRTUAL_ENV' in os.environ:
    BASE_ENV = os.environ['VIRTUAL_ENV']
else:
    BASE_ENV = '/'

ETC_FILES = ['etc/kytos.conf', 'etc/logging.ini']


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
    def lint(ignore=False):
        """Run pylama and radon."""
        files = 'setup.py tests kytos'
        print('Pylama is running. It may take several seconds...')
        ignore_options = '--ignore=W,R,D203,D213,I0011'
        options = ignore_options if ignore else ''
        cmd = 'pylama {} {}'.format(options, files)
        try:
            check_call(cmd, shell=True)
        except CalledProcessError as e:
            print('FAILED: please, fix the error(s) above.')
            if ignore is False:
                print('Note: the test target currently runs less checks with:')
                print('      pylama {} {}'.format(ignore_options, files))
            sys.exit(e.returncode)


class Test(TestCommand):
    """Run doctest and linter besides tests/*."""

    def run(self):
        """First, tests/*."""
        super().run()
        print('Running examples in documentation')
        check_call('make doctest -C docs/', shell=True)
        Linter.lint(ignore=True)


class Cleaner(SimpleCommand):
    """Custom clean command to tidy up the project root."""

    description = 'clean build, dist, pyc and egg from package and docs'

    def run(self):
        """Clean build, dist, pyc and egg from package and docs."""
        call('rm -vrf ./build ./dist ./*.pyc ./*.egg-info', shell=True)
        call('make -C docs clean', shell=True)


class DevelopMode(develop):
    """Recommended setup for kytos-core-napps developers.

    Instead of copying the files to the expected directories, a symlink is
    created on the system aiming the current source code.
    """

    def run(self):
        """Install the package in a developer mode."""
        super().run()
        for _file in ETC_FILES:
            self.create_path(_file)

    def create_path(self, file_name):
        """Method used to create the configurations files using develop."""
        etc_dir = os.path.join(BASE_ENV, 'etc')

        current_directory = os.path.dirname(__file__)
        src = os.path.join(os.path.abspath(current_directory), file_name)
        dst = os.path.join(BASE_ENV, file_name)

        if not os.path.exists(etc_dir):
            os.mkdir(etc_dir)

        if not os.path.exists(dst):
            os.symlink(src, dst)


# parse_requirements() returns generator of pip.req.InstallRequirement objects
requirements = parse_requirements('requirements.txt', session=False)

setup(name='kytos',
      version=__version__,
      description='Controller for OpenFlow Protocol from the Kytos project',
      url='http://github.com/kytos/kytos-core',
      author='Kytos Team',
      author_email='of-ng-dev@ncc.unesp.br',
      license='MIT',
      test_suite='tests',
      scripts=['bin/kytosd'],
      data_files=[(os.path.join(BASE_ENV, 'etc/kytos'),
                   ETC_FILES)],
      packages=find_packages(exclude=['tests']),
      install_requires=[str(ir.req) for ir in requirements],
      cmdclass={
          'develop': DevelopMode,
          'lint': Linter,
          'clean': Cleaner,
          'test': Test
      },
      zip_safe=False)
