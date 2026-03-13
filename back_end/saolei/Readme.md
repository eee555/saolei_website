- `config`：一些全局配置
  - `global_settings`：全局常量
  - `messages`：常用报错信息
- `msuser`：用户的扫雷数据库
- `saolei`：根
- `userprofile`：用户的账号信息库
- `utils`：和数据库无关的功能函数
- `videomanager`：录像数据库

# API索引
|API|类型|需要登录|管理员|限流|
|---|---|---|---|---|
|`common/uploadvideo/`|POST|是|否|5/s|
|`common/tasksummary/`|GET|否|否|1/5s|
|`accountlink/add/`|POST|是|否|10/d|
|`accountlink/delete/`|POST|是|否|-|
|`accountlink/get/`|GET|否|否|-|
|`accountlink/update/`|POST|是|否|6/h|
|`accountlink/verify/`|POST|是|是|-|
|`accountlink/unverify/`|POST|是|是|-|
|`accountlink/saolei_import_video/`|POST|是|否|-|
|`accountlink/saolei_import_videos/`|POST|是|否|-|


## `common`

### `uploadvideo`：上传录像
- POST
- 需要登录
- 每秒最多5次

## `accountlink`：第三方平台账号关联

### `Platform`：平台枚举
- `"a"` - 国际网
- `"c"` - 扫雷网
- `"q"` - QQ，隐私
- `"w"` - wom

### `add`：添加账号关联
- POST|需要登录|每个用户每天最多10次
- `platform`：`Platform`，必选
- `identifier`：平台ID，必选

- 返回`HttpResponseBadRequest`：参数缺失
- 返回`HttpResponseConflict`：已绑定账号
- 返回`HttpResponse`：操作成功

### `delete`：删除账号关联
- POST|需要登录
- `platform`：`Platform`，必选

- 返回`HttpResponseBadRequest`：参数缺失
- 返回`HttpResponseNotFound`：未关联账号
- 返回`HttpResponse`：操作成功

### `get`：查询账号关联数据
- GET
- `id`：用户ID，必选
- `platform`：`Platform`，可选。若有该参数，查询对应的关联账号的详细数据。若无该参数，查询用户所有关联账号的平台和ID。

普通用户不能查询其他用户的隐私/未审核账号。管理员可以查询所有用户的隐私/未审核账号，普通用户可以查询自己的隐私/未审核账号。

- 返回`HttpResponseBadRequest`：参数缺失
- 返回`HttpResponseNotFound`：未找到用户
- 返回`HttpResponseForbidden`：试图越权查询隐私账号
- 返回`JsonResponse`：
  - 有`platform`参数时，返回一个instance的Dict
  - 无`platform`参数时，返回一个`list[{platform, identifier}]`。如果有权限访问未审核账号，则还加一个`verified`。

### `update`：同步账号数据
- POST|需要登录|每个用户每小时最多6次
- `platform`：`Platform`，必选

- 返回`HttpResponseBadRequest`：参数缺失
- 返回`JsonResponse`
  - `{type: 'success'}`：操作成功
  - `{type: 'error', object: 'import', category: 'timeout'}`：第三方网站响应超时
  - `{type: 'error', object: 'import', category: 'indexerror'}`：HTML解析错误
  - `{type: 'error', object: 'import', category: 'requestexception'}`：请求返回`RequestException`
  - `{type: 'error', object: 'import', category: 'cooldown'}`：还在冷却中（12小时）
  - `{type: 'error', object: 'import', category: 'pageempty'}`：页面为空

### `saolei_import_video`：导入一个扫雷网录像
- POST|需要登录
- `video_id`：录像ID，必选

删除后台任务，直接导入这个录像。

- 返回`HttpResponseBadRequest`：参数缺失
- 返回`HttpResponseNotFound`：该录像未留档
- 返回`HttpResponseForbidden`：试图导入其他用户的录像
- 返回`HttpResponseConflict`：后台任务正在运行中
- 返回`JsonResponse`
  - `{type: 'success', import_video__id}`：导入成功
  - `{type: 'error', object: 'import', category: 'connection'}`：无法连接到扫雷网
  - `{type: 'error', object: 'import', category: 'timeout'}`：下载超时
  - `{type: 'error', object: 'import', category: 'unknown'}`：未知错误

### `saolei_import_videos`：批量导入扫雷网录像
- POST|需要登录
- `mode`：`"all"`或`"new"`，必选。`"all"`表示扫描所有页面，`"new"`表示扫描到没有新录像为止

- 返回`HttpResponseBadRequest`：参数缺失
- 返回`HttpResponseForbidden`：用户没有关联扫雷网账号
- 返回`HttpResponseConflict`：用户已经有了一个批量导入任务在排队或进行中
- 返回`HttpResponse`：成功创建批量导入任务

### `saolei/videolist/get/`：查询扫雷网录像列表
- GET|每个IP每秒1次
- `user_id`、`saolei_id`：用户ID和扫雷网ID。可选其一，不可同时存在。建议要选该参数，否则数据量可能太大。

- 返回`HttpResponseBadRequest`：`user_id`和`saolei_id`同时存在
- 返回`HttpResponseNotFound`：查询不到用户
- 返回`JsonResponse`：`list[{id, user__id, upload_time, level, bv, timems, nf, state, import_video__id, import_task__status}]`
