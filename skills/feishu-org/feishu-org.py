#!/usr/bin/env python3
"""
飞书组织架构工具
获取用户的直接下属、上级和部门成员信息
"""

import os
import sys
import json
import requests
from typing import List, Dict, Optional

# 飞书 API 基础 URL
FEISHU_API_BASE = "https://open.feishu.cn/open-apis"

# 颜色输出
class Colors:
    RED = '\033[0;31m'
    GREEN = '\033[0;32m'
    YELLOW = '\033[1;33m'
    NC = '\033[0m'

def error(msg: str):
    print(f"{Colors.RED}错误: {msg}{Colors.RED}", file=sys.stderr)

def warn(msg: str):
    print(f"{Colors.YELLOW}警告: {msg}{Colors.NC}", file=sys.stderr)

def success(msg: str):
    print(f"{Colors.GREEN}{msg}{Colors.NC}")

class FeishuOrgClient:
    def __init__(self, app_id: Optional[str] = None, app_secret: Optional[str] = None):
        self.app_id = app_id or os.environ.get('FEISHU_APP_ID')
        self.app_secret = app_secret or os.environ.get('FEISHU_APP_SECRET')
        self.tenant_access_token = None

        if not self.app_id or not self.app_secret:
            error("请设置 FEISHU_APP_ID 和 FEISHU_APP_SECRET 环境变量")
            sys.exit(1)

    def get_tenant_access_token(self) -> str:
        """获取租户访问令牌"""
        url = f"{FEISHU_API_BASE}/auth/v3/tenant_access_token/internal"
        payload = {
            "app_id": self.app_id,
            "app_secret": self.app_secret
        }

        try:
            response = requests.post(url, json=payload)
            response.raise_for_status()
            data = response.json()

            if data.get('code') != 0:
                error(f"获取 token 失败: {data.get('msg')}")
                sys.exit(1)

            self.tenant_access_token = data.get('tenant_access_token')
            success(f"Token 获取成功")
            return self.tenant_access_token

        except requests.exceptions.RequestException as e:
            error(f"请求失败: {e}")
            sys.exit(1)

    def _api_request(self, endpoint: str, method: str = "GET", **kwargs) -> Dict:
        """调用飞书 API"""
        if not self.tenant_access_token:
            self.get_tenant_access_token()

        url = f"{FEISHU_API_BASE}/{endpoint}"
        headers = {
            "Authorization": f"Bearer {self.tenant_access_token}",
            "Content-Type": "application/json; charset=utf-8"
        }

        try:
            if method == "GET":
                response = requests.get(url, headers=headers, **kwargs)
            elif method == "POST":
                response = requests.post(url, headers=headers, json=kwargs.get('json'))
            else:
                error(f"不支持的 HTTP 方法: {method}")
                sys.exit(1)

            response.raise_for_status()
            data = response.json()

            if data.get('code') != 0:
                error(f"API 调用失败: {data.get('msg')}")
                sys.exit(1)

            return data

        except requests.exceptions.RequestException as e:
            error(f"请求失败: {e}")
            sys.exit(1)

    def get_user(self, user_open_id: str) -> Dict:
        """获取用户信息"""
        data = self._api_request(f"contact/v3/users/{user_open_id}")
        return data.get('data', {}).get('user', {})

    def get_department(self, department_id: str) -> Dict:
        """获取部门信息"""
        data = self._api_request(f"contact/v3/departments/{department_id}")
        return data.get('data', {}).get('department', {})

    def get_department_members(self, department_id: str, page_size: int = 50) -> List[Dict]:
        """获取部门成员列表"""
        all_members = []
        page_token = ""

        while True:
            params = {
                "department_id": department_id,
                "page_size": page_size
            }
            if page_token:
                params["page_token"] = page_token

            data = self._api_request("contact/v3/users", params=params)
            items = data.get('data', {}).get('items', [])

            all_members.extend(items)

            has_more = data.get('data', {}).get('has_more', False)
            if not has_more:
                break

            page_token = data.get('data', {}).get('page_token', "")

        return all_members

    def get_direct_reports(self, user_open_id: str, department_id: Optional[str] = None) -> List[Dict]:
        """获取用户的直接下属"""
        # 获取用户信息
        user_info = self.get_user(user_open_id)

        user_name = user_info.get('name', 'Unknown')
        user_dept_ids = user_info.get('department_ids', [])

        print(f"用户: {user_name} (open_id: {user_open_id})")

        # 如果指定了部门，使用指定部门；否则使用用户所在部门
        if not department_id and user_dept_ids:
            department_id = user_dept_ids[0]

        if not department_id:
            error("无法获取部门信息")
            return []

        # 获取部门信息
        dept_info = self.get_department(department_id)
        dept_name = dept_info.get('name', 'Unknown')
        print(f"部门: {dept_name} (id: {department_id})")

        # 获取部门所有成员
        print("正在获取部门成员...")
        members = self.get_department_members(department_id)

        # 筛选出直接下属（leader_id 等于当前用户）
        direct_reports = [
            member for member in members
            if member.get('leader_id') == user_open_id
        ]

        return direct_reports

    def get_manager(self, user_open_id: str) -> Optional[Dict]:
        """获取用户的直属上级"""
        user_info = self.get_user(user_open_id)
        leader_id = user_info.get('leader_id')

        if not leader_id:
            return None

        manager_info = self.get_user(leader_id)
        return manager_info


