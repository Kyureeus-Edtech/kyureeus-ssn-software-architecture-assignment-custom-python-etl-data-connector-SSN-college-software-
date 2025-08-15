#!/usr/bin/env python3
"""
Setup script for MalShare ETL Connector
Author: [Shivakumaar] - [3122225001312]
"""

from setuptools import setup, find_packages
import os

# Read the contents of README file
this_directory = os.path.abspath(os.path.dirname(__file__))
with open(os.path.join(this_directory, 'README.md'), encoding='utf-8') as f:
    long_description = f.read()

# Read requirements from requirements.txt
def parse_requirements(filename):
    """Load requirements from a pip requirements file."""
    lineiter = (line.strip() for line in open(filename))
    return [line for line in lineiter if line and not line.startswith("#")]

requirements = parse_requirements('requirements.txt')

setup(
    name="malshare-etl-connector",
    version="1.0.0",
    author="[Your Name]",
    author_email="[Your Email]",
    description="ETL connector for MalShare malware intelligence API",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/[your-username]/malshare-etl-connector",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Intended Audience :: Information Technology",
        "Topic :: Security",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.8",
    install_requires=requirements,
    extras_require={
        "dev": [
            "pytest>=7.4.3",
            "pytest-cov>=4.1.0",
            "pytest-mock>=3.12.0",
            "black>=23.12.0",
            "flake8>=6.1.0",
            "mypy>=1.7.1",
        ],
        "docs": [
            "sphinx>=7.2.6",
            "sphinx-rtd-theme>=2.0.0",
        ],
    },
    entry_points={
        "console_scripts": [
            "malshare-etl=etl_connector:main",
        ],
    },
    keywords="etl malware cybersecurity api mongodb data-pipeline malshare",
    project_urls={
        "Documentation": "https://github.com/[your-username]/malshare-etl-connector#readme",
        "Source": "https://github.com/[your-username]/malshare-etl-connector",
        "Tracker": "https://github.com/[your-username]/malshare-etl-connector/issues",
    },
    include_package_data=True,
    zip_safe=False,
)