#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Python packaging."""
import os
import sys

from setuptools import setup


#: Absolute path to directory containing setup.py file.
here = os.path.abspath(os.path.dirname(__file__))
#: Boolean, ``True`` if environment is running Python version 2.
IS_PYTHON2 = sys.version_info[0] == 2


NAME = 'django-aggtrigg'
DESCRIPTION = 'Django complementary index definition and management.'
README = open(os.path.join(here, 'README.rst')).read()
VERSION = open(os.path.join(here, 'VERSION')).read().strip()
AUTHOR = u'Rodolphe Quiédeville'
EMAIL = 'rodolphe@quiedeville.org'
LICENSE = 'BSD'
URL = 'https://django-aggtrigg.readthedocs.org/'
CLASSIFIERS = [
    'Programming Language :: Python :: 2.7',
    'Development Status :: 3 - Alpha',
    'Framework :: Django',
    'License :: OSI Approved :: BSD License',
]
KEYWORDS = [
    'aggregat',
    'trigger',
    'count',
    'min',
    'max'
    'database',
    'index',
    'postgresql',
    'django',
]
PACKAGES = ['django_aggtrigg']

REQUIREMENTS = [
    'Django',
    'setuptools',
    'psycopg2',
    'jinja2',
    'six',
    'django-qmixin'
]
ENTRY_POINTS = {}
CMDCLASS = {}
SETUP_REQUIREMENTS = [
    'setuptools'
]


# Tox integration.
from setuptools.command.test import test as TestCommand


class Tox(TestCommand):
    """Test command that runs tox."""
    def finalize_options(self):
        TestCommand.finalize_options(self)
        self.test_args = []
        self.test_suite = True

    def run_tests(self):
        import tox  # import here, cause outside the eggs aren't loaded.
        errno = tox.cmdline(self.test_args)
        sys.exit(errno)


CMDCLASS['test'] = Tox


if __name__ == '__main__':  # Do not run setup() when we import this module.
    setup(
        name=NAME,
        version=VERSION,
        description=DESCRIPTION,
        long_description=README,
        classifiers=CLASSIFIERS,
        keywords=' '.join(KEYWORDS),
        author=AUTHOR,
        author_email=EMAIL,
        url=URL,
        license=LICENSE,
        packages=PACKAGES,
        include_package_data=True,
        zip_safe=False,
        install_requires=REQUIREMENTS,
        entry_points=ENTRY_POINTS,
        cmdclass=CMDCLASS,
        setup_requires=SETUP_REQUIREMENTS
    )
