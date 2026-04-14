#!/usr/bin/env python3
"""
backup-workspace: 备份 OpenClaw 工作区到 Git 仓库

用法:
    backup-workspace backup           # 增量备份（sessions 只备份昨天的）
    backup-workspace backup --full    # 全量备份（所有文件）
    backup-workspace backup --dry-run # 预览模式
    backup-workspace status           # 查看状态

目录结构:
    10.0.100.203/
    ├── workspace/
    │   ├── config/               # 配置文件，每天全量备份
    │   │   ├── 2026-04-07/
    │   │   │   ├── AGENTS.md
    │   │   │   ├── SOUL.md
    │   │   │   └── ...
    │   │   └── 2026-04-08/
    │   └── memory/               # memory 文件，按文件名日期
    │       ├── 2026-04-07/
    │       │   └── 2026-04-07.md
    │       └── 2026-04-08/
    └── sessions/
        └── main/
            └── 2026-04-07/       # 按文件名日期分类
                └── xxx.jsonl.reset.2026-04-07T...

规则:
    - workspace config: 每天全量备份，保留历史
    - workspace memory: 按文件名日期备份
    - sessions: 增量备份（只备份昨天的），按文件名日期分类
"""

import argparse
import json
import os
import re
import subprocess
import sys
import tempfile
import shutil
from pathlib import Path
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional, Tuple
from urllib.parse import quote

# 路径常量
OPENCLAW_DIR = Path.home() / ".openclaw"
SKILL_DIR = Path(os.path.realpath(__file__)).parent.parent
CREDENTIALS_FILE = SKILL_DIR / "config.yaml"

# 要备份的 workspace 配置文件（每天全量备份）
CONFIG_FILES = [
    "AGENTS.md",
    "SOUL.md",
    "USER.md",
    "IDENTITY.md",
    "TOOLS.md",
    "HEARTBEAT.md",
    "MEMORY.md",
    "WORKSPACE_STRUCTURE.md",
    "BOOTSTRAP.md",
]


def setup_logging():
    """创建日志文件"""
    now = datetime.now()
    date_dir = OPENCLAW_DIR / "logs" / "backup-workspace" / now.strftime("%Y-%m-%d")
    date_dir.mkdir(parents=True, exist_ok=True)
    
    log_file = date_dir / f"backup-workspace-{now.strftime('%H%M%S')}.log"
    
    sys.stdout = open(log_file, "w")
    sys.stderr = sys.stdout


def cleanup_old_logs():
    """删除超过 15 天的日志"""
    log_base = OPENCLAW_DIR / "logs" / "backup-workspace"
    if not log_base.exists():
        return
    
    cutoff = datetime.now() - timedelta(days=15)
    
    for date_dir in log_base.iterdir():
        if date_dir.is_dir():
            try:
                dir_date = datetime.strptime(date_dir.name, "%Y-%m-%d")
                if dir_date < cutoff:
                    shutil.rmtree(date_dir)
            except ValueError:
                pass


def load_credentials() -> Dict[str, Any]:
    """加载凭证配置"""
    if not CREDENTIALS_FILE.exists():
        raise FileNotFoundError(f"凭证文件不存在: {CREDENTIALS_FILE}")
    
    try:
        import yaml
        with open(CREDENTIALS_FILE, "r") as f:
            return yaml.safe_load(f) or {}
    except ImportError:
        with open(CREDENTIALS_FILE, "r") as f:
            return json.load(f)


def get_local_ip() -> str:
    """获取本机 IP"""
    import socket
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
        s.close()
        return ip
    except Exception:
        return "127.0.0.1"


def discover_workspaces() -> List[Path]:
    """发现所有 workspace 目录"""
    workspaces = []
    
    if not OPENCLAW_DIR.exists():
        return workspaces
    
    for entry in OPENCLAW_DIR.iterdir():
        if entry.is_dir() and (
            entry.name == "workspace" or 
            entry.name.startswith("workspace-")
        ):
            workspaces.append(entry)
    
    return sorted(workspaces, key=lambda x: x.name)


