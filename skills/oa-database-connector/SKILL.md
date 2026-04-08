---
name: oa-database-connector
description: 集团OA数据库连接技能。当用户需要查询集团OA数据库、连接100.67数据库、查询ecology数据库、查询OA系统数据时使用。自动提供连接参数和可复用的Python连接模块。
---

# 集团OA数据库连接技能

## 数据库信息

| 参数 | 值 |
|------|-----|
| 地址 | 192.168.100.67 |
| 数据库 | ecology |
| 用户名 | ReadOA |
| 密码 | oa168 |
| 类型 | SQL Server 2008 R2 (10.50.4000.0) |
| 权限 | 只读 (ReadOA) |

## 何时使用

- 用户提到"集团OA"、"OA数据库"、"100.67"、"ecology数据库"
- 需要查询OA系统中的人员、流程、表单等数据
- 需要连接 192.168.100.67 上的 ecology 库

## 快速使用方法

### 方法一：直接使用连接模块（推荐）

```python
import sys
sys.path.insert(0, r"C:\Users\veken\.opencode\skills\oa-database-connector\scripts")

from oa_db import query, query_df, oa_conn

# 查询并返回 list[dict]
rows = query("SELECT TOP 10 * FROM HrmResource")

# 查询并返回 DataFrame
df = query_df("SELECT TOP 100 * FROM HrmResource")

# 使用上下文管理器手动控制
with oa_conn() as conn:
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM HrmResource")
    print(cursor.fetchone()[0])
```

### 方法二：直接 pyodbc 连接

```python
import pyodbc

conn = pyodbc.connect(
    "DRIVER={SQL Server};"
    "SERVER=192.168.100.67;"
    "DATABASE=ecology;"
    "UID=ReadOA;"
    "PWD=oa168;",
    timeout=10
)
```

## 注意事项

1. ReadOA 为只读账号，不可执行 INSERT/UPDATE/DELETE
2. SQL Server 2008 R2 不支持 OFFSET...FETCH 分页，用 ROW_NUMBER() 替代
3. pyodbc 需已安装：`pip install pyodbc`
4. 驱动使用系统自带 `{SQL Server}`，无需额外安装驱动
5. SQL 语句中单引号需注意转义，建议使用参数化查询或脚本文件

## 测试连接

```bash
python "C:\Users\veken\.opencode\skills\oa-database-connector\scripts\oa_db.py"
```

---

## 核心表结构详解

### 一、HRM 人事表体系

#### HrmResource（人员信息，4707 行）

**关键字段：**

| 字段名 | 类型 | 说明 |
|--------|------|------|
| id | int | 主键，员工ID |
| loginid | varchar | 登录账号 |
| lastname | varchar | 姓名 |
| sex | char(1) | 性别 |
| birthday | char(10) | 生日 |
| mobile | varchar | 手机 |
| email | varchar | 邮箱 |
| departmentid | int | **→ HrmDepartment.id** |
| subcompanyid1 | int | **→ HrmSubCompany.id** |
| managerid | int | 直属上级 → HrmResource.id |
| jobtitle | int | 职务 |
| joblevel | int | 职级 |
| status | int | 状态：0=在职，1=试用，2=临时，3=离职，4=退休 |
| workcode | varchar | 工号 |
| resourcetype | char(1) | 资源类型 |
| startdate | char(10) | 入职日期 |
| enddate | char(10) | 离职日期 |
| createdate | char(10) | 创建日期 |

#### HrmDepartment（部门信息，694 行）

| 字段名 | 类型 | 说明 |
|--------|------|------|
| id | int | 主键，部门ID |
| departmentname | varchar | 部门名称 |
| departmentmark | varchar | 部门编码 |
| subcompanyid1 | int | **→ HrmSubCompany.id** |
| supdepid | int | 上级部门ID → HrmDepartment.id |
| allsupdepid | varchar | 所有上级部门ID路径 |
| canceled | char(1) | 是否撤销（0=正常，1=撤销） |
| tlevel | int | 层级 |

#### HrmSubCompany（分部/公司，112 行）

| 字段名 | 类型 | 说明 |
|--------|------|------|
| id | int | 主键，分部ID |
| subcompanyname | varchar | 分部/公司名称 |
| supsubcomid | int | 上级分部ID → HrmSubCompany.id |
| companyid | tinyint | 集团公司ID |
| canceled | char(1) | 是否撤销 |
| tlevel | int | 层级 |

