#!/usr/bin/env python
# -*- coding: utf-8 -*-

from setuptools import setup, find_packages
import gif_for_cli

setup(
    name='gif-for-cli',
    version=gif_for_cli.__version__,
    description="Render an animated GIF to your command line terminal.",
    author='Seán Hayes',
    author_email='gasphynx@gmail.com',
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "Intended Audience :: System Administrators",
        "Programming Language :: Python",
        "Topic :: Software Development :: Libraries",
        "Topic :: Software Development :: Libraries :: Python Modules"
    ],
    keywords='gif cli',
    packages=find_packages(),
    install_requires=[
        'ffmpeg-python==0.1.10', # Apache License 2.0
        'Pillow==5.1.0', # PIL Software License
        'requests==2.18.4', # Apache License 2.0
        'x256==0.0.3', # MIT License
    ],
    include_package_data=True,
)
