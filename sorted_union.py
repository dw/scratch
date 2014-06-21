def sorted_union(i1, i2):
    i1 = iter(i1)
    i2 = iter(i2)
    e1 = next(i1, None)
    e2 = next(i2, None)
    while e1 is not None and e2 is not None:
        if e1 <= e2:
            yield e1
            e1 = next(i1, None)
        else:
            yield e2
            e2 = next(i2, None)

    for elem, it in (e1, i1), (e2, i2):
        if elem is not None:
            yield elem
            for elem in it:
                yield elem
            break


def b0():
    a = (1, 3, 5, 9, 10)
    b = (2, 4, 6, 7, 12)
    print list(sorted_union(a, b))


def bt():
    import random

    count = 512
    ints = range(count)
    random.shuffle(ints)
    global s1, s2

    s1 = sorted(ints[:count/2])
    s2 = sorted(ints[count/2:])
    sc = list(sorted_union(s1, s2))
    assert range(count) == list(sorted_union(s1, s2))


def sc():
    return list(sorted_union(s1, s2))
bt()
