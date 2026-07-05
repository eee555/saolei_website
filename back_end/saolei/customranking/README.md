# `pLuck`排行榜开发文档

## 缓存结构

每个自定义配置有三张缓存表：RANK、DETAIL、PLAYER。RANK用于排序，DETAIL用于存储，PLAYER用于索引。缓存由`cache.py`提供的`PLuckRankingCache`类管理。

RANK是有序集zset，排序键`score`是`pluck`。同`pluck`时，再比较`time`，同`time`时比较`upload_time`。为了解决后面两个比较，`timems`和`upload_time`分别以8位整数和13位整数连接起来作为zset的主键`member`。为了彻底解决主键冲突，`member`的结尾还加上了`player_id`。

DETAIL是查找表hset，主键是RANK的`member`，字段是`video_id`、`mode`、`bv`。其中`mode`和`bv`来自入榜录像。

PLAYER是hset，存储`player_id`到`member`的映射。

## 功能支持

### 数据结构转换
来自于数据库的`CustomPluckRecord`和来自于缓存的`member`、`DETAIL`需要相互转换。

### 信号机制实现数据同步
当`VideoModel`更新时，会尝试更新`CustomPluckRecord`。当`CustomPluckRecord`更新时，会将变化同步到缓存。

### 缓存接口
- 缓存不同步时，管理员可以操作清空缓存
- 用户请求排行榜区间时，先取缓存，缓存不足时回源数据库并自动补充缓存，最多补到缓存上限（当前100）。这个机制可以自动处理缓存不足的情况。
- 缓存超额时，`PLuckRankingCache.clamp`直接裁剪到上限。这个机制在缓存增加时自动执行。

### 数据库刷新
`refresh_custom_pluck_rank_range`可以批量刷新指定用户的`CustomPluckRecord`
