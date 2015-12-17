from setuptools import setup
import os
import re

DIRNAME = os.path.abspath(os.path.dirname(__file__))
rel = lambda *parts: os.path.abspath(os.path.join(DIRNAME, *parts))

README = open(rel('README.rst')).read()
MAIN = open(rel('rediscache.py')).read()
VERSION = re.search("__version__ = '([^']+)'", MAIN).group(1)


setup(
    name='rediscache',
    version=VERSION,
    description='redis based cache',
    long_description=README,
    url='https://github.com/xi/rediscache',
    author='Tobias Bengfort',
    author_email='tobias.bengfort@posteo.de',
    py_modules=['rediscache'],
    extras_require={
        'cache': ['redis'],
    },
    license='GPLv2+',
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'License :: OSI Approved :: GNU General Public License v2 or later '
            '(GPLv2+)',
    ])
