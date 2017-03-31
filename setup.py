import codecs
import os
import re

from setuptools import setup, find_packages


HERE = os.path.abspath(os.path.dirname(__file__))


def read(*parts):  # Stolen from txacme
    with codecs.open(os.path.join(HERE, *parts), 'rb', 'utf-8') as f:
        return f.read()


def get_version(package):
    """
    Return package version as listed in `__version__` in `init.py`.
    """
    init_py = open(os.path.join(package, '__init__.py')).read()
    return re.search("__version__ = ['\"]([^'\"]+)['\"]", init_py).group(1)


version = get_version('rputilities')


setup(
    name="rp-utilities",
    version=version,
    url='http://github.com/praekeltfoundation/rp-utilities',
    license='BSD',
    description='RapidPro Utilities',
    long_description=read('README.rst'),
    author='Praekelt.org',
    author_email='dev@praekelt.org',
    packages=find_packages(),
    include_package_data=True,
    install_requires=[
        'attrs>=16.3.0',
        'backports.csv>=1.0.4',
        'click>=6.7',
        'rapidpro-python>=2.1.6',
    ],
    entry_points='''
        [console_scripts]
        rp-utils=rputilities.cli:cli
    ''',
    classifiers=[
        'Development Status :: 4 - Beta',
        'Framework :: Django',
        'License :: OSI Approved :: BSD License',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3.6',
        'Topic :: Software Development :: Libraries :: Python Modules',
    ],
)
