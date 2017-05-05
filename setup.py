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
    def build_sass():
        """Method to build the web-ui sass into a css file."""
        import sass
        flask_dir = Path(__file__).parent / 'kytos/web-ui/source'
        infile = flask_dir / 'sass/main.scss'
        cssdir = flask_dir / 'static/css'
        outfile = cssdir / 'style.css'
        outmap = cssdir / 'style.css.map'
        compiled = sass.compile(filename=str(infile),
                                source_map_filename=str(outmap))

        with open(outfile, 'w') as output:
            output.write(compiled[0])

        with open(outmap, 'w') as output:
            output.write(compiled[1])

    @classmethod
    def generate_file_from_template(cls, templates,
                                    destination=Path(__file__).parent,
                                    **kwargs):
        """Create a config file based on a template file.

        If no destination is passed, the new conf file will be created on the
        directory of the template file.

        Args:
            template (string):    Path of the template file
            destination (string): Directory in which the config file will
                                  be placed.
        """
        from jinja2 import Template

        cls.create_paths()
        for path in templates:
            with open(path, 'r', encoding='utf-8') as src_file:
                content = Template(src_file.read()).render(**kwargs)
                dst_path = Path(destination) / path.replace('.template', '')
                with open(dst_path, 'w') as dst_file:
                    dst_file.write(content)

    @staticmethod
    def create_pid_folder():
        """Create the folder in /var/run to hold the pidfile."""
        pid_folder = os.path.join(BASE_ENV, 'var/run/kytos')
        os.makedirs(pid_folder, exist_ok=True)
        if BASE_ENV == '/':  # system install
            os.chmod(pid_folder, 0o1777)  # permissions like /tmp

    @staticmethod
    def create_paths():
        """Method used to create the paths used by Kytos in develop mode."""
        directories = [os.path.join(BASE_ENV, 'etc/kytos')]
        for directory in directories:
            if not os.path.exists(directory):
                os.makedirs(directory)


class InstallMode(install, CommonInstall):
    """Class used to overwrite the default installation using setuptools.

    Besides doing the default install, the config files used by
    Kytos SDN Platform will also be created, based on templates.
    """

    def run(self):
        """Install the package in install mode.

        super().run() does not install dependencies when running
        ``python setup.py install`` (pypa/setuptools#456).
        """
        self.build_sass()

        if 'bdist_wheel' in sys.argv:
            # do not use eggs, but wheels
            super().run()
        else:
            # force install of deps' eggs during setup.py install
            self.do_egg_install()
        self.generate_file_from_template(TEMPLATE_FILES, BASE_ENV,
                                         prefix=BASE_ENV)
        self.create_pid_folder()


class DevelopMode(develop, CommonInstall):
    """Recommended setup for developers.

    Instead of copying the files to the expected directories, a symlink is
    created on the system aiming the current source code.
    """

    def run(self):
        """Install the package in a developer mode."""
        self.build_sass()
        super().run()

        self.generate_file_from_template(TEMPLATE_FILES, prefix=BASE_ENV)

        for file_name in ETC_FILES:
            self.generate_file_link(file_name)

        for file_name in TEMPLATE_FILES:
            self.generate_file_link(file_name.replace('.template', ''))
        self.create_pid_folder()

    @staticmethod
    def generate_file_link(file_name):
        """Method used to create a symbolic link from a file name."""
        current_directory = os.path.dirname(__file__)
        src = os.path.join(os.path.abspath(current_directory), file_name)
        dst = os.path.join(BASE_ENV, file_name)

        if not os.path.exists(dst):
            os.symlink(src, dst)


try:
    # Install dependencies' wheels (faster, don't compile libsass, etc)
    import pip
    pip_reqs = pip.req.parse_requirements('requirements.txt', session=False)
    pip.main(['install', *[str(r.req) for r in pip_reqs]])
except ImportError:
    # No pip, slow install compiling stuff
    print('Without Python pip, the installation will be very slow due to'
          'some third-party packages.\n'
          'We recommend to answer "n" (no), install pip and run this install '
          'again.\n')
    answer = input('Do you want to proceed (y/[n])? ').lower()
    if answer not in ['y', 'yes']:
        sys.exit()

setup_requires = ['jinja2', 'libsass']
install_requires = [i.strip() for i in open("requirements.txt").readlines()]

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
      setup_requires=setup_requires,
      install_requires=install_requires,
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
