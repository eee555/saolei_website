from django.db import transaction
from django.db.models import F, Max, Min, Q
from django.utils import timezone

from accountlink.models import AccountLinkQueue, Platform
from config.text_choices import MS_TextChoices
from userprofile.models import UserProfile
from videomanager.models import STNB_COEFFICIENTS, VideoModel
from .cache import invalidate_catalog, read_catalog, write_catalog
from .models import MedalDefinition, MedalGrant, MedalPins, MedalScan, PlayerProgress
from .tasks import enqueue_player_backfill, enqueue_player_refresh
from .utils import basic_definitions, BVS_SCALE, DIRECTION_DESC, KIND_COMPOSITE, KIND_MANUAL, KIND_MIN_VIDEO_ID, KIND_ONCE, KIND_PB, MAX_PINS, next_threshold, NOVICE_LEVELS, NOVICE_LEVELS_NF, NOVICE_MODES, NOVICE_REALNAME, NOVICE_REVIEW, NOVICE_SAOLEI, open_modes, reached_asc_stage, reached_desc_stage, scale_units, SHAREHOLDER_CODE, SHAREHOLDER_THRESHOLDS, STANDARD_LEVELS, STYLE_FL, STYLE_NF, threshold_index, THRP_SCALE


class MedalError(Exception):
    def __init__(self, code):
        super().__init__(code)
        self.code = code


class _Unset:
    pass


UNSET = _Unset()


def definition_payload(definition):
    return {
        'code': definition.code,
        'series': definition.series,
        'subseries': definition.subseries,
        'kind': definition.kind,
        'metric': definition.metric,
        'direction': definition.direction,
        'level': definition.level,
        'style': definition.style,
        'thresholds': list(definition.thresholds or []),
        'hidden': definition.hidden,
        'score_by_stage': list(definition.score_by_stage or []),
        'annotation': definition.annotation,
    }


def ensure_shareholder_definition():
    """补上原始股东这一行。已有的阈值和开关保持不动，运营改过的刻度不会被写回。"""
    definition, _created = MedalDefinition.objects.get_or_create(
        code=SHAREHOLDER_CODE,
        defaults={
            'series': '原始股东', 'kind': KIND_MIN_VIDEO_ID, 'metric': 'video_id', 'direction': DIRECTION_DESC,
            'thresholds': list(SHAREHOLDER_THRESHOLDS), 'score_by_stage': [], 'active': True,
        },
    )
    return definition


def ensure_basic_definitions():
    """补上新手和能力定义。已经存在的阈值、名单和开关保持不动。系列名与当前常量不一致时改名。"""
    specs = basic_definitions()
    codes = [item['code'] for item in specs]
    existing = dict(MedalDefinition.objects.filter(code__in=codes).values_list('code', 'series'))
    missing = [item for item in specs if item['code'] not in existing]
    created = MedalDefinition.objects.bulk_create([MedalDefinition(**item) for item in missing]) if missing else []
    renamed = [item for item in specs if item['code'] in existing and existing[item['code']] != item['series']]
    for item in renamed:
        MedalDefinition.objects.filter(code=item['code']).update(series=item['series'])
    if created or renamed:
        invalidate_catalog()
    return created


def active_definitions():
    ensure_shareholder_definition()
    ensure_basic_definitions()
    cached = read_catalog()
    if cached is not None:
        return cached
    rows = [definition_payload(item) for item in MedalDefinition.objects.filter(active=True).order_by('series', 'subseries', 'code')]
    write_catalog(rows)
    return rows


def _public_definition(row, include_annotation):
    payload = {
        'code': row['code'], 'series': row['series'], 'subseries': row['subseries'], 'kind': row['kind'],
        'metric': row['metric'], 'direction': row['direction'], 'level': row['level'], 'style': row['style'],
        'thresholds': row['thresholds'], 'hidden': row['hidden'], 'annotation': row['annotation'] if include_annotation else '',
    }
    return payload


