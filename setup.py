from setuptools import setup, find_packages
from os import path
import sys

if sys.platform == "win32":
    raise Exception("This package is incompatable with Windows.")

my_loc = path.abspath(path.dirname(__file__))

with open(path.join(my_loc, 'README.md'), encoding='utf-8') as readme:
    long_description = readme.read()

setup(
        name="craigslist_monitor",
        version="0.1",
        packages=find_packages(),
        python_requires="~=3.0",
        description="A monitor for craigslist searches.",
        author="Filip Osowski",
        email="filiposowski5@gmail.com",
        long_description=long_description,
        classifiers=[
            "License :: MIT License",
            "Development Status :: 3 - Alpha",
            "Programming Language :: Python :: 3",
        ],
        entry_points={
            "console_scripts": [
                "cmonitor = cmonitor.cli:cli"
            ]
        },
        project_urls={
            "Source/Github": "https://github.com/FilipOsowski/craigslist-monitor"
        }
)
