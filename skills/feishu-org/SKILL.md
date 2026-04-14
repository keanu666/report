---
name: Feishu Organization
slug: feishu-org
version: 1.0.0
homepage: https://github.com/openclaw/feishu-org
description: 飞书组织架构工具 - 获取用户的直接下属、上级信息和部门成员
metadata: {"clawdbot":{"emoji":"🏢","requires":{"bins":[]},"os":["linux","darwin","win32"]}}
---

## 概述

此 Skill 通过调用飞书 Open API 的通讯录接口，获取用户的组织架构信息：
- 直接下属列表
- 上级信息
- 部门成员列表

## 前置条件

1. 已安装飞书官方插件 `@larksuiteoapi/feishu-openclaw-plugin`
2. 已完成用户授权
3. **必需**：在飞书开放平台开通以下应用身份权限：
   - `contact:user.base:readonly` - 获取用户基本信息
   - `contact:user.readonly` - 获取用户详细信息（包括部门、职位）
   - `contact:department.base:readonly` - 获取部门基本信息
   - `contact:department.readonly` - 获取部门详细信息

## 工具列表

### 1. feishu_org_get_direct_reports

获取指定用户的直接下属列表。

**参数：**
- `user_open_id` (string, 必需) - 用户的 open_id
- `department_id` (string, 可选) - 限制在指定部门内查找

**返回：**
```json
{
  "user_name": "用户姓名",
  "user_open_id": "ou_xxx",
  "direct_reports": [
    {"name": "下属1", "open_id": "ou_xxx", "user_id": "xxx"},
    {"name": "下属2", "open_id": "ou_xxx", "user_id": "xxx"}
  ]
}
```

**实现原理：**
1. 调用飞书 API `getDepartment` 获取部门完整成员列表
2. 筛选出汇报给指定用户的成员

### 2. feishu_org_get_manager

获取指定用户的直属上级。

**参数：**
- `user_open_id` (string, 必需) - 用户的 open_id

**返回：**
```json
{
  "user_name": "用户姓名",
  "manager": {
    "name": "上级姓名",
    "open_id": "ou_xxx",
    "user_id": "xxx"
  }
}
```

### 3. feishu_org_get_department_members

获取指定部门的成员列表。

**参数：**
- `department_id` (string, 必需) - 部门 ID
- `max_results` (number, 可选, 默认: 50) - 最大返回数量

**返回：**
```json
{
  "department_id": "xxx",
  "department_name": "部门名称",
  "members": [
    {"name": "成员1", "open_id": "ou_xxx", "user_id": "xxx"},
    {"name": "成员2", "open_id": "ou_xxx", "user_id": "xxx"}
  ]
}
```

## 使用示例

### 获取马绅惟的直接下属

```
先通过 feishu_search_user 获取 open_id:
feishu_search_user(query="马绅惟")
→ open_id: "ou_e26cad9ffe00b1737ff10db0c1984f6b"

然后获取直接下属:
feishu_org_get_direct_reports(user_open_id="ou_e26cad9ffe00b1737ff10db0c1984f6b")
```

### 批量给下属创建任务

```
1. 获取下属列表
2. 使用 feishu_task_task 批量创建任务
```

## 权限配置

### 步骤 1：登录飞书开放平台

访问 https://open.feishu.cn/app

### 步骤 2：进入权限管理

切换到**应用身份权限**（不是用户身份权限）

### 步骤 3：添加通讯录权限

勾选以下权限：
- `contact:user.base:readonly`
- `contact:user.readonly`
- `contact:department.base:readonly`
- `contact:department.readonly`

### 步骤 4：提交审批

提交后等待管理员审批通过

### 步骤 5：重新授权

审批通过后，执行以下命令重新授权：
```
feishu_oauth_batch_auth
```

## 限制

1. **需要应用身份权限**：此 Skill 必须使用应用身份调用，不能使用用户身份
2. **需要管理员审批**：通讯录权限通常需要飞书管理员审批
3. **数据范围限制**：只能获取有权限查看的组织架构信息

## 故障排除

### 错误：权限不足

**症状：** 返回 `permission_denied` 或 `403`

**解决：**
1. 检查是否开通了应用身份权限
2. 确认管理员已审批通过
3. 重新执行 `feishu_oauth_batch_auth`

### 错误：找不到用户

**症状：** 返回空列表或 `user_not_found`

**解决：**
1. 确认 user_open_id 正确
2. 使用 `feishu_search_user` 先搜索获取正确的 open_id

### 错误：插件未加载

**症状：** 工具不存在

**解决：**
1. 检查飞书官方插件是否已安装
2. 执行 `openclaw doctor` 检查插件状态
3. 重启 Gateway：`openclaw gateway restart`

## 相关资源

- 飞书开放平台：https://open.feishu.cn
- 通讯录 API 文档：https://open.feishu.cn/document/server-docs/contact/introduction
- OpenClaw 技能中心：https://clawhub.com

## 反馈与贡献

如有问题或建议，请通过以下方式反馈：
- GitHub Issues
- 飞书社区：https://clawhub.com