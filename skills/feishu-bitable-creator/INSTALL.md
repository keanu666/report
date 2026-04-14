# 📦 安装与配置

## 技能文件位置

```
/home/chando/.openclaw/workspace/skills/feishu-bitable-creator/
```

## 已注册到 OpenClaw

工具已集成到 Feishu 扩展中，位置：
```
/home/chando/openclaw/extensions/feishu/src/bitable-creator.ts
```

## 可用工具

注册后，你可以在 OpenClaw 中使用以下工具：

### 1. `feishu_bitable_create_table`

创建单个数据表

**参数：**
- `app_token` (string): 多维表格 Token
- `table_name` (string): 表名
- `fields` (array): 字段数组
  - `field_name` (string): 字段名
  - `type` (number): 字段类型 (1=文本，2=数字，3=单选，4=多选，5=日期，7=复选框，11=人员)
  - `property` (object, 可选): 字段属性
- `view_name` (string, 可选): 视图名称，默认"默认视图"

**示例：**
```
feishu_bitable_create_table(
  app_token="FUAmbD3DIakMQSsHxaicY9KLnyc",
  table_name="项目表",
  fields=[
    {"field_name": "项目名称", "type": 1},
    {"field_name": "项目类型", "type": 3, "property": {"options": [{"name": "开发"}, {"name": "设计"}]}},
    {"field_name": "开始日期", "type": 5},
    {"field_name": "负责人", "type": 11}
  ]
)
```

### 2. `feishu_bitable_create_tables`

批量创建数据表

**参数：**
- `app_token` (string): 多维表格 Token
- `tables` (array): 表定义数组
  - `name` (string): 表名
  - `fields` (array): 字段数组
  - `view_name` (string, 可选): 视图名称

**示例：**
```
feishu_bitable_create_tables(
  app_token="FUAmbD3DIakMQSsHxaicY9KLnyc",
  tables=[
    {
      "name": "项目表",
      "fields": [
        {"field_name": "项目名称", "type": 1},
        {"field_name": "状态", "type": 3, "property": {"options": [{"name": "进行中"}]}}
      ]
    },
    {
      "name": "任务表",
      "fields": [
        {"field_name": "任务名称", "type": 1},
        {"field_name": "优先级", "type": 3, "property": {"options": [{"name": "高"}, {"name": "低"}]}}
      ]
    }
  ]
)
```

## 权限要求

飞书应用需要以下权限：

- ✅ `base:app:read` - 读取多维表格
- ✅ `base:table:create` - 创建数据表
- ✅ `base:field:create` - 创建字段
- ✅ `base:record:create` - 创建记录（可选）

## 配置飞书应用

### 1. 创建应用

访问 [飞书开发者后台](https://open.feishu.cn/app) 创建自建应用

### 2. 添加权限

在 "权限管理" 页面添加上述权限

### 3. 发布应用

- 填写版本号
- 提交审核（如需）
- 启用应用

### 4. 获取凭证

在 "凭证与基础信息" 页面获取：
- App ID
- App Secret

## 重启 Gateway

修改后需要重启 OpenClaw Gateway：

```bash
openclaw gateway restart
```

或者使用工具：
```
gateway(action="restart", reason="加载新工具")
```

## 验证安装

重启后，检查工具是否可用：

1. 在对话中询问："我有哪些飞书工具？"
2. 或尝试调用工具查看是否响应

## 故障排查

### 工具未注册

检查：
1. `bitable-creator.ts` 文件是否存在
2. `index.ts` 是否正确导入和调用
3. Gateway 是否已重启

### 权限错误

检查：
1. 应用是否有足够权限
2. 多维表格是否已授权给应用
3. App ID 和 Secret 是否正确

### SDK 找不到

确保已安装依赖：
```bash
cd /home/chando/openclaw/extensions/feishu
npm install @larksuiteoapi/node-sdk
```

## 独立使用技能

如果不使用 OpenClaw 集成，可以独立运行：

```bash
cd /home/chando/.openclaw/workspace/skills/feishu-bitable-creator
node create-tables.js
```

需要先在脚本中配置：
- App ID
- App Secret
- 多维表格 Token
- 表定义

## 更新技能

1. 修改 `/home/chando/.openclaw/workspace/skills/feishu-bitable-creator/` 中的文件
2. 复制到 `/home/chando/openclaw/extensions/feishu/src/bitable-creator.ts`
3. 重启 Gateway

## 备份

技能源码备份在：
```
/home/chando/.openclaw/workspace/skills/feishu-bitable-creator/
```

修改 OpenClaw 扩展前建议先备份。
