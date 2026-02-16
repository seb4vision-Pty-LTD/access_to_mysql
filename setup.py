#!/usr/bin/env python
"""
Setup configuration for Access to MySQL Converter
"""

from setuptools import setup, find_packages
import os

# Read README
with open('README_DISTRIBUTION.md', 'r', encoding='utf-8') as f:
    long_description = f.read()

# Read requirements
with open('backend/requirements.txt', 'r', encoding='utf-8') as f:
    requirements = [line.strip() for line in f if line.strip() and not line.startswith('#')]

setup(
    name='access-to-mysql-converter',
    version='1.0.0',
    description='Professional-grade application for migrating Microsoft Access databases to MySQL',
    long_description=long_description,
    long_description_content_type='text/markdown',
    author='Access to MySQL Converter Contributors',
    url='https://github.com/sipho-mancam/access-to-mysql-converter',
    license='MIT',
    packages=find_packages(),
    include_package_data=True,
    python_requires='>=3.13',
    install_requires=requirements,
    entry_points={
        'console_scripts': [
            'access-to-mysql=backend.app:main',
        ],
    },
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Environment :: Web Environment',
        'Intended Audience :: End Users/Desktop',
        'Intended Audience :: System Administrators',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
        'Programming Language :: Python :: 3.11',
        'Topic :: Database',
        'Topic :: System :: Monitoring',
    ],
    keywords='access database mysql migration converter',
    project_urls={
        'Documentation': 'https://github.com/sipho-mancam/access-to-mysql-converter#readme',
        'Source': 'https://github.com/yourusername/access-to-mysql-converter',
        'Tracker': 'https://github.com/yourusername/access-to-mysql-converter/issues',
    },
)
