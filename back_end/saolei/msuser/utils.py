def get_video_num_limit(timems: int):
    if timems < 30000:
        return 10000
    elif timems < 40000:
        return 8000
    elif timems < 50000:
        return 5000
    elif timems < 60000:
        return 3000
    elif timems < 100000:
        return 1000
    return 100
