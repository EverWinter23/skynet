'''
monday 9th june 2018
'''
import setuptools

with open("README.md", "r") as desc:
    long_description = desc.read()

setuptools.setup(
    name="s3kynet",
    version="1.6.0a1",          # marks alpha Release
    author="Rishabh Mehta",
    author_email="eternal.blizzard23@gmail.com",
    description="Sync folder to services like aws-s3, using resumable uploads.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/EverWinter23/skynet",
    packages=setuptools.find_packages(),
    python_requires='>=3',
    
    classifiers=(
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: AGPL-3.0-only License",
        "Operating System :: OS Independent",
    ),

    entry_points={
        'console_scripts': [
            'skynet=s3kynet.skymain:main',
        ],

        'gui_scripts': [
                'skytray=s3kynet.skytray:main',
        ]
    },
)
