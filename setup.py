#!/usr/bin/env python3
from distutils.core import setup


setup(
    name='PythonJS',
    version='0.9',
    description='Python to Javascript compiler for the browser',
    author='Amirouche Boubekki',
    author_email='amirouche.boubekki@gmail.com',
    url='http://www.pythonjs.net',
    zip_safe=False,
    packages=['pythonjs'],
    entry_points="""
    [console_scripts]
    pys=pythonjs.pys:main
    pythonjs=pythonjs.pythonjs:main
    python_to_pys=pythonjs.python_to_pys:command
    """,
)
