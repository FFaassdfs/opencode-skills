---
name: oa-management-template-guide
description: 当用户提到集团OA、自定义表单、OA管理模板、项目台账、产品台账、项目看板、静态HTML看板、主表明细表、枚举值显示、人员ID或部门ID映射、基于OA数据生成管理页面时使用。尤其适用于从 uf_* 表提取数据并构建项目、产品、合同、流程台账类模板。
---

# OA 管理模板通用指南

## Overview

这个技能用于把 OA 数据稳定地转换成可复用的管理模板。

核心原则：先把 OA 数据模型摸清楚，再做页面模板。页面只是最后一层，真正决定模板质量的是主表、明细表、枚举值、人员字段、部门字段和显示层建模是否稳定。

## When to Use

- 用户要基于 OA 数据做项目管理、产品管理、合同台账、流程台账、经营看板、静态 HTML 页面
- 用户提到 `uf_*` 主表、`_dt1/_dt2/_dt3` 明细表、`modeinfo`、`modefieldattr`
- 用户遇到枚举值显示成数字、人员显示成 ID、部门显示成 ID、字段名看不懂、明细表不确定等问题
- 用户要做本地脚本定时刷新页面，而不是依赖常驻服务

不要用于：

- 纯流程审批分析但不需要模板页面
- 只做单次临时 SQL 查询，不需要沉淀模板结构

## Required Skill

**REQUIRED SUB-SKILL:** 需要先使用 `oa-database-connector` 获取连接方式和复用查询模块。

## Reference Files

- `references/sql-patterns.md`
  当需要快速复用 OA 查询模板时读取。包含主表探查、明细表探查、distinct 枚举、人员/部门映射、元数据探查等常用 SQL。

## Standard Workflow

按这个顺序做，不要跳步：

1. 明确业务对象
2. 确认主表
3. 确认明细表
4. 看真实数据
5. 查字段元数据
6. 识别枚举/人员/部门字段
7. 建立原始值与显示值双层模型
8. 再做页面模板

## Step 1: 明确业务对象

先问清楚当前对象是什么：

- 项目
- 产品
- 合同
- 申请单/流程台账
- 其他自定义业务对象

一个业务对象通常对应：

- 1 张主表
- 0 到多张明细表

不要一开始就直接写页面。先建立数据对象模型。

## Step 2: 找主表

优先确认主表名，例如：

- `uf_HCTZXM_YTXM`
- `uf_HCZHCP_CPDA`

先看真实字段：

```sql
SELECT TOP 20 *
FROM uf_xxxxx
ORDER BY id DESC
```

目标：

- 看字段长什么样
- 看值是中文、数字还是 ID
- 看有没有 `requestId / formmodeid / modedatacreater`

不要只靠字段名猜业务含义。

如果已经进入具体探查阶段，优先参考 `references/sql-patterns.md` 中的现成 SQL。

## Step 3: 找明细表

通用规律：

- `uf_xxxxx_dt1`
- `uf_xxxxx_dt2`
- `uf_xxxxx_dt3`

但不要假设每张都存在，也不要假设每张都有数据。

要分别确认：

1. 表是否存在
2. 当前是否有数据
3. 每张明细表的业务含义

典型查询：

```sql
SELECT TOP 20 * FROM uf_xxxxx_dt1 ORDER BY id DESC
SELECT TOP 20 * FROM uf_xxxxx_dt2 ORDER BY id DESC
SELECT TOP 20 * FROM uf_xxxxx_dt3 ORDER BY id DESC
```

明细表一般通过 `mainid -> 主表.id` 关联。

## Step 4: 看真实数据，不只看元数据

这一步最重要。

字段元数据只能说明可能是什么，真实数据才能说明实际怎么用。

每个关键字段都建议看 distinct：

```sql
SELECT DISTINCT somefield
FROM uf_xxxxx
ORDER BY somefield
```

重点判断：

- 已经是中文
- 是数字枚举
- 是人员 ID
- 是部门 ID
- 是浏览按钮选出来的业务 ID
- 是附件、链接或路径

## Step 5: 再查字段元数据

优先查这几类表：

- `modeinfo`
- `modefieldattr`
- `modeformfield`
- `mode_expressionbase`
- `workflow_formdict`
- `cus_formdict`

常用查询：

```sql
SELECT id, modename, table_name, formid
FROM modeinfo
WHERE table_name = 'uf_xxxxx'
```

```sql
SELECT fa.fieldname, fa.fieldlabel, fa.fieldtype, fa.htmltype
FROM modefieldattr fa
JOIN modeinfo m ON fa.modeid = m.id
WHERE m.table_name = 'uf_xxxxx'
ORDER BY fa.fieldid
```

经验：

- 元数据表很有用，但不一定稳定
- 不同 OA 模块、不同版本、不同模型表结构可能不一致
- 有时能拿到字段中文名，但拿不到可靠的枚举选项
- 有时查出来的中文还会乱码

所以不要把元数据当成唯一真相。要和真实数据一起判断。

需要现成 SQL 时，读取 `references/sql-patterns.md`。

## Step 6: 专门识别三类特殊字段

### 6.1 枚举字段

常见特征：

- 只出现少量 distinct 值
- 值可能是 `0/1`
- 值可能是数字编码
- 值也可能直接是中文