def catalog_for(user):
    rows = active_definitions()
    unlocked = set()
    if getattr(user, 'is_authenticated', False):
        hidden_codes = [row['code'] for row in rows if row['hidden']]
        if hidden_codes:
            unlocked = set(MedalGrant.objects.filter(user=user, revoked_at__isnull=True, definition_code__in=hidden_codes).values_list('definition_code', flat=True))
    visible = []
    for row in rows:
        if row['hidden'] and row['code'] not in unlocked:
            continue
        visible.append(_public_definition(row, include_annotation=row['hidden']))
    return visible


def _evidence_id(video, participant, evidence):
    if video is not None and not isinstance(video, _Unset):
        return getattr(video, 'id', video)
    if isinstance(evidence, dict) and evidence.get('video_id') is not None:
        return evidence.get('video_id')
    if participant is not None and not isinstance(participant, _Unset):
        return getattr(participant, 'id', None)
    return None


def _append_log(grant, stage, at, evidence_id):
    log = list(grant.stage_log or [])
    if log and log[-1].get('stage') == stage:
        return log
    log.append({'stage': stage, 'at': at.isoformat(), 'evidence_id': evidence_id})
    return log


def _save_progress(user, definition, stage_value, current_value, extra, best_video):
    progress = PlayerProgress.objects.filter(user=user, code=definition.code).first()
    if progress is None:
        return PlayerProgress.objects.create(
            user=user, definition=definition, code=definition.code, current_stage=stage_value,
            current_value=None if current_value is UNSET else current_value,
            extra=None if extra is UNSET else extra,
            best_video=None if best_video is UNSET else best_video,
        )
    progress.definition = definition
    progress.current_stage = stage_value
    fields = ['definition', 'current_stage']
    if current_value is not UNSET:
        progress.current_value = current_value
        fields.append('current_value')
    if extra is not UNSET:
        progress.extra = extra
        fields.append('extra')
    if best_video is not UNSET:
        progress.best_video = best_video
        fields.append('best_video')
    progress.save(update_fields=fields)
    return progress


def _apply_grant_fields(grant, stage, video, participant, evidence, logged_at, append_log, clear_revoke):
    grant.stage = stage
    fields = ['stage']
    if video is not UNSET:
        grant.video = video
        fields.append('video')
    if participant is not UNSET:
        grant.participant = participant
        fields.append('participant')
    if evidence is not UNSET:
        grant.evidence = evidence
        fields.append('evidence')
    if append_log:
        grant.stage_log = _append_log(grant, stage, logged_at, _evidence_id(video, participant, grant.evidence))
        fields.append('stage_log')
    if clear_revoke:
        grant.revoked_at = None
        grant.revoke_reason = ''
        fields.extend(['revoked_at', 'revoke_reason'])
    grant.save(update_fields=fields)
    return grant


@transaction.atomic
def write_stage(user, definition, scope_key='', stage=0, current_value=UNSET, granted_at=None, video=UNSET, participant=UNSET, evidence=UNSET, best_video=UNSET, extra=UNSET, keep_evidence=True):
    """按当前阶段改写同一枚授予。0 表示一档都不够，撤销这一行。人工纪念不在这里撤销。"""
    new_rank = threshold_index(definition.thresholds, stage)
    if definition.kind == KIND_MANUAL and new_rank < 0:
        return MedalGrant.objects.filter(user=user, definition_code=definition.code, scope_key=scope_key).first()

    stage_value = stage if new_rank >= 0 else 0
    _save_progress(user, definition, stage_value, current_value, extra, best_video)
    grant = MedalGrant.objects.select_for_update().filter(user=user, definition_code=definition.code, scope_key=scope_key).first()
    logged_at = granted_at or timezone.now()

    if new_rank < 0:
        if grant is not None and grant.revoked_at is None:
            grant.revoked_at = timezone.now()
            grant.revoke_reason = 'stage'
            grant.save(update_fields=['revoked_at', 'revoke_reason'])
        return grant

    if grant is None:
        evidence_value = {} if evidence is UNSET else evidence
        return MedalGrant.objects.create(
            user=user, definition_code=definition.code, stage=stage, scope_key=scope_key,
            stage_log=[{'stage': stage, 'at': logged_at.isoformat(), 'evidence_id': _evidence_id(video, participant, evidence_value)}],
            video=None if video is UNSET else video, participant=None if participant is UNSET else participant,
            evidence=evidence_value, granted_at=logged_at,
        )

    old_rank = threshold_index(definition.thresholds, grant.stage)
    if grant.revoked_at is not None or new_rank != old_rank or not keep_evidence:
        same_evidence = grant.revoked_at is None and new_rank == old_rank and keep_evidence
        return _apply_grant_fields(
            grant, stage, video, participant, evidence, logged_at,
            append_log=not same_evidence and (grant.revoked_at is not None or new_rank != old_rank),
            clear_revoke=grant.revoked_at is not None,
        )
    return grant