**人事表关联关系：**
```
HrmResource.departmentid  → HrmDepartment.id
HrmResource.subcompanyid1 → HrmSubCompany.id
HrmResource.managerid     → HrmResource.id（自关联，上下级）
HrmDepartment.subcompanyid1 → HrmSubCompany.id
HrmDepartment.supdepid    → HrmDepartment.id（自关联，上下级）
HrmSubCompany.supsubcomid → HrmSubCompany.id（自关联，上下级）
```

**常用查询示例：**
```sql
-- 查询在职员工（含部门、公司名称）
SELECT r.id, r.lastname, r.workcode, r.loginid,
       d.departmentname, s.subcompanyname
FROM HrmResource r
LEFT JOIN HrmDepartment d ON r.departmentid = d.id
LEFT JOIN HrmSubCompany s ON r.subcompanyid1 = s.id
WHERE r.status = 0
```

---

### 二、Workflow 流程表体系

#### workflow_base（流程定义，1331 行）

| 字段名 | 类型 | 说明 |
|--------|------|------|
| id | int | 主键，流程ID |
| workflowname | varchar | 流程名称 |
| workflowtype | int | 流程类型 |
| formid | int | 关联表单ID |
| isvalid | char(1) | 是否有效 |
| istemplate | char(1) | 是否模板 |

#### workflow_requestbase（流程请求记录，388905 行）

| 字段名 | 类型 | 说明 |
|--------|------|------|
| requestid | int | 主键，申请单ID |
| workflowid | int | **→ workflow_base.id** |
| requestname | varchar | 申请单名称 |
| creater | int | **→ HrmResource.id**（创建人） |
| createdate | char(10) | 创建日期 |
| createtime | char(8) | 创建时间 |
| lastoperator | int | 最后操作人 → HrmResource.id |
| status | varchar | 状态（archived=归档，withdraw=撤回） |
| currentnodeid | int | 当前节点ID |
| deleted | tinyint | 是否删除 |
| currentstatus | int | 当前状态 |

#### workflow_currentoperator（当前待办，2345079 行）

| 字段名 | 类型 | 说明 |
|--------|------|------|
| id | int | 主键 |
| requestid | int | **→ workflow_requestbase.requestid** |
| userid | int | **→ HrmResource.id**（处理人） |
| nodeid | int | 节点ID |
| workflowid | int | 流程ID |
| iscomplete | int | 是否完成（1=完成，0=待处理） |
| isremark | int | 是否已批注 |
| receivedate | char(10) | 收到日期 |

#### workflow_nodebase（节点定义，12883 行）

| 字段名 | 类型 | 说明 |
|--------|------|------|
| id | int | 主键，节点ID |
| nodename | varchar | 节点名称 |
| isstart | char(1) | 是否开始节点 |
| isend | char(1) | 是否结束节点 |
| isreject | char(1) | 是否退回节点 |
| requestid | int | 关联流程ID |

**流程表关联关系：**
```
workflow_requestbase.workflowid   → workflow_base.id
workflow_requestbase.creater      → HrmResource.id
workflow_currentoperator.requestid → workflow_requestbase.requestid
workflow_currentoperator.userid   → HrmResource.id
workflow_flownode.workflowid      → workflow_base.id
workflow_flownode.nodeid          → workflow_nodebase.id
```

**常用查询示例：**
```sql
-- 查询某人的待办流程
SELECT r.requestname, r.createdate, wb.workflowname
FROM workflow_currentoperator co
JOIN workflow_requestbase r ON co.requestid = r.requestid
JOIN workflow_base wb ON r.workflowid = wb.id
JOIN HrmResource hr ON co.userid = hr.id
WHERE hr.loginid = 'zhangsan'
  AND co.iscomplete = 0
```

---

### 三、uf_* 自定义表单体系

数据库中共有 **1035 张** uf_* 表，是泛微 OA 表单模型（mode）生成的自定义业务数据表。

**命名规律：**
- `uf_xxxxx` — 主表（含主记录，每行对应一条完整业务数据）
- `uf_xxxxx_dt1` — 明细表1（子表，通过 `mainid` 关联主表 `id`）
- `uf_xxxxx_dt2` — 明细表2
- `uf_xxxxx_dt3` — 明细表3

