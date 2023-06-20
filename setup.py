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
    # pylint: disable=unused-import
    import pip  # noqa
    from setuptools import Command, find_packages, setup
    from setuptools.command.egg_info import egg_info
except ModuleNotFoundError:
    print('Please install python3-pip and run setup.py again.')
    sys.exit(-1)

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
        ("k=", None, "Specify a pytest -k expression."),
    ]

    def get_args(self):
        """Return args to be used in test command."""
        if self.k:
            return f"-k '{self.k}'"
        return ""

    def initialize_options(self):
        """Set default size and type args."""
        self.k = ""

    def finalize_options(self):
        """Post-process."""
        pass


class Cleaner(SimpleCommand):
    """Custom clean command to tidy up the project root."""

    description = 'clean build, dist, pyc and egg from package and docs'

    def run(self):
        """Clean build, dist, pyc and egg from package and docs."""
        call('make clean', shell=True)


class Test(TestCommand):
    """Run all tests."""

    description = "run tests and display results"

    def run(self):
        """Run tests."""
        cmd = f"python3 -m pytest tests/ {self.get_args()}"
        try:
            check_call(cmd, shell=True)
        except CalledProcessError as exc:
            print(exc)
            print('Unit tests failed. Fix the errors above and try again.')
            sys.exit(-1)


class TestCoverage(Test):
    """Display test coverage."""

    description = "run tests and display code coverage"

    def run(self):
        """Run tests quietly and display coverage report."""
        cmd = f"python3 -m pytest --cov=. tests/ {self.get_args()}"
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
with open("kytos/core/metadata.py", encoding="utf8") as file:
    meta_file = file.read()
METADATA = dict(re.findall(r"(__[a-z]+__)\s*=\s*'([^']+)'", meta_file))

with open("README.pypi.rst", "r", encoding="utf8") as file:
    long_description = file.read()

with open("requirements/run.txt", "r", encoding="utf8") as file:
    install_requires = [line.strip() for line in file
                        if not line.startswith("#")]

setup(name='kytos',
      version=METADATA.get('__version__'),
      description=METADATA.get('__description__'),
      long_description=long_description,
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
      install_requires=install_requires,
      extras_require={'dev': [
          'pip-tools >= 2.0',
          'pytest==7.2.1',
          'pytest-cov==4.0.0',
          'pytest-asyncio==0.20.3',
          'black==23.3.0',
          'isort==5.12.0',
          'pylint==2.15.0',
          'pycodestyle==2.10.0',
          'yala==3.2.0',
          'tox==3.28.0',
          'virtualenv==20.21.0',
          'typing-extensions==4.5.0'
      ]},
      cmdclass={
          'clean': Cleaner,
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
          'Programming Language :: Python :: 3.7',
          'Programming Language :: Python :: 3.8',
          'Programming Language :: Python :: 3.9',
          'Topic :: System :: Networking',
          'Development Status :: 4 - Beta',
          'Environment :: Console',
          'Environment :: No Input/Output (Daemon)',
      ])
