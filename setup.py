from setuptools import setup

setup(
    name='VertFlow',
    version='0.0.1',
    description='Apache Airflow operator for running Cloud Run Jobs in the greenest region.',
    long_description='Apache Airflow operator for running Cloud Run Jobs in the greenest region.',
    long_description_content_type="text/x-rst",
    author='OVO Energy',
    author_email='trading.dl@ovoenergy.com',
    packages=['VertFlow'],
    package_dir={'VertFlow': 'src'},
    include_package_data=True,
    package_data={'VertFlow': ['data/*']},
    python_requires='>=3.7',
    install_requires=["google-api-python-client==2.51.0"],
    license="Apache 2.0"
)

# TODO
# Once complete, check for FAILED, CANCELLED tasks.
# Finish license, packaging, publishing, etc.
# Propagate message if wait_until fails.
# Tidy README examples.
# Add closure to the CSV Reader
# Provide map of region:NEG
# Keep job if spec is identical.
