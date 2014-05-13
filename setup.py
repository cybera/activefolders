from setuptools import setup, find_packages
import os


def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()

setup(
    name="activefolders",
    version="0.0.2-SNAPSHOT",
    packages=find_packages(exclude=['test']),
    author="Cybera Inc.",
    author_email="devops@cybera.ca",
    license="BSD",
    url="https://github.com/cybera/active-folders",
    description="A gridftp wrapper intended to provide Dropbox-like service to scientists",
    long_description=read('README.md'),
    install_requires=["bottle", "peewee", "requests", "gunicorn"],
    entry_points={
        'console_scripts': ["dtnd = activefolders.main:default_start"]
    }
    )
