# class definition header
_PythonJSClass_attrs = JSObject()
_PythonJSClass_bases = [__pythonjs_object]
# _PythonJSClass_metaclass = type  # this “done” in runtime.py

# attributes definitions
_PythonJSClass_my_method_signature = JSObject()
_PythonJSClass_my_method_signature["args"] = ["self", "initial"]
def _PythonJSClass_my_method(args, kwargs):
    parameters = get_arguments(_PythonJSClass_my_method_signature, args, kwargs)
    self = parameters["self"]
    initial = parameters["initial"]
    return initial*2
_PythonJSClass_my_method.NAME = "my_method"
_PythonJSClass_my_method.pythonjs_function = True
_PythonJSClass_attrs["my_method"] = _PythonJSClass_my_method


_PythonJSClass_metaclass = get_metaclass(_PythonJSClass_attrs, _PythonJSClass_bases)

_PythonJSClass_metaclass__call__ = get_attribute(_PythonJSClass_metaclass, "__call__")

PythonJSClass = _PythonJSClass_metaclass__call__([_PythonJSClass_metaclass, "PythonJSClass", _PythonJSClass_bases, _PythonJSClass_attrs], JSObject())

create_class_instance = get_attribute(PythonJSClass, "__call__")
instance = create_class_instance([], JSObject())
instance.__name__ = "instance"
my_method = get_attribute(instance, "my_method")
my_method__call__ = get_attribute(my_method, "__call__")
print(my_method__call__([21], JSObject()))
