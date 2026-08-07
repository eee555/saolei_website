# 缓存结构

本文记录项目当前使用的 Redis / Django cache 结构，以及缓存与数据库、API 之间的读写流向。数据库字段结构以各 app 的 `models.py` 为准，这里只记录缓存中实际保存的数据结构。

## 总览

```dot
digraph cache {
    graph [
        layout=neato,
        overlap=false,
        splines=true,
        outputorder=edgesfirst,
        bgcolor="transparent",
        sep="+24",
        K=1.2,
        start=7
    ];

    node [
        shape=box,
        style="rounded,filled",
        fillcolor="${#f8fafc|#1f2937}",
        color="${#94a3b8|#64748b}",
        fontcolor="${#0f172a|#e5e7eb}",
        fontsize=12
    ];

    edge [
        color="${#64748b|#94a3b8}",
        fontcolor="${#475569|#cbd5e1}",
        fontsize=9,
        arrowsize=0.7
    ];

    subgraph api_nodes {
        get_account_links [label="/api/accountlink/{user_id}"];
        create_account_link [label="/api/accountlink/create/"];
        task_summary [label="/api/common/tasksummary"];
        disk_usage [label="/api/common/diskusage"];
        video_summary [label="/api/common/videosummary"];
        video_upload [label="/common/uploadvideo/"];
        pluck_rank [label="/api/customranking/pluck"];
        player_pluck_records [label="/api/customranking/pluck/player"]
        add_identifier [label="/identifier/add/"];
        del_identifier [label="/identifier/del/"];
        get_records [label="/api/msuser/records"];
        get_records_abstract [label="/api/msuser/records_abstract"];
        player_rank [label="/msuser/player_rank/"];
        get_tournament_list [label="/api/tournament/get_list"];
        get_tournament [label="/api/tournament/get"];
        set_tournament [label="/api/tournament/set"];
        cancel_tournament [label="/api/tournament/cancel"];
        get_participant_list [label="/api/tournament/participants"];
        get_participant_videos [label="/api/tournament/get_videos/participant"];
        get_tournament_news [label="/api/tournament/get_news"];
        download_all_videos [label="/api/tournament/download"];
        download_videos_participant [label="/api/tournament/download/participant"];
        get_gscinfo [label="/api/tournament/gsc/info"];
        create_gsc_participant [label="/api/tournament/gsc/participant"];
        register_gsc_participant_identifier [label="/api/tournament/gsc/participant/identifier"];
        get_user_info [label="/api/userprofile/info/{user_id}"];
        get_user_info_bulk [label="/api/userprofile/infobulk"];
        get_user_info_updated [label="/api/userprofile/infoupdated"];
        get_user_identifier [label="/api/userprofile/identifier"];
        get_user_avatar [label="/api/userprofile/avatar/{user_id}"];
        get_user_videos [label="/api/userprofile/videolist"];
        update_user_profile [label="/api/userprofile/update_profile"];
        update_user_avatar [label="/api/userprofile/update_avatar"];
        user_login [label="/userprofile/login/"];
        user_retrieve [label="/userprofile/retrieve/"];
        user_register [label="/userprofile/register/"];
        check_collision [label="/userprofile/checkcollision/"];
        refresh_captcha [label="/userprofile/refresh_captcha/"];
        get_email_captcha [label="/userprofile/get_email_captcha/"];
        get_review_queue [label="/api/video/review_queue"];
        get_video_info_bulk [label="/api/video/infobulk"];
        get_video_detail_bulk [label="/api/video/detailbulk"];
        get_software [label="/video/get_software/"]
        video_preview [label="/video/preview/"];
        video_download [label="/video/download/"];
        video_query [label="/video/query/"];
        video_query_by_id [label="/video/query_by_id/"];
        newest_queue [label="/video/newest_queue/"];
        news_queue [label="/video/news_queue/"];
        freeze_queue [label="/video/freeze_queue/"];
        video_api [label="video GET APIs"];
    }

    subgraph db_nodes {
        node [shape=cylinder, fillcolor="${#e0f2fe|#0f172a}"];
        captcha_db [label="CaptchaStore"];
        task_db [label="DBTaskResult"];
        accountlinkqueue_db [label="AccountLinkQueue\nplatform accounts"];
        accountlinkplatform_db [label="AccountSaolei\nAccountMinesweeperGames\nAccountBilibili\nAccountWorldOfMinesweeper\nAccountQQ"];
        videosaolei_db [label="VideoSaolei"];
        custom_pluck_db [label="CustomPluckRecord"];
        identifier_db [label="Identifier"];
        userms_db [label="UserMS"];
        tournament_db [label="Tournament\nGSCTournament"];
        participant_db [label="TournamentParticipant\nGSCParticipant"];
        userprofile_db [label="UserProfile"];
        email_otp_db [label="EmailVerifyRecord"]
        video_db [label="VideoModel\nExpandVideoModel"];
    }

    subgraph cache_nodes {
        node [shape=box, fillcolor="${#dcfce7|#14532d}"];
        task_summary_cache [label="api:common/tasksummary"];
        disk_usage_cache [label="api:common/diskusage"];
        video_summary_cache [label="api:common/videosummary"];
        pluck_rank_cache [label="customranking:pluck:{level}:rank\nzset"];
        pluck_detail_cache [label="customranking:pluck:{level}:detail\nhash"];
        newest_cache [label="newest_queue\nhash"];
        freeze_cache [label="freeze_queue\nhash"];
        review_cache [label="review_queue\nhash"];
        news_cache [label="news_queue\nzset"];
        player_record_cache [label="player_{stat}_{mode}_{user_id}\nhash"];
        player_rank_cache [label="player_{stat}_{mode}_ids\nzset"];
        tournament_cache [label="tournament:normal\nhash"];
        participant_cache [label="tournament:normal:participants\nhash"];
        common_summary_cache [label="api:common/*\nTTL 300s"];
    }

    subgraph file_nodes {
        node [shape=folder, fillcolor="${#e0f2fe|#0f172a}"];
        video_files [label="video files"];
        avatar_files [label="avatar files"];
    }

    // accountlink API
    accountlinkqueue_db -> get_account_links;
    accountlinkplatform_db -> get_account_links;
    create_account_link -> accountlinkqueue_db;

    // common API
    task_db -> task_summary_cache -> task_summary;
    video_db -> disk_usage_cache -> disk_usage;
    video_db -> video_summary_cache -> video_summary;
    video_upload -> video_db;
    video_upload -> video_files;

    // customranking API
    pluck_rank_cache -> pluck_rank
    pluck_detail_cache -> pluck_rank
    pluck_rank_cache -> player_pluck_records
    pluck_detail_cache -> player_pluck_records

    //identifier API
    userms_db -> add_identifier;
    video_db -> add_identifier;
    add_identifier -> identifier_db;
    add_identifier -> userms_db;
    add_identifier -> custom_pluck_db;
    userms_db -> del_identifier;
    video_db -> del_identifier;
    del_identifier -> identifier_db;
    del_identifier -> userms_db;
    del_identifier -> custom_pluck_db;

    // msuser API
    userms_db -> get_records;
    userms_db -> get_records_abstract;
    player_record_cache -> player_rank;
    player_rank_cache -> player_rank;

    // tournament API
    tournament_db -> get_tournament_list;
    tournament_cache -> get_tournament_list;
    tournament_db -> get_tournament;
    userprofile_db -> set_tournament;
    tournament_db -> set_tournament;
    set_tournament -> tournament_db;
    userprofile_db -> cancel_tournament;
    tournament_db -> cancel_tournament;
    cancel_tournament -> tournament_db;
    tournament_db -> get_participant_list;
    participant_db -> get_participant_list;
    userprofile_db -> get_participant_videos;
    tournament_db -> get_participant_videos;
    participant_db -> get_participant_videos;
    video_db -> get_participant_videos;
    tournament_cache -> get_tournament_news;
    tournament_db -> download_all_videos;
    video_db -> download_all_videos;
    video_files -> download_all_videos;
    tournament_db -> download_videos_participant;
    userprofile_db -> download_videos_participant;
    video_db -> download_videos_participant;
    video_files -> download_videos_participant;

    // tournament gsc API
    tournament_db -> get_gscinfo;
    participant_db -> get_gscinfo;
    identifier_db -> get_gscinfo;
    userprofile_db -> get_gscinfo;
    tournament_db -> create_gsc_participant;
    userprofile_db -> create_gsc_participant;
    create_gsc_participant -> participant_db;
    userprofile_db -> register_gsc_participant_identifier;
    tournament_db -> register_gsc_participant_identifier;
    participant_db -> register_gsc_participant_identifier;
    identifier_db -> register_gsc_participant_identifier;
    register_gsc_participant_identifier -> identifier_db;
    register_gsc_participant_identifier -> participant_db;
    register_gsc_participant_identifier -> userms_db;
    register_gsc_participant_identifier -> video_db;

    // userprofile API
    userprofile_db -> get_user_info;
    userprofile_db -> get_user_info_bulk;
    userprofile_db -> get_user_info_updated;
    userprofile_db -> get_user_identifier;
    userms_db -> get_user_identifier;
    userprofile_db -> get_user_avatar;
    avatar_files -> get_user_avatar;
    userprofile_db -> get_user_videos;
    video_db -> get_user_videos;
    userprofile_db -> update_user_profile;
    userms_db -> update_user_profile;
    update_user_profile -> userprofile_db;
    userprofile_db -> update_user_avatar;
    userms_db -> update_user_avatar;
    update_user_avatar -> userprofile_db;
    update_user_avatar -> avatar_files;
    captcha_db -> user_login;
    userprofile_db -> user_login;
    userms_db -> user_login;
    video_db -> user_login;
    email_otp_db -> user_retrieve;
    userms_db -> user_retrieve;
    video_db -> user_retrieve;
    userprofile_db -> user_retrieve;
    user_retrieve -> userprofile_db;
    user_retrieve -> email_otp_db;
    email_otp_db -> user_register;
    userms_db -> user_register;
    video_db -> user_register;
    userprofile_db -> user_register;
    user_register -> userprofile_db;
    user_register -> email_otp_db;
    userprofile_db -> check_collision;
    refresh_captcha -> captcha_db;
    captcha_db -> refresh_captcha;
    captcha_db -> get_email_captcha;
    get_email_captcha -> captcha_db;

    // videomanager API
    video_db -> get_review_queue;
    video_db -> get_video_info_bulk;
    video_db -> get_video_detail_bulk;
    video_db -> get_software;
    userprofile_db -> get_software;
    video_db -> video_preview;
    userprofile_db -> video_preview;
    video_files -> video_preview;
    video_db -> video_download;
    userprofile_db -> video_download;
    video_files -> video_download;
    userprofile_db -> video_query;
    video_db -> video_query;
    userprofile_db -> video_query_by_id;
    video_db -> video_query_by_id;
    newest_cache -> newest_queue;
    news_cache -> news_queue;
    freeze_cache -> freeze_queue;

    // customranking signals
}
```

