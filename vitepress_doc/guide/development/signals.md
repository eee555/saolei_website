# 信号触发关系

```automaton
flowchart LR
    video_pre_save[VideoModel pre_save]
    video_post_save[VideoModel post_save]
    video_post_delete[VideoModel post_delete]
    userms_pre_save[UserMS pre_save]
    userms_post_save[UserMS post_save]
    pluck_pre_save[CustomPluckRecord pre_save]
    pluck_post_save[CustomPluckRecord post_save]
    pluck_post_delete[CustomPluckRecord post_delete]
    tournament_post_save[Tournament post_save]
    tournament_post_delete[Tournament post_delete]
    gsc_post_save[GSCTournament post_save]
    participant_post_save[TournamentParticipant post_save]
    gsc_participant_post_save[GSCParticipant post_save]
    participant_post_delete[TournamentParticipant post_delete]

    video_pre_save --> capture_video_update[捕获字段旧值]
    capture_video_update --> video_post_save
    video_pre_save --> checkin_video_before_create[比赛录像检测]
    checkin_video_before_create --> video_post_save

    video_post_save --> refresh_state_queue_on_video_save[刷新状态队列]
    video_post_save --> update_video_count_on_video_save[更新用户录像计数]
    video_post_save --> update_video_count_limit_on_video_save[更新用户录像上限]
    video_post_save --> add_created_video_to_checked_tournaments[将比赛录像挂载到比赛]
    video_post_save --> refresh_personal_record_on_video_save[刷新经典纪录]
    video_post_save --> refresh_custom_pluck_rank_on_video_save[刷新pluck纪录]

    video_post_delete --> update_video_count_on_video_delete[更新用户录像计数]
    video_post_delete --> refresh_personal_record_on_video_delete[刷新个人纪录]

    update_video_count_on_video_save --> userms_pre_save
    refresh_personal_record_on_video_save --> userms_pre_save
    refresh_personal_record_on_video_delete --> userms_pre_save

    userms_pre_save --> capture_previous_records_for_news_queue[捕获旧纪录]
    capture_previous_records_for_news_queue --> userms_post_save
    userms_post_save --> push_news_queue_on_record_save[推送新闻]

    refresh_custom_pluck_rank_on_video_save --> pluck_pre_save
    refresh_custom_pluck_rank_on_video_save --> pluck_post_delete
    pluck_pre_save --> pluck_post_save
    pluck_post_save --> update_custom_pluck_cache_on_record_save[更新pluck榜缓存]
    pluck_post_delete --> update_custom_pluck_cache_on_record_delete[删除pluck榜缓存]

    add_created_video_to_checked_tournaments -. m2m_changed .-> no_video_signal[无]

    tournament_post_save --> update_cache_on_tournament_save[更新比赛缓存]
    gsc_post_save --> update_cache_on_tournament_save
    tournament_post_delete --> update_cache_on_tournament_delete[删除比赛缓存]

    participant_post_save --> update_cache_on_participant_save[更新参赛缓存]
    gsc_participant_post_save --> update_cache_on_participant_save
    participant_post_delete --> remove_participant_cache_on_delete[删除参赛缓存]
    update_cache_on_participant_save -->|created| add_existing_videos_to_participant_tournament[补录比赛录像]

    add_existing_videos_to_participant_tournament -. m2m_changed .-> no_participant_signal[无]

    click video_pre_save "#signal-function-map" "VideoModel 保存前触发"
    click video_post_save "#signal-function-map" "VideoModel 保存后触发"
    click video_post_delete "#signal-function-map" "VideoModel 删除后触发"
    click userms_pre_save "#signal-function-map" "UserMS 保存前触发"
    click userms_post_save "#signal-function-map" "UserMS 保存后触发"
    click pluck_pre_save "#signal-function-map" "CustomPluckRecord 保存前触发"
    click pluck_post_save "#signal-function-map" "CustomPluckRecord 保存后触发"
    click pluck_post_delete "#signal-function-map" "CustomPluckRecord 删除后触发"
    click tournament_post_save "#signal-function-map" "Tournament 保存后触发"
    click tournament_post_delete "#signal-function-map" "Tournament 删除后触发"
    click gsc_post_save "#signal-function-map" "GSCTournament 保存后触发"
    click participant_post_save "#signal-function-map" "TournamentParticipant 保存后触发"
    click gsc_participant_post_save "#signal-function-map" "GSCParticipant 保存后触发"
    click participant_post_delete "#signal-function-map" "TournamentParticipant 删除后触发"

    click capture_video_update "#signal-function-map" "保存前记录录像旧状态，用于保存后判断副作用"
    click checkin_video_before_create "#signal-function-map" "录像创建前，根据用户参赛缓存判断是否属于比赛录像"
    click refresh_state_queue_on_video_save "#signal-function-map" "根据录像状态同步普通录像队列"
    click update_video_count_on_video_save "#signal-function-map" "录像保存后同步用户录像计数"
    click update_video_count_limit_on_video_save "#signal-function-map" "录像保存后同步用户录像数量上限"
    click add_created_video_to_checked_tournaments "#signal-function-map" "录像创建后写入命中的比赛录像关系"
    click refresh_personal_record_on_video_save "#signal-function-map" "录像保存后刷新经典个人纪录"
    click refresh_custom_pluck_rank_on_video_save "#signal-function-map" "录像保存后刷新自定义 pluck 排行"
    click update_video_count_on_video_delete "#signal-function-map" "录像删除后同步用户录像计数"
    click refresh_personal_record_on_video_delete "#signal-function-map" "录像删除后刷新经典个人纪录"
    click capture_previous_records_for_news_queue "#signal-function-map" "UserMS 保存前记录旧纪录，用于生成新闻"
    click push_news_queue_on_record_save "#signal-function-map" "UserMS 保存后推送纪录相关新闻"
    click update_custom_pluck_cache_on_record_save "#signal-function-map" "pluck 纪录保存后同步排行缓存"
    click update_custom_pluck_cache_on_record_delete "#signal-function-map" "pluck 纪录删除后同步排行缓存"
    click update_cache_on_tournament_save "#signal-function-map" "比赛保存后同步 NORMAL 比赛缓存"
    click update_cache_on_tournament_delete "#signal-function-map" "比赛删除后移除比赛缓存和相关参赛缓存"
    click update_cache_on_participant_save "#signal-function-map" "参赛关系保存后同步用户参赛缓存"
    click remove_participant_cache_on_delete "#signal-function-map" "参赛关系删除后移除用户参赛缓存"
    click add_existing_videos_to_participant_tournament "#signal-function-map" "创建参赛关系后扫描并补录既有比赛录像"
```

