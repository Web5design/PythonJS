HACKING
#######

A Python program is compiled in two steps:

#. first it is translated to a subset of Python called ``PYS``
#. ``PYS`` code is translated to Javascript code


``PYS``
=======

``PYS`` will be the javascript subset of Python otherwise said, the subset of Python that we can translate pristine to Javascript. It will support the following:

- Functions with positional arguments
- Scope, automatic use ``var`` on new assignements, except if the variable is global
- ``try``/``except``/``raise``
- ``list`` literals converted to javascript arrays
- ``dict`` literals converted to javascript objects
- ``yield`` keyword
- Subscript
- Attribute access
- ``print`` will still be translated to ``console.log``
- ``while``
- ``for`` with support for javascript arrays and objects
- binary operators, expressions and comparisons
- ``in`` operator

What will not be supported by ``PYS``:

- ``import`` and ``import ... from ...``, PythonJS programs will support modules and packages but ``PYS`` will only handle one file at a time
- ``lambda``, functions will be converted to ``PYS`` before

``runtime/pythonpys.py``
========================

``pythonpys.py`` contains some low level ``pys`` code that is needed by pythonjs programs to run it implements among other things the following:

- Python type system (metaclass, class, type and root object called ``__pythonjs_object``)
- Arguments conversion between the internal convention where functions takes only ``args`` and ``kwargs`` arguments to Python arguments throught ``get_arguments`` function

And some other utility function among which some Python builtins need by the runtime library like ``isinstance`` and ``issubclass``.

``runtime/builtins.py``
=======================

Defines builtins datastructures needed at runtime but not part of the very core of what ``pythonpys`` is. For instance you don't need ``list`` and ``dict`` at runtime if you don't use variable arguments or variable keyword arguments.

Unittests
=========

We you want to run the unittests suite, you will need ``envoy`` which at the time of writring is not installable from pypi you need to execute the following command::

  pip install git+https://github.com/kennethreitz/envoy.git

Then you can use one of the following options with ``./runtests.py``:

- ``--pys`` executes only low level tests
- ``--runtime`` executes tests of the runtime library
- ``--pythonjs`` executes tests of the compiler

So for instance ``./runtests.py --pys`` will run all low level tests.

