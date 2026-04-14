/**
 * 示例：项目管理系统表结构
 * 
 * 可以直接复制到 create-tables.js 中使用
 */

const { singleSelectField, textField, numberField, dateField, userField, checkboxField, linkField } = require('../bitable-creator.js');

// 项目管理系统 - 5 张表
const projectManagementTables = [
  {
    name: '项目基本信息表',
    fields: [
      textField('项目名称'),
      textField('项目编号'),
      singleSelectField('项目类型', ['应用开发', '数据开发', 'AI 项目', '系统集成']),
      textField('需求部门'),
      userField('项目经理'),
      dateField('开始日期'),
      dateField('预计结束日期'),
      dateField('实际结束日期'),
      singleSelectField('项目状态', ['规划中', '未开始', '进行中', '已暂停', '已完成', '已取消']),
      singleSelectField('优先级', ['P0-紧急', 'P1-高', 'P2-中', 'P3-低']),
      numberField('预算'),
      textField('备注')
    ]
  },
  {
    name: '任务分解表',
    fields: [
      textField('任务名称'),
      textField('任务编号'),
      textField('所属项目'),
      userField('负责人'),
      textField('参与人'),
      dateField('计划开始日期'),
      dateField('计划结束日期'),
      dateField('实际开始日期'),
      dateField('实际结束日期'),
      numberField('计划人天'),
      numberField('实际人天'),
      singleSelectField('任务状态', ['待开始', '进行中', '待验收', '已完成', '已取消']),
      numberField('完成百分比'),
      checkboxField('是否延期'),
      textField('延期原因'),
      checkboxField('是否返工'),
      numberField('返工次数'),
      singleSelectField('任务优先级', ['高', '中', '低'])
    ]
  },
  {
    name: '进度填报表',
    fields: [
      dateField('填报日期'),
      userField('填报人'),
      textField('所属项目'),
      textField('关联任务'),
      textField('今日工作内容'),
      numberField('完成进度'),
      numberField('耗时 (小时)'),
      checkboxField('是否遇到问题'),
      textField('问题描述'),
      textField('AI 分析结果'),
      singleSelectField('风险等级', ['低', '中', '高']),
      textField('明日计划')
    ]
  },
  {
    name: '需求文档表',
    fields: [
      textField('需求标题'),
      textField('需求编号'),
      textField('所属项目'),
      textField('原始内容'),
      textField('结构化需求'),
      singleSelectField('需求类型', ['功能需求', '性能需求', '界面需求', '其他']),
      singleSelectField('需求状态', ['待评审', '已通过', '开发中', '已上线', '已废弃']),
      numberField('变更次数'),
      dateField('创建日期'),
      dateField('最后更新日期')
    ]
  },
  {
    name: '卡点/风险登记表',
    fields: [
      textField('卡点标题'),
      textField('卡点编号'),
      singleSelectField('卡点类型', ['技术难题', '资源不足', '沟通问题', '需求变更', '外部依赖', '其他']),
      singleSelectField('严重等级', ['低', '中', '高', '紧急']),
      textField('问题描述'),
      textField('根本原因'),
      textField('解决方案'),
      singleSelectField('解决状态', ['待处理', '处理中', '待验证', '已解决', '已关闭']),
      userField('责任人'),
      dateField('发现日期'),
      dateField('解决日期'),
      textField('经验总结')
    ]
  },
  {
    name: '会议记录表',
    fields: [
      textField('会议主题'),
      dateField('会议日期'),
      textField('参会人员'),
      textField('会议议程'),
      textField('会议结论'),
      textField('待办事项'),
      userField('记录人'),
      textField('关联项目')
    ]
  }
];

module.exports = projectManagementTables;
