#!/usr/bin/env python3
import sys
from types import GeneratorType

from ast import Str
from ast import Name
from ast import Tuple
from ast import parse
from ast import Assign
from ast import Global
from ast import Attribute
from ast import FunctionDef
from ast import NodeVisitor


class JSGenerator(NodeVisitor):

    def visit_In(self, node):
        return ' in '

    def visit_Module(self, node):
        return '\n'.join(map(self.visit, node.body))
            
    def visit_Tuple(self, node):
        return '[{}]'.format(', '.join(map(self.visit, node.elts)))

    def visit_List(self, node):
        return '[{}]'.format(', '.join(map(self.visit, node.elts)))

    def visit_Try(self, node):
        out = 'try {\n'
        out += '\n'.join(map(self.visit, node.body))
        out += '\n}\n'
        out += 'catch(__exception__) {\n'
        out += '\n'.join(map(self.visit, node.handlers))
        out += '\n}\n'
        return out

    def visit_Raise(self, node):
        return 'throw {};'.format(self.visit(node.exc))

    def visit_Yield(self, node):
        return 'yield {};'.format(self.visit(node.value))

    def visit_ImportFrom(self, node):
        # ignore because we still need do write imports to avoid warnings from pep8
        return ''

    def visit_ExceptHandler(self, node):
        out = ''
        if node.type:
            out = 'if (__exception__ == {}) {\n'.format(self.visit(node.type), self.visit(node.type))
        if node.name:
            out += 'var {} = __exception__;\n'.format(self.visit(node.name))
        out += '\n'.join(map(self.visit, node.body)) + '\n'
        if node.type:
            out += '}\n'
        return out

    def visit_Global(self, node):
        # handled in visit_FunctionDef
        return ''

    def visit_FunctionDef(self, node):
        if not hasattr(self, '_function_stack'):  ## track nested functions ##
            self._function_stack = []

        self._function_stack.append(node.name)
        f = self.visit(node.args)
        buffer = 'var {} = function({}) {{\n'.format(node.name, f)

        # check for variable creation use var if not global
        def retrieve_vars(body):
            local_vars = set()
            global_vars = set()
            for n in body:
                if isinstance(n, Assign) and isinstance(n.targets[0], Name):  ## assignment to local
                    local_vars.add(n.targets[0].id)
                elif isinstance(n, Global):
                    global_vars.update( n.names )
                elif hasattr(n, 'body') and not isinstance(n, FunctionDef):
                    # do a recursive search inside new block except function def
                    l, g = retrieve_vars(n.body)
                    local_vars.update(l)
                    global_vars.update(g)
                    if hasattr(n, 'orelse'):
                        l, g = retrieve_vars(n.orelse)
                        local_vars.update(l)
                        global_vars.update(g)                        
                else:
                    print('fuuu', n)
            return local_vars, global_vars

        local_vars, global_vars = retrieve_vars(node.body)

        if local_vars - global_vars:
            a = ','.join(local_vars-global_vars)
            buffer += 'var {};\n'.format(a)

        # output function body
        body = '\n'.join(map(self.visit, node.body))
        buffer += body
        buffer += '\n}\n'

        if node.name == self._function_stack[0]:  ## to be safe do not export nested functions
            buffer += 'window["{}"] = {} \n'.format(node.name, node.name)  ## export to global namespace so Closure will not remove them

        assert node.name == self._function_stack.pop()
        return buffer

    def visit_Subscript(self, node):
        return '{}[{}]'.format(self.visit(node.value), self.visit(node.slice.value))

    def visit_arguments(self, node):
        # no support for annotation
        return ', '.join(map(lambda x: x.arg, node.args))

    def visit_Name(self, node):
        if node.id == 'None':
            return 'undefined'
        elif node.id == 'True':
            return 'true'
        elif node.id == 'False':
            return 'false'
        elif node.id == 'null':
            return 'null'
        return node.id

    def visit_Attribute(self, node):
        name = self.visit(node.value)
        attr = node.attr
        return '{}.{}'.format(name, attr)

    def visit_keyword(self, node):
        if isinstance(node.arg, basestring):
            return node.arg, self.visit(node.value)
        return self.visit(node.arg), self.visit(node.value)

    def visit_Call(self, node):
        name = self.visit(node.func)
        if name == 'instanceof':
            # this gets used by "with javascript:" blocks 
            # to test if an instance is a JavaScript type
            args = map(self.visit, node.args)
            if len(args) == 2:
                return '{} instanceof {}'.format(*tuple(args))
            else:
                raise SyntaxError( args )
        elif name == 'JSObject':
            if node.keywords:
                kwargs = map(self.visit, node.keywords)
                f = lambda x: '"{}": {}'.format(x[0], x[1])
                out = ', '.join(map(f, kwargs))
                return '{{}}'.format(out)
            else:
                return 'Object()'
        elif name == 'var':
            args = map(self.visit, node.args)
            out = ', '.join(args)
            return 'var {}'.format(out)
        elif name == 'JSArray':
            if node.args:
                args = map(self.visit, node.args)
                out = ', '.join(args)
            else:
                out = ''
            return '[{}]'.format(out)
        elif name == 'JS':
            return node.args[0].s
        elif name == 'print':
            args = [self.visit(e) for e in node.args]
            s = 'console.log({});'.format(', '.join(args))
            return s
        else:
            if node.args:
                args = [self.visit(e) for e in node.args]
                args = ', '.join([e for e in args if e])
            else:
                args = ''
            return '{}({})'.format(name, args)

    def visit_While(self, node):
        body = '\n'.join(map(self.visit, node.body))
        return 'while({}) {{\n{}\n}}'.format(self.visit(node.test), body)

    def visit_AugAssign(self, node):
        target = self.visit(node.target)
        return '{} = {} {} {}'.format(target, target, self.visit(node.op), self.visit(node.value))

    def visit_Str(self, node):
        s = node.s.replace('\n', '\\n')
        if '"' in s:
            return "'{}'".format(s)
        return '"{}"'.format(s)

    def visit_BinOp(self, node):
        left = self.visit(node.left)
        op = self.visit(node.op)
        right = self.visit(node.right)
        return '{} {} {}'.format(left, op, right)

    def visit_Mult(self, node):
        return '*'

    def visit_Add(self, node):
        return '+'

    def visit_Sub(self, node):
        return '-'

    def visit_Div(self, node):
        return '/'

    def visit_Mod(self, node):
        return '%'

    def visit_Lt(self, node):
        return '<'

    def visit_Gt(self, node):
        return '>'

    def visit_GtE(self, node):
        return '>='

    def visit_LtE(self, node):
        return '<='

    def visit_LShift(self, node):
        return '<<'

    def visit_RShift(self, node):
        return '>>'

    def visit_BitXor(self, node):
        return '^'

    def visit_BitOr(self, node):
        return '|'

    def visit_BitAnd(self, node):
        return '&'

    def visit_Assign(self, node):
        # XXX: I'm not sure why it is a list since, mutiple targets are inside a tuple
        target = node.targets[0]
        if isinstance(target, Tuple):
            raise NotImplementedError
        else:
            target = self.visit(target)
            value = self.visit(node.value)
            code = '{} = {};'.format(target, value)
            return code

    def visit_Expr(self, node):
        s = self.visit(node.value)
        if not s.endswith(';'):
            s += ';'
        return s

    def visit_Return(self, node):
        if node.value:
            return 'return {};'.format(self.visit(node.value))
        return 'return undefined;'

    def visit_Pass(self, node):
        return '/*pass*/'

    def visit_Eq(self, node):
        return '=='

    def visit_NotEq(self, node):
        return '!='

    def visit_Num(self, node):
        return str(node.n)

    def visit_Is(self, node):
        return '==='

    def visit_Compare(self, node):
        comp = [self.visit(node.left)]
        for i in range(len(node.ops)):
            comp.append(self.visit(node.ops[i]))
            comp.append(self.visit(node.comparators[i]))
        return ' '.join(comp)

    def visit_Not(self, node):
        return '!'

    def visit_IsNot(self, node):
        return '!=='

    def visit_UnaryOp(self, node):
        return self.visit(node.op) + self.visit(node.operand)

    def visit_And(self, node):
        return ' && '

    def visit_Or(self, node):
        return ' || '

    def visit_BoolOp(self, node):
        op = self.visit(node.op)
        return op.join([self.visit(v) for v in node.values])

    def visit_If(self, node):
        test = self.visit(node.test)
        body = '\n'.join(map(self.visit, node.body)) + '\n'
        if node.orelse:
            orelse = '\n'.join(map(self.visit, node.orelse)) + '\n'
            return 'if({}) {{\n{}}}\nelse {{\n{}}}\n'.format(test, body, orelse)
        else:
            return 'if({}) {{\n{}}}\n'.format(test, body)

    def visit_Dict(self, node):
        a = []
        for i in range(len(node.keys)):
            k = self.visit(node.keys[i])
            v = self.visit(node.values[i])
            a.append('{}:{}'.format(k,v))
        b = ','.join(a)
        return '{{ {} }}'.format(b)

    def visit_For(self, node):
        # support both arrays and objects iteration
        target = node.target.id
        iter = self.visit(node.iter)
        # iter is the python iterator
        init_iter = 'var iter = {};\n'.format(iter)
        # backup iterator and affect value of the next element to the target
        pre = 'var backup = {};\n{} = iter[{}];\n'.format(target, target, target)
        # replace the replace target with the javascript iterator
        post = '{} = backup;\n'.format(target)
        body = '\n'.join(map(self.visit, node.body)) + '\n'
        body = pre + body + post
        for_block = init_iter + 'for (var {}=0; {} < iter.length; {}++) {{\n{}}}\n'.format(target, target, target, body)
        return for_block

    def visit_Continue(self, node):
        return 'continue'


def pys(script):
    input = parse(script)
    tree = parse(input)
    return JSGenerator().visit(tree)


def main():
    print(pys(sys.stdin.read()))

if __name__ == '__main__':
    main()
