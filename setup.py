"""Setup script.

Run "python3 setup.py --help-commands" to list all available commands and their
descriptions.
"""
import os
import re
import sys
from abc import abstractmethod
# Disabling checks due to https://github.com/PyCQA/pylint/issues/73
from pathlib import Path
from subprocess import CalledProcessError, call, check_call

try:
    # Check if pip is installed
    import pip  # pylint: disable=unused-import
    from setuptools import Command, find_packages, setup
    from setuptools.command.egg_info import egg_info
except ModuleNotFoundError:
    print('Please install python3-pip and run setup.py again.')
    sys.exit(-1)

BASE_ENV = Path(os.environ.get('VIRTUAL_ENV', '/'))
ETC_FILES = []

NEEDS_PYTEST = {'pytest', 'test', 'coverage'}.intersection(sys.argv)
PYTEST_RUNNER = ['pytest-runner'] if NEEDS_PYTEST else []


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

    def initialize_options(self):
        """Set default values for options."""

    def finalize_options(self):
        """Post-process options."""


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


# pylint: disable=attribute-defined-outside-init, abstract-method
class TestCommand(Command):
    """Test tags decorators."""

    user_options = [
        ('size=', None, 'Specify the size of tests to be executed.'),
        ('type=', None, 'Specify the type of tests to be executed.'),
    ]

    sizes = ('small', 'medium', 'large', 'all')
    types = ('unit', 'integration', 'e2e')

    def get_args(self):
        """Return args to be used in test command."""
        return '--size %s --type %s' % (self.size, self.type)

    def initialize_options(self):
        """Set default size and type args."""
        self.size = 'all'
        self.type = 'unit'

    def finalize_options(self):
        """Post-process."""
        try:
            assert self.size in self.sizes, ('ERROR: Invalid size:'
                                             f':{self.size}')
            assert self.type in self.types, ('ERROR: Invalid type:'
                                             f':{self.type}')
        except AssertionError as exc:
            print(exc)
            sys.exit(-1)


class Cleaner(SimpleCommand):
    """Custom clean command to tidy up the project root."""

    description = 'clean build, dist, pyc and egg from package and docs'

    def run(self):
        """Clean build, dist, pyc and egg from package and docs."""
        call('make clean', shell=True)


class Test(TestCommand):
    """Run all tests."""

    description = 'run tests and display results'

    def get_args(self):
        """Return args to be used in test command."""
        markers = self.size
        if markers == "small":
            markers = 'not medium and not large'
        size_args = "" if self.size == "all" else "-m '%s'" % markers
        return '--addopts="tests/%s %s"' % (self.type, size_args)

    def run(self):
        """Run tests."""
        cmd = 'python setup.py pytest %s' % self.get_args()
        try:
            check_call(cmd, shell=True)
        except CalledProcessError as exc:
            print(exc)
            print('Unit tests failed. Fix the error(s) above and try again.')
            sys.exit(-1)


class TestCoverage(Test):
    """Display test coverage."""

    description = 'run tests and display code coverage'

    def run(self):
        """Run tests quietly and display coverage report."""
        cmd = 'coverage3 run setup.py pytest %s' % self.get_args()
        cmd += '&& coverage3 report'
        try:
            check_call(cmd, shell=True)
        except CalledProcessError as exc:
            print(exc)
            print('Coverage tests failed. Fix the errors above and try again.')
            sys.exit(-1)


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
            sys.exit(-1)


class CITest(TestCommand):
    """Run all CI tests."""

    description = 'run all CI tests: unit and doc tests, linter'

    def run(self):
        """Run unit tests with coverage, doc tests and linter."""
        coverage_cmd = 'python setup.py coverage %s' % self.get_args()
        doctest_cmd = 'python setup.py doctest'
        lint_cmd = 'python setup.py lint'
        cmd = '%s && %s && %s' % (coverage_cmd, doctest_cmd, lint_cmd)
        check_call(cmd, shell=True)


# class InstallMode(install):
#     """Class used to overwrite the default installation using setuptools."""

#     def run(self):
#         """Install the package in install mode.

#         super().run() does not install dependencies when running
#         ``python setup.py install`` (pypa/setuptools#456).
#         """
#         if 'bdist_wheel' in sys.argv:
#             # do not use eggs, but wheels
#             super().run()
#         else:
#             # force install of deps' eggs during setup.py install
#             self.do_egg_install()


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
      setup_requires=PYTEST_RUNNER,
      tests_require=['pytest'],
      cmdclass={
          'clean': Cleaner,
          'ci': CITest,
          'coverage': TestCoverage,
          'doctest': DocTest,
          'egg_info': EggInfo,
          'lint': Linter,
          'test': Test
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
