from string import ascii_letters

from setuptools import setup, find_packages

# Read the requirements.txt file, but exclude blank lines, comments, options, etc
with open('requirements.txt') as f:
    requirements = list(filter(lambda x: x.startswith(tuple(char for char in ascii_letters)), f.read().splitlines()))

setup(
    name='VertFlow',
    version='0.0.1',
    description='Apache Airflow operator for running Cloud Run Jobs in the greenest region.',
    author='OVO Energy',
    author_email='trading.dl@ovoenergy.com',
    packages=find_packages(),
    python_requires='>=3.7',
    install_requires=requirements
)
