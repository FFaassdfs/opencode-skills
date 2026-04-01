---
name: scheduled-automation-builder
description: 构建定时自动任务、计划任务、自动更新 HTML/报表/数据文件、自动调用 OpenCode 或 AI 模型生成分析内容时必须使用。适用于 Windows 计划任务、批处理、Python 自动化、OpenCode server API、日报/行情页/统计页自动刷新、定时生成 Markdown/HTML/JSON/Excel/PDF 等场景。用户只要提到“定时运行”“自动更新”“计划任务”“自动生成页面/报告”“定时 AI 分析”“收盘后自动执行”等，即使没有明确提到 skill，也应触发本技能。
---

# Scheduled Automation Builder

## 概述

本技能用于帮助模型稳定生成“可长期运行”的自动化任务方案，重点避免以下常见弯路：

- 把 GUI 程序当成 CLI 调用
- 把 prompt 当位置参数误传，导致被识别为路径
- 假设 OpenCode 安装路径固定
- 假设 `opencode` 在 PATH 中
- 在 Windows 计划任务里遗漏工作目录、编码、认证变量
- 直接用 CLI `run`，却踩到 session 或环境问题
- 生成的 `.bat` 脚本含 `pause`，导致计划任务卡住
- 使用中文路径但未处理 PowerShell/批处理调用方式
- 只写主脚本，不写日志、失败提示、可配置项与回退策略

本技能的目标不是只生成“能跑一次”的脚本，而是生成：

- 可重复执行
- 可部署到别人的机器
- 路径可发现
- 失败可诊断
- 配置可覆盖
- 输出结构清晰

## 适用场景

- Windows 计划任务 `schtasks`
- 定时更新 HTML 页面、报表、行情页、监控页、日报
- 定时拉取数据并生成 JSON / Markdown / HTML / Excel / PDF
- 定时调用 OpenCode 或模型写 AI 点评
- 定时任务串联：更新数据 -> 生成页面 -> AI 分析 -> 写回页面
- 需要通过 `.bat`、Python、PowerShell 组合落地自动化任务
- 需要面向 GitHub 用户或他人机器共享自动化方案

## 强制流程

处理此类任务时，按以下顺序思考并输出。

1. 明确最终产物
2. 明确触发方式
3. 明确运行入口
4. 明确 OpenCode / 模型接入方式
5. 明确路径发现与可配置策略
6. 明确日志、错误处理与回退策略
7. 生成脚本、批处理、计划任务命令
8. 给出验证方法

不要跳过第 4 和第 5 步。很多自动任务失败，根因都在这里。

## 第一步：明确最终产物

先判断任务最终要更新什么：

- HTML 页面
- JSON / CSV / TSV
- Markdown 报告
- Excel 文件
- PDF 文件
- 多文件组合输出

再判断 AI 内容是：

- 只生成独立分析文本
- 直接写回 HTML 页面
- 同时写回页面和归档到单独文件

如果用户没有说清，要优先补齐：

- 输出文件路径
- 输出文件类型
- 是否覆盖原文件
- 是否保留历史版本

## 第二步：明确触发方式

常见触发方式：

- 手动执行
- 批处理手动执行
- Windows 计划任务定时执行
- 收盘后固定时间执行
- 每日 / 每周 / 工作日执行
- 事件触发执行

如果用户提到“定时”“自动”“每天几点运行”，默认应产出：

- 主执行脚本
- `.bat` 启动脚本
- `schtasks` 示例命令

## 第三步：明确运行入口

优先把自动化链路拆成稳定的步骤：

1. 数据更新脚本
2. AI 分析脚本
3. 总入口批处理

推荐结构：

- `update_*.py`：负责拉取数据、生成基础文件
- `analyze_*.py`：负责调用模型并写回分析内容
- `run_daily.bat`：负责编排与计划任务调用

当流程较简单时，也可以合并为一个 Python 脚本，但前提是：

- 职责清晰
- 容易单独调试
- 日志能区分数据阶段和 AI 阶段

## 第四步：OpenCode / 模型接入方式

可直接复用的脚本模板：

- `scripts/opencode_server_client.py`
- `scripts/scheduled_analysis_template.py`

### 核心原则

在自动化场景里，**不要默认直接调用 GUI 程序**。

必须区分：

- `OpenCode.exe`：通常更偏桌面/GUI 入口
- `opencode-cli.exe`：更适合自动化与 CLI 调用