**uf_* 表通用字段（每张主表都有）：**

| 字段名 | 说明 |
|--------|------|
| id | 主键 |
| requestId | 关联流程申请单 → workflow_requestbase.requestid（无流程则为空） |
| formmodeid | 表单模型ID → modeinfo.id |
| modedatacreater | 创建人 → HrmResource.id |
| modedatacreatertype | 创建人类型 |
| modedatacreatedate | 创建日期 |
| modedatacreatetime | 创建时间 |
| modedatamodifier | 最后修改人 |
| modedatamodifydatetime | 最后修改时间 |
| MODEUUID | 唯一标识UUID |

**明细表通用字段：**

| 字段名 | 说明 |
|--------|------|
| id | 主键 |
| mainid | **→ 主表.id**（关联主表行） |

**uf_* 关联关系：**
```
uf_xxxxx.requestId  → workflow_requestbase.requestid（有流程审批的表单）
uf_xxxxx.modedatacreater → HrmResource.id
uf_xxxxx_dt1.mainid → uf_xxxxx.id
uf_xxxxx_dt2.mainid → uf_xxxxx.id
uf_xxxxx_dt3.mainid → uf_xxxxx.id
```

#### 已知关键业务表（部分）

| 表名 | 行数 | 业务含义 |
|------|------|---------|
| uf_HCTZXM_YTXM | — | 合创投资·已投项目主表 |
| uf_HCTZXM_YTXM_dt1 | — | 已投项目·历年财务数据 |
| uf_HCTZXM_YTXM_dt2 | — | 已投项目·股票价格记录 |
| uf_HCTZXM_YTXM_dt3 | — | 已投项目·相关文件归档 |
| uf_ajfatz | 134 | 案件发案综记录 |
| uf_ajjzdj | 123 | 案件结案登记 |
| uf_ajsbtz | 130 | 案件申报通知 |
| uf_annex_type | 118 | 附件类型管理 |
| uf_ay | 1403 | 案由数据 |

#### 已投项目表字段说明（uf_HCTZXM_YTXM）

**主表字段（业务字段名 → 数据库列名）：**

| 中文名 | 字段名 | 类型 |
|--------|--------|------|
| 已投项目编号 | ytxmbh | 文本 |
| 选择储备项目 | xzcbxm | 单选按钮 |
| 1.01 项目名称 | xmmc | 文本 |
| 1.02 公司名称 | gsmc | 单选按钮 |
| 1.03 企业负责人 | qyfzr | 文本 |
| 1.04 地区（省市） | dqss | 文本 |
| 1.05 行业 | xy | 文本 |
| 1.06 主营业务 | zyyw | 文本 |
| 1.07 成立时间 | clsj | 文本 |
| 1.08 注册资本（万元） | zczb | 文本 |
| 1.09 人员规模 | rygm | 文本 |
| 2.01 投资状态 | tzzt | 单选按钮 |
| 2.02 项目负责人 | xmfzr | 文本 |
| 2.03 投资日期 | tzrq | 日期 |
| 2.04 已投出金额（万元） | ytcjey | 数值 |
| 2.05 投资持股比%  | tzcgb | 数值 |
| 2.06 持股数量 | cgsl | 文本 |
| 2.07 主要对接人 | zydjr | 文本 |
| 2.08 职位 | zw | 文本 |
| 2.09 联系方式 | lxfs | 文本 |
| 2.10 董事/董事席位 | dsjsxw | 文本 |
| 2.11 是否直接股东 | sfzjgd | 是/否 |
| 2.12 中间主体名称 | zjztmc | 文本 |
| 2.13 投资方式 | tzfs | 文本 |
| 2.14 投资历程 | tzlc | 文本 |
| 3.01 当前历程 | dqlc | 文本 |
| 3.02 确认出让中间值（万元） | qrcyjzy | 数值 |
| 3.03 最新持股比例% | zxcgbl | 数值 |
| 3.04 出让数量 | cysl | 文本 |
| 3.05 综合历程估值（万元） | zhlcgzy | 数值 |
| 3.06 确认净值总资产% | qrjzzcl | 数值 |
| 3.07 确认覆盖率（万元） | qrfyy | 数值 |
| 3.08 项目IRR% | xmirr | 数值 |

**明细表1（dt1）— 历年财务数据：**

