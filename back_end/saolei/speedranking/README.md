# 竞速排行榜

本 app 不新增数据库模型。录像仍以 `VideoModel` 为事实来源，排行和个人纪录查询只读 Redis，不自动回源或重建。

## Saolei.wang 规则

这是竞速排行中的一套规则，并非所有大榜的默认规则。`speedranking` 和 `SpeedRanking.vue` 保留为通用入口；前端该规则使用 `SaoleiRanking.vue`、`SaoleiCard.vue`、`saoleiRankingService.ts` 及 `Saolei*` 类型。未来其他大榜应使用自己的专名，不必沿用下面的指标和纪录结构。

- `saolei` 接收 STD、OFFICIAL、`ongoing_tournament=False` 的普通三等级录像。
- `saolei_nf` 是独立榜，额外要求 `right_ce == 0`；未知值不属于 NF。标准榜也接收 NF 录像。
- Time 门槛：初级 3BV >= 2，中级 >= 30，高级 >= 100。3BV/s 门槛：初级 >= 4，中级 >= 30，高级 >= 100。
- 单项先比较成绩，再比较 `upload_time`，上传更早优先；3BV/s 同分不再比较 timems。
- `sumt` 缺项按 999999 毫秒补齐，`sumb` 缺项按 0 补齐。至少有一项有效纪录才进入总榜。
- 总分同分时，使用组成该总分的现有纪录中最晚的上传时间，即当前成绩组合的达成时间。
- `is_lucky` 当前不参与准入判断。头像和签名资格读取标准榜 `et < 200000`，因此包含高级 3BV >= 100 的门槛。

## 缓存

当前两个 Saolei.wang 榜各使用一个 `speedranking:{ranking_name}:records` hash，field 为玩家 id；JSON 包含八项成绩、六个录像 id 和内部 `_uploads` 排序时间。

zset 舍弃部分精度并限制数值范围，是为了简化缓存逻辑：将成绩与上传时间合并进一个 score 后，member 只需使用玩家 id，更新成绩可直接覆盖，无需查找、删除旧的复合 member。zset 仅作为排名和排名区间查询的索引，允许近似排序，不从 score 恢复数据用于纪录比较；hash 仍保存原始纪录，个人选优、补位及求和逻辑不受影响。

每项使用 `speedranking:{ranking_name}:{stat}` zset，member 只保存玩家 id。令 `M = 3_000_000_000`、`upload` 为 Unix UTC 分钟数：Time 的 score 为 `timems * M + upload`，3BV/s 为 `-bvs_units * M + upload`，其中 `bvs_units` 是以 0.0001 为单位的整数。统一升序读取，相同玩家由 ZADD 直接覆盖。不同玩家同分同分钟时不再按更细时间区分。

`0 <= upload < M`，约可覆盖 5700 年。单项单位值最多 999999，总项最多 2999997，因此所有 score 都在 double 的精确整数范围内。hash 中的成绩保留原始精度，内部 `_uploads` 保存 UTC 微秒时间戳，API 不暴露 `_uploads`。只在生成 score 时将 Bvs 四舍五入至四位小数、时间截断到分钟，总分在求和后量化。允许 zset 对极接近的成绩给出近似排序；增量选优、补位查询和批量重建仍按原始成绩、上传时间比较。

范围限制仅作用于 zset：Time 单项最多 999999 毫秒，Bvs 单项最多 99.9999；`sumt` 最多 2999997 毫秒，`sumb` 最多 299.9997。编码前按原始值判断，超限不写入对应 zset，并移除已有条目；恢复范围后可重新入榜。超限纪录照常参与个人选优、保存至 hash 和求和，不以较差的录像替代。总榜按总值独立判断，单项超限不一定导致总榜超限。

`SpeedRankingCache.update` 使用 WATCH/MULTI/EXEC 保护个人纪录的读改写及九个 key 的一致性。分页同样检测读取期间是否发生更新。不要在缓存类外直接修改这些 key。

## 写入与补位

- `post_save(VideoModel)` 复用 `videomanager` 的 `_old_values`，只对有关字段变化执行刷新；在事务提交后重新读取持久化的录像及派生 bvs。
- 成绩提高时直接比较缓存；变差或失去资格时，仅查询由该录像保持的单项并补位。
- 玩家或等级、模式、NF、审核状态、比赛隐藏状态改变时，旧分类补位，新分类尝试加入。
- `post_delete(VideoModel)` 仅补位被删除录像保持的单项；没有任何剩余纪录时删除玩家的 hash 和 zset 项。
- `add_videos_to_speed_ranks(queryset)` 支持标识绑定、比赛批量公开，在数据库按玩家和指标分桶取最佳。按玩家 id 分段以限制内存。
- `remove_videos_from_speed_ranks(queryset)` 用于批量失效后的补位，传入按录像 id 固定的 queryset，不要继续使用依赖旧状态的过滤条件。录像仍须存在；实际删除由删除信号处理。
- Redis 更新在 `transaction.on_commit` 执行，不参与数据库回滚。Redis 故障可能导致数据库已提交但榜单未同步，修复后应重建。全量重建期间暂停上传、审核、绑定、删除、比赛公开等写入。

## 重建与接口

```bash
python manage.py rebuild_speed_ranks
python manage.py rebuild_speed_ranks --ranking-name saolei_nf --batch-size 1000
```

命令构建独立临时榜，单个大榜构建成功后原子替换正式榜，最后清理临时 key。构建失败不会先清空正式榜；进程被强制终止时可能遗留 `speedranking:rebuild:*` 临时 key。两个大榜依次发布，并非同时切换。

从旧的“微秒时间戳 + 玩家 id” member 格式升级时，暂停相关读写，使用新代码执行 `python manage.py rebuild_speed_ranks`，完成两个大榜的重建后再恢复服务；不能混用新旧格式。无需修改录像数据库。

- `GET /api/speedranking/rank?ranking_name=saolei&stat=sumt&start=0&end=20`：左闭右开、最多 100 条，返回 `count` 和 `players`。
- `GET /api/speedranking/player/{player_id}`：一次返回 `saolei` 和 `saolei_nf`，每组包含原始纪录和八项 `ranks`。通过一次 Redis 事务 pipeline 读取 hash 和各 zset 的 ZRANK，排名从 1 开始，未入榜为 `null`（包括超限但仍保留原始成绩的情况）。无纪录也返回完整字段，单项为空、总项使用缺省值。
- 前端竞速榜使用 `ElTable` 和 `ElPagination`，通过 `start/end` 请求后端分页，并提供 NF checkbox；个人纪录使用原生 HTML table 和 Element Plus 配色，按初级、中级、高级、总和四列及 Time、Bvs、Time (NF)、Bvs (NF) 四行显示 `score(rank)`。旧新闻和姓名弹窗不恢复。

测试：`python manage.py test speedranking common.tests.VideoUploadRankingIntegrationTest identifier tournament --keepdb --noinput`。