<a id="cache-data-structure"></a>

## 缓存数据结构

| 所属 app | key | Redis 类型 | 数据结构 |
| --- | --- | --- | --- |
| `videomanager` | `newest_queue` | hash | `field = video_id`；`value = VideoQueue JSON`，包含 `state`、`tournament`、`software`、`time`、`player_id`、`identifier`、`level`、`mode`、`timems`、`bv`、`cl`、`ce`。 |
| `videomanager` | `freeze_queue` | hash | 同 `newest_queue`，用于冻结录像队列。 |
| `videomanager` | `review_queue` | hash | 同 `newest_queue`，用于待审核录像队列。 |
| `msuser` / `videomanager` | `news_queue` | zset | `member = news JSON`；`score = time.timestamp()`；最多保留 200 条。JSON 包含 `time`、`player_id`、`video_id`、`index`、`mode`、`level`、`value`、`old_value`。 |
| `msuser` | `player_{stat}_{mode}_{user_id}` | hash | 三关个人纪录详情。字段为 `b`、`i`、`e`、`b_id`、`i_id`、`e_id`、`sum`。 |
| `msuser` | `player_{stat}_{mode}_ids` | zset | `member = user_id`；`score = 三关 sum`。`player_rank` 使用它作为排序入口，并通过 Redis `SORT GET` 读取详情 hash。 |
| `customranking` | `customranking:pluck:{level}:rank` | zset | `member = player_id`；`score = pluck`，当 `pluck == 0` 时使用 `timems - MAX_TIMEMS` 降低 0 碰撞风险。 |
| `customranking` | `customranking:pluck:{level}:detail` | hash | `field = player_id`；`value = detail JSON`，包含 `video_id`、`mode`、`timems`、`bv`、`upload_time`。 |
| `tournament` | `tournament:normal` | hash | `field = tournament_id`；`value = CachedNormalTournament JSON`，包含 NORMAL 首页和 GSC 入口需要的概要信息。 |
| `tournament` | `tournament:normal:participants` | hash | `field = user_id`；`value = list[CachedNormalParticipant] JSON`，每项包含 `id`、`token`、`arbiter_identifier`、`tournament`、`start_time`、`end_time`。 |
| `common` | `api:common/videosummary` | Django cache | `video_summary` 返回体，TTL 300 秒。 |
| `common` | `api:common/tasksummary` | Django cache | `task_summary` 返回体，TTL 300 秒。 |
| `common` | `api:common/diskusage` | Django cache | `disk_usage` 返回体，TTL 300 秒。 |
| `article` | `articles` | list | 文章目录项字符串，来自 `assets/article` 或静态目录下的文章文件。 |

