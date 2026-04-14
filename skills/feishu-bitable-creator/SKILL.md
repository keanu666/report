# feishu-bitable-creator

飞书多维表格自动创建技能

## 功能

自动在飞书多维表格中创建数据表，支持：
- 创建单个或多个数据表
- 自动配置字段（文本、数字、日期、单选、多选、人员、复选框等）
- 批量创建字段选项（单选/多选）
- 支持关联字段配置

## 使用方法

### 通过 exec 调用

```bash
node /path/to/feishu-bitable-creator/create-tables.js
```

### 参数配置

在脚本中配置：
- `APP_ID`: 飞书应用 App ID
- `APP_SECRET`: 飞书应用 App Secret
- `APP_TOKEN`: 多维表格 Token
- `tables`: 表定义数组

### 表定义格式

```javascript
{
  name: '表名',
  fields: [
    { field_name: '字段名', type: 1 },  // 1=文本
    { field_name: '单选字段', type: 3, property: { options: [{ name: '选项 1' }, { name: '选项 2' }] } },
    { field_name: '日期字段', type: 5 },
    { field_name: '人员字段', type: 11 },
    { field_name: '复选框', type: 7 },
    { field_name: '数字', type: 2 }
  ]
}
```

### 字段类型

| 类型 | ID | 说明 |
|------|-----|------|
| TEXT | 1 | 文本 |
| NUMBER | 2 | 数字 |
| SINGLE_SELECT | 3 | 单选 |
| MULTI_SELECT | 4 | 多选 |
| DATETIME | 5 | 日期 |
| CHECKBOX | 7 | 复选框 |
| USER | 11 | 人员 |

## 依赖

- `@larksuiteoapi/node-sdk`
- Node.js 18+

## 权限要求

飞书应用需要以下权限：
- `base:app:read` - 读取多维表格
- `base:table:create` - 创建数据表
- `base:field:create` - 创建字段
- `base:record:create` - 创建记录

## 示例

```javascript
const tables = [
  {
    name: '项目表',
    fields: [
      { field_name: '项目名称', type: 1 },
      { field_name: '项目类型', type: 3, property: { options: [{ name: '开发' }, { name: '设计' }] } },
      { field_name: '开始日期', type: 5 },
      { field_name: '负责人', type: 11 }
    ]
  }
];
```

## 错误处理

- `99992402`: 字段验证失败 - 检查字段配置格式
- `9499`: Bad Request - 检查请求参数
- `99991154`: 权限不足 - 检查应用权限配置

## 注意事项

1. 单选字段选项不要带 `color` 属性（容易验证失败）
2. 日期字段默认格式为 `yyyy-MM-dd`
3. 人员字段需要飞书用户 ID
4. 关联字段需要额外的配置（目前不支持自动创建）

## 文件结构

```
feishu-bitable-creator/
├── SKILL.md              # 技能说明
├── create-tables.js      # 主脚本
├── bitable-creator.js    # 核心函数库
└── examples/             # 示例配置
    └── project-management.js
```

## 更新日志

- 2026-03-03: 初始版本，支持基本字段类型创建