| 中文名 | 字段名 |
|--------|--------|
| 年份 | nf |
| 营业收入（万元） | yysry |
| 净利润（万元） | jlry |
| 资产总额（万元） | zczey |
| 净资产总额（万元） | jzczey |
| 毛利率% | mll |
| 净资产收益率% | jzcsyl |
| 销售净利率% | xsjll |
| 应收账款周转天数 | chzzts |
| 速动比率% | sdbl |
| 应收账款周转天数 | yszkzzts |
| 营业周期 | yyzq |
| 应付账款周转天数 | yfzkzzts |
| 经营周期 | jyyzq |
| 资产负债率% | zcfzl |
| 有效资产负债率% | yxzcfzl |
| 流动比率% | ldbl |

**明细表2（dt2）— 股票价格：**

| 中文名 | 字段名 |
|--------|--------|
| 日期 | rq |
| 股票价格 | gpjg |
| 记录人 | djr |

**明细表3（dt3）— 相关文件：**

| 中文名 | 字段名 |
|--------|--------|
| 日期 | rq |
| 文件摘要 | wjzx（多选：投前/在投/后投） |
| 相关流程 | xglc（档案链接） |
| 附件 | fj |
| 备注 | bz |
| 记录人 | djr |

---

### 四、表单模型（modeinfo）体系

表单模型是 uf_* 表的元数据，记录表结构定义。

| 关键表 | 说明 |
|--------|------|
| modeinfo | 模型基础信息（模型名、数据表名） |
| modefieldattr | 模型字段属性（字段名、类型、标签） |
| modeformfield | 模型布局字段信息 |
| mode_customsearch | 查询列表配置 |
| moderightinfo | 权限配置 |

**查找某业务对应的 uf_ 表：**
```sql
SELECT id, modename, table_name, formid
FROM modeinfo
WHERE modename LIKE '%投资%'
```

**查看某 uf_ 表的字段中文名：**
```sql
SELECT fa.fieldname, fa.fieldlabel, fa.fieldtype, fa.htmltype
FROM modefieldattr fa
JOIN modeinfo m ON fa.modeid = m.id
WHERE m.table_name = 'uf_HCTZXM_YTXM'
```

---

### 五、完整表间关系图

```
HrmSubCompany (公司/分部)
    ↑ subcompanyid1
HrmDepartment (部门)
    ↑ departmentid
HrmResource (人员) ←────────────────────────────────────┐
    ↑ creater / modedatacreater                         │
    │                                                    │
workflow_requestbase (流程申请单)                         │
    ↑ requestid                   ↑ workflowid           │
workflow_currentoperator      workflow_base (流程定义)     │
    (当前待办/处理记录)               ↑ userid            │
                                                         │
uf_xxxxx (自定义表单主表)                                  │
    id ──→ uf_xxxxx_dt1.mainid                           │
    id ──→ uf_xxxxx_dt2.mainid                           │
    id ──→ uf_xxxxx_dt3.mainid                           │
    requestId ──→ workflow_requestbase.requestid          │
    modedatacreater ─────────────────────────────────────┘
    formmodeid ──→ modeinfo.id
```

---

### 六、附件与操作日志表

#### DownloadLog（附件下载记录，约 67 万行）

记录用户从知识文档中心**下载附件**的行为日志。

| 字段名 | 类型 | 说明 |
|--------|------|------|
| userid | int | 下载人ID → HrmResource.id |
| username | varchar(60) | 下载人姓名（冗余字段） |
| downloadtime | char(19) | 下载时间（格式：yyyy-MM-dd HH:mm:ss） |
| imageid | int | 附件文件ID（对应知识文档中心中的文件） |
| imagename | varchar(1000) | 附件文件名（含扩展名） |
| docid | int | 所属文档ID |
| docname | varchar(1000) | 所属文档名（不含扩展名） |
| clientaddress | varchar(1001) | 下载者IP地址 |

**常用查询：**
```sql
-- 查询某人最近的下载记录
SELECT TOP 20 dl.downloadtime, dl.imagename, dl.docname, dl.clientaddress
FROM DownloadLog dl
WHERE dl.userid = (SELECT id FROM HrmResource WHERE loginid = 'zhangsan')
ORDER BY dl.downloadtime DESC

-- 查询某文件被下载次数
SELECT imagename, COUNT(*) as download_count
FROM DownloadLog
WHERE imagename LIKE '%合同%'
GROUP BY imagename
ORDER BY download_count DESC
```