### 推荐顺序

1. 优先使用 OpenCode server API
2. 其次考虑 `opencode-cli.exe` 的稳定 CLI 子命令
3. 最后才考虑 GUI 可执行文件

### 为什么优先 server API

在 Windows 自动化里，CLI 可能出现：

- `Session not found`
- prompt 被当成路径
- 交互行为不稳定
- PATH / 启动目录问题

而 `serve + HTTP API` 的优点是：

- 行为更稳定
- 可明确认证
- 可显式创建 session
- 可指定 provider/model
- 更适合 Python 自动化

### 推荐的 OpenCode server 调用链路

1. 启动服务：`opencode-cli.exe serve --hostname 127.0.0.1 --port 4096`
2. 用 Basic Auth 调 `/global/health`
3. `POST /session` 创建 session
4. `POST /session/:id/message` 发送 prompt
5. 提取返回 `parts` 中的 `text`

如果用户是“定时 AI 点评”类任务，默认优先给出这种方案。

## 第五步：OpenCode 路径发现与可配置策略

这是共享给其他用户时最关键的部分。

### 禁止事项

不要写死：

- `D:\opencode\OpenCode.exe`
- `D:\opencode\opencode-cli.exe`
- 假设 `opencode` 已在 PATH

### 必须包含的路径发现策略

先尝试以下顺序：

1. `Get-Command opencode`
2. `Get-Command opencode-cli`
3. 当前用户提供的环境变量，如：`OPENCODE_CLI_PATH`
4. 常见文件名搜索：`opencode-cli.exe`, `OpenCode.exe`
5. 常见目录搜索：用户自定义安装目录、项目目录、已知软件目录
6. 找不到时明确报错，并提示用户手动配置路径

### 推荐的可配置项

脚本里应预留：

- `OPENCODE_CLI_PATH`
- `OPENCODE_SERVER_URL`
- `OPENCODE_SERVER_USERNAME`
- `OPENCODE_SERVER_PASSWORD`
- `MODEL_PROVIDER`
- `MODEL_ID`
- `WORK_DIR`
- `OUTPUT_PATH`

### PowerShell 路径探测示例

```powershell
$cli = $env:OPENCODE_CLI_PATH

if (-not $cli) {
    $cmd = Get-Command opencode -ErrorAction SilentlyContinue
    if ($cmd) { $cli = $cmd.Source }
}

if (-not $cli) {
    $cmd = Get-Command opencode-cli -ErrorAction SilentlyContinue
    if ($cmd) { $cli = $cmd.Source }
}

if (-not $cli) {
    $candidates = @(
        "D:\opencode\opencode-cli.exe",
        "D:\opencode\OpenCode.exe",
        "$env:USERPROFILE\AppData\Local\Programs\OpenCode\opencode-cli.exe"
    )
    foreach ($path in $candidates) {
        if (Test-Path $path) {
            $cli = $path
            break
        }
    }
}

if (-not $cli) {
    throw "未找到 OpenCode CLI。请设置 OPENCODE_CLI_PATH 或把 opencode-cli.exe 加入 PATH。"
}
```

### 共享方案建议

如果脚本要共享给 GitHub 上的其他人：

- 把路径写成“自动发现 + 环境变量覆盖”
- 在 README 或注释里告诉用户如何设置 `OPENCODE_CLI_PATH`
- 不要把你本机路径硬编码进最终模板

## 第六步：Windows 计划任务注意事项

详情见 `references/task-scheduler-checklist.md`。

必须注意：

- `.bat` 中不要保留 `pause`
- 用 `cd /d "目标目录"` 切换工作目录
- 如果脚本需要 UTF-8，可加 `chcp 65001 >nul`
- 计划任务里应优先调用 `.bat`，不要把复杂逻辑全塞进 `schtasks /tr`
- 若依赖环境变量，需确认计划任务运行账户能拿到这些变量
- 计划任务和手工终端的 PATH 不一定一致

## 第七步：认证与环境变量

如果使用 `serve + HTTP API`：

- 检查 `OPENCODE_SERVER_USERNAME`
- 检查 `OPENCODE_SERVER_PASSWORD`
- 默认用户名通常可回退到 `opencode`
- 调用 API 时需带 Basic Auth

如果没有密码：