def _medal_item(definition, grant, progress):
    thresholds = definition['thresholds']
    stage = grant.stage if grant is not None else None
    value = None
    if progress is not None and (grant is None or grant.scope_key == ''):
        value = progress.current_value
    evidence = grant.evidence if grant is not None and isinstance(grant.evidence, dict) else {}
    rank = evidence.get('rank') if isinstance(evidence.get('rank'), int) else None
    tournament_id = None
    if grant is not None and grant.participant_id:
        tournament_id = grant.participant.tournament_id
    elif isinstance(evidence.get('tournament_id'), int):
        tournament_id = evidence['tournament_id']
    index = threshold_index(thresholds, stage) if stage else -1
    scores = definition['score_by_stage']
    score = 0
    if grant is not None and not definition['hidden'] and 0 <= index < len(scores):
        score = int(scores[index])
    return {
        'code': definition['code'], 'series': definition['series'], 'subseries': definition['subseries'],
        'kind': definition['kind'], 'stage': stage, 'stage_count': len(thresholds), 'direction': definition['direction'],
        'current_value': value, 'next_threshold': next_threshold(thresholds, stage or 0),
        'granted_at': grant.granted_at if grant is not None else None,
        'video_id': grant.video_id if grant is not None else None, 'tournament_id': tournament_id, 'rank': rank,
        'hidden': definition['hidden'], 'annotation': definition['annotation'] if definition['hidden'] and grant is not None else '',
        'score': score, 'grant_id': grant.id if grant is not None else None,
        'scope_key': grant.scope_key if grant is not None else '', 'thresholds': thresholds,
    }


def _require_user(user_id):
    if not UserProfile.objects.filter(pk=user_id).exists():
        raise MedalError('user')


def player_summary(user_id):
    _require_user(user_id)
    if not MedalScan.objects.filter(user_id=user_id).exists():
        enqueue_player_backfill(user_id)
    definitions = active_definitions()
    grants = list(MedalGrant.objects.filter(user_id=user_id, revoked_at__isnull=True).select_related('participant').order_by('scope_key', 'id'))
    grants_by_code = {}
    for grant in grants:
        grants_by_code.setdefault(grant.definition_code, []).append(grant)
    progress_by_code = {row.code: row for row in PlayerProgress.objects.filter(user_id=user_id)}
    series = []
    index_by_name = {}
    items_by_grant = {}

    def add(item):
        name = item['series']
        if name not in index_by_name:
            index_by_name[name] = len(series)
            series.append({'series': name, 'items': []})
        series[index_by_name[name]]['items'].append(item)
        if item['grant_id'] is not None:
            items_by_grant[item['grant_id']] = item

    for definition in definitions:
        matching = grants_by_code.get(definition['code'], [])
        if definition['hidden'] and not matching:
            continue
        progress = progress_by_code.get(definition['code'])
        if matching:
            for grant in matching:
                add(_medal_item(definition, grant, progress))
        else:
            add(_medal_item(definition, None, progress))

    stored = []
    pins_row = MedalPins.objects.filter(user_id=user_id).first()
    if pins_row and isinstance(pins_row.grant_ids, list):
        stored = [item for item in pins_row.grant_ids if isinstance(item, int)]
    pin_items = [items_by_grant[item] for item in stored if item in items_by_grant][:MAX_PINS]
    return {
        'score': sum(item['score'] for group in series for item in group['items']),
        'max_pins': MAX_PINS,
        'pin_ids': [item['grant_id'] for item in pin_items],
        'pins': pin_items,
        'series': series,
    }


