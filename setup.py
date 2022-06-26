from setuptools import setup, find_packages

VERSION = '0.0.1' 
DESCRIPTION = 'Convert python 3 program with typehint into python 2'

setup(
        name="autocompile", 
        version=VERSION,
        python_requires='>=3.7.0',
        author="Wayho Wang",
        author_email="<wweihao@outlook.com>",
        description=DESCRIPTION,
        packages=find_packages(),
        install_requires=['watchdog'],
        keywords=['python', 'watchdog'], 
        classifiers= [
            "Programming Language :: Python :: 3",
        ]
)
