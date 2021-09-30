from setuptools import setup, find_packages
from os.path import join, dirname

setup(
    name='sa_core',
    version='1.2.1.22',
    packages=find_packages(),
    description="Steganalysis core",
    long_description=open(join(dirname(__file__), 'README.txt')).read(),
    author="Yaroslav Grachev",
    python_requires='>=3.3, !=2.*',
    install_requires=[
        'numpy',
        'scipy',
        'Pillow'
    ]
)