<a id="signal-function-map"></a>

| 图中名称 | 函数 |
| --- | --- |
| 捕获字段旧值 | `capture_video_update` |
| 比赛录像检测 | `checkin_video_before_create` |
| 刷新状态队列 | `refresh_state_queue_on_video_save` |
| 更新用户录像计数 | `update_video_count_on_video_save` / `update_video_count_on_video_delete` |
| 更新用户录像上限 | `update_video_count_limit_on_video_save` |
| 将比赛录像挂载到比赛 | `add_created_video_to_checked_tournaments` |
| 刷新经典纪录 | `refresh_personal_record_on_video_save` / `refresh_personal_record_on_video_delete` |
| 刷新pluck纪录 | `refresh_custom_pluck_rank_on_video_save` |
| 捕获旧纪录 | `capture_previous_records_for_news_queue` |
| 推送新闻 | `push_news_queue_on_record_save` |
| 更新pluck榜缓存 | `update_custom_pluck_cache_on_record_save` |
| 删除pluck榜缓存 | `update_custom_pluck_cache_on_record_delete` |
| 更新比赛缓存 | `update_cache_on_tournament_save` |
| 删除比赛缓存 | `update_cache_on_tournament_delete` |
| 更新参赛缓存 | `update_cache_on_participant_save` |
| 删除参赛缓存 | `remove_participant_cache_on_delete` |
| 补录比赛录像 | `add_existing_videos_to_participant_tournament` |

`Tournament` / `GSCTournament` 的保存信号分别绑定到同一个 `update_cache_on_tournament_save` 接收器。`TournamentParticipant` / `GSCParticipant` 的保存信号分别绑定到同一个 `update_cache_on_participant_save` 接收器。删除信号只保留父类接收器；多表继承删除子类时会继续触发父表删除。
