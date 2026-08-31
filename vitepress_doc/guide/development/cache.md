---
title: 缓存结构 - 开源扫雷网
description: 开源扫雷网Redis/Django缓存结构详解，包括录像队列、玩家排行、比赛缓存等数据结构和读写流向。
---

# 缓存结构

本文记录项目当前使用的 Redis / Django cache 结构，以及缓存与数据库、API 之间的读写流向。数据库字段结构以各 app 的 `models.py` 为准，这里只记录缓存中实际保存的数据结构。

## 总览

```dot
digraph cache {
    graph [
        layout=neato,
        model=subset,
        overlap=prism,
        splines=true,
        outputorder=edgesfirst,
        bgcolor="transparent",
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

    // Degree 较大的节点增大最小尺寸，减少 neato 布局中高密度连边贴边重叠。

    subgraph api_nodes {
        get_account_links [label="/api/accountlink/{user_id}"];
        create_account_link [label="/api/accountlink/create/"];
        delete_link [label="/accountlink/delete/"];
        update_link [label="/accountlink/update/"];
        view_saolei_import_one_video [label="/accountlink/saolei_import_video/"];
        view_saolei_import_videos [label="/accountlink/saolei_import_videos/"];
        view_saolei_get_import_list [label="/accountlink/saolei/videolist/get/"];
        view_saolei_get_import_summary [label="/accountlink/saolei/videoimport/stat/"];
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
        get_gsc_results [label="/api/tournament/gsc/results"];
        create_gsc_participant [label="/api/tournament/gsc/participant"];
        register_gsc_participant_identifier [label="/api/tournament/gsc/participant/identifier"];
        get_weekly_results [label="/api/tournament/weekly/results"];
        create_weekly_participant [label="/api/tournament/weekly/participant"];
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
    }

    subgraph db_nodes {
        node [shape=cylinder, fillcolor="${#e0f2fe|#0f172a}"];
        captcha_db [label="CaptchaStore"];
        task_db [label="DBTaskResult", width=2.0, height=0.8];
        accountlinkqueue_db [label="AccountLinkQueue\nplatform accounts"];
        accountlinkplatform_db [label="AccountSaolei\nAccountMinesweeperGames\nAccountBilibili\nAccountWorldOfMinesweeper\nAccountQQ", width=3.0, height=1.4];
        videosaolei_db [label="VideoSaolei"];
        custom_pluck_db [label="CustomPluckRecord"];
        identifier_db [label="Identifier"];
        userms_db [label="UserMS", width=3, height=3, fontsize=30];
        tournament_db [label="Tournament\nGSCTournament\nWeeklyTournament", width=2.5, height=1.1];
        participant_db [label="TournamentParticipant\nGSCParticipant\nWeeklyParticipant", width=2.8, height=1.1];
        tournament_user_db [label="TournamentUser", width=2.2, height=0.8];
        userprofile_db [label="UserProfile", width=4, height=4, fontsize=40];
        email_otp_db [label="EmailVerifyRecord"]
        video_db [label="VideoModel\nExpandVideoModel", width=4, height=4, fontsize=30];
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
        news_cache [label="news_queue\nzset", width=1.8, height=0.8];
        player_record_cache [label="player_{stat}_{mode}_{user_id}\nhash", width=2.8, height=0.9];
        player_rank_cache [label="player_{stat}_{mode}_ids\nzset", width=2.5, height=0.9];
        tournament_cache [label="tournament:normal\nhash\nsubclass + data", width=2.6, height=1.0];
        participant_cache [label="tournament:normal:participants\nhash", width=3.2, height=0.9];
        common_summary_cache [label="api:common/*\nTTL 300s"];
    }

    subgraph file_nodes {
        node [shape=folder, fillcolor="${#e0f2fe|#0f172a}"];
        video_files [label="video files"];
        avatar_files [label="avatar files"];
    }

    subgraph signal_nodes {
        node [
            shape=box,
            fillcolor="${#fef3c7|#713f12}",
            color="${#f59e0b|#d97706}"
        ];
        capture_video_update [label="capture_video_update"];
        refresh_state_queue_on_video_save [label="refresh_state_queue_on_video_save"];
        update_video_count_on_video_save [label="update_video_count_on_video_save"];
        update_video_count_limit_on_video_save [label="update_video_count_limit_on_video_save"];
        update_video_count_on_video_delete [label="update_video_count_on_video_delete"];
        capture_previous_records_for_news_queue [label="capture_previous_records_for_news_queue"];
        push_news_queue_on_record_save [label="push_news_queue_on_record_save"];
        refresh_personal_record_on_video_save [label="refresh_personal_record_on_video_save"];
        refresh_personal_record_on_video_delete [label="refresh_personal_record_on_video_delete"];
        refresh_custom_pluck_rank_on_video_save [label="refresh_custom_pluck_rank_on_video_save"];
        update_custom_pluck_cache_on_record_save [label="update_custom_pluck_cache_on_record_save"];
        update_custom_pluck_cache_on_record_delete [label="update_custom_pluck_cache_on_record_delete"];
        checkin_video_before_create [label="checkin_video_before_create"];
        add_created_video_to_checked_tournaments [label="add_created_video_to_checked_tournaments"];
        update_cache_on_tournament_delete [label="update_cache_on_tournament_delete"];
        update_cache_on_tournament_save [label="update_cache_on_tournament_save"];
        update_cache_on_participant_save [label="update_cache_on_participant_save"];
        update_best_score_on_gsc_participant_save [label="update_best_score_on_gsc_participant_save", width=3.4, height=0.8];
        update_best_score_on_weekly_participant_save [label="update_best_score_on_weekly_participant_save", width=3.7, height=0.8];
        update_best_score_on_gsc_participant_delete [label="update_best_score_on_gsc_participant_delete", width=3.5, height=0.8];
        update_best_score_on_weekly_participant_delete [label="update_best_score_on_weekly_participant_delete", width=3.8, height=0.8];
        remove_participant_cache_on_delete [label="remove_participant_cache_on_delete"];
    }

    subgraph task_nodes {
        node [
            shape=box,
            fillcolor="${#ede9fe|#4c1d95}",
            color="${#8b5cf6|#a78bfa}"
        ];
        task_saolei_video_import_bulk [label="task_saolei_video_import_bulk"];
        task_saolei_video_import [label="task_saolei_video_import"];
        task_gsc_finish [label="task_gsc_finish"];
        task_weekly_finish [label="task_weekly_finish"];
    }

    // accountlink API
    accountlinkqueue_db -> get_account_links;
    accountlinkplatform_db -> get_account_links;
    create_account_link -> accountlinkqueue_db;
    accountlinkqueue_db -> delete_link;
    delete_link -> accountlinkqueue_db;
    delete_link -> accountlinkplatform_db;
    accountlinkplatform_db -> update_link;
    update_link -> accountlinkplatform_db;
    videosaolei_db -> view_saolei_import_one_video;
    accountlinkplatform_db -> view_saolei_import_one_video;
    task_db -> view_saolei_import_one_video;
    video_db -> view_saolei_import_one_video;
    video_files -> view_saolei_import_one_video;
    view_saolei_import_one_video -> task_db;
    view_saolei_import_one_video -> videosaolei_db;
    view_saolei_import_one_video -> video_db;
    view_saolei_import_one_video -> video_files;
    accountlinkplatform_db -> view_saolei_import_videos;
    videosaolei_db -> view_saolei_import_videos;
    task_db -> view_saolei_import_videos;
    view_saolei_import_videos -> task_db [label="enqueue/delete"];
    view_saolei_import_videos -> accountlinkplatform_db;
    view_saolei_import_videos -> task_saolei_video_import_bulk [label="enqueue"];
    task_db -> task_saolei_video_import_bulk [label="read/delete"];
    accountlinkplatform_db -> task_saolei_video_import_bulk [label="read"];
    videosaolei_db -> task_saolei_video_import_bulk [label="read/write"];
    task_saolei_video_import_bulk -> videosaolei_db [label="write"];
    task_saolei_video_import_bulk -> task_db [label="enqueue/delete"];
    task_saolei_video_import_bulk -> task_saolei_video_import [label="enqueue each"];
    task_db -> task_saolei_video_import [label="status/read"];
    videosaolei_db -> task_saolei_video_import [label="read"];
    accountlinkplatform_db -> task_saolei_video_import [label="FK read"];
    userprofile_db -> task_saolei_video_import [label="O2O read"];
    userms_db -> task_saolei_video_import [label="O2O read"];
    identifier_db -> task_saolei_video_import [label="read"];
    video_db -> task_saolei_video_import [label="collision/read"];
    video_files -> task_saolei_video_import [label="read"];
    task_saolei_video_import -> task_db [label="status write"];
    task_saolei_video_import -> videosaolei_db [label="write"];
    task_saolei_video_import -> userms_db [label="create"];
    task_saolei_video_import -> video_db [label="write"];
    task_saolei_video_import -> video_files [label="write"];
    userprofile_db -> view_saolei_get_import_list;
    accountlinkplatform_db -> view_saolei_get_import_list;
    videosaolei_db -> view_saolei_get_import_list;
    task_db -> view_saolei_get_import_list;
    accountlinkplatform_db -> view_saolei_get_import_summary;
    videosaolei_db -> view_saolei_get_import_summary;
    task_db -> view_saolei_get_import_summary;

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
    identifier_db -> get_participant_list;
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
    tournament_db -> get_gsc_results;
    participant_db -> get_gsc_results;
    userprofile_db -> get_gsc_results;
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

    // tournament weekly API
    tournament_db -> get_weekly_results;
    participant_db -> get_weekly_results;
    tournament_db -> create_weekly_participant;
    userprofile_db -> create_weekly_participant;
    create_weekly_participant -> participant_db;

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

    // tournament finish tasks
    task_db -> task_gsc_finish [label="status/read"];
    tournament_db -> task_gsc_finish [label="read/write"];
    participant_db -> task_gsc_finish [label="read/write/delete"];
    video_db -> task_gsc_finish [label="read/write"];
    tournament_user_db -> task_gsc_finish [label="read/decay"];
    task_gsc_finish -> participant_db [label="score/rank/award"];
    task_gsc_finish -> tournament_db [label="state write"];
    task_gsc_finish -> tournament_user_db [label="award/decay"];
    task_gsc_finish -> newest_cache [label="restore queues"];
    task_gsc_finish -> freeze_cache [label="restore queues"];
    task_gsc_finish -> review_cache [label="restore queues"];
    task_gsc_finish -> player_record_cache [label="restore records"];
    task_gsc_finish -> player_rank_cache [label="restore records"];
    task_gsc_finish -> pluck_rank_cache [label="restore pluck"];
    task_gsc_finish -> pluck_detail_cache [label="restore pluck"];

    task_db -> task_weekly_finish [label="status/read"];
    tournament_db -> task_weekly_finish [label="read/write"];
    participant_db -> task_weekly_finish [label="read/write/delete"];
    video_db -> task_weekly_finish [label="read/write"];
    tournament_user_db -> task_weekly_finish [label="read/decay"];
    task_weekly_finish -> participant_db [label="score/rank/award"];
    task_weekly_finish -> tournament_db [label="state write"];
    task_weekly_finish -> tournament_user_db [label="award/decay"];
    task_weekly_finish -> newest_cache [label="restore queues"];
    task_weekly_finish -> freeze_cache [label="restore queues"];
    task_weekly_finish -> review_cache [label="restore queues"];
    task_weekly_finish -> player_record_cache [label="restore records"];
    task_weekly_finish -> player_rank_cache [label="restore records"];
    task_weekly_finish -> pluck_rank_cache [label="restore pluck"];
    task_weekly_finish -> pluck_detail_cache [label="restore pluck"];

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

    // videomanager signals
    video_db -> capture_video_update [label="pre_save"];
    video_db -> capture_video_update [label="read"];
    video_db -> refresh_state_queue_on_video_save [label="post_save"];
    video_db -> refresh_state_queue_on_video_save [label="O2O read"];
    userprofile_db -> refresh_state_queue_on_video_save [label="FK read"];
    refresh_state_queue_on_video_save -> newest_cache [label="write/delete"];
    refresh_state_queue_on_video_save -> freeze_cache [label="write/delete"];
    refresh_state_queue_on_video_save -> review_cache [label="write/delete"];

    // msuser signals
    video_db -> update_video_count_on_video_save [label="post_save"];
    userprofile_db -> update_video_count_on_video_save [label="FK read"];
    userms_db -> update_video_count_on_video_save [label="O2O read"];
    update_video_count_on_video_save -> userms_db [label="write"];

    video_db -> update_video_count_limit_on_video_save [label="post_save"];
    userprofile_db -> update_video_count_limit_on_video_save [label="FK read"];
    userms_db -> update_video_count_limit_on_video_save [label="O2O read"];
    update_video_count_limit_on_video_save -> userms_db [label="write"];

    video_db -> update_video_count_on_video_delete [label="post_delete"];
    userprofile_db -> update_video_count_on_video_delete [label="FK read"];
    userms_db -> update_video_count_on_video_delete [label="O2O read"];
    update_video_count_on_video_delete -> userms_db [label="write"];

    userms_db -> capture_previous_records_for_news_queue [label="pre_save"];
    userms_db -> capture_previous_records_for_news_queue [label="read"];

    userms_db -> push_news_queue_on_record_save [label="post_save"];
    userprofile_db -> push_news_queue_on_record_save [label="reverse O2O read"];
    news_cache -> push_news_queue_on_record_save [label="read size"];
    push_news_queue_on_record_save -> news_cache [label="write/trim"];

    video_db -> refresh_personal_record_on_video_save [label="post_save"];
    video_db -> refresh_personal_record_on_video_save [label="read/refresh"];
    userprofile_db -> refresh_personal_record_on_video_save [label="FK/query read"];
    userms_db -> refresh_personal_record_on_video_save [label="O2O read"];
    refresh_personal_record_on_video_save -> userms_db [label="write"];
    refresh_personal_record_on_video_save -> player_record_cache [label="write"];
    refresh_personal_record_on_video_save -> player_rank_cache [label="write"];

    video_db -> refresh_personal_record_on_video_delete [label="post_delete"];
    video_db -> refresh_personal_record_on_video_delete [label="read best"];
    userprofile_db -> refresh_personal_record_on_video_delete [label="FK read"];
    userms_db -> refresh_personal_record_on_video_delete [label="O2O read"];
    refresh_personal_record_on_video_delete -> userms_db [label="write"];
    refresh_personal_record_on_video_delete -> player_record_cache [label="write"];
    refresh_personal_record_on_video_delete -> player_rank_cache [label="write"];

    // customranking signals
    video_db -> refresh_custom_pluck_rank_on_video_save [label="post_save"];
    video_db -> refresh_custom_pluck_rank_on_video_save [label="read best"];
    userprofile_db -> refresh_custom_pluck_rank_on_video_save [label="FK read"];
    custom_pluck_db -> refresh_custom_pluck_rank_on_video_save [label="read"];
    refresh_custom_pluck_rank_on_video_save -> custom_pluck_db [label="write/delete"];

    custom_pluck_db -> update_custom_pluck_cache_on_record_save [label="post_save"];
    video_db -> update_custom_pluck_cache_on_record_save [label="FK read"];
    update_custom_pluck_cache_on_record_save -> pluck_rank_cache [label="write"];
    update_custom_pluck_cache_on_record_save -> pluck_detail_cache [label="write"];

    custom_pluck_db -> update_custom_pluck_cache_on_record_delete [label="post_delete"];
    update_custom_pluck_cache_on_record_delete -> pluck_rank_cache [label="delete"];
    update_custom_pluck_cache_on_record_delete -> pluck_detail_cache [label="delete"];

    // tournament signals
    video_db -> checkin_video_before_create [label="pre_save"];
    video_db -> checkin_video_before_create [label="O2O read"];
    participant_cache -> checkin_video_before_create [label="read"];
    tournament_db -> checkin_video_before_create [label="query read"];
    checkin_video_before_create -> video_db [label="write field"];

    video_db -> add_created_video_to_checked_tournaments [label="post_save"];
    add_created_video_to_checked_tournaments -> tournament_db [label="m2m write"];

    tournament_db -> update_cache_on_tournament_delete [label="post_delete"];
    update_cache_on_tournament_delete -> tournament_cache [label="delete"];
    participant_cache -> update_cache_on_tournament_delete [label="scan/read"];
    update_cache_on_tournament_delete -> participant_cache [label="write/delete"];

    tournament_db -> update_cache_on_tournament_save [label="post_save"];
    tournament_db -> update_cache_on_tournament_save [label="subclass read"];
    update_cache_on_tournament_save -> tournament_cache [label="write/delete"];
    participant_cache -> update_cache_on_tournament_save [label="scan/read"];
    update_cache_on_tournament_save -> participant_cache [label="write/delete"];

    participant_db -> update_cache_on_participant_save [label="post_save"];
    participant_cache -> update_cache_on_participant_save [label="read"];
    tournament_db -> update_cache_on_participant_save [label="FK/m2m read"];
    identifier_db -> update_cache_on_participant_save [label="FK read"];
    video_db -> update_cache_on_participant_save [label="query read"];
    update_cache_on_participant_save -> participant_cache [label="write/delete"];
    update_cache_on_participant_save -> tournament_db [label="m2m write"];

    participant_db -> update_best_score_on_gsc_participant_save [label="post_save"];
    tournament_db -> update_best_score_on_gsc_participant_save [label="FK/subclass read"];
    tournament_user_db -> update_best_score_on_gsc_participant_save [label="read/create"];
    update_best_score_on_gsc_participant_save -> tournament_user_db [label="write best"];

    participant_db -> update_best_score_on_weekly_participant_save [label="post_save"];
    tournament_db -> update_best_score_on_weekly_participant_save [label="FK/subclass read"];
    tournament_user_db -> update_best_score_on_weekly_participant_save [label="read/create"];
    update_best_score_on_weekly_participant_save -> tournament_user_db [label="write best"];

    participant_db -> update_best_score_on_gsc_participant_delete [label="post_delete"];
    participant_db -> update_best_score_on_gsc_participant_delete [label="query best"];
    tournament_db -> update_best_score_on_gsc_participant_delete [label="FK/subclass read"];
    tournament_user_db -> update_best_score_on_gsc_participant_delete [label="read"];
    update_best_score_on_gsc_participant_delete -> tournament_user_db [label="write best"];

    participant_db -> update_best_score_on_weekly_participant_delete [label="post_delete"];
    participant_db -> update_best_score_on_weekly_participant_delete [label="query best"];
    tournament_db -> update_best_score_on_weekly_participant_delete [label="FK/subclass read"];
    tournament_user_db -> update_best_score_on_weekly_participant_delete [label="read"];
    update_best_score_on_weekly_participant_delete -> tournament_user_db [label="write best"];

    participant_db -> remove_participant_cache_on_delete [label="post_delete"];
    participant_cache -> remove_participant_cache_on_delete [label="read"];
    remove_participant_cache_on_delete -> participant_cache [label="write/delete"];
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
| `tournament` | `tournament:normal` | hash | `field = tournament_id`；`value = CachedTournament JSON`，包含 `id`、`state`、`subclass`、`host_id`、`start_time`、`end_time`、`data`。`data` 保存子类独占字段：GSC 为 `order`、`token`；周赛为 `year`、`week`、`tournament_format`。 |
| `tournament` | `tournament:normal:participants` | hash | `field = user_id`；`value = list[CachedNormalParticipant] JSON`，每项包含 `id`、`token`、`arbiter_identifier`、`tournament`、`start_time`、`end_time`。 |
| `common` | `api:common/videosummary` | Django cache | `video_summary` 返回体，TTL 300 秒。 |
| `common` | `api:common/tasksummary` | Django cache | `task_summary` 返回体，TTL 300 秒。 |
| `common` | `api:common/diskusage` | Django cache | `disk_usage` 返回体，TTL 300 秒。 |
| `article` | `articles` | list | 文章目录项字符串，来自 `assets/article` 或静态目录下的文章文件。 |

`TournamentUser` 是比赛积分的持久化汇总表，不是缓存。站内用户创建 `TournamentParticipant` / `GSCParticipant` / `WeeklyParticipant` 时，保存信号会在当前数据库事务内立即创建缺失的 `TournamentUser`；删除 participant 不会跟随删除 `TournamentUser`。GSC / 周赛 finish 任务会先调用 `delete_participants_without_videos` 删除无录像站内 participant。排名积分发放和 best 刷新是独立的非关键后台任务，会各自从本场剩余站内 participant 出发，通过 `participant.user.tournamentuser` 取得对应的 `TournamentUser`，并使用 `select_related('user__tournamentuser')` 避免 N+1。积分发放任务读取并衰减既有 `TournamentUser.score_current`，再根据本场 participant 的 `rank_score` 增量写回 `TournamentUser` 和 `TournamentParticipant.rank_score`。历史最好成绩在 participant 保存后只读取当前 participant 和对应比赛子表，并与 `TournamentUser.gsc_best` / `weekly_classic_best` 直接比较；只有当前成绩更好时才改变内存值。结算流程使用 `bulk_update` 写入 `rank_score`，不会触发保存信号，因此 best 刷新通过 `refresh_gsc_best_scores` / `refresh_weekly_best_scores` 作为独立后台任务执行；best 与排名积分发放没有顺序依赖。为了简化结算代码，积分发放和 best 刷新都不筛选字段是否发生变化，会统一 `bulk_update` 候选 participant 和对应 `TournamentUser`。结算链路通过 `tournament` logger 写入 `logs/tournament.log`，记录后台任务、删除无录像 participant、读取 `TournamentUser`、成绩/排名刷新、积分发放、best 刷新、状态切换和录像公开等阶段的处理数量。没有有效历史成绩时，best 字段使用 `MAX_TOURNAMENT_BEST` 作为哨兵值。participant 删除时，GSC / 周赛各自的信号会在当前事务内按需调用 `calculate_gsc_best_score` / `calculate_weekly_classic_best` 重算该类型历史最好成绩。由于 `TournamentUser` 是数据库汇总数据，participant 信号触发的创建和 best 更新必须在当前事务内立即执行，不使用 `transaction.on_commit`。如果需要修复历史汇总数据，尤其是把旧的 `0` best 值迁移到新的最大值哨兵，可以运行 `manage.py refresh_tournament_user_stats`。该命令会先调用 `tournament.services.refresh_tournament_user_total_fields` 重建 `score_total`、`gsc_total`、`weekly_total` 和 `weekly_classic_total`，再执行命令内的 best 重建步骤写回 `gsc_best` 和 `weekly_classic_best`；`score_current` 依赖实时衰减，不由该命令刷新。

`GSCParticipant.t37` 是数据库持久化 generated field，并建立 `gsc_t37_idx` 索引，服务于 GSC 排名和历史最好成绩查询。保存信号使用当前 participant 实例上的临时 `t37` 值进行 best 增量比较，因此不会为了读取 generated field 再查询一次 participant。

## 写入与重建入口

| 缓存 | 主要写入入口 | 重建 / 清理入口 |
| --- | --- | --- |
| 录像状态队列 | `videomanager.signals.refresh_state_queue_on_video_save` | `videomanager.cache.add_videos_to_state_queues_bulk` 可按状态批量恢复普通队列。 |
| 纪录新闻 | `msuser.signals.push_news_queue_on_record_save` | `videomanager.management.commands.refresh_stnb` 会清理 `news_queue`。 |
| 经典三关排行 | `UserMS.update_3_level_cache_record` | `UserMS.del_user_record_redis` 删除单个用户所有排行缓存；个人纪录重建后会重新写入。 |
| 自定义 pluck 排行 | `customranking.services.update_custom_pluck_top_cache` | `manage.py rebuild_custom_pluck_cache` 从 `CustomPluckRecord` 全量重建。 |
| NORMAL 比赛 | `TournamentCache.update_tournament` | `manage.py rebuild_tournament_cache` 显式查询 `NORMAL` GSC 与周赛并重建。 |
| NORMAL 参赛关系 | `TournamentCache.update_participant` / `remove_participant` | `manage.py rebuild_tournament_cache` 按 `user_id` 分组重建。 |
| common 摘要 | 对应 API 内部 `cache.set` | TTL 到期自动失效。 |
| 文章目录 | `article.views.update_list` | 管理员手动调用 `update_list` 全量刷新。 |

## 读取约定

- NORMAL 比赛列表只读 `tournament:normal`，不在缓存未命中时回落数据库；缓存与数据库不同步视为写路径 bug。
- 录像队列缓存不保存比赛录像，`VideoQueueCache.add` / `add_bulk` 会跳过 `ongoing_tournament=True` 的录像。
- 参赛 checkin 先读 `tournament:normal:participants`，命中后再按 tournament id 查询数据库对象，用于写入录像的多对多关系。
- `customranking:pluck:{level}:rank` 只保存排序所需数据，展示字段来自同级 `detail` hash。
- `player_rank` 的请求参数直接指定 Redis 排行 key 和详情 key；调用方必须保证 key 与 `UserMS.update_3_level_cache_record` 写入规则一致。
