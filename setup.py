from setuptools import setup, find_packages

with open("toolbox/version") as f:
    version = f.read()

setup(name='toolbox', version=version, packages=find_packages())