---

#### DocDetailLog（文档操作详细日志，约 125 万行）

记录知识文档中心所有文档的**全量操作行为**（阅读、新建、修改、删除、下载等）。

| 字段名 | 类型 | 说明 |
|--------|------|------|
| id | int | 主键 |
| docid | int | 文档ID |
| docsubject | varchar(1000) | 文档标题 |
| doccreater | int | 文档创建人 → HrmResource.id |
| operatetype | varchar | **操作类型代码**（见下表） |
| operatedesc | varchar(1000) | 操作说明（通常为空） |
| operateuserid | int | 操作人 → HrmResource.id |
| operatedate | char(10) | 操作日期 |
| operatetime | char(8) | 操作时间 |
| clientaddress | varchar(256) | 操作者IP |
| usertype | char(1) | 用户类型（1=普通用户） |
| creatertype | char(1) | 创建人类型 |
| operateitem | varchar(1000) | 操作项目（301=文档中心） |

**operatetype 枚举值（来自 ecology_log_operatetype 表）：**

| operatetype | 含义 |
|-------------|------|
| 0 | 阅读 |
| 1 | 新建 |
| 2 | 修改 |
| 3 | 删除 |
| 12 | 复制 |
| 13 | 发布 |
| 14 | 失效 |
| 15 | 作废 |
| 16 | 添加新版本 |
| 18 | 自动签出 |
| 20 | 自动签入 |
| 21 | 打印 |
| 22 | 下载 |
| 23 | 更改文档状态 |

> 注意：operatetype=0（阅读）和 operatetype=22（下载）是两种不同行为。
> 文件下载行为优先使用 `DownloadLog` 表（更直接），DocDetailLog 可用于综合分析。

**常用查询：**
```sql
-- 统计某段时间内各操作类型的数量
SELECT operatetype, COUNT(*) as cnt
FROM DocDetailLog
WHERE operatedate >= '2026-01-01'
GROUP BY operatetype
ORDER BY cnt DESC

-- 查询谁在下载文档（operatetype=22）
SELECT dl.docsubject, hr.lastname, dl.operatedate, dl.operatetime
FROM DocDetailLog dl
JOIN HrmResource hr ON dl.operateuserid = hr.id
WHERE dl.operatetype = '22'
ORDER BY dl.operatedate DESC, dl.operatetime DESC
```

---

#### ImageFileLog（文件重命名记录，约 6785 行）

记录知识文档中心中附件文件**被重命名**的历史。

| 字段名 | 类型 | 说明 |
|--------|------|------|
| imagefileid | int | 附件文件ID |
| oldfilename | varchar(2000) | 改名前的文件名 |
| newfilename | varchar(2000) | 改名后的文件名 |
| userid | int | 操作人 → HrmResource.id |
| operatedate | varchar(10) | 操作日期 |
| operatetime | varchar(8) | 操作时间 |

---

#### DocPrintLog（文档打印记录，0 行，暂无数据）

| 字段名 | 说明 |
|--------|------|
| id | 主键 |
| printUserId | 打印人 → HrmResource.id |
| printDocId | 打印的文档ID |
| printDate | 打印日期 |
| printTime | 打印时间 |
| printNum | 打印份数 |
| clientAddress | 打印者IP |

---

#### ecology_log_operatetype（操作类型字典表）

存储 DocDetailLog.operatetype 的含义映射（全局字典）。

| 字段名 | 说明 |
|--------|------|
| id | 主键 |
| operatetype | 操作类型代码 |
| mouldid | 模板ID（NULL=通用，1=文档模板，15=其他） |
| operatetypelabel | 多语言Label ID |
| operatetypedesc | 操作名称（中文） |

```sql
-- 查询所有操作类型含义
SELECT operatetype, operatetypedesc FROM ecology_log_operatetype
WHERE mouldid IS NULL OR mouldid = 1
ORDER BY operatetype
```

---

### 七、中文表名与字段中文名的存储位置

泛微 ecology 的中文标签分两层存储，**没有直接在 uf_* 表的列上标注中文**，需通过元数据表反查。

#### 表（模型）的中文名 → `modeinfo`

