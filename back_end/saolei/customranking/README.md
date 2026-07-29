# `pLuck`排行榜开发文档

## 缓存结构

每个自定义配置有两张缓存表：RANK、DETAIL。RANK用于排序，DETAIL用于存储展示数据。缓存由`cache.py`提供的`PLuckRankingCache`类管理。

RANK是有序集zset，`member`直接使用`player_id`，因此同一用户天然去重。排序键`score`通常是`pluck`；当`pluck > 0`时`score = pluck`，当`pluck == 0`时`score = timems - MAX_TIMEMS`。这个规则放弃正数`pluck`碰撞时的严格 tie-breaker，但能处理最主要的`pluck == 0`碰撞风险。

DETAIL是查找表hset，主键是RANK的`member`，字段是API展示所需的`video_id`、`mode`、`pluck`、`timems`、`bv`、`upload_time`。

## 功能支持

### 数据结构转换
来自于数据库的`CustomPluckRecord`和来自于缓存的`member`、`DETAIL`需要相互转换。

### 信号机制实现数据同步
当`VideoModel`更新时，会尝试更新`CustomPluckRecord`。当`CustomPluckRecord`更新时，会将变化同步到缓存。

### 缓存接口
- 用户请求排行榜区间时只读取缓存，不回源数据库。
- 缓存不再限制长度，原则上缓存所有用户的`CustomPluckRecord`。
- 缓存需要重建时，使用管理命令`rebuild_custom_pluck_cache`从数据库全量灌入Redis；命令内部会先清空对应缓存再重建。

### 数据库刷新
`refresh_custom_pluck_rank_range`可以批量刷新指定用户的`CustomPluckRecord`
