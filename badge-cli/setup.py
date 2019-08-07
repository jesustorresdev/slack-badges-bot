from setuptools import setup
import sys

#if sys.version_info < (3,7):
#    sys.exit('3.7 != {0}'.format(sys.version_info))

setup(
    name='badge_cli',
    version='0.1',
    py_modules=['badge_cli'],
    install_requires=[
        'Click',
        'requests',
        'Pillow',
    ],
    entry_points='''
        [console_scripts]
        badgecli=badge_cli.badge_cli:cli
    ''',
)