def list_grants(user_id, page, page_size):
    _require_user(user_id)
    definitions = {row['code']: row for row in active_definitions()}
    queryset = MedalGrant.objects.filter(user_id=user_id, revoked_at__isnull=True, definition_code__in=list(definitions)).select_related('participant').order_by('-granted_at', '-id')
    count = queryset.count()
    start = (page - 1) * page_size
    rows = list(queryset[start:start + page_size])
    progress_by_code = {row.code: row for row in PlayerProgress.objects.filter(user_id=user_id, code__in=[row.definition_code for row in rows])}
    items = [_medal_item(definitions[row.definition_code], row, progress_by_code.get(row.definition_code)) for row in rows]
    return {'count': count, 'page': page, 'page_size': page_size, 'items': items}


def replace_pins(user, grant_ids):
    if len(grant_ids) > MAX_PINS:
        raise MedalError('too_many')
    if len(set(grant_ids)) != len(grant_ids):
        raise MedalError('duplicate')
    owned = set(MedalGrant.objects.filter(user=user, revoked_at__isnull=True, id__in=grant_ids).values_list('id', flat=True))
    if owned != set(grant_ids):
        raise MedalError('unavailable')
    MedalPins.objects.update_or_create(user=user, defaults={'grant_ids': list(grant_ids)})
    return list(grant_ids)


def refresh_player(user_id):
    _require_user(user_id)
    enqueue_player_refresh(user_id)


def backfill_player(user_id):
    """历史补发。低优先级，按这一名玩家重算，不在页面请求里扫表。"""
    _require_user(user_id)
    enqueue_player_backfill(user_id)


def grant_manual(actor, code, user_id, reason, granted_at):
    if not str(reason or '').strip():
        raise MedalError('reason')
    user = UserProfile.objects.filter(pk=user_id).first()
    if user is None:
        raise MedalError('user')
    definition = MedalDefinition.objects.filter(pk=code).first()
    if definition is None:
        raise MedalError('definition')
    if not definition.active or definition.kind != KIND_MANUAL:
        raise MedalError('not_manual')
    return write_stage(
        user, definition, stage=definition.thresholds[0] if definition.thresholds else 1, current_value=1,
        granted_at=granted_at, evidence={'reason': reason.strip(), 'actor_id': actor.id}, keep_evidence=False,
    )


def evaluate_player(user_id):
    """重算该玩家已经接上的勋章。用户不存在时直接返回。跑完才记下 MedalScan。"""
    user = UserProfile.objects.filter(pk=user_id).first()
    if user is None:
        return
    ensure_basic_definitions()
    evaluate_min_video_id(user)
    evaluate_once(user)
    evaluate_pb(user)
    evaluate_composite(user)
    MedalScan.objects.update_or_create(user=user, defaults={'scanned_at': timezone.now()})


def evaluate_min_video_id(user):
    """按该玩家仍在库里的最小录像 id 改写原始股东。不看出审、模式和难度。"""
    definition = ensure_shareholder_definition()
    if not definition.active:
        return None
    video = VideoModel.objects.filter(player_id=user.id).order_by('id').first()
    if video is None:
        return write_stage(user, definition, stage=0, current_value=None, best_video=None)
    stage = reached_desc_stage(definition.thresholds, video.id)
    existing = MedalGrant.objects.filter(user=user, definition_code=definition.code, scope_key='').first()
    evidence_remains = (
        existing is not None and existing.revoked_at is None and existing.stage == stage and existing.video_id is not None
        and VideoModel.objects.filter(pk=existing.video_id, player_id=user.id).exists()
    )
    return write_stage(
        user, definition, stage=stage, current_value=video.id, granted_at=video.upload_time,
        video=video, best_video=video, evidence={'video_id': video.id}, keep_evidence=evidence_remains,
    )


def _official_videos(user):
    return VideoModel.objects.filter(player_id=user.id, state=MS_TextChoices.State.OFFICIAL)


def _style_key(definition):
    if definition.style in (STYLE_NF, STYLE_FL):
        return definition.style
    return 'any'


def _pb_queryset(user, level):
    return VideoModel.objects.filter(
        player_id=user.id, state=MS_TextChoices.State.OFFICIAL, mode=MS_TextChoices.Mode.STD,
        level=level, ongoing_tournament=False,
    )