def print_user_list(users: List[Dict], title: str = ""):
    """打印用户列表"""
    if title:
        print(f"\n{title} ({len(users)} 人):")

    if not users:
        print("  (无)")
        return

    for i, user in enumerate(users, 1):
        name = user.get('name', 'Unknown')
        open_id = user.get('open_id', 'N/A')
        user_id = user.get('user_id', 'N/A')
        print(f"  {i}. {name}")
        print(f"     open_id: {open_id}")
        print(f"     user_id: {user_id}")


def show_help():
    print("""
飞书组织架构工具

用法:
    python feishu-org.py <command> [arguments]

命令:
    get-user <open_id>              获取用户信息
    get-department <department_id>  获取部门信息
    get-members <department_id>     获取部门成员列表
    get-reports <open_id> [dept_id] 获取直接下属列表
    get-manager <open_id>           获取直属上级

环境变量:
    FEISHU_APP_ID                  飞书应用 ID
    FEISHU_APP_SECRET              飞书应用密钥

示例:
    # 设置环境变量
    export FEISHU_APP_ID="cli_xxx"
    export FEISHU_APP_SECRET="xxx"

    # 获取用户信息
    python feishu-org.py get-user ou_e26cad9ffe00b1737ff10db0c1984f6b

    # 获取直接下属
    python feishu-org.py get-reports ou_e26cad9ffe00b1737ff10db0c1984f6b

    # 获取部门成员
    python feishu-org.py get-members 3671520

注意:
    需要在飞书开放平台开通以下应用身份权限:
    - contact:user.base:readonly
    - contact:user.readonly
    - contact:department.base:readonly
    - contact:department.readonly
""")


def main():
    if len(sys.argv) < 2:
        show_help()
        sys.exit(0)

    client = FeishuOrgClient()
    command = sys.argv[1]

    if command == "get-user":
        if len(sys.argv) != 3:
            error("用法: get-user <open_id>")
            sys.exit(1)
        user_info = client.get_user(sys.argv[2])
        print(json.dumps(user_info, indent=2, ensure_ascii=False))

    elif command == "get-department":
        if len(sys.argv) != 3:
            error("用法: get-department <department_id>")
            sys.exit(1)
        dept_info = client.get_department(sys.argv[2])
        print(json.dumps(dept_info, indent=2, ensure_ascii=False))

    elif command == "get-members":
        if len(sys.argv) != 3:
            error("用法: get-members <department_id>")
            sys.exit(1)
        members = client.get_department_members(sys.argv[2])
        print_user_list(members, "部门成员")

    elif command == "get-reports":
        if len(sys.argv) < 3:
            error("用法: get-reports <open_id> [department_id]")
            sys.exit(1)
        user_open_id = sys.argv[2]
        department_id = sys.argv[3] if len(sys.argv) > 3 else None
        reports = client.get_direct_reports(user_open_id, department_id)
        print_user_list(reports, "直接下属")

    elif command == "get-manager":
        if len(sys.argv) != 3:
            error("用法: get-manager <open_id>")
            sys.exit(1)
        manager = client.get_manager(sys.argv[2])
        if manager:
            print("\n直属上级:")
            print(f"  姓名: {manager.get('name', 'Unknown')}")
            print(f"  open_id: {manager.get('open_id', 'N/A')}")
            print(f"  user_id: {manager.get('user_id', 'N/A')}")
        else:
            print("未找到直属上级")

    else:
        error(f"未知命令: {command}")
        show_help()
        sys.exit(1)


if __name__ == "__main__":
    main()