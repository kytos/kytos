"""Setup script.

Run "python3 setup --help-commands" to list all available commands and their
descriptions.
"""
import os
import re
import shutil
import sys
from abc import abstractmethod
# Disabling checks due to https://github.com/PyCQA/pylint/issues/73
from distutils.command.clean import clean  # pylint: disable=E0401,E0611
from pathlib import Path
from subprocess import call

try:
    import pip
    from setuptools import Command, find_packages, setup
    from setuptools.command.develop import develop
    from setuptools.command.egg_info import egg_info
    from setuptools.command.install import install
except ModuleNotFoundError:
    print('Please install python3-pip and run setup.py again.')
    exit(-1)

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


class SASSBuild(SimpleCommand):
    """Build CSS from SASS."""

    description = 'Force CSS (re)build.'

    _cssdir = Path(__file__).parent / 'kytos/web-ui/static/css'
    style_css = _cssdir / 'style.css'

    def run(self):
        """Only build."""
        self.build()

    @classmethod
    def build(cls):
        """Build the web-UI CSS from SASS."""
        # Can't make tox in scrutinizer use libsass unless written in
        # requirements.txt, but our users don't need it.
        try:
            import sass
        except ModuleNotFoundError:
            pip.main(['install', 'libsass'])
            import sass

        sassdir = Path(__file__).parent / 'web-ui-src/sass'
        main_scss = sassdir / 'main.scss'
        style_map = cls._cssdir / 'style.css.map'
        compiled = sass.compile(filename=str(main_scss),
                                source_map_filename=str(style_map))
        for content, filename in zip(compiled, (cls.style_css, style_map)):
            with open(filename, 'w', encoding='utf-8') as output:
                output.write(content)


class EggInfo(egg_info):
    """Prepare files to be packed."""

    def run(self):
        """Build css."""
        self._install_deps_wheels()
        self._check_sass()
        super().run()

    @staticmethod
    def _install_deps_wheels():
        """Python wheels are much faster (no compiling)."""
        reqs = pip.req.parse_requirements('requirements.txt', session=False)
        print('Installing dependencies...')
        pip.main(['install', *[str(r.req) for r in reqs]])

    @staticmethod
    def _check_sass():
        """Do not build CSS if it exists (e.g. installing from PyPI source)."""
        if SASSBuild.style_css.exists():
            print('CSS already built. Not overriding it.')
        else:
            SASSBuild.build()


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
        cmd = 'coverage3 run setup.py test && coverage3 report'
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

        if kwargs.get('prefix').endswith('/'):
            kwargs['prefix'] = kwargs['prefix'][:-1]

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
        if 'bdist_wheel' in sys.argv:
            # do not use eggs, but wheels
            super().run()
        else:
            # force install of deps' eggs during setup.py install
            self.do_egg_install()
        self.generate_file_from_template(TEMPLATE_FILES, BASE_ENV,
                                         prefix=BASE_ENV)
        # data_files is not enough when installing from PyPI
        for file in ETC_FILES:
            shutil.copy2(file, Path(BASE_ENV) / file)

        self.create_pid_folder()


class DevelopMode(develop, CommonInstall):
    """Recommended setup for developers.

    Instead of copying the files to the expected directories, a symlink is
    created on the system aiming the current source code.
    """

    def run(self):
        """Install the package in a developer mode."""
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
          'lint': Linter,
          'egg_info': EggInfo,
          'build_sass': SASSBuild
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