def _thrp_filter(style):
    base = Q(ce__gt=0, bv__isnull=False)
    if style == STYLE_NF:
        return base & Q(right_ce=0, ce__gte=F('bv'))
    if style == STYLE_FL:
        return base & Q(right_ce__gt=0)
    return base


def _qualified(user, definition):
    queryset = _pb_queryset(user, definition.level)
    style = _style_key(definition)
    if definition.metric == 'thrp':
        return queryset.filter(_thrp_filter(style))
    if style == STYLE_NF:
        return queryset.filter(right_ce=0)
    if style == STYLE_FL:
        return queryset.filter(right_ce__gt=0)
    return queryset


def _video_qualifies(video, definition, user_id):
    if video is None or video.player_id != user_id or video.ongoing_tournament:
        return False
    if video.state != MS_TextChoices.State.OFFICIAL or video.mode != MS_TextChoices.Mode.STD or video.level != definition.level:
        return False
    style = _style_key(definition)
    if style == STYLE_NF and video.right_ce != 0:
        return False
    if style == STYLE_FL and (video.right_ce is None or video.right_ce <= 0):
        return False
    if definition.metric == 'timems':
        return video.timems is not None
    if definition.metric == 'bvs':
        return video.bvs is not None
    if definition.metric == 'stnb':
        return video.iqg is not None and definition.level in STNB_COEFFICIENTS
    if definition.metric != 'thrp':
        return False
    if video.thrp is None or video.ce is None or video.bv is None or video.ce <= 0:
        return False
    if style == STYLE_NF and video.ce < video.bv:
        return False
    return True


def _raw_value(video, definition):
    if video is None:
        return None
    if definition.metric == 'timems':
        return video.timems
    if definition.metric == 'bvs':
        return video.bvs
    if definition.metric == 'stnb':
        coefficient = STNB_COEFFICIENTS.get(definition.level)
        if coefficient is None or video.iqg is None:
            return None
        return coefficient * video.iqg
    if definition.metric == 'thrp':
        return video.thrp
    return None


def _units_of(definition, raw):
    if raw is None:
        return None
    if definition.metric == 'timems':
        return int(raw)
    if definition.metric == 'stnb':
        return scale_units(raw, 1)
    if definition.metric == 'bvs':
        return scale_units(raw, BVS_SCALE)
    if definition.metric == 'thrp':
        return scale_units(raw, THRP_SCALE)
    return None


def _stage_of(definition, raw):
    if raw is None:
        return 0
    if definition.metric == 'timems':
        return reached_desc_stage(definition.thresholds, raw)
    if definition.metric == 'stnb':
        return reached_asc_stage(definition.thresholds, raw)
    return reached_asc_stage(definition.thresholds, _units_of(definition, raw))


def _meets_stage(definition, raw, stage):
    if raw is None or not stage:
        return False
    if definition.metric == 'timems':
        return raw < stage
    if definition.metric == 'stnb':
        return raw >= stage
    units = _units_of(definition, raw)
    return units is not None and units >= stage


def _candidate_filter(definition):
    style = _style_key(definition)
    if definition.metric == 'thrp':
        return _thrp_filter(style)
    if style == STYLE_NF:
        return Q(right_ce=0)
    if style == STYLE_FL:
        return Q(right_ce__gt=0)
    return Q()


def _better_filter(definition, video):
    style_filter = _candidate_filter(definition)
    if definition.metric == 'timems' and video.timems is not None:
        return style_filter & Q(timems__lt=video.timems)
    if definition.metric == 'bvs' and video.bvs is not None:
        return style_filter & Q(bvs__gt=video.bvs)
    if definition.metric == 'stnb' and video.iqg is not None:
        return style_filter & Q(iqg__gt=video.iqg)
    if definition.metric == 'thrp' and video.thrp is not None:
        return style_filter & Q(thrp__gt=video.thrp)
    return None


def _matches_any_video(clause):
    return not clause.children and clause.connector == Q.AND


