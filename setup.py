from setuptools import setup, find_packages

with open('README.rst', 'r') as readme:
    long_description = readme.read()

setup(
    name='rumple',
    version='0.2.0',
    description='A simple dependency injection container',
    long_description=long_description,
    author='Kilte Leichnam',
    author_email='nwotnbm@gmail.com',
    url='https://github.com/Kilte/rumple',
    packages=find_packages(exclude=('tests',)),
    license='MIT',
    keywords=['container', 'dependency injection', 'inversion of control'],
    test_suite='tests'
)
