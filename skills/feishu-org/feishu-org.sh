#!/bin/bash
# 飞书组织架构工具
# 使用飞书 Open API 获取用户上下级关系

set -e

# 飞书应用配置
# 这些值需要从 ~/.openclaw/extensions/feishu-openclaw-plugin/src/core/token-store.js 中获取
# 或者从飞书开放平台获取
APP_ID="${FEISHU_APP_ID:-}"
APP_SECRET="${FEISHU_APP_SECRET:-}"
TENANT_ACCESS_TOKEN=""

# 颜色输出
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# 错误处理
error() {
    echo -e "${RED}错误: $1${NC}" >&2
    exit 1
}

warn() {
    echo -e "${YELLOW}警告: $1${NC}" >&2
}

success() {
    echo -e "${GREEN}$1${NC}"
}

# 检查依赖
check_dependencies() {
    if ! command -v curl &> /dev/null; then
        error "需要安装 curl"
    fi

    if ! command -v jq &> /dev/null; then
        warn "推荐安装 jq 以获得更好的 JSON 格式化"
    fi
}

# 获取 tenant_access_token
get_tenant_access_token() {
    if [ -z "$APP_ID" ] || [ -z "$APP_SECRET" ]; then
        error "请设置环境变量 FEISHU_APP_ID 和 FEISHU_APP_SECRET"
    fi

    echo "正在获取 tenant_access_token..."

    response=$(curl -s -X POST "https://open.feishu.cn/open-apis/auth/v3/tenant_access_token/internal" \
        -H "Content-Type: application/json; charset=utf-8" \
        -d "{\"app_id\":\"$APP_ID\",\"app_secret\":\"$APP_SECRET\"}")

    if command -v jq &> /dev/null; then
        error_code=$(echo "$response" | jq -r '.code // empty')
        if [ "$error_code" != "0" ] && [ -n "$error_code" ]; then
            error "获取 token 失败: $(echo "$response" | jq -r '.msg')"
        fi
        TENANT_ACCESS_TOKEN=$(echo "$response" | jq -r '.tenant_access_token')
    else
        # 简单的 grep 解析（不推荐）
        TENANT_ACCESS_TOKEN=$(echo "$response" | grep -o '"tenant_access_token":"[^"]*' | cut -d'"' -f4)
    fi

    if [ -z "$TENANT_ACCESS_TOKEN" ]; then
        error "无法解析 tenant_access_token"
    fi

    success "Token 获取成功"
}

# 调用飞书 API
feishu_api() {
    local endpoint="$1"
    shift

    curl -s -X GET "https://open.feishu.cn/open-apis/$endpoint" \
        -H "Authorization: Bearer $TENANT_ACCESS_TOKEN" \
        "$@"
}

# 获取用户信息
get_user() {
    local user_open_id="$1"

    echo "获取用户信息: $user_open_id"

    response=$(feishu_api "contact/v3/users/$user_open_id" \
        -H "Content-Type: application/json; charset=utf-8")

    if command -v jq &> /dev/null; then
        echo "$response" | jq '.'
    else
        echo "$response"
    fi
}

# 获取部门信息
get_department() {
    local department_id="$1"

    echo "获取部门信息: $department_id"

    response=$(feishu_api "contact/v3/departments/$department_id" \
        -H "Content-Type: application/json; charset=utf-8")

    if command -v jq &> /dev/null; then
        echo "$response" | jq '.'
    else
        echo "$response"
    fi
}