def _level_needs_aggregate(user, level, definitions, progress):
    missing = []
    better = None
    for definition in definitions:
        row = progress.get(definition.code)
        video = None if row is None else row.best_video
        qualified = video is not None and _video_qualifies(video, definition, user.id)
        if row is not None and row.current_stage > 0 and not qualified:
            return True
        if row is not None and video is not None and not qualified:
            return True
        if qualified:
            fresh = _units_of(definition, _raw_value(video, definition))
            if fresh != row.current_value:
                return True
            clause = _better_filter(definition, video)
            if clause is not None:
                better = clause if better is None else better | clause
            continue
        missing.append(definition)
    if missing:
        wanted = None
        for item in missing:
            clause = _candidate_filter(item)
            if _matches_any_video(clause):
                if _pb_queryset(user, level).exists():
                    return True
                continue
            wanted = clause if wanted is None else wanted | clause
        if wanted is not None and _pb_queryset(user, level).filter(wanted).exists():
            return True
    if better is not None and _pb_queryset(user, level).filter(better).exists():
        return True
    return False


def _aggregate_level(user, level):
    queryset = _pb_queryset(user, level)
    nf = Q(right_ce=0)
    return queryset.aggregate(
        time_any=Min('timems'), bvs_any=Max('bvs'), iqg_any=Max('iqg'),
        time_nf=Min('timems', filter=nf), bvs_nf=Max('bvs', filter=nf), iqg_nf=Max('iqg', filter=nf),
        thrp_nf=Max('thrp', filter=_thrp_filter(STYLE_NF)), thrp_fl=Max('thrp', filter=_thrp_filter(STYLE_FL)),
    )


def _aggregate_raw(stats, definition):
    style = _style_key(definition)
    metric = definition.metric
    if metric == 'timems':
        return stats['time_nf'] if style == STYLE_NF else stats['time_any']
    if metric == 'bvs':
        return stats['bvs_nf'] if style == STYLE_NF else stats['bvs_any']
    if metric == 'stnb':
        iqg = stats['iqg_nf'] if style == STYLE_NF else stats['iqg_any']
        coefficient = STNB_COEFFICIENTS.get(definition.level)
        if iqg is None or coefficient is None:
            return None
        return coefficient * iqg
    if metric == 'thrp':
        return stats['thrp_nf'] if style == STYLE_NF else stats['thrp_fl'] if style == STYLE_FL else None
    return None


def _ordered_best(user, definition):
    queryset = _qualified(user, definition)
    if definition.metric == 'timems':
        ordering = ('timems', 'upload_time', 'id')
    elif definition.metric == 'stnb':
        ordering = ('-iqg', 'upload_time', 'id')
    elif definition.metric == 'bvs':
        ordering = ('-bvs', 'upload_time', 'id')
    else:
        ordering = ('-thrp', 'upload_time', 'id')
    return queryset.order_by(*ordering).first()


def _earliest_for_stage(user, definition, stage):
    queryset = _qualified(user, definition)
    if definition.metric == 'timems':
        queryset = queryset.filter(timems__lt=stage)
    elif definition.metric == 'stnb':
        coefficient = STNB_COEFFICIENTS.get(definition.level)
        if not coefficient:
            return None
        queryset = queryset.filter(iqg__gte=stage / coefficient)
    elif definition.metric == 'bvs':
        queryset = queryset.filter(bvs__gte=stage / BVS_SCALE)
    else:
        queryset = queryset.filter(thrp__gte=stage / THRP_SCALE)
    return queryset.order_by('upload_time', 'id').first()


def _evidence_stands(grant, definition, stage, user_id):
    if grant is None or grant.revoked_at is not None or grant.stage != stage or grant.video_id is None:
        return False
    video = grant.video
    raw = _raw_value(video, definition)
    return _video_qualifies(video, definition, user_id) and _meets_stage(definition, raw, stage)


def _apply_pb(user, definition, stats, progress, grant):
    raw = _aggregate_raw(stats, definition)
    units = _units_of(definition, raw)
    stage = _stage_of(definition, raw)
    best = None if raw is None else _ordered_best(user, definition)
    if best is None:
        stage = 0
        units = None
    if stage <= 0:
        if progress is None and grant is None:
            return None
        if progress is not None and progress.current_stage == 0 and progress.current_value == units and progress.best_video_id == (None if best is None else best.id) and (grant is None or grant.revoked_at is not None):
            return grant
        return write_stage(user, definition, stage=0, current_value=units, best_video=best)
    stands = _evidence_stands(grant, definition, stage, user.id)
    same_progress = progress is not None and progress.current_stage == stage and progress.current_value == units and progress.best_video_id == best.id
    if stands and same_progress:
        return grant
    if stands:
        return write_stage(user, definition, stage=stage, current_value=units, best_video=best, keep_evidence=True)
    earliest = _earliest_for_stage(user, definition, stage) or best
    return write_stage(
        user, definition, stage=stage, current_value=units, best_video=best, video=earliest,
        granted_at=None if earliest is None else earliest.upload_time, evidence={'video_id': None if earliest is None else earliest.id},
        keep_evidence=False,
    )


