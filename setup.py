#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from setuptools import setup, find_packages
import os
import sys

def read_requirements():
    """Read the requirements file"""
    req_file = os.path.join(os.path.dirname(__file__), 'requirements.txt')
    if os.path.exists(req_file):
        with open(req_file, 'r') as f:
            return [line.strip() for line in f if line.strip() and not line.startswith('#')]
    return []

# Define package metadata
setup(
    name='CreepyAI',
    version='2.5.0',
    description='Geolocation OSINT tool with AI capabilities',
    author='CreepyAI Team',
    author_email='info@creepyai.org',
    url='https://github.com/creepyai/creepyai',
    packages=find_packages(),
    include_package_data=True,
    install_requires=read_requirements(),
    extras_require={
        'kml': ['simplekml>=1.3.5'],
        'excel': ['openpyxl>=3.0.7'],
        'dev': [
            'pytest>=6.2.5',
            'pytest-qt>=4.0.0',
            'black>=21.7b0',
        ],
    },
    entry_points={
        'console_scripts': [
            'creepyai=creepy.ui.creepyai_gui:main',
        ],
    },
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Environment :: X11 Applications :: Qt',
        'Intended Audience :: Science/Research',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Topic :: Scientific/Engineering :: Information Analysis',
    ],
    python_requires='>=3.6',
)
