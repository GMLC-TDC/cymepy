#!/usr/bin/env python
import io
import os
import re

try:
    from setuptools import setup , find_packages
except ImportError:
    from distutils.core import setup

with open('requirements.txt') as f:
    all_lines = f.read().splitlines()
    print(all_lines)
requirements = [x for x in all_lines if "git+" not in x]
dependencies = [x for x in all_lines if "git+" in x]


print("Precise installation requirements:")
for i, req in enumerate(requirements):
    print(f"{i}. {req}")

print("Precise installation dependencies:")
for i, req in enumerate(requirements):
    print(f"{i}. {req}")

# Read the version from the __init__.py file without importing it
def read(*names, **kwargs):
    with io.open(
        os.path.join(os.path.dirname(__file__), *names),
        encoding=kwargs.get("encoding", "utf8")
    ) as fp:
        return fp.read()

def find_version(*file_paths):
    version_file = read(*file_paths)
    version_match = re.search(r"^__version__ = ['\"]([^'\"]*)['\"]",
                              version_file, re.M)
    if version_match:
        return version_match.group(1)
    raise RuntimeError("Unable to find version string.")

setup(
    name='CYMEPY',
    version=find_version("src", "__init__.py"),
    description='Helice interface for CYME',
    author='Aadil Latif',
    author_email='Aadil.Latif@nrel.gov',
    #url='',
    packages=find_packages(),
    install_requires=all_lines,
    dependency_links=dependencies,
    package_data={'cymepy': ['*.toml']},
    entry_points={
        "console_scripts": [
            "cymepy=src.cli.cymepy:cli",
        ],
    },
    license='BSD 3 clause',
    python_requires='>=3.6',
    classifiers=[
        'Development Status :: 4 - Beta',
        'Environment :: Console',
        'Environment :: Web Environment',
        'Intended Audience :: Developers',
        'Intended Audience :: Science/Research',
        'Operating System :: OS Independent',
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: BSD License",
    ],
)
