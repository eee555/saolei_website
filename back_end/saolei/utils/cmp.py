# 比较两个成绩的好坏

SmallIsBetter = {"time": True, "bvs": False, "stnb": False, "ioe": False, "path": True}
def isbetter(item, a, b):
    if SmallIsBetter[item]:
        return a<b
    else:
        return a>b