- 不能假设服务一定可匿名访问
- 应在脚本里显式检测并报错，或提示用户先设置环境变量

## 第八步：日志与错误处理

自动化任务必须具备最低限度的可诊断能力。

至少做到：

- 找不到路径时给出明确错误
- 数据文件不存在时给出明确错误
- OpenCode 服务启动失败时给出明确错误
- 模型返回为空时给出明确错误
- HTML 结构不符合预期时给出明确错误

推荐增强项：

- 把 stdout/stderr 落到日志文件
- 记录开始时间、结束时间、运行阶段
- 区分“数据阶段失败”和“AI 阶段失败”

## 第九步：输出模式

详情见 `references/output-patterns.md`。

生成方案时，应尽量根据需求选择以下模式之一：

### 模式 A：仅更新数据

- 更新 JSON / HTML / CSV
- 不调用 AI

### 模式 B：更新数据 + 单独生成 AI 报告

- 页面与分析文件分离
- 适合归档和审阅

### 模式 C：更新数据 + 把 AI 写回 HTML

- 最适合展示页/行情页/日报页
- 需要稳定定位 HTML 插入点

### 模式 D：更新数据 + HTML + 分析归档

- 页面展示最新结果
- 另外落盘 `analysis_YYYYMMDD.md` 等历史文件

如果用户提到“页面中直接显示 AI 评价”，默认选模式 C。

## 第十步：默认交付物

对于“定时自动任务”类请求，默认应该尽量给出这些文件或内容：

1. 主数据脚本
2. AI 分析脚本
3. 总入口 `.bat`
4. `schtasks` 创建命令
5. 运行验证命令
6. 注意事项说明

如果任务更复杂，再补：

- `.env.example`
- README
- 历史归档脚本
- 日志目录约定

## 可复用模板

### 1. OpenCode server API 客户端

优先复用：`scripts/opencode_server_client.py`

适用场景：

- 需要发现 OpenCode CLI 路径
- 需要自动拉起 `serve`
- 需要通过 HTTP API 创建 session 并发送消息
- 需要共享给他人机器使用

### 2. 定时分析主模板

优先复用：`scripts/scheduled_analysis_template.py`

适用场景：

- 输入是 JSON 数据
- 输出是 HTML 页面
- 需要把 AI 分析插入 HTML
- 需要保留前一日或上一版本数据用于对比

### 3. GitHub 可共享示例项目

参考：`examples/github-share-template/`

包含：

- `README.md`
- `run_daily.bat`
- `update_report.py`
- `analyze_and_update.py`

当用户明确要求“做一个可共享到 GitHub 的自动化方案”时，优先按这个示例项目组织输出。

## 生成内容时的推荐结构

推荐按以下顺序输出：

1. 方案概述
2. 文件清单
3. 关键配置项
4. 主脚本
5. 批处理脚本
6. 计划任务命令
7. 验证方式
8. 风险与注意事项

## 验证清单

在声称“方案可用”前，至少检查：

- OpenCode 路径是否可发现
- 模型名是否符合 `provider/model` 或 API 请求格式
- 认证变量是否可用
- HTML 更新逻辑是否能定位插入点
- `.bat` 是否不会卡住
- `schtasks` 命令是否可直接复用

## 典型模板

### 1. 手动执行

```bat
py -3.11 update_report.py
py -3.11 analyze_report.py
```

### 2. 批处理执行

```bat
@echo off
chcp 65001 >nul
cd /d "D:\path\to\project"

py -3.11 update_report.py
py -3.11 analyze_report.py
```

### 3. 计划任务

```bat
schtasks /create /tn "Daily Report" /tr "D:\path\to\run_daily.bat" /sc daily /st 16:00
```

## 不确定时的默认建议

如果用户没有明确指定实现方式，优先采用：

- Windows: `Python + .bat + schtasks`
- OpenCode 调用: `opencode-cli serve + HTTP API`
- 输出更新: 原页面覆盖 + HTML 中插入 AI 分析块
- 路径策略: 自动发现 + 环境变量覆盖
- 调度策略: 单独 `run_daily.bat` 作为计划任务入口

## 参考资料

- `references/windows-opencode-automation.md`
- `references/task-scheduler-checklist.md`
- `references/output-patterns.md`
- `scripts/opencode_server_client.py`
- `scripts/scheduled_analysis_template.py`
- `examples/github-share-template/`
