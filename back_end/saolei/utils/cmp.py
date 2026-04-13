# 比较两个成绩的好坏

SmallIsBetter = {'timems': True, 'bvs': False, 'stnb': False, 'ioe': False, 'path': True}


def isbetter(item: str, a: int | float, b: int | float):
    if SmallIsBetter[item]:
        return a < b
    else:
        return a > b
