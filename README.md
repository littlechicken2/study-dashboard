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

安装器还会在登录 Windows 时恢复上次 Chrome 会话，并额外打开公开学习监督台。
每次开机登录时，TCF 阅读会以关机前的累计题数建立新基线；监督台只统计本次开机后新增完成的题目。

## 有效学习时长

开机启动器会运行桌面 watcher：Anki 前台且 60 秒内有输入计入 Verb，Adobe Acrobat 前台计入 Grammar。Chrome 扩展会记录 TCF 阅读、本地课程/PDF、ChatGPT 的有效前台时间；Bilibili、YouTube、抖音会暂停计时并显示警告。更新扩展代码后，需要在 `chrome://extensions` 点击扩展的刷新按钮。

手机网页只能检测当前学习网页是否可见；无法检测手机上其他 App（Bilibili/YouTube/抖音）的前台状态。手机端娱乐 App 拦截需要使用系统屏幕使用时间、数字健康、专注模式或网络层工具。

课程播放器在本地服务器运行时，会将浏览器中的观看进度同步到 `data/course_progress.json`。

## TCF 阅读自动同步

Chrome 扩展目录为 `tcf-progress-extension`。在 `chrome://extensions` 开启开发者模式，选择“加载已解压的扩展程序”，加载该目录。之后打开 `tcfca.cn/reading/testXX` 时，扩展只会读取页面上显示的 Test 名称、已答题数、分数和计时，并同步到本地看板。

## GitHub Pages

将此目录推送到公开 GitHub 仓库，并在仓库设置的 Pages 中选择 `GitHub Actions`。此后本机计划任务会每日采集、提交并推送最新进度。
