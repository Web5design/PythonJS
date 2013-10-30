PythonJS
########

:version: 0.9
:license: New BSD

PythonJS translates Python 3 to Javascript. You can install it with ``pip``::

  pip install pythonjs

You will also need a pythonjs.js grab it with the following command::

  wget https://raw.github.com/PythonJS/PythonJS/master/pythonjs.js

You start playing with a minimal page like the following::

  <script src="pythonjs.js"></script>
  <script src="app.js"></script>

``app.js`` must be generated with the ``pythonjs`` command::

  pythonjs < app.py > app.js

A minimal ``app.py`` is::

  print 'Héllo world!'

Contributing
============

TODO

