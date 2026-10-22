def player_batches(videos, batch_size: int):
    """按玩家 id 分段，避免一次加载所有玩家。"""
    last_player = 0
    while players := list(videos.filter(player_id__gt=last_player).order_by('player_id').values_list('player_id', flat=True).distinct()[:batch_size]):
        yield players
        last_player = players[-1]
