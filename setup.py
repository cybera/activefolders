from setuptools import setup, find_packages
import os


def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname), encoding='utf-8').read()

setup(
    name="activefolders",
    version="1.0.0",
    packages=find_packages(exclude=['test']),
    author="Cybera Inc.",
    author_email="devops@cybera.ca",
    license="Apache 2.0",
    url="https://github.com/cybera/activefolders",
    description="A gridftp wrapper intended to provide Dropbox-like service to scientists",
    long_description=read('README.md'),
    install_requires=["bottle", "paramiko", "peewee", "requests", "pycrypto"],
    entry_points={
        'console_scripts': ["dtnd = activefolders.main:start"]
    }
    )
