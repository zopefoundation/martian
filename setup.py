import os
from setuptools import setup, find_packages


def read(*rnames):
    return open(os.path.join(os.path.dirname(__file__), *rnames)).read()


long_description = (
    read('README.rst')
    + '\n' +
    read('src', 'martian', 'README.rst')
    + '\n' +
    read('CHANGES.rst')
    + '\n' +
    'Download\n'
    '********\n'
)

setup(
    name='martian',
    version='1.2',
    url='https://github.com/zopefoundation/martian',
    author='Grok project',
    author_email='grok-dev@zope.org',
    description="""\
Martian is a library that allows the embedding of configuration
information in Python code. Martian can then grok the system and
do the appropriate configuration registrations. One example of a system
that uses Martian is the system where it originated: Grok
(http://grok.zope.org)
""",
    long_description=long_description,
    classifiers=[
        'Development Status :: 6 - Mature',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: Zope Public License',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: Implementation :: CPython',
        'Programming Language :: Python :: Implementation :: PyPy',
        'Topic :: Utilities',
    ],
    packages=find_packages('src'),
    package_dir={'': 'src'},
    include_package_data=True,
    zip_safe=False,
    license='ZPL',
    test_suite='martian.tests.test_all.test_suite',
    install_requires=[
        'zope.interface',
        'setuptools',
    ],
    extras_require=dict(test=['zope.testing']),
)
