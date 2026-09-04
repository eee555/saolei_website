# 后端代码规范

后端位置：`back_end\saolei`。测试参考：
- linter：`.github\workflows\flake8.yml`
- 生产安全：`.github\workflows\BackendSafety.yml`
- 业务逻辑：`.github\workflows\backend.yml`

## API
项目里API分为旧的Django views和新的Ninja API。如需创建API，使用Ninja API。如需修改旧的Django views，直接迁移到Ninja API。

### Ninja API Schema
输出的Schema如果涉及到模型，优先使用`create_schema`生成。

## 换行约定
- 倾向不换行。一定不换行的场景：`import`。
- 一行的长度（除去开头的空格）至少达到80字符才需要考虑换行。例外：Python的后缀条件表达式中，如果有链式表达的嵌套逻辑，例如`[x for x in y if z]`或者`x = y if a else z`，则每层逻辑都需要换行。
- 换行后，倾向于将同类元素（如果顺序不重要）放在同一行。
- 不修改已经存在的代码的换行。
- 若flake8报错，则按照flake8的规则修改。

## 后台任务
后台任务，使用Django 6.0支持的Tasks，后端使用`django-tasks-db`。

## 模型字段定义修改
修改模型字段定义后，使用Django命令自动生成迁移脚本，禁止手动修改迁移脚本。如果某个需求必须手写迁移脚本，请先和用户沟通。

## 文档更新
API文档由Ninja API自动生成。

VitePress的更新需求：
- 数据库和缓存操作：`vitepress_doc\guide\development\cache.md`
- 管理命令：`vitepress_doc\guide\development\management-commands.md`
- 信号接收器：`vitepress_doc\guide\development\signals.md`

## APP结构

### 同APP
APP内引用链条：`utils -> models -> services -> api`
- `utils.py`存放APP专有的基础函数和常量。此文件不应当引入同APP的任何其他模块
- `services.py`存放涉及到模型的业务逻辑
- `api.py`存放Ninja API。
- 如果有其他APP的API需要用到的Schema，存放在`schema.py`
- 如果需要Redis缓存，缓存逻辑存放在`cache.py`
- 其他文件命名均使用一般的约定

### 跨APP
- 底层APP，仅提供常量配置和工具函数：`config`, `utils`。
- 基础APP，不引用任何其他APP的模型：`videomanager`, `userprofile`。注意：实际上`userprofile`引用了`msuser`，这是唯一的例外，属于历史遗留问题。
- 顶层APP，负责涉及面非常广的业务逻辑和API：`common`。
- 根APP：`saolei`。

禁止临时引用和循环引用。遇到此类问题时，首先考虑为架构设计问题，其次使用信号接收器，最后考虑用`common`APP。例外：属于common practice的情况，例如在`app.py`中临时引入signals的信号接收器。

# 前端代码规范

前端位置：`front_end`。测试参考
- linter：`.github\workflows\eslint.yml`
- ts模块：`.github\workflows\vitest.yml`
- vue组件：`.github\workflows\cypress.yml`
- e2e：`.github\workflows\CypressE2E.yml`

## 换行约定
- 数组、字典、html属性，倾向不换行。换行后，倾向于将同类元素（如果顺序不重要）放在同一行。
- 若eslint报错，则按照eslint的规则修改。

## 本地化
本地化有两种模式：全局本地化位于`front_end\src\i18n`，用于可复用的messages。不可复用的messages放在vue SFC内部，示例`front_end\src\components\ExperimentalFeature.vue`。注意：SFC内部的本地化尽量往`script`块的末尾放。

## 测试注意事项

### 本地化
测试不需要设置本地化语言。默认情况下，Cypress组件测试的语言为英文，E2E测试的语言为中文。

### 组件`PlayerName`
该组件用于渲染用户名字，其涉及到复杂的缓存逻辑，因此如果不需要测试其具体内容，应当用`cy.mockPlayerNameFallback()` stub相应的API。

### 临时组件
创建临时测试组件时，用`render`语法，不要用`template`。

# 前后端协调原则
这部分用于辅助思考，不属于强制规范。

- 后端服务器性能较差，带宽较低，单个请求返回体一般不要超过300KB。
- 前端设计上应该采用批量请求数据+本地计算的方式。
- 后端需要即时响应的业务逻辑，应当避免对于数据库的低效查询，这包括不必要的多次查询、对非索引列的排序。如需后端排序，考虑两个解决方案：添加索引、添加缓存。