def evaluate_pb(user):
    """按难度聚合生涯最佳。当前最佳仍有效、也没有更好的录像时，不重扫该难度。"""
    definitions = list(MedalDefinition.objects.filter(active=True, kind=KIND_PB, metric__in=['timems', 'bvs', 'stnb', 'thrp'], level__in=STANDARD_LEVELS))
    if not definitions:
        return
    codes = [item.code for item in definitions]
    progress = {row.code: row for row in PlayerProgress.objects.filter(user=user, code__in=codes).select_related('best_video')}
    grants = {row.definition_code: row for row in MedalGrant.objects.filter(user=user, definition_code__in=codes, scope_key='').select_related('video')}
    by_level = {}
    for definition in definitions:
        by_level.setdefault(definition.level, []).append(definition)
    for level, level_definitions in by_level.items():
        if not _level_needs_aggregate(user, level, level_definitions, progress):
            continue
        stats = _aggregate_level(user, level)
        for definition in level_definitions:
            _apply_pb(user, definition, stats, progress.get(definition.code), grants.get(definition.code))


def _mode_list(definition):
    stored = definition.scope.get('modes') if isinstance(definition.scope, dict) else None
    if isinstance(stored, list) and stored:
        return [str(item) for item in stored]
    return open_modes()


def _earliest_official(user, **filters):
    return _official_videos(user).filter(**filters).order_by('upload_time', 'id').first()


def _completing_video(videos):
    if not videos:
        return None
    return max(videos, key=lambda video: (video.upload_time, video.id))


def _saolei_platform(definition):
    if isinstance(definition.scope, dict) and definition.scope.get('platform'):
        return definition.scope['platform']
    return Platform.SAOLEI


def _covers(found, needed):
    return set(needed) <= set(found)


def _once_satisfied(user, definition):
    if definition.code == NOVICE_REALNAME:
        return user.has_realname()
    if definition.code == NOVICE_REVIEW:
        return _official_videos(user).exists()
    if definition.code == NOVICE_LEVELS:
        found = _official_videos(user).filter(level__in=STANDARD_LEVELS).values_list('level', flat=True).distinct()
        return _covers(found, STANDARD_LEVELS)
    if definition.code == NOVICE_LEVELS_NF:
        found = _official_videos(user).filter(level__in=STANDARD_LEVELS, right_ce=0).values_list('level', flat=True).distinct()
        return _covers(found, STANDARD_LEVELS)
    if definition.code == NOVICE_MODES:
        modes = _mode_list(definition)
        found = _official_videos(user).filter(mode__in=modes).values_list('mode', flat=True).distinct()
        return _covers(found, modes)
    if definition.code == NOVICE_SAOLEI:
        return AccountLinkQueue.objects.filter(userprofile=user, platform=_saolei_platform(definition), verified=True).exists()
    return False


def _once_video(user, definition):
    if definition.code == NOVICE_REVIEW:
        return _earliest_official(user)
    if definition.code == NOVICE_LEVELS:
        return _completing_video([_earliest_official(user, level=level) for level in STANDARD_LEVELS])
    if definition.code == NOVICE_LEVELS_NF:
        return _completing_video([_earliest_official(user, level=level, right_ce=0) for level in STANDARD_LEVELS])
    if definition.code == NOVICE_MODES:
        return _completing_video([_earliest_official(user, mode=mode) for mode in _mode_list(definition)])
    return None


