HACKING
=======

A Python program is translated in two steps:

#. first it is translated to a subset of Python called ``PYS``
#. ``PYS`` code is translated to Javascript code


``PYS``
-------

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

This is what is supported by the current low level langauge of PythonJS except scope which is handled in the higher level translator.

What will not be supported by ``PYS``:

- ``import`` and ``import ... from ...``, PythonJS.NEXT programs will support modules and packages but ``PYS`` will only handle one file at a time
- ``lambda``, functions will be converted to ``PYS`` before

