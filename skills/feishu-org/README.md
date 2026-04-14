# 飞书组织架构工具 - 使用说明

## 快速开始

### 步骤 1：获取飞书应用凭证

**方法 A：从飞书开放平台获取**

1. 访问 https://open.feishu.cn/app
2. 创建或选择你的应用
3. 进入「凭证与基础信息」
4. 记录 `App ID` 和 `App Secret`

**方法 B：从现有插件配置读取**

插件会自动管理凭证，但脚本需要手动提供。

---

### 步骤 2：开通通讯录权限

1. 在飞书开放平台，进入「权限管理」
2. 切换到**应用身份权限**
3. 勾选以下权限：
   - ✅ `contact:user.base:readonly` - 获取用户基本信息
   - ✅ `contact:user.readonly` - 获取用户详细信息
   - ✅ `contact:department.base:readonly` - 获取部门基本信息
   - ✅ `contact:department.readonly` - 获取部门详细信息
4. 提交审批（需要管理员审批）

---

### 步骤 3：设置环境变量

```bash
# 临时设置（当前会话）
export FEISHU_APP_ID="cli_xxxxxxxxxxxxxxxxxxxx"
export FEISHU_APP_SECRET="xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx"

# 永久设置（添加到 ~/.bashrc 或 ~/.zshrc）
echo 'export FEISHU_APP_ID="cli_xxxxxxxxxxxxxxxxxxxx"' >> ~/.bashrc
echo 'export FEISHU_APP_SECRET="xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx"' >> ~/.bashrc
source ~/.bashrc
```

---

### 步骤 4：使用工具

#### Python 版本（推荐）

```bash
# 获取马绅惟的直接下属
python ~/.openclaw/workspace/skills/feishu-org/feishu-org.py get-reports ou_e26cad9ffe00b1737ff10db0c1984f6b

# 获取部门成员
python ~/.openclaw/workspace/skills/feishu-org/feishu-org.py get-members 3671520

# 获取用户信息
python ~/.openclaw/workspace/skills/feishu-org/feishu-org.py get-user ou_e26cad9ffe00b1737ff10db0c1984f6b

# 获取直属上级
python ~/.openclaw/workspace/skills/feishu-org/feishu-org.py get-manager ou_e26cad9ffe00b1737ff10db0c1984f6b
```

#### Bash 版本（备用）

```bash
# 获取马绅惟的直接下属
~/.openclaw/workspace/skills/feishu-org/feishu-org.sh get-reports ou_e26cad9ffe00b1737ff10db0c1984f6b
```

---

## 实际案例：给马绅惟的下属批量创建任务

### 完整流程

```bash
# 1. 设置环境变量
export FEISHU_APP_ID="你的AppID"
export FEISHU_APP_SECRET="你的AppSecret"

# 2. 获取马绅惟的 open_id
feishu_search_user(query="马绅惟")
# 返回: open_id = "ou_e26cad9ffe00b1737ff10db0c1984f6b"

# 3. 获取直接下属列表
python ~/.openclaw/workspace/skills/feishu-org/feishu-org.py get-reports ou_e26cad9ffe00b1737ff10db0c1984f6b

# 输出示例:
# 直接下属 (3 人):
#   1. 张三
#      open_id: ou_xxx1
#      user_id: xxx1
#   2. 李四
#      open_id: ou_xxx2
#      user_id: xxx2
#   3. 王五
#      open_id: ou_xxx3
#      user_id: xxx3

# 4. 批量创建飞书任务（使用飞书官方工具）
# 对每个下属调用 feishu_task_task
```

---

## 如何在我的 OpenClaw 中集成

由于这个工具需要应用身份权限，不能直接作为 OpenClaw 工具使用。但你可以在 OpenClaw 中这样调用：

### 方案 A：使用 exec 工具

```bash
# 在 OpenClaw 中执行
exec: python ~/.openclaw/workspace/skills/feishu-org/feishu-org.py get-reports ou_e26cad9ffe00b1737ff10db0c1984f6b
```

### 方案 B：创建别名（推荐）

```bash
# 在 ~/.bashrc 中添加别名
alias feishu-reports='python ~/.openclaw/workspace/skills/feishu-org/feishu-org.py get-reports'
alias feishu-members='python ~/.openclaw/workspace/skills/feishu-org/feishu-org.py get-members'

# 然后直接使用
feishu-reports ou_e26cad9ffe00b1737ff10db0c1984f6b
```

---

## 常见问题

### Q: 如何获取 App ID 和 App Secret？

A:
1. 访问 https://open.feishu.cn/app
2. 选择你的应用
3. 进入「凭证与基础信息」
4. 复制 App ID 和 App Secret

---

### Q: 为什么返回 "权限不足"？

A:
1. 检查是否开通了**应用身份权限**（不是用户身份权限）
2. 确认管理员已审批通过
3. 检查 App ID 和 App Secret 是否正确

---

### Q: 如何获取用户的 open_id？

A:
1. 在 OpenClaw 中使用 `feishu_search_user`
2. 或者在飞书客户端中查看用户信息

---

### Q: 可以获取整个组织架构吗？

A:
可以，但需要多次调用：
1. 先获取根部门 ID
2. 递归获取所有子部门
3. 对每个部门调用 `get-members`

---

### Q: Python 版本和 Bash 版本有什么区别？

A:
- Python 版本：功能更完善，错误处理更好，支持更复杂操作
- Bash 版本：轻量级，但需要 jq 才能获得好的输出格式

推荐使用 Python 版本。

---

## 安全建议

1. **不要提交凭证到 Git**：App Secret 应该保密
2. **使用环境变量**：避免将凭证硬编码在脚本中
3. **最小权限原则**：只开通必需的通讯录权限

---

## 扩展功能

### 按部门筛选下属

```bash
python ~/.openclaw/workspace/skills/feishu-org/feishu-org.py get-reports ou_e26cad9ffe00b1737ff10db0c1984f6b 3671520
```

### 导出部门成员到 CSV

```python
# 创建一个辅助脚本
import csv
client = FeishuOrgClient()
members = client.get_department_members("3671520")

with open('members.csv', 'w', newline='', encoding='utf-8') as f:
    writer = csv.writer(f)
    writer.writerow(['姓名', 'open_id', 'user_id', '职位', '邮箱'])
    for m in members:
        writer.writerow([m.get('name'), m.get('open_id'), m.get('user_id'),
                       m.get('position'), m.get('email')])
```

---

## 联系与反馈

如有问题或建议，请通过以下方式反馈：
- OpenClaw 技能中心：https://clawhub.com
- 飞书开放社区