def discover_agents() -> List[str]:
    """发现所有 agent 目录"""
    agents = []
    agents_dir = OPENCLAW_DIR / "agents"
    
    if not agents_dir.exists():
        return agents
    
    for entry in agents_dir.iterdir():
        if entry.is_dir():
            agents.append(entry.name)
    
    return sorted(agents)


def build_auth_url() -> str:
    """构建带认证的 Git URL"""
    creds = load_credentials()
    backup_repo = creds.get("backup_repo", "agent-log.git")
    base_url = creds.get("base_url", "").rstrip("/")
    username = creds.get("username", "")
    password = creds.get("password", "")
    
    repo_url = f"{base_url}/{backup_repo}"
    
    if username and password:
        encoded_password = quote(password, safe='')
        return repo_url.replace("https://", f"https://{username}:{encoded_password}@")
    
    return repo_url


def run_git(*args, cwd: Optional[Path] = None) -> subprocess.CompletedProcess:
    """执行 git 命令"""
    cmd = ["git"] + list(args)
    env = {**os.environ, "GIT_TERMINAL_PROMPT": "0"}
    
    return subprocess.run(cmd, cwd=cwd, capture_output=True, text=True, env=env)


def get_file_date(file_path: Path) -> Optional[str]:
    """
    获取文件的日期（用于分类）
    
    优先级：
    1. 文件名中的日期（如 2026-04-07.md 或 .reset.2026-04-07T...）
    2. 文件修改时间
    """
    filename = file_path.name
    
    # 从文件名提取日期（匹配 YYYY-MM-DD 格式）
    date_match = re.search(r'(\d{4}-\d{2}-\d{2})', filename)
    if date_match:
        return date_match.group(1)
    
    # 使用文件修改时间
    mtime = datetime.fromtimestamp(file_path.stat().st_mtime)
    return mtime.strftime("%Y-%m-%d")


