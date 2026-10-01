# 该APP仅作为测试用途，所有API需使用`@local_only`限制访问权限，且仅允许测试环境使用。

## 本地公开数据快照

- `public_snapshot.py`：导入及初始化编排，保留生产标记和本地测试环境检查。
- `download_public_data.py`：公开元数据快照下载入口，支持断点续传。
- `init_local_test.py`：本地快照导入及测试数据初始化入口，会清空本地数据库和对应 Redis 数据库。
- `cache.py`：本地快照的 Redis 检查与清理。
- `utils.py`：快照路径、JSON 读写及完整性校验，不依赖 Django 初始化。

两个入口均位于本 app 内，不在后端根目录保留转发脚本，也不注册管理命令，避免其他模块导入 `dangerzone`。在 `back_end/saolei` 目录使用模块方式运行，确保包导入和 Django 配置路径正确：

```bash
python -m dangerzone.download_public_data
python -m dangerzone.download_public_data --skip-details
python -m dangerzone.init_local_test
python -m dangerzone.init_local_test --no-weekly
```

默认数据目录仍为 `back_end/saolei/tmp/public-data`，不因入口迁移而改变。下载使用 `--output-dir`，导入使用 `--snapshot-dir` 指定其他目录。导入前停止本地 worker、定时任务及其他写入；生产标记和本地测试环境限制保持不变。

仅检查入口和静态安全限制，不下载数据或清库：

```bash
python -m dangerzone.download_public_data --help
python -m dangerzone.init_local_test --help
python -m pytest static_tests/
```
