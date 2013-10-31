from pythonjs import JS
from pythonjs import var
from pythonjs import Array
from pythonjs import JSObject
from pythonjs import arguments


def jsrange(num):
    """Emulates Python's range function"""
    i = 0
    r = []
    while i < num:
        r.push(i)
        i = i + 1
    return r


def create_array():
    """Used to fix a bug/feature of Javascript where new Array(number)
    created a array with number of undefined elements which is not
    what we want"""
    array = []
    for i in jsrange(arguments.length):
        array.push(arguments[i])
    return array


def adapt_arguments(handler):
    """Useful to transform Javascript arguments to Python arguments"""
    def func():
        handler(Array.prototype.slice.call(arguments), JSObject())
    return func

def get_arguments(signature, args, kwargs):
    """Based on ``signature`` and ``args``, ``kwargs`` parameters retrieve
    the actual parameters.

    This will set default keyword arguments and retrieve positional arguments
    in kwargs if their called as such"""

    if args is None:
        args = []
    if kwargs is None:
        kwargs = JSObject()
    out = JSObject()

    # if the caller did not specify supplemental positional arguments e.g. *args in the signature
    # raise an error
    if args.length > signature.args.length:
        if signature.vararg:
            pass
        else:
            print('ERROR args:', args, 'kwargs:', kwargs, 'sig:', signature)
            raise TypeError("Supplemental positional arguments provided but signature doesn't accept them")

    j = 0
    while j < signature.args.length:
        name = signature.args[j]
        if name in kwargs:
            # value is provided as a keyword argument
            out[name] = kwargs[name]
        elif j < args.length:
            # value is positional and within the signature length
            out[name] = args[j]
        elif signature.kwargs and name in signature.kwargs:
            # value is not found before and is in signature.length
            out[name] = signature.kwargs[name]
        j += 1

    args = args.slice(j)
    if signature.vararg:
        out[signature.vararg] = args
    if signature.varkwarg:
        out[signature.varkwarg] = kwargs
    return out
get_arguments.pythonjs_function = True



### bootstrap type system #

### bootstrap object object

FunctionType = JSObject()
FunctionType["__name__"] = "function type"

# this is a base object also because functions are a special type
__pythonjs_object = JSObject()
__pythonjs_object["__name__"] = "object"

## define the only method of object which is __getattribute__


def get_attribute(object, attribute):
    """Retrieve an attribute, method, property, or wrapper function.

    method are actually functions which are converted to methods by
    prepending their arguments with the current object. Properties are
    not functions!

    DOM support:
        http://stackoverflow.com/questions/14202699/document-createelement-not-working
        https://developer.mozilla.org/en-US/docs/Web/JavaScript/Reference/Operators/instanceof

    Direct JavaScript Calls:
        if an external javascript function is found, and it was not a wrapper that was generated here,
        check the function for a 'cached_wrapper' attribute, if none is found then generate a new
        wrapper, cache it on the function, and return the wrapper.
    """
    # if attribute is __call__ and the object is a function return the wrapped function
    # we wrap Javascript functions to unwrap arguments as it is the case in PythonJS
    # calling convention
    if attribute == '__call__':
        if JS("{}.toString.call(object) === '[object Function]'"):
            if object.pythonjs_function:
                return object
            elif object.is_wrapper:
                return object
            elif object.cached_wrapper:
                return object.cached_wrapper
            else:
                def wrapper(args, kwargs): return object.apply(None, args)
                wrapper.is_wrapper = True
                object.cached_wrapper = wrapper
                return wrapper

    if JS("object instanceof HTMLDocument"):
        if typeof(attr) == 'function':
            def wrapper(args, kwargs): return attr.apply(object, args)
            wrapper.is_wrapper = True
            return wrapper
        else:
            return attr
    elif JS("object instanceof HTMLElement"):
        if typeof(attr) == 'function':
            def wrapper(args, kwargs): return attr.apply(object, args)
            wrapper.is_wrapper = True
            return wrapper
        else:
            return attr

    # it's not a javascript object so we need to go through __getattribute__
    # retrive it and call it

    # we need this ugly hack because we have added javascript Object.prototype.__contains__
    if attribute == '__contains__':
        attribute = '__CONTAINS__'

    # we need the same algorithm as __getattribute__ except we look for the right __getattribute__
    # so call the __getattribute__...
    inherited_getattribute = _object__getattribute__([object, "__getattribute__"], JSObject())
    
    # now that we have the right __getattribute__ call it with the __attribute__ we actually look for
    return inherited_getattribute([object, attribute], JSObject())
    
