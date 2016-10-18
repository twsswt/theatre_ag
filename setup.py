from setuptools import setup

setup(
    name='theatre_ag',
    version='0.1',
    packages=['theatre_ag'],
    package_dir={'': '.'},
    url='https://github.com/twsswt/theatre_ag',
    license='',
    author='Tim Storer',
    author_email='timothy.storer@glasgow.ac.uk',
    description='A framework for developing agent oriented simulations.',
    setup_requires=['sortedcontainers', 'nose', 'nose_parameterized'],
    test_suite='nose.collector',
    tests_require=['mock', 'nose']
)
