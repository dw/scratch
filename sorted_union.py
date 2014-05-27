def sorted_union(i1, i2):
    i1 = iter(i1)
    i2 = iter(i2)
    e1 = next(i1, None)
    e2 = next(i2, None)
    while e1 and e2:
        if e1 <= e2:
            yield e1
            e1 = next(i1, None)
        else:
            yield e2
            e2 = next(i2, None)

    for elem, it in (e1, i1), (e2, i2):
        if elem:
            yield elem
            for elem in it:
                yield elem
            break


a = (1, 3, 5, 9, 10)
b = (2, 4, 6, 7, 12)
print list(sorted_union(a, b))