处理原则：

1. 如果已经是可读中文，直接保留
2. 如果是明确代码值，走映射表
3. 如果是未知值，原样透传，不要瞎翻译

### 6.2 人员字段

常见字段：

- `djr`
- `tbr`
- `modedatacreater`
- `modedatamodifier`
- 其他负责人、创建人、登记人字段

通用映射：

```sql
SELECT id, lastname
FROM HrmResource
WHERE id IN (...)
```

### 6.3 部门字段

常见字段名特征：

- `gzbm`
- `bm`
- `dept`
- `department`

通用映射：

```sql
SELECT id, departmentname
FROM HrmDepartment
WHERE id IN (...)
```

不要默认部门字段已经是中文。很多时候实际存的是部门 ID。

## Step 7: 永远保留原始值 + 显示值双层模型

这是复用模板时最关键的经验。

不要直接覆盖原字段，应该建立 `_display`：

```python
row["_display"][field] = display_value
```

原始值用于：

- 统计
- 计算
- 排序
- 调试
- 后续兼容

显示值用于：

- 列表
- 详情
- 搜索
- 标签

错误做法：

- 直接把 `1` 改成 `是`
- 直接把 `701` 改成 `资管业务部`

正确做法：

- 原值保留在原字段
- 显示值写到 `_display`

## 推荐的数据组织方式

### 主表与明细表

建议统一组织为：

```python
row["_details"] = {
    "records": [...],
    "files": [...],
    "navHistory": [...],
    "financials": [...],
}
```

### 推荐的通用函数

以后做新模板时，优先复用这类函数：

```python
normalize_rows(...)
group_rows(...)
build_hrm_map(...)
build_department_map(...)
build_display_value(...)
apply_display_fields(...)
```

职责建议：

- `normalize_rows`：把 decimal、日期等转成 JSON 可用值
- `group_rows`：按 `mainid` 组织明细表
- `build_hrm_map`：人员 ID -> 姓名
- `build_department_map`：部门 ID -> 部门名
- `build_display_value`：单字段显示规则
- `apply_display_fields`：批量填充 `_display`

## 页面模板经验

### 列表页展示什么

列表页优先放：

- 编号
- 名称
- 类型或状态
- 负责人或归属部门
- 核心金额或日期

不要把所有字段都堆进列表页。

### 详情弹窗展示什么

详情页适合承接：

- 主信息
- 管理信息
- 规则信息
- 明细表
- 趋势图
- 附件归档

### 搜索怎么做

搜索不要只搜原值，也要搜显示值。

否则用户搜：

- 中文枚举
- 部门名
- 人员姓名

会搜不到。

## 自动刷新经验

页面不要负责刷新后台数据。

推荐始终有一个统一入口脚本，例如：

```python
refresh_all.py
```

它负责顺序生成：

- 业务页 A
- 业务页 B
- 首页

Linux 和 Windows 定时任务都只跑这一个脚本。

## 常见坑

### 1. 只看字段名，不看数据

会导致字段理解错误。

### 2. 假设所有 `_dt` 表都存在

很多模型只有部分明细表。

### 3. 假设枚举值能自动查到中文

实际经常查不到，或查出来不可靠。

### 4. 直接覆盖原始值

后续统计、排序、调试都会变复杂。

### 5. 人员/部门字段直接上页面

最后页面会出现一堆 ID。

### 6. 只查元数据，不查 distinct

会错过真实值风格。

### 7. 页面先行，数据建模滞后

后面会反复返工。

## Quick Reference

| 场景 | 推荐动作 |
|------|----------|
| 新做一个 OA 模板 | 先确认主表、明细表、关键字段、distinct 值 |
| 字段像枚举 | 先查 distinct，再决定是否映射 |
| 字段像人员 ID | 查 `HrmResource` |
| 字段像部门 ID | 查 `HrmDepartment` |
| 页面要展示中文 | 统一写到 `_display` |
| 明细表很多 | 按 `_details` 结构组织 |
| 需要后台刷新 | 用统一入口脚本，不靠页面按钮 |

## SQL Server / OA 注意事项

- OA 常见数据库是 SQL Server，老版本很多是 2008 R2
- SQL Server 2008 R2 不支持 `OFFSET ... FETCH`
- 某些 `text/ntext/image` 字段不能直接参与某些比较操作
- 中文字段、老表结构、浏览按钮字段经常需要结合真实值来判断
- 读权限账号通常只能 `SELECT`，不要假设能改表或写数据

## Common Query Pack

这些场景优先直接参考 `references/sql-patterns.md`：

- 快速探查主表
- 快速探查明细表
- 查询字段 distinct 值
- 查询人员姓名映射
- 查询部门名称映射
- 查询 `modeinfo / modefieldattr` 元数据
- 判断某个字段到底是中文、枚举、人员 ID 还是部门 ID

## Recommended Starting Pattern

当用户要基于 OA 做新模板时，优先按这个模式启动：

1. 明确业务对象
2. 找主表和明细表
3. 看真实样本数据
4. 看 distinct 值
5. 查元数据补中文含义
6. 识别枚举、人员、部门字段
7. 建 `_display` 与 `_details`
8. 最后生成页面模板

如果顺序反了，后续通常会频繁返工。
