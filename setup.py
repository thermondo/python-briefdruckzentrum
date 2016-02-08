#!/usr/bin/env python
from setuptools import setup, Command


class PyTest(Command):
    user_options = []

    def initialize_options(self):
        pass

    def finalize_options(self):
        pass

    def run(self):
        import sys
        import subprocess

        errno = subprocess.call([sys.executable, 'runtests.py'])
        raise SystemExit(errno)


setup(
    name='python-briefdruckzentrum',
    version='0.1.3',
    description='a lightweight python wrapper for briefdruckzentrum.de API',
    author='codingjoe',
    url='https://github.com/Thermondo/python-briefdruckzentrum',
    author_email='info@johanneshoppe.com',
    license='MIT',
    classifiers=[
        'Development Status :: 2 - Pre-Alpha',
        'Topic :: Printing',
        'Environment :: Web Environment',
        'Topic :: Office/Business :: Financial :: Accounting',
        'Intended Audience :: Developers',
        'Intended Audience :: Financial and Insurance Industry',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Topic :: Software Development',
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3.2',
        'Programming Language :: Python :: 3.3',
    ],
    packages=['briefdruckzentrum'],
    include_package_data=True,
    install_requires=['requests>=2.3', 'xmltodict>=0.9', 'money>=1.2'],
    tests_require=['pytest', 'pytest-pep8', 'pytest-flakes'],
    cmdclass={'test': PyTest},
)
