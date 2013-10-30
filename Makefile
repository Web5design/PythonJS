all: pythonjs

pythonjs:
	mkdir build
	./pythonjs/pys.py < runtime/pythonpys.py > build/pythonpys.js
	./pythonjs/pythonjs.py < runtime/builtins.py > build/builtins.js
	cat build/pythonpys.js build/builtins.js > pythonjs.js

clean:
	rm build dist pythonjs.js PythonJS.egg-info -rf 