def _once_evidence_stands(grant, definition):
    if grant is None or grant.revoked_at is not None or grant.stage != 1:
        return False
    if definition.code in (NOVICE_REALNAME, NOVICE_SAOLEI):
        return True
    video = grant.video
    if video is None or video.state != MS_TextChoices.State.OFFICIAL or video.player_id != grant.user_id:
        return False
    if definition.code == NOVICE_LEVELS_NF and video.right_ce != 0:
        return False
    if definition.code == NOVICE_LEVELS and video.level not in STANDARD_LEVELS:
        return False
    if definition.code == NOVICE_MODES and video.mode not in _mode_list(definition):
        return False
    return True


def _write_once(user, definition, met):
    grant = MedalGrant.objects.filter(user=user, definition_code=definition.code, scope_key='').select_related('video').first()
    if not met:
        if grant is None or grant.revoked_at is not None:
            return grant
        return write_stage(user, definition, stage=0, current_value=0, best_video=None)
    if _once_evidence_stands(grant, definition):
        return write_stage(user, definition, stage=1, current_value=1, keep_evidence=True)
    video = _once_video(user, definition)
    if video is None and definition.code not in (NOVICE_REALNAME, NOVICE_SAOLEI):
        if grant is None or grant.revoked_at is not None:
            return grant
        return write_stage(user, definition, stage=0, current_value=0, best_video=None)
    evidence = {} if video is None else {'video_id': video.id}
    return write_stage(
        user, definition, stage=1, current_value=1, video=video, best_video=video,
        granted_at=None if video is None else video.upload_time, evidence=evidence, keep_evidence=False,
    )


def evaluate_once(user):
    """实名、过审、全级别、全模式，以及扫雷网已验证。其他平台这一步不发。"""
    codes = [NOVICE_REALNAME, NOVICE_REVIEW, NOVICE_LEVELS, NOVICE_LEVELS_NF, NOVICE_MODES, NOVICE_SAOLEI]
    definitions = {item.code: item for item in MedalDefinition.objects.filter(active=True, kind=KIND_ONCE, code__in=codes)}
    for code in codes:
        definition = definitions.get(code)
        if definition is None:
            continue
        _write_once(user, definition, _once_satisfied(user, definition))


def evaluate_composite(user):
    """三阶只读三个难度的进度，不扫录像，也不撤掉单级授予。"""
    definitions = list(MedalDefinition.objects.filter(active=True, kind=KIND_COMPOSITE, metric='thrp'))
    if not definitions:
        return
    codes = [code for definition in definitions for code in (definition.depends_on or [])]
    progress = {row.code: row for row in PlayerProgress.objects.filter(user=user, code__in=codes).select_related('best_video')}
    for definition in definitions:
        depended = list(definition.depends_on or [])
        if len(depended) < 3:
            continue
        stages = []
        video_ids = []
        uploaded = []
        for code in depended:
            row = progress.get(code)
            stages.append(0 if row is None else row.current_stage)
            if row is not None and row.best_video_id:
                video_ids.append(row.best_video_id)
                if row.best_video is not None:
                    uploaded.append(row.best_video.upload_time)
        stage = reached_asc_stage(definition.thresholds, min(stages) if stages else 0)
        grant = MedalGrant.objects.filter(user=user, definition_code=definition.code, scope_key='').first()
        if stage <= 0:
            if grant is None or grant.revoked_at is not None:
                continue
            write_stage(user, definition, stage=0, current_value=min(stages) if stages else 0)
            continue
        if grant is not None and grant.revoked_at is None and grant.stage == stage:
            write_stage(user, definition, stage=stage, current_value=stage, keep_evidence=True)
            continue
        write_stage(
            user, definition, stage=stage, current_value=stage,
            granted_at=max(uploaded) if uploaded else None, evidence={'video_ids': video_ids}, keep_evidence=False,
        )


def revoke_manual(grant_id, reason):
    if not str(reason or '').strip():
        raise MedalError('reason')
    grant = MedalGrant.objects.filter(pk=grant_id).first()
    if grant is None:
        raise MedalError('missing')
    if grant.revoked_at is not None:
        raise MedalError('revoked')
    grant.revoked_at = timezone.now()
    grant.revoke_reason = reason.strip()
    grant.save(update_fields=['revoked_at', 'revoke_reason'])
    if grant.scope_key == '':
        PlayerProgress.objects.filter(user_id=grant.user_id, code=grant.definition_code).update(current_stage=0)
    return grant