## 写入与重建入口

| 缓存 | 主要写入入口 | 重建 / 清理入口 |
| --- | --- | --- |
| 录像状态队列 | `videomanager.signals.refresh_state_queue_on_video_save` | `videomanager.cache.add_videos_to_state_queues_bulk` 可按状态批量恢复普通队列。 |
| 纪录新闻 | `msuser.signals.push_news_queue_on_record_save` | `videomanager.management.commands.refresh_stnb` 会清理 `news_queue`。 |
| 经典三关排行 | `UserMS.update_3_level_cache_record` | `UserMS.del_user_record_redis` 删除单个用户所有排行缓存；个人纪录重建后会重新写入。 |
| 自定义 pluck 排行 | `customranking.services.update_custom_pluck_top_cache` | `manage.py rebuild_custom_pluck_cache` 从 `CustomPluckRecord` 全量重建。 |
| NORMAL 比赛 | `TournamentCache.update_tournament` | `manage.py rebuild_tournament_cache` 从 `Tournament.objects.filter(state=NORMAL).select_subclasses()` 重建。 |
| NORMAL 参赛关系 | `TournamentCache.update_participant` / `remove_participant` | `manage.py rebuild_tournament_cache` 按 `user_id` 分组重建。 |
| common 摘要 | 对应 API 内部 `cache.set` | TTL 到期自动失效。 |
| 文章目录 | `article.views.update_list` | 管理员手动调用 `update_list` 全量刷新。 |

## 读取约定

- NORMAL 比赛列表只读 `tournament:normal`，不在缓存未命中时回落数据库；缓存与数据库不同步视为写路径 bug。
- 录像队列缓存不保存比赛录像，`VideoQueueCache.add` / `add_bulk` 会跳过 `ongoing_tournament=True` 的录像。
- 参赛 checkin 先读 `tournament:normal:participants`，命中后再按 tournament id 查询数据库对象，用于写入录像的多对多关系。
- `customranking:pluck:{level}:rank` 只保存排序所需数据，展示字段来自同级 `detail` hash。
- `player_rank` 的请求参数直接指定 Redis 排行 key 和详情 key；调用方必须保证 key 与 `UserMS.update_3_level_cache_record` 写入规则一致。