def backup_workspace(
    workspace_path: Path, 
    repo_dir: Path,
    local_ip: str,
    dry_run: bool = False,
    full_backup: bool = False
) -> Tuple[List[str], int]:
    """
    备份单个 workspace
    
    - config 文件：每天全量备份到 config/日期/ 目录
    - memory 文件：按文件名日期备份到 memory/日期/ 目录
    
    Args:
        workspace_path: workspace 路径
        repo_dir: Git 仓库目录
        local_ip: 本机 IP
        dry_run: 预览模式
        full_backup: 全量备份
    
    Returns:
        (备份日志列表, 文件数)
    """
    logs = []
    file_count = 0
    
    workspace_name = workspace_path.name
    today = datetime.now().strftime("%Y-%m-%d")
    yesterday = (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d")
    
    # 目录结构: IP/workspace名/
    base_backup_dir = repo_dir / local_ip / workspace_name
    
    # 1. 备份配置文件到 config/日期/ 目录（每天全量备份）
    config_backup_date = today if full_backup else yesterday
    
    for filename in CONFIG_FILES:
        src = workspace_path / filename
        if not src.exists():
            continue
        
        # 目标目录: workspace/config/日期/
        dst_dir = base_backup_dir / "config" / config_backup_date
        dst = dst_dir / filename
        
        if dry_run:
            logs.append(f"  [预览] {workspace_name}/config/{config_backup_date}/{filename}")
        else:
            dst_dir.mkdir(parents=True, exist_ok=True)
            shutil.copy2(src, dst)
            logs.append(f"  ✅ {workspace_name}/config/{config_backup_date}/{filename}")
        file_count += 1
    
    # 2. 备份 memory 目录到 memory/日期/ 目录（按文件名日期）
    memory_src = workspace_path / "memory"
    if memory_src.exists():
        for md_file in memory_src.glob("*.md"):
            # memory 文件名就是日期
            file_date = md_file.stem  # 2026-04-07
            
            # 验证日期格式
            if not re.match(r'\d{4}-\d{2}-\d{2}', file_date):
                file_date = get_file_date(md_file)
            
            # 增量模式：只备份昨天的
            if not full_backup and file_date != yesterday:
                continue
            
            # 目标目录: workspace/memory/日期/
            dst_dir = base_backup_dir / "memory" / file_date
            dst = dst_dir / md_file.name
            
            if dry_run:
                logs.append(f"  [预览] {workspace_name}/memory/{file_date}/{md_file.name}")
            else:
                dst_dir.mkdir(parents=True, exist_ok=True)
                shutil.copy2(md_file, dst)
                logs.append(f"  ✅ {workspace_name}/memory/{file_date}/{md_file.name}")
            file_count += 1
    
    return logs, file_count


def backup_sessions(
    repo_dir: Path,
    local_ip: str,
    dry_run: bool = False,
    full_backup: bool = False
) -> Tuple[List[str], int]:
    """
    备份 sessions 文件
    
    sessions 文件增量备份，按文件名日期分类到 sessions/agent/日期/ 目录
    
    Args:
        repo_dir: Git 仓库目录
        local_ip: 本机 IP
        dry_run: 预览模式
        full_backup: 全量备份（备份所有文件）
    
    Returns:
        (备份日志列表, 文件数)
    """
    logs = []
    file_count = 0
    
    agents_dir = OPENCLAW_DIR / "agents"
    if not agents_dir.exists():
        return logs, file_count
    
    yesterday = (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d")
    base_backup_dir = repo_dir / local_ip / "sessions"
    
    # 遍历所有 agent
    for agent_name in discover_agents():
        sessions_dir = agents_dir / agent_name / "sessions"
        
        if not sessions_dir.exists():
            continue
        
        # 遍历所有 session 文件
        for session_file in sessions_dir.iterdir():
            if not session_file.is_file():
                continue
            
            # 跳过 .lock 文件
            if session_file.name.endswith(".lock"):
                continue
            
            # 只处理 .jsonl 和 .jsonl.* 文件
            if not (session_file.name.endswith(".jsonl") or ".jsonl." in session_file.name):
                continue
            
            # 获取文件日期
            file_date = get_file_date(session_file)
            
            # 增量模式：只备份昨天的文件
            if not full_backup and file_date != yesterday:
                continue
            
            # 目标目录: sessions/agent名/日期/
            dst_dir = base_backup_dir / agent_name / file_date
            dst = dst_dir / session_file.name
            
            if dry_run:
                logs.append(f"  [预览] sessions/{agent_name}/{file_date}/{session_file.name}")
            else:
                dst_dir.mkdir(parents=True, exist_ok=True)
                shutil.copy2(session_file, dst)
                logs.append(f"  ✅ sessions/{agent_name}/{file_date}/{session_file.name}")
            file_count += 1
    
    return logs, file_count


def cmd_backup(args):
    """执行备份"""
    dry_run = args.dry_run
    full_backup = args.full
    
    if not dry_run:
        setup_logging()
        cleanup_old_logs()
    
    print("=" * 60)
    print("OpenClaw Workspace 备份")
    print("=" * 60)
    
    mode_str = "全量" if full_backup else "增量"
    print(f"\n[{mode_str}模式]")
    print("  - workspace config: " + ("全量备份" if full_backup else "全量备份（每天）"))
    print("  - workspace memory: " + ("全量备份" if full_backup else "只备份昨天的"))
    print("  - sessions: " + ("全量备份" if full_backup else "只备份昨天的"))
    
    local_ip = get_local_ip()
    print(f"\n本机 IP: {local_ip}")
    
    workspaces = discover_workspaces()
    agents = discover_agents()
    
    print(f"发现 {len(workspaces)} 个 workspace:")
    for ws in workspaces:
        print(f"  - {ws.name}")
    
    print(f"\n发现 {len(agents)} 个 agent:")
    for agent in agents:
        print(f"  - {agent}")
    
    if not workspaces and not agents:
        print("❌ 没有找到要备份的内容")
        return
    
    try:
        creds = load_credentials()
        backup_repo = creds.get("backup_repo", "agent-log.git")
        print(f"\n备份仓库: {backup_repo}")
    except Exception as e:
        print(f"❌ {e}")
        return
    
    if dry_run:
        print("\n[预览模式] 不会实际提交")
    
    # 准备仓库
    auth_url = build_auth_url()
    branch = creds.get("branch", "main")
    
    if not dry_run:
        repo_dir = Path(tempfile.mkdtemp(prefix="backup-"))
        print(f"\n克隆仓库...")
        
        result = run_git("clone", auth_url, str(repo_dir))
        if result.returncode != 0 and "empty repository" not in result.stderr.lower():
            repo_dir.mkdir(parents=True, exist_ok=True)
            run_git("init", cwd=repo_dir)
            run_git("remote", "add", "origin", auth_url, cwd=repo_dir)
        
        print(f"仓库目录: {repo_dir}")
    else:
        repo_dir = Path("/tmp/preview")
    
    total_files = 0
    
    # 备份各 workspace
    for workspace_path in workspaces:
        print(f"\n{'='*60}")
        print(f"Workspace: {workspace_path.name}")
        print(f"{'='*60}")
        
        logs, count = backup_workspace(
            workspace_path, repo_dir, local_ip, dry_run, full_backup
        )
        
        for line in logs:
            print(line)
        
        total_files += count
    
    # 备份 sessions
    print(f"\n{'='*60}")
    print(f"Sessions:")
    print(f"{'='*60}")
    
    logs, count = backup_sessions(repo_dir, local_ip, dry_run, full_backup)
    
    for line in logs:
        print(line)
    
    total_files += count
    
    if dry_run:
        print(f"\n[预览完成] 共 {total_files} 个文件")
        return
    
    if total_files == 0:
        print("\n没有需要备份的文件")
        shutil.rmtree(repo_dir)
        return
    
    # Git 操作
    print(f"\n{'='*60}")
    print("Git 操作")
    print(f"{'='*60}")
    
    run_git("checkout", "-B", branch, cwd=repo_dir)
    run_git("add", ".", cwd=repo_dir)
    
    result = run_git("status", "--short", cwd=repo_dir)
    if result.stdout.strip():
        print(f"变更文件:\n{result.stdout}")
    else:
        print("没有变更")
        shutil.rmtree(repo_dir)
        return
    
    timestamp = datetime.now().strftime("%Y-%m-%d-%H%M%S")
    result = run_git("commit", "-m", f"backup: {local_ip} - {timestamp}", cwd=repo_dir)
    
    if result.returncode != 0:
        if "nothing to commit" in result.stdout:
            print("没有变更需要提交")
        else:
            print(f"提交失败: {result.stderr}")
    else:
        print(f"✅ 提交成功")
    
    print(f"\n推送到 {branch}...")
    result = run_git("push", "-u", "origin", branch, cwd=repo_dir)
    
    if result.returncode != 0:
        print("推送失败，正在拉取最新代码...")
        run_git("fetch", "origin", cwd=repo_dir)
        run_git("rebase", f"origin/{branch}", cwd=repo_dir)
        result = run_git("push", "-u", "origin", branch, cwd=repo_dir)
    
    if result.returncode == 0:
        print(f"\n{'='*60}")
        print(f"✅ 备份完成!")
        print(f"  服务器: {local_ip}")
        print(f"  模式: {mode_str}")
        print(f"  文件数: {total_files}")
        print(f"{'='*60}")
    else:
        print(f"❌ 推送失败: {result.stderr}")
    
    shutil.rmtree(repo_dir)


def cmd_status(args):
    """查看状态"""
    print("=" * 60)
    print("Backup Workspace 状态")
    print("=" * 60)
    
    local_ip = get_local_ip()
    print(f"\n本机 IP: {local_ip}")
    
    # Sessions 状态
    agents_dir = OPENCLAW_DIR / "agents"
    print(f"\nSessions:")
    if agents_dir.exists():
        for agent_dir in agents_dir.iterdir():
            if not agent_dir.is_dir():
                continue
            
            agent_name = agent_dir.name
            sessions_dir = agent_dir / "sessions"
            
            if sessions_dir.exists():
                jsonl_count = len(list(sessions_dir.glob("*.jsonl")))
                archived_count = len([f for f in sessions_dir.iterdir() 
                                     if f.is_file() and ".jsonl." in f.name])
                total_size = sum(f.stat().st_size for f in sessions_dir.glob("*") if f.is_file())
                print(f"  📁 {agent_name}/sessions")
                print(f"     活跃: {jsonl_count} 个, 归档: {archived_count} 个, 大小: {total_size / 1024 / 1024:.2f} MB")
    
    workspaces = discover_workspaces()
    print(f"\nWorkspace 列表 ({len(workspaces)} 个):")
    
    for ws in workspaces:
        print(f"\n  {ws.name}/")
        for f in CONFIG_FILES:
            p = ws / f
            if p.exists():
                mtime = datetime.fromtimestamp(p.stat().st_mtime).strftime("%Y-%m-%d %H:%M")
                print(f"    ✅ {f} ({mtime})")
        
        memory_dir = ws / "memory"
        if memory_dir.exists():
            md_files = sorted(memory_dir.glob("*.md"))
            if md_files:
                latest = md_files[-1].name
                print(f"    📁 memory/ ({len(md_files)} 个, 最新: {latest})")
    
    print(f"\n凭证配置:")
    if CREDENTIALS_FILE.exists():
        creds = load_credentials()
        print(f"  ✅ 备份仓库: {creds.get('backup_repo', '未配置')}")
        print(f"  ✅ 分支: {creds.get('branch', 'main')}")
    else:
        print(f"  ❌ 凭证文件不存在")


def check_and_setup_cron():
    """检查并自动配置定时任务"""
    home = os.environ.get("HOME", "/root")
    cron_job = f"0 23 * * * {home}/.local/bin/backup-workspace backup"
    
    result = subprocess.run(["crontab", "-l"], capture_output=True, text=True)
    current_cron = result.stdout if result.returncode == 0 else ""
    
    if "backup-workspace backup" in current_cron:
        return False
    
    new_cron = current_cron.rstrip() + "\n" + cron_job + "\n"
    
    process = subprocess.Popen(["crontab", "-"], stdin=subprocess.PIPE, text=True)
    process.communicate(new_cron)
    
    if process.returncode == 0:
        print(f"ℹ️  已自动配置每天 23:00 自动备份")
        return True
    
    return False


def cmd_setup_cron(args):
    """配置定时任务"""
    hour = args.hour or 23
    home = os.environ.get("HOME", "/root")
    cron_job = f"0 {hour} * * * {home}/.local/bin/backup-workspace backup"
    
    result = subprocess.run(["crontab", "-l"], capture_output=True, text=True)
    current_cron = result.stdout if result.returncode == 0 else ""
    
    if "backup-workspace backup" in current_cron:
        print("✅ 定时任务已存在")
        for line in current_cron.split("\n"):
            if "backup-workspace" in line:
                print(f"  {line}")
        return
    
    new_cron = current_cron.rstrip() + "\n" + cron_job + "\n"
    
    process = subprocess.Popen(["crontab", "-"], stdin=subprocess.PIPE, text=True)
    process.communicate(new_cron)
    
    if process.returncode == 0:
        print(f"✅ 已配置每天 {hour}:00 自动备份")
    else:
        print("❌ 配置失败")


def main():
    parser = argparse.ArgumentParser(description="OpenClaw Workspace 备份工具")
    subparsers = parser.add_subparsers(dest="command", help="命令")
    
    backup_parser = subparsers.add_parser("backup", help="立即备份")
    backup_parser.add_argument("--dry-run", action="store_true", help="预览模式")
    backup_parser.add_argument("--full", action="store_true", help="全量备份")
    
    subparsers.add_parser("status", help="查看状态")
    
    cron_parser = subparsers.add_parser("setup-cron", help="配置定时备份")
    cron_parser.add_argument("--hour", type=int, help="备份时间（小时）")
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        sys.exit(1)
    
    if args.command != "setup-cron":
        check_and_setup_cron()
    
    try:
        if args.command == "backup":
            cmd_backup(args)
        elif args.command == "status":
            cmd_status(args)
        elif args.command == "setup-cron":
            cmd_setup_cron(args)
    except Exception as e:
        print(f"❌ 错误: {e}")
        if os.environ.get("DEBUG"):
            import traceback
            traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()