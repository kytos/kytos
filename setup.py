import os
import sys
from setuptools import setup, find_packages, Command


class Doctest(Command):
    if sys.argv[-1] == 'test':
        print("Running docs make and make doctest")
        os.system("make doctest -C docs/")

setup(name='Kyco - Kytos Controller',
      version='0.1',
      description='Kytos Controller for OpenFlow Protocol',
      url='http://github.com/kytos/kyco',
      author='Kytos Team',
      author_email='of-ng-dev@ncc.unesp.br',
      license='MIT',
      test_suite='tests',
      scripts=['bin/kyco'],
      packages=find_packages(exclude=[]),
      cmdclass={
        'doctests': Doctest
      },
      zip_safe=False)
