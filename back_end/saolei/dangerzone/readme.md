# 该APP仅作为测试用途，所有API需使用`@local_only`限制访问权限，且仅允许测试环境使用。

## 本地公开数据快照

- `public_snapshot.py`：导入及初始化编排，保留生产标记和本地测试环境检查。
- `cache.py`：本地快照的 Redis 检查与清理。
- `utils.py`：快照路径、JSON 读写及完整性校验，不依赖 Django 初始化。
- `test_public_snapshot.py`：下载、导入及安全限制测试。

后端根目录的 `download_public_data.py` 和 `init_local_test.py` 保留为脚本入口，不注册管理命令。默认数据目录仍为 `back_end/saolei/tmp/public-data`。

测试命令：`python manage.py test dangerzone.test_public_snapshot`。
