
def bvs(bv, timems):
    if bv is None or timems is None:
        return None
    if timems == 0:
        return 0.0
    return bv / timems * 1000


def iqg(bv, timems):
    if bv is None or timems is None:
        return None
    if timems == 0:
        return 0.0
    return bv / (timems / 1000) ** 1.7


def ioe(bv, left, right, double):
    if bv is None or left is None or right is None or double is None:
        return None
    cl = left + right + double
    if cl == 0:
        return None
    return bv / cl


def cmp(x: int | float | None, y: int | float | None):
    # 当前调用场景不需要区分 cmp(None, 0)，因为参与比较的参数不会为 0。
    if x == y:
        return 0
    elif x is None:
        return -y
    elif y is None:
        return x
    else:
        return x - y
