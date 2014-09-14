


def custom_unit(base_type, name='Unit'):
    Unit = type(name, (base_type,), {})

    def unary_wrapper(func):
        def wrapper(self, other):
            if other.__class__ is not self.__class__:
                raise TypeError('%s: cannot mix type %s with %s'
                                % (func.__name__,
                                   type(self).__name__,
                                   type(other).__name__))
            print func, self, other
            return func(self, other)
        wrapper.__name__ = func.__name__
        return wrapper

    for binary in ('__add__', '__sub__', '__mul__',
                   '__floordiv__', '__mod__', '__divmod__', '__lshift__',
                   '__rshift__', '__and__', '__xor__', '__or__', '__div__',
                   '__truediv__', '__radd__', '__rsub__', '__rmul__',
                   '__rdiv__', '__rtruediv__', '__rfloordiv__', '__rmod__',
                   '__rdivmod__', '__rpow__', '__rlshift__', '__rrshift__',
                   '__rand__', '__rxor__', '__ror__', '__iadd__',
                   '__isub__', '__imul__', '__idiv__', '__itruediv__',
                   '__ifloordiv__', '__imod__', '__ilshift__',
                   '__irshift__', '__iand__', '__ixor__', '__ior__',
                   '__coerce__', '__lt__', '__le__', '__eq__', '__ne__',
                   '__gt__', '__ge__'):
        bbin = getattr(base_type, binary, None)
        obin = getattr(object, binary, None)
        if bbin != obin:
            print bbin, obin
            setattr(Unit, binary, unary_wrapper(getattr(base_type, binary)))

    return Unit


Mbps = custom_unit(int, 'Mbps')
Gbps = custom_unit(int, 'Gbps')


x = Mbps('1')
y = Gbps('1')
print x == Mbps(y)
print x == y
