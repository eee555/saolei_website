# 参与贡献

这篇文档面向刚开始学习编程、只上过学校编程课程的同学。你不需要一开始就理解整个网站，只要能完成一个小改动，并学会提交给我们，就已经是在参与开源贡献。

## 先从什么开始

最适合新手的贡献通常不是“大功能”，而是这些小任务：

- 修正文档错别字
- 补充一段使用说明
- 改进页面上的中文或英文文案
- 修复一个简单样式问题
- 补充一张截图
- 把自己遇到的问题整理成 Issue

暂时不建议一开始就修改登录、权限、录像审核、排行榜、比赛结算等复杂功能。

## 需要安装的软件

建议先安装这些工具：

| 软件 | 用途 |
| --- | --- |
| Git | 下载代码、保存修改 |
| VS Code | 编辑代码和文档 |
| Python | 运行后端 |
| Node.js | 运行前端和文档 |
| MySQL | 本地数据库 |
| Redis | 本地缓存 |

如果你只是修改文档，通常只需要：

- Git
- VS Code
- Node.js

## 下载代码

打开终端，选择一个放代码的目录，然后执行：

```bash
git clone https://github.com/eee555/saolei_website.git
cd saolei_website
```

如果你准备提交 Pull Request，建议先在 GitHub 网页上点击 **Fork**，再克隆你自己的仓库。

## 只修改文档

文档目录是：

```text
vitepress_doc
```

进入目录：

```bash
cd vitepress_doc
```

安装依赖：

```bash
npm install
```

启动文档网站：

```bash
npm run dev
```

浏览器打开：

```text
http://localhost:5173/docs/
```

修改 Markdown 文件后，浏览器通常会自动刷新。

提交前建议运行：

```bash
npm run build
```

如果构建成功，说明文档基本没有明显问题。

## 运行前端页面

如果你要修改网站页面，需要进入前端目录：

```bash
cd front_end
npm install
npm run dev
```

浏览器打开：

```text
http://localhost:8080
```

如果你只修改页面样式或普通文案，可以先连接线上服务器：

```bash
npm run frontend
```

这样可以少配置本地后端。

## 运行本地后端

如果你要修改接口、数据库、登录、录像上传等功能，需要运行后端。

进入后端目录：

```bash
cd back_end/saolei
```

创建虚拟环境：

```bash
python -m venv .venv
```

Windows 激活：

```bash
.\.venv\Scripts\activate
```

安装依赖：

```bash
pip install -r requirements.txt
```

准备好 MySQL 和 Redis 后，执行：

```bash
python manage.py makemigrations
python manage.py migrate userprofile
python manage.py migrate
python manage.py runserver --nostatic
```

后端默认地址是：

```text
http://127.0.0.1:8000
```

::: tip
本地后端配置比文档和前端更容易出问题。如果你只是想先做一次贡献，可以从文档或前端小改动开始。
:::

## 常用检查命令

文档：

```bash
cd vitepress_doc
npm run build
```

前端：

```bash
cd front_end
npm run lint
```

后端：

```bash
cd back_end/saolei
python manage.py check
```

不确定该运行什么时，可以在 PR 里说明：

```text
我修改了文档，只运行了 npm run build。
```

## 提交 Issue

Issue 用来报告问题或提出建议。

一个好的 Issue 可以包含：

- 你遇到的问题
- 你期望的结果
- 实际发生的结果
- 复现步骤
- 截图或报错

示例：

```text
标题：比赛页面的说明文字不够清楚

问题：
我第一次进入比赛页面时，不知道 Arbiter 标识应该在哪里填写。

期望：
希望文档或页面提示里说明操作位置。

截图：
……
```

## 提交 Pull Request

Pull Request 简称 PR，用来把你的修改提交给项目维护者审核。

基本流程：

1. Fork 仓库。
2. 克隆自己的仓库。
3. 新建一个分支。
4. 修改文件。
5. 本地检查。
6. 提交 commit。
7. 推送到 GitHub。
8. 在 GitHub 页面创建 PR。

常用命令：

```bash
git checkout -b docs/fix-guide
git status
git add vitepress_doc/guide/某个文件.md
git commit -m "docs: improve guide"
git push origin docs/fix-guide
```

PR 描述可以这样写：

```text
## 做了什么
- 修改比赛文档的说明文字

## 如何检查
- npm run build
```

## 如果被要求修改

维护者可能会在 PR 里留言，请你再改一点。这很正常，不代表你做得不好。

你只需要：

1. 在同一个分支继续修改。
2. 再次 commit。
3. 再次 push。

原来的 PR 会自动更新。

## 如何提问

提问时尽量带上这些信息：

- 你正在做什么
- 你执行了什么命令
- 报错的完整文字
- 你的系统，例如 Windows 11
- 你猜测问题可能在哪里

比起：

```text
运行不了，怎么办？
```

更推荐：

```text
我在 Windows 11 上运行 npm install 失败。
目录是 vitepress_doc。
报错最后几行是……
我不确定是不是 Node.js 版本太旧。
```

这样别人更容易帮你。

## 最重要的事

第一次贡献不需要很大。修一个错别字、补一句说明、提一个清楚的 Issue，都是有效贡献。

先完成一个小 PR，你就已经走进开源协作了。