_object__getattribute__signature = JSObject()
_object__getattribute__signature["args"] = ['self', 'attribute']

def _object__getattribute__(args, kwargs):
    parameters = get_arguments(_object__getattribute__signature, args, kwargs)
    object = parameters["self"]
    attribute = parameters["attribute"]

    # Small optimization: if the object has the __getattribute__ attached to it return it
    # this is the case for object.__getattribute__ and type methods
    attr = object[attribute]

    if attr is not None:
        # if it's a function and it's not wrapped wrap it
        if typeof(attr) == 'function' and attr.pythonjs_function is None and attr.is_wrapper is None:
            # XXX: this happens only when there is a function that is added by javascript to a PythonJS
            # object ?
            def wrapper(args,kwargs): return attr.apply(object, args)
            wrapper.is_wrapper = True
            return wrapper
        else:
            return attr

    # Check object.__class__.__dict__ for data descriptors named attr
    __class__ = object.__class__
    if __class__:
        __dict__ = __class__.__dict__
        attr = __dict__[attribute]
        if attr:
            __get__ = get_attribute(attr, '__get__')
            if __get__:
                return __get__([object, __class__])
        bases = __class__.bases
        for base in bases:
            attr = get_attribute(base, attribute)
            if attr:
                __get__ = get_attribute(attr, '__get__')
                if __get__:
                    return __get__([object, __class__])
    # Check object.__dict__ for attr and its bases if it a class
    # in the case if the descriptor is found return it
    __dict__ = object["__dict__"]
    bases = object["__bases__"]
    if __dict__:
        attr = __dict__[attribute]
        if attr:
            if bases:
                __get__ = get_attribute(attr, '__get__')
                if __get__:
                    return __get__([None, __class__])
                else:
                    return attr
    if bases:
        for base in bases:
            attr = get_attribute(base, attribute)
            if attr:
                print("qsmdlkqsmdlkqsmldk")
                __get__ = get_attribute(attr, '__get__')
                if __get__:
                    return __get__([object, __class__])
                else:
                    return attr
    # if it's class, look in the class attributes
    if __class__:
        __dict__ = __class__.__dict__
        if attribute in __dict__:
            attr = __dict__[attribute]
            if JS("{}.toString.call(attr) === '[object Function]'"):
                def method():
                    args =  Array.prototype.slice.call(arguments)
                    if (JS('args[0] instanceof Array') and JS("{}.toString.call(args[1]) === '[object Object]'") and args.length == 2):
                        pass
                    else:
                        # in the case where the method was submitted to javascript code
                        # put the arguments in order to be processed by PythonJS
                        args = [args, JSObject()]
                    args[0].splice(0, 0, object)
                    return attr.apply(None, args)
                method.is_wrapper = True
                return method
            else:
                return attr

        bases = __class__.bases

        for base in bases:
            # XXX: this raises an AtttributeError now...
            attr = _get_upstream_attribute(base, attribute)
            if attr:
                if JS("{}.toString.call(attr) === '[object Function]'"):
                    def method():
                        args =  Array.prototype.slice.call(arguments)
                        if (JS('args[0] instanceof Array') and JS("{}.toString.call(args[1]) === '[object Object]'") and args.length == 2):
                            pass
                        else:
                            # in the case where the method was submitted to javascript code
                            # put the arguments in order to be processed by PythonJS
                            args = [args, JSObject()]

                        args[0].splice(0, 0, object)
                        return attr.apply(None, args)
                    method.is_wrapper = True
                    return method
                else:
                    return attr

        for base in bases:  ## upstream property getters come before __getattr__
            getter = _get_upstream_property(base, attribute)
            if getter:
                return getter( [object] )

        if '__getattr__' in __dict__:
            return __dict__['__getattr__']( [object, attribute])

        for base in bases:
            f = _get_upstream_attribute(base, '__getattr__')
            if f:
                return f([object, attribute])
    raise AttributeError
