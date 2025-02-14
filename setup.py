import os

from setuptools import find_packages
from setuptools import setup


def read(*rnames):
    return open(os.path.join(os.path.dirname(__file__), *rnames)).read()


long_description = (
    read('README.rst')
    + '\n' +
    read('src', 'martian', 'README.rst')
    + '\n' +
    read('CHANGES.rst')
)

setup(
    name='martian',
    version='2.1.dev0',
    url='https://github.com/zopefoundation/martian',
    author='Grok project',
    author_email='grok-dev@zope.org',
    description="Embedding of configuration information in Python code.",
    long_description=long_description,
    classifiers=[
        'Development Status :: 6 - Mature',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: Zope Public License',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
        'Programming Language :: Python :: 3.11',
        'Programming Language :: Python :: 3.12',
        'Programming Language :: Python :: 3.13',
        'Programming Language :: Python :: Implementation :: CPython',
        'Programming Language :: Python :: Implementation :: PyPy',
        'Topic :: Utilities',
    ],
    packages=find_packages('src'),
    package_dir={'': 'src'},
    include_package_data=True,
    zip_safe=False,
    license='ZPL',
    python_requires='>=3.9',
    install_requires=[
        'zope.interface',
        'setuptools',
    ],
    extras_require=dict(test=['zope.testing']),
)
