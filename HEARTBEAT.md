# HEARTBEAT.md

# Keep this file empty (or with only comments) to skip heartbeat API calls.

# Add tasks below when you want the agent to check something periodically.

---

## 定时任务

### 会议室自动检查（每周一 12:00）
- 检查当天 16:00-19:00 的会议室预定状态
- 优先确认 22 会议室是否可用
- 如 22 会议室不可用，自动改订 23 会议室
- 通过飞书消息通知检查结果

