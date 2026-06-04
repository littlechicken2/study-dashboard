# Study Dashboard

轻量公开学习进度看板。公开数据只包含数字统计，不包含 Anki 卡片内容、本地路径或个人资料。

## 本地更新

```powershell
python .\scripts\collect_progress.py
python .\scripts\update_reading.py --questions 20 --correct 16 --minutes 35
```

安装自动更新器（登录 Windows 后启动，每小时采集并在有变化时推送）：

```powershell
powershell -ExecutionPolicy Bypass -File .\scripts\install_daily_update.ps1
```

课程播放器在本地服务器运行时，会将浏览器中的观看进度同步到 `data/course_progress.json`。

## GitHub Pages

将此目录推送到公开 GitHub 仓库，并在仓库设置的 Pages 中选择 `GitHub Actions`。此后本机计划任务会每日采集、提交并推送最新进度。