_object__getattribute__.pythonjs_function = True
__pythonjs_object.__getattribute__ = _object__getattribute__


def _get_upstream_attribute(base, attr):
    if attr in base.__dict__:
        return base.__dict__[attr]
    for parent in base.bases:
        return _get_upstream_attribute(parent, attr)

def _get_upstream_property(base, attr):
    if attr in base.__properties__:
        return base.__properties__[ attr ]
    for parent in base.bases:
        return _get_upstream_property(parent, attr)


### bootstrap type object

type = JSObject()
type["bases"] = [__pythonjs_object]
type["__name__"] = "type"

_type__call__signature = JSObject()
_type__call__signature["args"] = ["self", "object_or_name", "bases", "attrs"]
_type__call__signature["kwargs"] = {"bases": None, "attrs": None}

def _type__call__(args, kwargs):
    parameters = get_arguments(_type__call__signature, args, kwargs)
    self = parameters["self"]
    object_or_name = parameters["object_or_name"]
    bases = parameters["bases"]
    attrs = parameters["attrs"]
    
    if isinstance([object_or_name, str]):
        name = object_or_name
        __new__ = getattribute(self, "__new__")
        klass = __new__.call(__new__, [name, bases, attrs])
        if klass:
            __init__ = getattribute(self, "__init__")
            __init__.call(__init__, [klass, name, bases, attrs])
            return klass
        else:
            return None
    else:
        object = object_or_name
        # we want the type of the object
        if object == __pythonjs_object:
            return type
        elif object["__class__"]:
            return object["__class__"]
        else:
            try:
                # it's class
                return get_attribute(object, "__metaclass__")
            except:  # XXX: this must be named
                # it's a pythonjs function
                if object.pythonjs_function:
                    return __pythonjs_function
                # or not a pythonjs object
                return None
type["__call__"] = _type__call__

type["__metaclass__"] == type

def _type__new__(args, kwargs):
    parameters = get_arguments(this["signature"], args, kwargs)
    cls = parameters["cls"]  # metaclass
    name = parameters["name"]
    bases = parameters["bases"]
    attrs = parameters["attrs"]
    object = JSObject()
    object.__metaclass__ = cls
    object.__bases__ = [__pythonjs_object]
    object.__name__ = name
    object.__dict__ = attrs
    return object
_type__new__["signature"] = JSObject()
_type__new__["signature"]["args"] = ["cls", "name", "bases", "attrs"]
type["__new__"] = _type__new__



def _type__init__(args, kwargs):
    pass  # default init does nothing
type["__init__"] = _type__init__



# other internal functions

def set_attribute(object, attribute, value):
    """Set an attribute on an object by updating its __dict__ property"""
    __class__ = object.__class__
    if __class__:
        __dict__ = __class__.__dict__
        attr = __dict__[attribute]
        if attr != None:
            __set__ = get_attribute(attr, '__set__')
            if __set__:
                __set__([object, value])
                return
        bases = __class__.bases
        for i in jsrange(bases.length):
            base = bases[i]
            attr = get_attribute(base, attribute)
            if attr:
                __set__ = get_attribute(attr, '__set__')
                if __set__:
                    __set__([object, value])
                    return
    __dict__ = object.__dict__
    if __dict__:
        __dict__[attribute] = value
    else:
        object[attribute] = value
set_attribute.pythonjs_function = True

def getattr(args, kwargs):
    var(object, attribute)
    object = args[0]
    attribute = args[1]
    return get_attribute(object, attribute)
getattr.pythonjs_function = True

def setattr(args, kwargs):
    # XXX: use get_arguments
    object = args[0]
    attribute = args[1]
    value = args[2]
    return set_attribute(object, attribute, value)
setattr.pythonjs_function = True

def issubclass(args, kwargs):
    # XXX: use get_arguments
    C = args[0]
    B = args[1]
    if C is B:
        return True
    for index in jsrange(C.bases.length):
        base = C.bases[index]
        if issubclass([base, B], JSObject()):
            return True
    return False
issubclass.pythonjs_function = True

def isinstance(args, kwargs):
    # XXX: use get_arguments
    object = args[0]
    klass = args[1]
    object_class = object.__class__
    if object_class is None:
        return False
    return issubclass([object_class, klass])
isinstance.pythonjs_function = True