# Windows OpenCode Automation

## 核心结论

在 Windows 自动化场景下，优先把 OpenCode 当作“本地 HTTP 服务”来用，而不是直接依赖交互式 CLI 行为。

推荐顺序：

1. `opencode-cli.exe serve`
2. 调用 HTTP API
3. 必要时再尝试 CLI `run`

## 原因

直接 CLI 自动化容易出现：

- `Session not found`
- prompt 被误识别为项目路径
- 运行目录影响行为
- GUI 程序无 stdout/stderr

## 推荐实现

1. 探测 CLI 路径
2. 检查 `OPENCODE_SERVER_USERNAME` / `OPENCODE_SERVER_PASSWORD`
3. 若服务未启动，则后台启动 `serve`
4. 调 `/global/health` 验证
5. `POST /session`
6. `POST /session/:id/message`
7. 解析 `parts` 中 `type=text` 的内容

## 认证

OpenCode server 常见需要 Basic Auth。

典型变量：

- `OPENCODE_SERVER_USERNAME`
- `OPENCODE_SERVER_PASSWORD`

默认用户名通常可用 `opencode` 回退，但不要假设密码为空。

## 模型格式

CLI 或 API 中应尽量明确 provider 与 model：

- CLI: `opencode/big-pickle`
- API:
  - `providerID: opencode`
  - `modelID: big-pickle`

## 共享时的注意事项

- 不要把本机安装路径写死到模板中
- 把路径发现逻辑和环境变量覆盖作为默认能力
- README 中说明如何手动设置 `OPENCODE_CLI_PATH`
