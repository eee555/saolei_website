# `pLuck`排行榜开发文档

## 缓存结构

每个自定义配置有三张缓存表：RANK、DETAIL、PLAYER。RANK用于排序，DETAIL用于存储，PLAYER用于索引。缓存由`cache.py`提供的`PLuckRankingCache`类管理。

RANK是有序集zset，排序键`score`是`pluck`。同`pluck`时，再比较`time`，同`time`时比较`upload_time`。为了解决后面两个比较，`timems`和`upload_time`分别以8位整数和13位整数连接起来作为zset的主键`member`。为了彻底解决主键冲突，`member`的结尾还加上了`player_id`。

DETAIL是查找表hset，主键是RANK的`member`，字段是`video_id`、`mode`、`bv`。其中`mode`和`bv`来自入榜录像。

PLAYER是hset，存储`player_id`到`member`的映射。

## 功能支持

### 数据结构转换
来自于数据库的`CustomPluckRecord`和来自于缓存的`member`、`DETAIL`需要相互转换。
- `CustomPluckRecord`转`member`：`record_to_member`
- `CustomPluckRecord`转`DETAIL`：`record_to_detail`
- `member`提取`player_id`：`member_to_player_id`
- 缓存转API字典：`cache_to_dict`

### 缓存刷新
- 清空缓存：`flush_custom_pluck_cache`
- 读取排行榜区间，缓存不足时回源数据库并自动补齐缓存：`get_pluck_rank_range`
- 将一个新纪录加入缓存：`update_custom_pluck_top_cache`
- 从缓存中移除一个纪录：`update_custom_pluck_top_cache`

### 数据库刷新

数据库刷新时需要触发缓存刷新

- 刷新一个用户一个级别的纪录：`refresh_custom_pluck_rank`
- 刷新一个玩家 id 区间内的纪录：`refresh_custom_pluck_rank_range`
- 接收到新录像时判断并加入纪录：`add_to_custom_pluck_rank`
- 将一个录像移出排行榜：`remove_from_custom_pluck_rank`
- 按玩家 id 分段刷新全库：`refresh_all_custom_pluck_ranks`

### 被动缓存刷新

单条`CustomPluckRecord`保存或删除时，通过`signal`刷新对应玩家的缓存。数据库刷新逐条保存纪录，不主动重建缓存；缓存为空或长度不足时，由用户请求通过`get_pluck_rank_range`自动回源并补齐。
