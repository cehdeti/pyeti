from setuptools import setup

setup(
    name='pyeti',
    version='0.1',
    description='The awesomest Python package from ETI',
    url='https://github.com/cehdeti/pyeti',
    author='ETI',
    author_email='saun0063@umn.edu',
    license='MIT',
    packages=['pyeti'],
    install_requires=['python-dateutil', 'requests'],
    zip_safe=False,
)
