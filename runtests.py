#!/usr/bin/env python3
import os
import sys
from difflib import Differ

from envoy import run


from pythonjs.pys import pys


PYTHONJS_TEST_ROOT = os.path.join(os.path.dirname(__file__), 'unittests', 'pythonjs')
PYS_TEST_ROOT = os.path.join(os.path.dirname(__file__), 'unittests', 'pys')
RUNTIME_TEST_ROOT = os.path.join(os.path.dirname(__file__), 'unittests', 'runtime')


PYS_MOCK = """
// PYS MOCK START
window = {};
HTMLDocument = HTMLElement = function() {};
// PYS MOCK END
"""

RUNTIME_MOCK = """
// RUNTIME MOCK START
str = {__doc__: "str type"};
AttributeError = {__doc__: "AttributeError Exception"};
// RUNTIME MOCK END
"""

if __name__ == '__main__':
    # PYS tests
    if '--pys' in sys.argv or '--all' in sys.argv:
        for test in os.listdir(PYS_TEST_ROOT):
            if test.endswith('.py'):
                filepath = os.path.join(PYS_TEST_ROOT, test)
                with open(filepath) as f:
                    script = f.read()
                exec_script = test + 'exec.js'
                exec_script = os.path.join('/tmp', exec_script)
                with open(exec_script, 'w') as f:
                    f.write(PYS_MOCK)
                    f.write(pys(script))
                r = run('nodejs %s' % exec_script)
                if r.status_code != 0:
                    print(r.std_out)
                    print(r.std_err)
                    print('%s ERROR :(' % test)
                else:
                    expected = run('python3 {}'.format(filepath))
                    expected = expected.std_out
                    if expected == r.std_out:
                        print('%s PASS :)' % test)
                    else:
                        compare = Differ().compare
                        diff = compare(expected.split('\n'), r.std_out.split('\n'))
                        for line in diff:
                            print(line)
                        print('%s FAILED :(' % test)
    # runtime tests
    if '--runtime' in sys.argv or '--all' in sys.argv:
        for test in os.listdir(RUNTIME_TEST_ROOT):
            if test.endswith('.py'):
                filepath = os.path.join(RUNTIME_TEST_ROOT, test)
                with open(filepath) as f:
                    script = f.read()
                exec_script = test + 'exec.js'
                exec_script = os.path.join('/tmp', exec_script)
                with open(os.path.join('runtime', 'pythonpys.py')) as f:
                    runtimejs = pys(f.read())
                with open(exec_script, 'w') as f:
                    f.write(PYS_MOCK)
                    f.write(RUNTIME_MOCK)
                    f.write(runtimejs)
                    f.write(pys(script))
                r = run('nodejs %s' % exec_script)
                if r.status_code != 0:
                    print(r.std_out)
                    print(r.std_err)
                    print('%s ERROR :(' % test)
                else:
                    expected = os.path.join(RUNTIME_TEST_ROOT, test + '.expected')
                    with open(expected) as f:
                        expected = f.read()
                    if expected == r.std_out:
                        print('%s PASS :)' % test)
                    else:
                        compare = Differ().compare
                        diff = compare(expected.split('\n'), r.std_out.split('\n'))
                        for line in diff:
                            print(line)
                        print('%s FAILED :(' % test)

    # PYTHONJS tests
    # XXX: build it dynamically instead of relying on the result of make
    with open('pythonjs.js') as f:
        PYTHONJS = f.read()

    if '--pythonjs' in sys.argv or '--all' in sys.argv:
        for test in os.listdir(PYTHONJS_TEST_ROOT):
            if test.endswith('.py'):
                filepath = os.path.join(PYTHONJS_TEST_ROOT, test)
                with open(filepath) as f:
                    script = f.read()
                exec_script = test + 'exec.js'
                exec_script = os.path.join('/tmp', exec_script)
                with open(exec_script, 'w') as f:
                    f.write(PYS_MOCK)
                    f.write(PYTHONJS)
                    f.write(pythonjs(script))
                r = run('nodejs %s' % exec_script)
                if r.status_code != 0:
                    print(r.std_out)
                    print(r.std_err)
                    print('%s ERROR :(' % test)
                else:
                    expected = os.path.join(ROOT, test + '.expected')
                    with open(expected) as f:
                        expected = f.read()
                    if expected == r.std_out:
                        print('%s PASS :)' % test)
                    else:
                        compare = Differ().compare
                        diff = compare(expected.split('\n'), r.std_out.split('\n'))
                        for line in diff:
                            print(line)
                        print('%s FAILED :(' % test)