# 获取部门成员
get_department_members() {
    local department_id="$1"
    local page_size="${2:-50}"
    local page_token=""

    echo "获取部门成员: $department_id (每页 $page_size)"

    all_members=()

    while true; do
        url="contact/v3/users?page_size=$page_size&department_id=$department_id"
        if [ -n "$page_token" ]; then
            url="$url&page_token=$page_token"
        fi

        response=$(feishu_api "$url" \
            -H "Content-Type: application/json; charset=utf-8")

        if command -v jq &> /dev/null; then
            # 提取成员列表
            members=$(echo "$response" | jq -c '.data.items[]')
            if [ -n "$members" ]; then
                while IFS= read -r member; do
                    all_members+=("$member")
                done <<< "$members"
            fi

            # 检查是否有下一页
            has_more=$(echo "$response" | jq -r '.data.has_more // false')
            if [ "$has_more" = "false" ]; then
                break
            fi
            page_token=$(echo "$response" | jq -r '.data.page_token // empty')
        else
            echo "$response"
            break
        fi
    done

    # 输出所有成员
    if [ ${#all_members[@]} -gt 0 ]; then
        echo "部门成员列表 (${#all_members[@]} 人):"
        printf '%s\n' "${all_members[@]}"
    fi
}

# 获取用户的直接下属（通过部门成员筛选）
get_direct_reports() {
    local user_open_id="$1"
    local department_id="$2"

    echo "获取直接下属: $user_open_id"

    # 先获取用户信息
    user_info=$(get_user "$user_open_id")

    if command -v jq &> /dev/null; then
        user_name=$(echo "$user_info" | jq -r '.data.user.name')
        user_dept_id=$(echo "$user_info" | jq -r '.data.user.department_ids[0] // empty')

        echo "用户: $user_name (open_id: $user_open_id)"

        # 如果指定了部门，使用指定部门；否则使用用户所在部门
        if [ -z "$department_id" ] && [ -n "$user_dept_id" ]; then
            department_id="$user_dept_id"
        fi

        if [ -z "$department_id" ]; then
            error "无法获取部门信息"
        fi

        echo "部门: $department_id"

        # 获取部门成员
        echo "正在获取部门成员..."
        members=$(curl -s -X GET "https://open.feishu.cn/open-apis/contact/v3/users?page_size=50&department_id=$department_id" \
            -H "Authorization: Bearer $TENANT_ACCESS_TOKEN" \
            -H "Content-Type: application/json; charset=utf-8")

        # 筛选出直接下属（这里需要根据实际的汇报关系字段来筛选）
        # 飞书 API 的用户信息中包含 leader_id 字段，指向直属上级
        direct_reports=$(echo "$members" | jq -r ".data.items[] | select(.leader_id == \"$user_open_id\") | {name, open_id, user_id}")

        report_count=$(echo "$direct_reports" | wc -l)

        if [ "$report_count" -eq 0 ]; then
            echo "未找到直接下属"
        else
            echo "直接下属列表 ($report_count 人):"
            echo "$direct_reports" | jq '.'
        fi
    else
        echo "$user_info"
        warn "请安装 jq 以获得更好的输出格式"
    fi
}

# 帮助信息
show_help() {
    cat << EOF
飞书组织架构工具

用法:
    $0 <command> [arguments]

命令:
    get-user <open_id>              获取用户信息
    get-department <department_id>  获取部门信息
    get-members <department_id>     获取部门成员列表
    get-reports <open_id> [dept_id] 获取直接下属列表

环境变量:
    FEISHU_APP_ID                  飞书应用 ID
    FEISHU_APP_SECRET              飞书应用密钥

示例:
    # 设置环境变量
    export FEISHU_APP_ID="cli_xxx"
    export FEISHU_APP_SECRET="xxx"

    # 获取用户信息
    $0 get-user ou_e26cad9ffe00b1737ff10db0c1984f6b

    # 获取直接下属
    $0 get-reports ou_e26cad9ffe00b1737ff10db0c1984f6b

    # 获取部门成员
    $0 get-members 3671520

依赖:
    - curl (必需)
    - jq (推荐，用于 JSON 格式化)

注意:
    需要在飞书开放平台开通以下应用身份权限:
    - contact:user.base:readonly
    - contact:user.readonly
    - contact:department.base:readonly
    - contact:department.readonly

EOF
}

# 主函数
main() {
    check_dependencies

    if [ $# -eq 0 ]; then
        show_help
        exit 0
    fi

    get_tenant_access_token

    case "$1" in
        get-user)
            if [ $# -ne 2 ]; then
                error "用法: $0 get-user <open_id>"
            fi
            get_user "$2"
            ;;
        get-department)
            if [ $# -ne 2 ]; then
                error "用法: $0 get-department <department_id>"
            fi
            get_department "$2"
            ;;
        get-members)
            if [ $# -ne 2 ]; then
                error "用法: $0 get-members <department_id>"
            fi
            get_department_members "$2"
            ;;
        get-reports)
            if [ $# -lt 2 ]; then
                error "用法: $0 get-reports <open_id> [department_id]"
            fi
            get_direct_reports "$2" "${3:-}"
            ;;
        *)
            error "未知命令: $1

运行 '$0 --help' 查看帮助"
            ;;
    esac
}

main "$@"