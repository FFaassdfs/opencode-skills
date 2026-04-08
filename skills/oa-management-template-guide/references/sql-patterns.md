# OA SQL Patterns

这份参考文件用于快速复用 OA 管理模板开发中的常用 SQL 查询。

## 1. 主表探查

```sql
SELECT TOP 20 *
FROM uf_xxxxx
ORDER BY id DESC
```

用途：

- 看主表字段全貌
- 看值是中文、数字、ID 还是链接
- 判断是否存在 `requestId / formmodeid / modedatacreater`

## 2. 明细表探查

```sql
SELECT TOP 20 *
FROM uf_xxxxx_dt1
ORDER BY id DESC
```

```sql
SELECT TOP 20 *
FROM uf_xxxxx_dt2
ORDER BY id DESC
```

```sql
SELECT TOP 20 *
FROM uf_xxxxx_dt3
ORDER BY id DESC
```

用途：

- 判断明细表是否存在、是否有数据
- 判断每张明细表的业务含义
- 确认通过 `mainid -> 主表.id` 关联

## 3. distinct 值探查

```sql
SELECT DISTINCT somefield
FROM uf_xxxxx
ORDER BY somefield
```

用途：

- 判断字段是否是枚举/布尔/状态字段
- 判断字段到底是代码值还是中文值
- 识别低基数字段

## 4. 主表与明细表联查样本

```sql
SELECT TOP 50
    m.id AS main_id,
    m.xmmc,
    d.*
FROM uf_xxxxx m
LEFT JOIN uf_xxxxx_dt1 d ON d.mainid = m.id
ORDER BY m.id DESC, d.id DESC
```

用途：

- 快速确认主表和明细表关系
- 看某张明细表到底记录什么内容

## 5. 人员 ID -> 姓名

```sql
SELECT id, lastname
FROM HrmResource
WHERE id IN (4540, 3724, 7010)
```

常见适用字段：

- `djr`
- `tbr`
- `modedatacreater`
- `modedatamodifier`

## 6. 部门 ID -> 部门名

```sql
SELECT id, departmentname
FROM HrmDepartment
WHERE id IN (701, 702, 703)
```

常见适用字段：

- `gzbm`
- `bm`
- `departmentid`
- 其他看起来像部门字段的 ID 列

## 7. 查询模型基础信息

```sql
SELECT id, modename, table_name, formid
FROM modeinfo
WHERE table_name = 'uf_xxxxx'
```

用途：

- 确认 `uf_*` 表对应哪个模型
- 找 `modeid` 和 `formid`

## 8. 查询字段中文名

```sql
SELECT fa.fieldname, fa.fieldlabel, fa.fieldtype, fa.htmltype
FROM modefieldattr fa
JOIN modeinfo m ON fa.modeid = m.id
WHERE m.table_name = 'uf_xxxxx'
ORDER BY fa.fieldid
```

用途：

- 从字段英文名/拼音名反查中文含义
- 辅助判断字段类型

## 9. 查询多个候选字段的元数据

```sql
SELECT fieldname, fieldlabel, htmltype, fieldtype
FROM mode_expressionbase
WHERE fieldname IN ('tzzt', 'sfzjgd', 'cplx', 'gzbm')
ORDER BY fieldname
```

用途：

- 批量看可疑字段是否像枚举/单选字段
- 辅助建立显示映射

注意：

- 这个表不一定能稳定给出可靠的选项中文
- 需要和真实数据一起验证

## 10. 查询 `workflow_formdict`

```sql
SELECT id, fieldname, description, fieldhtmltype
FROM workflow_formdict
WHERE fieldname IN ('xmmc', 'tzzt', 'gzbm')
ORDER BY fieldname
```

用途：

- 当模型元数据不完整时，补充看字段描述

## 11. 查询 `cus_formdict`

```sql
SELECT fieldname, fieldlabel, fieldhtmltype, fielddbtype, type, scope
FROM cus_formdict
WHERE fieldname IN ('xmmc', 'tzzt', 'gzbm')
ORDER BY fieldname
```

用途：

- 查询部分自定义字段定义
- 补充字段中文名和类型线索

## 12. 查询表是否存在

```sql
SELECT COUNT(*) AS cnt
FROM INFORMATION_SCHEMA.TABLES
WHERE TABLE_NAME = 'uf_xxxxx_dt2'
```

用途：

- 判断某张明细表到底存在不存在

## 13. 查询表字段列表

```sql
SELECT COLUMN_NAME, DATA_TYPE
FROM INFORMATION_SCHEMA.COLUMNS
WHERE TABLE_NAME = 'uf_xxxxx'
ORDER BY ORDINAL_POSITION
```

用途：

- 当 `SELECT *` 还不够清晰时，进一步看表结构

## 14. 浏览按钮 / 组织字段的进一步判断

如果字段值长得像 ID，但不确定是人、部门还是别的，建议这样排查：

1. 先看 distinct 值
2. 再尝试对 `HrmResource`
3. 再尝试对 `HrmDepartment`
4. 再结合字段标签与业务上下文判断

例如：

```sql
SELECT DISTINCT gzbm
FROM uf_HCZHCP_CPDA
ORDER BY gzbm
```

```sql
SELECT id, departmentname
FROM HrmDepartment
WHERE id IN (701, 702)
```

## 15. SQL Server 2008 R2 注意事项

- 不支持 `OFFSET ... FETCH`
- 某些 `text/ntext/image` 字段不能直接参与某些比较或排序
- 对中文字段和旧表结构要保守处理
- 只读账号下默认只做 `SELECT`

## 16. 推荐探查顺序

拿到一个新 OA 模板对象时，优先按这个顺序查：

1. 主表 `TOP 20`
2. 明细表 `TOP 20`
3. 关键字段 `DISTINCT`
4. `modeinfo`
5. `modefieldattr`
6. 人员/部门映射表

不要一开始就直接写页面或直接写枚举映射。
