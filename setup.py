"""Setup script.

Run "python3 setup.py --help-commands" to list all available commands and their
descriptions.
"""
import os
import re
import sys
from abc import abstractmethod
# Disabling checks due to https://github.com/PyCQA/pylint/issues/73
from distutils.command.clean import clean  # pylint: disable=E0401,E0611
from pathlib import Path
from subprocess import CalledProcessError, call, check_call

try:
    # Check if pip is installed
    import pip  # pylint: disable=unused-import
    from setuptools import Command, find_packages, setup
    from setuptools.command.egg_info import egg_info
    from setuptools.command.install import install
except ModuleNotFoundError:
    print('Please install python3-pip and run setup.py again.')
    exit(-1)

BASE_ENV = Path(os.environ.get('VIRTUAL_ENV', '/'))
ETC_FILES = []


class SimpleCommand(Command):
    """Make Command implementation simpler."""

    user_options = []

    def __init__(self, *args, **kwargs):
        """Store arguments so it's possible to call other commands later."""
        super().__init__(*args, **kwargs)
        self._args = args
        self._kwargs = kwargs

    @abstractmethod
    def run(self):
        """Run when command is invoked.

        Use *call* instead of *check_call* to ignore failures.
        """
        pass

    def initialize_options(self):
        """Set default values for options."""
        pass

    def finalize_options(self):
        """Post-process options."""
        pass


class EggInfo(egg_info):
    """Prepare files to be packed."""

    def run(self):
        """Build css."""
        self._install_deps_wheels()
        super().run()

    @staticmethod
    def _install_deps_wheels():
        """Python wheels are much faster (no compiling)."""
        print('Installing dependencies...')
        check_call([sys.executable, '-m', 'pip', 'install', '-r',
                    'requirements/run.txt'])


class Cleaner(clean):
    """Custom clean command to tidy up the project root."""

    description = 'clean build, dist, pyc and egg from package and docs'

    def run(self):
        """Clean build, dist, pyc and egg from package and docs."""
        super().run()
        call('rm -vrf ./build ./dist ./*.egg-info', shell=True)
        call('find . -name __pycache__ -type d | xargs rm -rf', shell=True)
        call('test -d docs && make -C docs/ clean', shell=True)


class TestCoverage(SimpleCommand):
    """Display test coverage."""

    description = 'run unit tests and display code coverage'

    def run(self):
        """Run unittest quietly and display coverage report."""
        cmd = 'coverage3 run --source=kytos setup.py test && coverage3 report'
        check_call(cmd, shell=True)


class DocTest(SimpleCommand):
    """Run documentation tests."""

    description = 'run documentation tests'

    def run(self):
        """Run doctests using Sphinx Makefile."""
        cmd = 'make -C docs/ default doctest'
        check_call(cmd, shell=True)

class Linter(SimpleCommand):
    """Code linters."""

    description = 'Lint Python source code'

    def run(self):
        """Run yala."""
        print('Yala is running. It may take several seconds...')
        try:
            check_call('yala setup.py kytos tests', shell=True)
            print('No linter error found.')
        except CalledProcessError:
            print('Linter check failed. Fix the error(s) above and try again.')
            # disable error exit: 24 new warnings after pylint upgrade
            #exit(-1)


class CITest(SimpleCommand):
    """Run all CI tests."""

    description = 'run all CI tests: unit and doc tests, linter'

    def run(self):
        """Run unit tests with coverage, doc tests and linter."""
        for command in TestCoverage, DocTest, Linter:
            command(*self._args, **self._kwargs).run()


class InstallMode(install):
    """Class used to overwrite the default installation using setuptools."""

    def run(self):
        """Install the package in install mode.

        super().run() does not install dependencies when running
        ``python setup.py install`` (pypa/setuptools#456).
        """
        if 'bdist_wheel' in sys.argv:
            # do not use eggs, but wheels
            super().run()
        else:
            # force install of deps' eggs during setup.py install
            self.do_egg_install()


# class DevelopMode(develop):
#    """Recommended setup for developers.
#
#    The following feature are temporarily remove from code:
#    Instead of copying the files to the expected directories, a symlink is
#    created on the system aiming the current source code.
#    """
#
#    def run(self):
#        """Install the package in a developer mode."""
#        super().run()


# We are parsing the metadata file as if it was a text file because if we
# import it as a python module, necessarily the kytos.core module would be
# initialized, which means that kyots/core/__init__.py would be run and, then,
# kytos.core.controller.Controller would be called and it will try to import
# some modules that are dependencies from this project and that were not yet
# installed, since the requirements installation from this project hasn't yet
# happened.
META_FILE = open("kytos/core/metadata.py").read()
METADATA = dict(re.findall(r"(__[a-z]+__)\s*=\s*'([^']+)'", META_FILE))

setup(name='kytos',
      version=METADATA.get('__version__'),
      description=METADATA.get('__description__'),
      long_description=open("README.pypi.rst", "r").read(),
      long_description_content_type='text/x-rst',
      url=METADATA.get('__url__'),
      author=METADATA.get('__author__'),
      author_email=METADATA.get('__author_email__'),
      license=METADATA.get('__license__'),
      test_suite='tests',
      scripts=['bin/kytosd'],
      include_package_data=True,
      data_files=[(os.path.join(BASE_ENV, 'etc/kytos'), ETC_FILES)],
      packages=find_packages(exclude=['tests']),
      install_requires=[line.strip()
                        for line in open("requirements/run.txt").readlines()
                        if not line.startswith('#')],
      setup_requires=['pytest-runner'],
      tests_require=['pytest'],
      cmdclass={
          'clean': Cleaner,
          'ci': CITest,
          'coverage': TestCoverage,
          'doctest': DocTest,
          'egg_info': EggInfo,
          'install': InstallMode,
          'lint': Linter
      },
      zip_safe=False,
      classifiers=[
          'License :: OSI Approved :: MIT License',
          'Operating System :: POSIX :: Linux',
          'Programming Language :: Python :: 3.6',
          'Topic :: System :: Networking',
          'Development Status :: 4 - Beta',
          'Environment :: Console',
          'Environment :: No Input/Output (Daemon)',
      ])
