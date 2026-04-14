# 🛠️ 飞书多维表格创建技能

自动在飞书多维表格中创建数据表的工具技能

## 📦 安装

```bash
cd /path/to/feishu-bitable-creator
npm install @larksuiteoapi/node-sdk
```

或者使用 feishu 扩展的依赖（如果已安装）：
```bash
# 脚本会自动从 feishu 扩展加载 SDK
```

## 🚀 快速开始

### 1. 配置凭证

编辑 `create-tables.js`：

```javascript
const CONFIG = {
  appId: '你的 App ID',
  appSecret: '你的 App Secret',
  domain: 'feishu' // 或 'lark'
};

const APP_TOKEN = '你的多维表格 Token';
```

### 2. 定义表结构

```javascript
const TABLES = [
  {
    name: '我的表',
    fields: [
      { field_name: '字段名', type: 1 },  // 1=文本
      { field_name: '单选', type: 3, property: { options: [{ name: '选项 1' }] } }
    ]
  }
];
```

### 3. 运行

```bash
node create-tables.js
```

## 📋 字段类型

| 类型 | ID | 辅助函数 | 说明 |
|------|-----|----------|------|
| TEXT | 1 | `textField()` | 文本 |
| NUMBER | 2 | `numberField()` | 数字 |
| SINGLE_SELECT | 3 | `singleSelectField(name, options)` | 单选 |
| MULTI_SELECT | 4 | `multiSelectField(name, options)` | 多选 |
| DATETIME | 5 | `dateField(name, format)` | 日期 |
| CHECKBOX | 7 | `checkboxField()` | 复选框 |
| USER | 11 | `userField()` | 人员 |

## 💡 使用示例

### 简单示例

```javascript
const { createClient, createTables, textField, singleSelectField } = require('./bitable-creator.js');

const client = createClient({
  appId: 'cli_xxx',
  appSecret: 'xxx'
});

const tables = [{
  name: '项目表',
  fields: [
    textField('项目名称'),
    singleSelectField('状态', ['进行中', '已完成'])
  ]
}];

createTables(client, '你的 APP_TOKEN', tables);
```

### 使用示例配置

```javascript
const projectTables = require('./examples/project-management.js');
const { createClient, createTables } = require('./bitable-creator.js');

const client = createClient(CONFIG);
createTables(client, APP_TOKEN, projectTables);
```

## 🔧 API 参考

### createClient(config)

创建飞书客户端

```javascript
createClient({
  appId: 'cli_xxx',
  appSecret: 'xxx',
  domain: 'feishu' // 或 'lark'
})
```

### createTable(client, appToken, tableName, fields, viewName)

创建单个数据表

```javascript
await createTable(client, appToken, '表名', [
  { field_name: '字段', type: 1 }
]);
```

### createTables(client, appToken, tables)

批量创建数据表

```javascript
await createTables(client, appToken, [
  { name: '表 1', fields: [...] },
  { name: '表 2', fields: [...] }
]);
```

## ⚠️ 注意事项

1. **单选字段选项**：不要带 `color` 属性，容易验证失败
2. **日期格式**：默认 `yyyy-MM-dd`
3. **人员字段**：需要飞书用户 ID（OU_xxx 格式）
4. **关联字段**：需要额外的配置，目前不支持自动创建双向关联

## 🐛 常见错误

| 错误码 | 说明 | 解决方案 |
|--------|------|----------|
| 99992402 | 字段验证失败 | 检查字段配置格式，移除 color 属性 |
| 9499 | Bad Request | 检查请求参数和 APP_TOKEN |
| 99991154 | 权限不足 | 在飞书开发者后台添加应用权限 |

## 📁 文件结构

```
feishu-bitable-creator/
├── README.md                 # 本文件
├── SKILL.md                  # 技能详细说明
├── bitable-creator.js        # 核心函数库
├── create-tables.js          # 主脚本（可直接运行）
├── package.json              # 依赖配置
└── examples/
    └── project-management.js # 项目管理示例
```

## 📝 更新日志

- **1.0.0** (2026-03-03): 初始版本
  - 支持基本字段类型创建
  - 提供辅助函数简化配置
  - 包含项目管理示例

## 🔗 相关资源

- [飞书开放平台](https://open.feishu.cn/)
- [多维表格 API 文档](https://open.feishu.cn/document/ukTMukTMukTM/uAjLw4CM/ukTMukTMukTM/reference/bitable-v1/app-table/create)
- [OpenClaw 文档](https://docs.openclaw.ai)
