#!/usr/bin/env python
import sys
if sys.version_info < (3, 4):
    raise Exception('exa requires Python 3.4+')
from setuptools import setup, find_packages
from exa import __version__


try:
    setup(
        name='exa',
        version=__version__,
        description='Core exa functionality',
        author='Tom Duignan & Alex Marchenko',
        author_email='exa.data.analytics@gmail.com',
        url='https://exa-analytics.github.io/website',
        packages=find_packages(),
        package_data={
            'exa': [
                'templates/*',
                'static/js/*.js',
                'static/js/libs/*.js',
                'static/css/*.css',
                'static/img/*.*'
                'static/html/*.html'
            ]
        },
        entry_points={'console_scripts': ['exa = exa.__main__:main']},
        include_package_data=True
    )
finally:
    from exa.install import initialize
    initialize()
