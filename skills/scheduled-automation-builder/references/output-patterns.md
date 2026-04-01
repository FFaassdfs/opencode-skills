# Output Patterns

## 模式 A：更新数据文件

适合：

- 只刷新 JSON / CSV / Excel
- 不需要 AI 分析

建议交付：

- `update_data.py`
- `run_daily.bat`
- `schtasks` 命令

## 模式 B：更新数据 + 生成 AI 报告

适合：

- 页面与分析分离
- 需要保留分析文档

建议交付：

- `update_data.py`
- `analyze_data.py`
- `analysis_YYYYMMDD.md`
- `run_daily.bat`

## 模式 C：更新数据 + 写回 HTML

适合：

- 行情展示页
- 监控大屏
- 日报页面

建议交付：

- `update_html.py`
- `analyze_and_update.py`
- `run_daily.bat`

## 模式 D：更新数据 + 写回 HTML + 历史归档

适合：

- 用户既要展示最新结果，又要保留历史分析

建议交付：

- `update_html.py`
- `analyze_and_update.py`
- `analysis_YYYYMMDD.md`
- `run_daily.bat`

## 默认选择建议

- 用户提到“HTML 里直接显示 AI 点评” -> 模式 C
- 用户提到“保留历史分析” -> 模式 D
- 用户只提到“自动刷新数据” -> 模式 A
- 用户提到“日报/总结文件” -> 模式 B 或 D
