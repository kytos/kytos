"""Setup script.

Run "python3 setup --help-commands" to list all available commands and their
descriptions.
"""
import os
import re
import sys
from abc import abstractmethod
# Disabling checks due to https://github.com/PyCQA/pylint/issues/73
from distutils.command.clean import clean  # pylint: disable=E0401,E0611
from pathlib import Path
from subprocess import call

from setuptools import Command, find_packages, setup
from setuptools.command.develop import develop
from setuptools.command.install import install

if 'bdist_wheel' in sys.argv:
    raise RuntimeError("This setup.py does not support wheels")


BASE_ENV = os.environ.get('VIRTUAL_ENV', None) or '/'
ETC_FILES = ['etc/kytos/logging.ini']
TEMPLATE_FILES = ['etc/kytos/kytos.conf.template']


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
        cmd = 'coverage3 run -m unittest discover -qs tests' \
              ' && coverage3 report'
        call(cmd, shell=True)


class DocTest(SimpleCommand):
    """Run documentation tests."""

    description = 'run documentation tests'

    def run(self):
        """Run doctests using Sphinx Makefile."""
        cmd = 'make -C docs/ doctest'
        call(cmd, shell=True)


class Linter(SimpleCommand):
    """Code linters."""

    description = 'lint Python source code'

    def run(self):
        """Run pylama."""
        print('Pylama is running. It may take several seconds...')
        call('pylama setup.py tests kytos', shell=True)


class CommonInstall:
    """Class with common method used by children classes."""

    @staticmethod
    def add_jinja2_to_path():
        """Add Jinja2 into sys.path.

        As Jinja2 may be installed during this setup, it will not be available
        on runtime to be used here. So, we need to look for it and append it on
        the sys.path.
        """
        #: First we find the 'site_pkg' directory
        site_pkg = None
        for path in sys.path:
            if Path(path).stem == 'site-packages':
                site_pkg = Path(path)
                break

        #: Then we get the 'Jinja2' egg directory and append it into the
        #: current sys.path.
        jinja2path = next(site_pkg.glob('Jinja2*'))
        sys.path.append(str(jinja2path))

    @staticmethod
    def generate_file_from_template(templates,
                                    destination=os.path.dirname(__file__),
                                    **kwargs):
        """Create a config file based on a template file.

        If no destination is passed, the new conf file will be created on the
        directory of the template file.

        Args:
            template (string):    Path of the template file
            destination (string): Directory in which the config file will
                                  be placed.
        """
        CommonInstall.add_jinja2_to_path()
        from jinja2 import Template  # pylint: disable=import-error

        for path in templates:
            with open(path, 'r', encoding='utf-8') as src_file:
                content = Template(src_file.read()).render(**kwargs)
                dst_path = os.path.join(destination,
                                        path.replace('.template', ''))
                with open(dst_path, 'w') as dst_file:
                    dst_file.write(content)


class InstallMode(install, CommonInstall):
    """Class used to overwrite the default installation using setuptools.

    Besides doing the default install, the config files used by
    Kytos SDN Platform will also be created, based on templates.
    """

    def run(self):
        """Install the package in an install mode."""
        super().run()
        self.generate_file_from_template(TEMPLATE_FILES, BASE_ENV,
                                         prefix=BASE_ENV)


class DevelopMode(develop, CommonInstall):
    """Recommended setup for developers.

    Instead of copying the files to the expected directories, a symlink is
    created on the system aiming the current source code.
    """

    def run(self):
        """Install the package in a developer mode."""
        super().run()

        self.create_paths()
        self.generate_file_from_template(TEMPLATE_FILES, prefix=BASE_ENV)

        for file_name in ETC_FILES:
            self.generate_file_link(file_name)

        for file_name in TEMPLATE_FILES:
            self.generate_file_link(file_name.replace('.template', ''))

    @staticmethod
    def generate_file_link(file_name):
        """Method used to create a symbolic link from a file name."""
        current_directory = os.path.dirname(__file__)
        src = os.path.join(os.path.abspath(current_directory), file_name)
        dst = os.path.join(BASE_ENV, file_name)

        if not os.path.exists(dst):
            os.symlink(src, dst)

    @staticmethod
    def create_paths():
        """Method used to create the paths used by Kytos in develop mode."""
        directories = [os.path.join(BASE_ENV, 'etc/kytos')]
        for directory in directories:
            if not os.path.exists(directory):
                os.makedirs(directory)


requirements = [i.strip() for i in open("requirements.txt").readlines()]

# We are parsing the metadata file as if it was a text file because if we
# import it as a python module, necessarily the kytos.core module would be
# initialized, which means that kyots/core/__init__.py would be run and, then,
# kytos.core.controller.Controller would be called and it will try to import
# some modules that are dependencies from this project and that were not yet
# installed, since the requirements installation from this project hasn't yet
# happened.
meta_file = open("kytos/core/metadata.py").read()
metadata = dict(re.findall(r"(__[a-z]+__)\s*=\s*'([^']+)'", meta_file))

setup(name='kytos',
      version=metadata.get('__version__'),
      description=metadata.get('__description__'),
      url=metadata.get('__url__'),
      author=metadata.get('__author__'),
      author_email=metadata.get('__author_email__'),
      license=metadata.get('__license__'),
      test_suite='tests',
      install_requires=requirements,
      dependency_links=[
          'https://github.com/cemsbr/python-daemon/tarball/latest_release'
          '#egg=python-daemon-2.1.2'
      ],
      scripts=['bin/kytosd'],
      include_package_data=True,
      data_files=[(os.path.join(BASE_ENV, 'etc/kytos'), ETC_FILES)],
      packages=find_packages(exclude=['tests']),
      cmdclass={
          'clean': Cleaner,
          'coverage': TestCoverage,
          'develop': DevelopMode,
          'install': InstallMode,
          'doctest': DocTest,
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
