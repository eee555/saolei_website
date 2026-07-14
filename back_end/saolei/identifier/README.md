# identifier 业务说明

本文档记录 `identifier` app 的业务约束和当前实现。标识绑定/解绑会影响录像状态和多个排行系统，修改相关逻辑前应先确认本文档仍符合目标业务。

## 业务约束

- `Identifier.identifier` 是只读业务字段。
  - 创建后不应修改。
  - 如果需要更名，应创建新 `Identifier`，并删除或解绑旧记录。
- `Identifier.userms` 只允许在空和非空之间转换。
  - `None -> UserMS`：绑定标识。
  - `UserMS -> None`：解绑标识。
  - `UserMS A -> UserMS B`：暂不支持，应拆成解绑 A 再绑定 B。
- `Identifier.safe=False` 时，`Identifier.userms` 必须为空。
  - 不安全标识不能绑定用户。
  - 如果安全标识需要重新判为不安全，管理员必须先解绑，再修改 `safe`。
- `UserMS.identifiers` 是面向用户的标识列表，应与 `Identifier.userms` 保持一致。

## 当前架构

标识绑定/解绑副作用由 `identifier.services` 显式处理，不再依赖 `Identifier` 的 `pre_save` / `post_save` / `post_delete` receiver。

- `identifier.signals` 只保留说明性空模块。
  - `IdentifierConfig.ready()` 仍可安全导入该模块。
  - 不应在这里恢复录像状态或排行刷新逻辑。
- 业务代码不应直接修改 `identifier.userms` 或手动维护 `userms.identifiers`。
  - 绑定统一调用 `bind_identifier(identifier, userms)`。
  - 解绑统一调用 `unbind_identifier(identifier, userms=None)`。
  - 修改审核状态统一调用 `set_safe(identifier, safe)`。

## 绑定流程

`bind_identifier(identifier, userms)` 负责 `None -> UserMS`。

前置检查：

- `identifier.safe` 必须为 `True`。
- 如果 `identifier.userms` 已绑定其他用户，直接抛错。

事务内操作：

- 将 `identifier.identifier` 加入 `userms.identifiers`。
- 设置 `identifier.userms = userms`。
- 查询该用户、该标识、状态为 `IDENTIFIER` 的录像。
- 使用 `queryset.update` 批量将这些录像改为 `OFFICIAL`。

批量更新后的显式补偿：

- 使用 `newest_cache.update_bulk` 更新已在 `newest_queue` 中的录像项。
- 调用 `msuser.services.update_personal_records_from_videos` 吸收新增官方录像对经典个人纪录的影响。
- 调用 `customranking.services.add_videos_to_custom_pluck_ranks` 吸收新增官方录像对自定义 pluck 纪录的影响。

## 解绑流程

`unbind_identifier(identifier, userms=None)` 负责 `UserMS -> None`。

前置检查：

- 如果未传入 `userms`，使用 `identifier.userms`。
- 标识必须处于已绑定状态。
- 如果传入的 `userms` 与当前绑定用户不一致，直接抛错。

事务内操作：

- 查询该用户、该标识、状态为 `OFFICIAL` 的录像。
- 在状态更新前，根据这些录像 id 找出当前 `UserMS` 中受影响的经典纪录字段。
- 将 `identifier.identifier` 从 `userms.identifiers` 移除。
- 设置 `identifier.userms = None`。
- 使用 `queryset.update` 批量将这些录像改为 `IDENTIFIER`。

批量更新后的显式补偿：

- 对内存中的录像对象同步设置 `state=IDENTIFIER`，再使用 `newest_cache.update_bulk` 更新已在 `newest_queue` 中的录像项。
- 调用 `customranking.services.remove_videos_from_custom_pluck_ranks` 刷新受影响的自定义 pluck 纪录。
- 调用 `msuser.services.rebuild_personal_records` 只重建受影响的经典个人纪录字段。

## 当前入口

- 用户绑定：`identifier.views.add_identifier`
- 用户解绑：`identifier.views.del_identifier`
- 管理员绑定：`identifier.views.staff_add_identifier`
- 管理员解绑或删除：`identifier.views.staff_del_identifier`
- 管理员过审：`identifier.views.staff_approve_identifier`
- GSC 报名自动绑定：`tournament.views.gsc.register_GSCParticipant`

这些入口应调用 `bind_identifier` / `unbind_identifier` / `set_safe`，不应直接写 `identifier.userms` 或 `identifier.safe`。

## 审核状态

`set_safe(identifier, safe)` 负责修改标识审核状态。

- `safe=True`：只修改审核状态，不自动绑定用户。
- `safe=False`：要求 `identifier.userms is None`，否则直接拒绝。
- 管理员如果需要将已绑定标识改为不安全，必须先调用解绑流程。

## 注意事项

- `queryset.update` 不触发 `VideoModel` 的 `pre_save` / `post_save`。
  - identifier service 使用批量更新时，必须同步补偿队列缓存和排行刷新。
- `newest_queue` 同时包含 `IDENTIFIER` 和 `OFFICIAL` 录像。
  - 绑定/解绑只需要更新已在缓存中的项，因此使用 `newest_cache.update_bulk`，不无条件新增。
- 如果某条录像没有进入 `newest_queue`，`update_bulk` 不会创建新缓存项。
- 解绑时只重建当前纪录指向被解绑录像的字段，避免全量重建。

## TODO

- 保护 `Identifier.identifier` 只读语义。
  - 当前模型层没有阻止修改 `identifier` 字段。
  - 可以在 service 层限制，也可以在模型保存时检测旧值并抛错。
- 补充接口级测试。
  - 当前已有 service/integration 覆盖绑定、解绑、经典纪录和 pluck 纪录刷新。
  - 仍可补充 view 层对冲突、未过审、不存在标识的响应测试。
