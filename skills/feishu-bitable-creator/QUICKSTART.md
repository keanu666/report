# 🚀 快速使用指南

## 方法一：直接运行脚本（最简单）

### 1. 编辑配置

打开 `create-tables.js`，修改配置：

```javascript
const CONFIG = {
  appId: 'cli_a92bdcf990badcd1',  // 你的 App ID
  appSecret: 'rDDzgikWrcM25sWR1vAx8cyIQMQ8JZeh',  // 你的 App Secret
  domain: 'feishu'
};

const APP_TOKEN = 'FUAmbD3DIakMQSsHxaicY9KLnyc';  // 你的多维表格 Token
```

### 2. 定义表结构

在 `TABLES` 数组中添加你的表定义：

```javascript
const TABLES = [
  {
    name: '我的表',
    fields: [
      { field_name: '字段 1', type: 1 },  // 文本
      { field_name: '字段 2', type: 3, property: { options: [{ name: '选项 A' }, { name: '选项 B' }] } }  // 单选
    ]
  }
];
```

### 3. 运行

```bash
cd /path/to/feishu-bitable-creator
node create-tables.js
```

## 方法二：作为库使用（更灵活）

```javascript
const { createClient, createTables, textField, singleSelectField } = require('./bitable-creator.js');

// 创建客户端
const client = createClient({
  appId: '你的 App ID',
  appSecret: '你的 App Secret'
});

// 定义表
const tables = [{
  name: '项目表',
  fields: [
    textField('项目名称'),
    singleSelectField('状态', ['进行中', '已完成', '已取消'])
  ]
}];

// 创建
const results = await createTables(client, '你的 APP_TOKEN', tables);
console.log(results);
```

## 方法三：使用 OpenClaw 工具（如果已注册）

在 OpenClaw 中直接调用：

```
feishu_bitable_create_table(
  app_token="FUAmbD3DIakMQSsHxaicY9KLnyc",
  table_name="我的表",
  fields=[
    {"field_name": "字段名", "type": 1}
  ]
)
```

## 📋 字段类型速查

| 类型 | type 值 | 示例 |
|------|---------|------|
| 文本 | 1 | `{field_name: '名称', type: 1}` |
| 数字 | 2 | `{field_name: '数量', type: 2}` |
| 单选 | 3 | `{field_name: '状态', type: 3, property: {options: [{name: '选项'}]}}` |
| 多选 | 4 | `{field_name: '标签', type: 4, property: {options: [{name: '标签 A'}]}}` |
| 日期 | 5 | `{field_name: '日期', type: 5}` |
| 复选框 | 7 | `{field_name: '完成', type: 7}` |
| 人员 | 11 | `{field_name: '负责人', type: 11}` |

## 🎯 常用辅助函数

```javascript
const {
  textField,        // 文本字段
  numberField,      // 数字字段
  dateField,        // 日期字段
  singleSelectField, // 单选字段
  multiSelectField,  // 多选字段
  userField,        // 人员字段
  checkboxField     // 复选框字段
} = require('./bitable-creator.js');

// 使用示例
const fields = [
  textField('项目名称'),
  numberField('预算'),
  dateField('开始日期'),
  singleSelectField('优先级', ['P0', 'P1', 'P2', 'P3']),
  userField('负责人'),
  checkboxField('是否紧急')
];
```

## 🔍 获取多维表格 Token

1. 打开飞书多维表格
2. 查看 URL：`https://xxx.feishu.cn/base/TOKEN`
3. 复制 `TOKEN` 部分

例如：`https://yidtwc7476.feishu.cn/base/FUAmbD3DIakMQSsHxaicY9KLnyc`
Token 就是：`FUAmbD3DIakMQSsHxaicY9KLnyc`

## 🛠️ 获取飞书应用凭证

1. 访问 [飞书开发者后台](https://open.feishu.cn/app)
2. 选择你的应用
3. 点击 "凭证与基础信息"
4. 复制 App ID 和 App Secret

## ⚡ 完整示例

```javascript
const { createClient, createTables } = require('./bitable-creator.js');

async function main() {
  // 1. 创建客户端
  const client = createClient({
    appId: 'cli_xxx',
    appSecret: 'xxx',
    domain: 'feishu'
  });

  // 2. 定义表结构
  const tables = [
    {
      name: '客户管理表',
      fields: [
        { field_name: '客户名称', type: 1 },
        { field_name: '联系人', type: 1 },
        { field_name: '电话', type: 1 },
        { field_name: '客户类型', type: 3, property: { options: [{ name: '企业' }, { name: '个人' }] } },
        { field_name: '创建日期', type: 5 },
        { field_name: '负责人', type: 11 }
      ]
    }
  ];

  // 3. 创建表
  const results = await createTables(client, '你的 APP_TOKEN', tables);
  
  // 4. 查看结果
  console.log('创建完成:', results);
}

main();
```

## ❓ 遇到问题？

1. **权限错误**：检查应用是否有 `base:table:create` 权限
2. **字段验证失败**：移除单选选项的 `color` 属性
3. **找不到 SDK**：确保已安装 `@larksuiteoapi/node-sdk`

更多帮助见 [README.md](README.md) 或 [SKILL.md](SKILL.md)
