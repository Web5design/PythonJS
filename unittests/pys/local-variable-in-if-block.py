a = 42
b = 0

def func():
    a = 1
    if True:
        a = 2
        b = 84
func()
print(a)
print(b)
