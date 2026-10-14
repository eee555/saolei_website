"""Convert public WOM statistics to the account-link fields, without inventory data."""

STAT_FIELDS = {
    'trophy': 'score', 'experience': 'exp', 'arena_point': 'arenaPoints',
    'max_difficulty': 'diff', 'win': 'winsAll',
    'experience_total': 'expAll', 'minecoin_total': 'coinsAll',
    'gem_total': 'gemsAll', 'arena_coin_total': 'arenaCoinsAll',
    'game_count': 'games', 'win_nf': 'winsNf', 'play_time_ms': 'timeAll',
    'arena_play_time_ms': 'arenaDuration', 'bbbv_total': 'bbbvAll', 'season_count': 'seasons',
    'b_win': 'wins1', 'i_win': 'wins2', 'e_win': 'wins3',
    'b_ng_win': 'wins11', 'i_ng_win': 'wins12', 'e_ng_win': 'wins13',
}
ENDURANCE_BASE_MS = 86400000
FIRST_MONTHLY_SEASON = 24192
UINT16_MAX = 2 ** 16 - 1
UINT32_MAX = 2 ** 32 - 1
STAT_FIELD_MAXIMUMS = {
    'trophy': UINT16_MAX, 'arena_point': UINT16_MAX, 'season_count': UINT16_MAX,
    'play_time_ms': 2 ** 63 - 1, 'arena_play_time_ms': 2 ** 63 - 1,
}


def _counter(value, maximum=UINT32_MAX):
    if value is None:
        return None
    if type(value) is not int or not 0 <= value <= maximum:
        raise ValueError('Expected a nonnegative integer statistic within the field range')
    return value


def _records(profile, key):
    records = profile[key]
    if records is None:
        return {}
    if not isinstance(records, dict):
        raise ValueError('Expected a record dictionary')
    return records


def _record_value(records, level, key):
    record = records.get(str(level))
    if record is None:
        return None
    if not isinstance(record, dict) or key not in record:
        raise ValueError('Invalid personal-best record')
    return _counter(record[key])


def normalize_wom_profile(profile, user_id: int) -> dict:
    if not isinstance(profile, dict) or not isinstance(profile.get('user'), dict):
        raise ValueError('Missing user identity')
    remote_id = profile['user'].get('id')
    if type(remote_id) is not int or remote_id != user_id:
        raise ValueError('User identity does not match the linked account')
    if 'userStat' not in profile:
        raise ValueError('Missing public statistics section')
    stat = profile['userStat']
    if stat is None:
        # Hidden or unavailable statistics do not clear previously imported records.
        experience = profile.get('noUserStatExp')
        if experience is None or experience == -1:
            raise ValueError('No public statistics are available')
        return {'experience': _counter(experience)}
    if not isinstance(stat, dict):
        raise ValueError('Invalid public statistics section')

    data = {
        field: _counter(stat[key], STAT_FIELD_MAXIMUMS.get(field, UINT32_MAX))
        for field, key in STAT_FIELDS.items()
        if key in stat
    }
    if 'lastSeason' in stat:
        season = _counter(stat['lastSeason'])
        if not season:
            data['last_season'] = None
        elif season < 10000:
            data['last_season'] = season
        elif season >= FIRST_MONTHLY_SEASON:
            data['last_season'] = season - FIRST_MONTHLY_SEASON + 1
        else:
            raise ValueError('Unknown season encoding')
        data['last_season'] = _counter(data['last_season'], UINT16_MAX)

    for level, prefix in enumerate(('b', 'i', 'e'), 1):
        for field, key in (('mastery', 'mastery'), ('winstreak', 'ws')):
            stat_key = f'{key}{level}'
            if stat_key in stat:
                data[f'{prefix}_{field}'] = _counter(stat[stat_key], UINT16_MAX)
        endurance_key = f'end{level}'
        if endurance_key in stat:
            score = _counter(stat[endurance_key])
            if score is not None and score > ENDURANCE_BASE_MS:
                raise ValueError('Invalid endurance score')
            data[f'{prefix}_endurance_ms'] = ENDURANCE_BASE_MS - (score or 0)
        if 'timeResults' in profile:
            times = _records(profile, 'timeResults')
            data[f'{prefix}_t_ms'] = _record_value(times, level, 'duration')
            data[f'{prefix}_ng_t_ms'] = _record_value(times, level + 10, 'duration')
        if 'effResults' in profile:
            efficiency = _record_value(_records(profile, 'effResults'), level, 'eff100')
            # Keep the integer percentage previously read from the profile page.
            data[f'{prefix}_ioe'] = ((efficiency + 50) // 100) / 100 if efficiency is not None else None
    if not data:
        raise ValueError('No supported public statistics are available')
    return data
