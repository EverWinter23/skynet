'''
monday 9th june 2018
'''
import os
import errno
import setuptools
from pathlib import Path

SKYNET = 'skynet'
SKYNET_HOME = os.path.join(str(Path.home()),
                           SKYNET)
PCKG = 'skylarkskynet'
ICONS = 'icons'
ICON_DIR = os.path.join(PCKG, ICONS)

ICON_FILES = os.listdir(ICON_DIR)

try:
    # will automatically create skynet folder
    os.makedirs(ICON_DIR)
except OSError as error:
    if error.errno == errno.EEXIST and os.path.isdir(ICON_DIR):
        pass

with open("README.md", "r") as desc:
    long_description = desc.read()

setuptools.setup(
    name="skylark-skynet",
    version="1.0.0a3",          # TODO: marks --first alpha Release on pypi
    author="Rishabh Mehta",
    author_email="eternal.blizzard23@gmail.com",
    description="Sync folder to services like aws-s3, using resumable uploads.",
    long_description=long_description,
    # long_description_content_type="text/markdown",
    url="https://github.com/EverWinter23/skynet",
    packages=setuptools.find_packages(),
    python_requires='>=3',
    license="Apache License 3.0",
    # include_package_data=True,
    package_data={
        "skylarkskynet.icons": ICON_FILES,
    },

    install_requires=[
        'boto3',
        'PyQt5',
        'pysftp',
        'watchdog',
        'filechunkio',
        'persist-queue',
        'psycopg2-binary',
    ],

    dependency_links=[
        'https://pypi.org/project/PyQt5/',
        'https://pypi.org/project/boto3/',
        'https://pypi.org/project/pysftp/',
        'https://pypi.org/project/watchdog/',
        'https://pypi.org/project/filechunkio/',
        'https://pypi.org/project/persist-queue/',
        'https://pypi.org/project/psycopg2-binary/'
    ],

    classifiers=(
        "Programming Language :: Python :: 3.6",
        "License :: OSI Approved :: Apache Software License",
        "Operating System :: OS Independent",
    ),

    entry_points={
        'console_scripts': [
            'skynet=skylarkskynet.skymain:main',
        ],

        'gui_scripts': [
                'skytray=skylarkskynet.skytray:main',
        ]
    },
)
