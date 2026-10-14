

def weekly_encode_best(score: int, year: int, week: int):
    return score * 100000 + (year % 1000) * 100 + week
