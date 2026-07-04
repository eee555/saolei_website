# `pLuck`排行榜开发文档

## 缓存结构

每个自定义配置有四张缓存表：RANK、DETAIL、PLAYER、READY。RANK用于排序，DETAIL用于存储，PLAYER用于索引，READY用于标记表的状态。缓存由`cache.py`提供的`PLuckRankingCache`类管理。

RANK是有序集zset，排序键`score`是`pluck`。同`pluck`时，再比较`time`，同`time`时比较`upload_time`。为了解决后面两个比较，`timems`和`upload_time`分别以7位整数和13位整数连接起来作为zset的主键`member`。为了彻底解决主键冲突，`member`的结尾还加上了`player_id`。

DETAIL是查找表hset，主键是RANK的`member`，字段是`video_id`、`mode`、`bv`。其中`mode`和`bv`来自入榜录像。

PLAYER是hset，存储`player_id`到`member`的映射。

## 功能支持

### 数据结构转换
来自于数据库的`CustomPluckRecord`和来自于缓存的`member`、`DETAIL`需要相互转换。
- `CustomPluckRecord`转`member`：`get_custom_pluck_member`
- `CustomPluckRecord`转`DETAIL`：`serialize_custom_pluck_cache_detail`
- `member`转`CustomPluckRecord`：`parse_custom_pluck_member`
- `DETAIL`转`CustomPluckRecord`：`serialize_custom_pluck_cache_player`

### 缓存刷新
- 从数据库重建缓存：`build_custom_pluck_cache`
- 读取排行榜区间，缓存外部分回源数据库：`get_pluck_rank_range`
- 将一个新纪录加入缓存：`update_custom_pluck_top_cache`
- 从缓存中移除一个纪录：`update_custom_pluck_top_cache`

### 数据库刷新

数据库刷新时需要触发缓存刷新

- 刷新一个用户一个级别的纪录：`refresh_custom_pluck_rank`
- 接收到新录像时判断并加入纪录：`add_to_custom_pluck_rank`
- 将一个录像移出排行榜：`remove_from_custom_pluck_rank`
- 全库重建：`refresh_all_custom_pluck_ranks`

### 被动缓存刷新

单条`CustomPluckRecord`保存或删除时，通过`signal`刷新对应玩家的缓存。全库重建使用`bulk_create`生成数据库纪录，然后重新构建每个级别的完整缓存。