| 字段 | 说明 |
|------|------|
| `id` | 模型ID（即 `formmodeid`，uf_* 主表通用字段） |
| `modename` | **表的中文名**（如 `已投项目`、`律师管理-律所库`） |
| `attitle` | 表的显示标题（通常与 modename 相同） |
| `formid` | 表单ID（负数），连接字段定义的关键外键 |

```sql
-- 按中文名查找对应模型
SELECT id, modename, formid FROM modeinfo WHERE modename LIKE '%投资%'

-- 查某 uf_* 表对应的模型（通过 formmodeid 反查）
SELECT m.modename, m.formid
FROM modeinfo m
WHERE m.id = (SELECT TOP 1 formmodeid FROM uf_HCTZXM_YTXM)
```

---

#### 字段的中文名 → `workflow_billfield` + `HtmlLabelInfo`

**关联链条（三表两跳）：**

```
modeinfo.formid（如 -1548）
    ↓  billid = formid
workflow_billfield.fieldname   ← 数据库列名（如 xmmc）
workflow_billfield.fieldlabel  ← 多语言ID（如 -162103，负整数）
    ↓  indexid = fieldlabel，languageid = 7
HtmlLabelInfo.labelname        ← 中文标签文本（如 "1.01项目名称"）
```

**`workflow_billfield` 关键字段：**

| 字段 | 说明 |
|------|------|
| `billid` | = `modeinfo.formid`（负数） |
| `fieldname` | 数据库列名（对应 uf_* 表的实际列） |
| `fieldlabel` | 多语言文本ID → `HtmlLabelInfo.indexid` |
| `fielddbtype` | 数据库类型（varchar/int/decimal 等） |
| `type` | 字段类型：1=文本，2=日期，3=数值，161=单选，171=关联流程，402=年份 |
| `dsporder` | 表单中的显示顺序 |

**`HtmlLabelInfo` 关键字段：**

| 字段 | 说明 |
|------|------|
| `indexid` | 多语言ID（负整数，与 `fieldlabel` 对应） |
| `labelname` | 标签文本 |
| `languageid` | 语言：**7=简体中文**，8=繁体中文，9=英文 |

**完整查询模板（获取任意 uf_* 表的字段中文名）：**

```sql
-- 第一步：通过表名找 formid
-- （方法A：直接查 modeinfo）
SELECT id, modename, formid FROM modeinfo WHERE modename LIKE '%已投项目%'
-- 得到 formid = -1548

-- 第二步：查该表所有字段的中文标签
SELECT
    wbf.fieldname    AS db列名,
    hli.labelname    AS 中文标签,
    wbf.fielddbtype  AS 数据库类型,
    wbf.type         AS 字段类型,
    wbf.dsporder     AS 显示顺序
FROM workflow_billfield wbf
LEFT JOIN HtmlLabelInfo hli
    ON wbf.fieldlabel = hli.indexid AND hli.languageid = 7
WHERE wbf.billid = -1548       -- 替换为目标 formid
ORDER BY wbf.type, wbf.dsporder
```

**一步到位（已知 uf_* 表名）：**

```sql
SELECT
    wbf.fieldname    AS db列名,
    hli.labelname    AS 中文标签,
    wbf.fielddbtype  AS 数据库类型,
    wbf.dsporder     AS 显示顺序
FROM modeinfo m
JOIN workflow_billfield wbf ON wbf.billid = m.formid
LEFT JOIN HtmlLabelInfo hli
    ON wbf.fieldlabel = hli.indexid AND hli.languageid = 7
WHERE m.modename = '已投项目'    -- 替换为目标模型名
ORDER BY wbf.type, wbf.dsporder
```

**补充表间关系：**

```
modeinfo (模型元数据)
    formid ──→ workflow_billfield.billid（字段定义）
                   fieldlabel ──→ HtmlLabelInfo.indexid（中文文本，languageid=7）
                   fieldname  ←── uf_xxxxx 的实际列名

uf_xxxxx.formmodeid ──→ modeinfo.id（反查中文表名）
```

> **注意事项：**
> - `modeinfo.formid` 通常为负数，`workflow_billfield.billid` 与之完全相同（包括负号）
> - `HtmlLabelInfo` 共约 28 万条记录，languageid=7（简体中文）约 14.7 万条
> - uf_* 表本身的列名（如 `xmmc`）是拼音缩写，**没有内置中文注释**，必须通过上述三表反查
