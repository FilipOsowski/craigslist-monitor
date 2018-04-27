from setuptools import setup, find_packages
from os import path
import sys

if sys.platform == "win32":
    raise Exception("This package is incompatable with Windows.")

my_loc = path.abspath(path.dirname(__file__))

with open(path.join(my_loc, "README.rst"), "r") as readme:
    long_description = readme.read()

setup(
        name="craigslist_monitor",
        version="0.1.3",
        license="MIT",
        packages=find_packages(),
        python_requires="~=3.0",
        description="A monitor for craigslist searches.",
        long_description=long_description,
        author="Filip Osowski",
        author_email="filiposowski5@gmail.com",
        url="https://github.com/FilipOsowski/craigslist-monitor",
        install_requires=["python-daemon>=2.0.0", "requests>=2.0.0", "lxml>=4.0.0"],
        classifiers=[
            "Development Status :: 3 - Alpha",
            "Programming Language :: Python :: 3",
        ],
        entry_points={
            "console_scripts": [
                "cmonitor = cmonitor.cli:cli"
            ]
        },
)
