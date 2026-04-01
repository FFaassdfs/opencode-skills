# Scheduled Automation Template

这是一个适合分享给 GitHub 其他用户的 Windows 定时自动化示例项目，演示如何：

1. 更新数据
2. 生成或刷新 HTML 页面
3. 通过 OpenCode 本地 server API 调用模型
4. 将 AI 分析写回 HTML 页面
5. 通过 Windows Task Scheduler 定时执行

## 目标

- 不写死本机 OpenCode 安装路径
- 支持环境变量覆盖与自动发现 OpenCode CLI
- 优先使用 `serve + HTTP API` 保持自动化稳定
- 让 `schtasks` 只调用一个明确入口文件

## 目录结构

```text
.
├── run_daily.bat
├── update_report.py
├── analyze_and_update.py
├── report.html
├── data.json
├── data_old.json
└── logs/
```

## 推荐环境变量

建议设置：

- `OPENCODE_CLI_PATH`
- `OPENCODE_SERVER_USERNAME`
- `OPENCODE_SERVER_PASSWORD`

可选设置：

- `AUTOMATION_MODEL_PROVIDER`
- `AUTOMATION_MODEL_ID`

## 注意事项

- 不要假设别人的机器上有 `D:\opencode`
- 自动化优先使用 `opencode-cli.exe`，不要默认使用 `OpenCode.exe`
- Windows 定时任务优先用 `serve + HTTP API`，不要默认依赖 CLI `run`
- 提供给计划任务使用的 `.bat` 不要带 `pause`

## 计划任务示例

```bat
schtasks /create /tn "Daily Report" /tr "C:\path\to\project\run_daily.bat" /sc daily /st 16:00
```
