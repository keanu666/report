#!/usr/bin/env node

/**
 * 飞书多维表格批量创建工具
 * 
 * 使用方法：
 * 1. 配置下面的 APP_ID、APP_SECRET、APP_TOKEN
 * 2. 定义要创建的 tables 数组
 * 3. 运行：node create-tables.js
 */

const path = require('path');
const { createClient, createTables, singleSelectField, textField, numberField, dateField, userField, checkboxField } = require('./bitable-creator.js');

// ============ 配置区域 ============

const CONFIG = {
  appId: 'cli_a92bdcf990badcd1',
  appSecret: 'rDDzgikWrcM25sWR1vAx8cyIQMQ8JZeh',
  domain: 'feishu' // 或 'lark'
};

// 多维表格 Token（从 URL 获取：https://xxx.feishu.cn/base/TOKEN）
const APP_TOKEN = 'FUAmbD3DIakMQSsHxaicY9KLnyc';

// ============ 表定义区域 ============

const TABLES = [
  {
    name: '项目基本信息表',
    fields: [
      textField('项目名称'),
      textField('项目编号'),
      singleSelectField('项目类型', ['应用开发', '数据开发', 'AI 项目']),
      textField('需求部门'),
      userField('项目经理'),
      dateField('开始日期'),
      dateField('预计结束日期'),
      dateField('实际结束日期'),
      singleSelectField('项目状态', ['未开始', '进行中', '已暂停', '已完成']),
      singleSelectField('优先级', ['P0', 'P1', 'P2', 'P3'])
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
      singleSelectField('任务状态', ['未开始', '进行中', '已完成', '已取消']),
      numberField('完成百分比'),
      checkboxField('是否延期'),
      textField('延期原因'),
      checkboxField('是否返工'),
      numberField('返工次数')
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
      numberField('耗时'),
      checkboxField('是否遇到问题'),
      textField('问题描述'),
      textField('AI 分析结果'),
      singleSelectField('风险等级', ['低', '中', '高'])
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
      numberField('变更次数')
    ]
  },
  {
    name: '卡点/风险登记表',
    fields: [
      textField('卡点标题'),
      textField('卡点编号'),
      singleSelectField('卡点类型', ['技术', '资源', '沟通', '其他']),
      singleSelectField('严重等级', ['低', '中', '高']),
      textField('问题描述'),
      textField('根本原因'),
      textField('解决方案'),
      singleSelectField('解决状态', ['待处理', '处理中', '已解决', '已关闭']),
      userField('责任人')
    ]
  }
];

// ============ 主函数 ============

async function main() {
  console.log('===========================================');
  console.log('   飞书多维表格批量创建工具');
  console.log('===========================================\n');
  
  console.log('配置信息:');
  console.log(`  AppID: ${CONFIG.appId}`);
  console.log(`  多维表格 Token: ${APP_TOKEN}`);
  console.log(`  待创建表数：${TABLES.length}\n`);
  
  // 创建客户端
  const client = createClient(CONFIG);
  console.log('✓ 客户端初始化完成\n');
  
  // 批量创建表
  const results = await createTables(client, APP_TOKEN, TABLES);
  
  // 统计结果
  console.log('\n===========================================');
  console.log('   创建结果统计');
  console.log('===========================================\n');
  
  const successCount = results.filter(r => r.success).length;
  const failCount = results.length - successCount;
  
  console.log(`总计：${results.length} 张表`);
  console.log(`成功：${successCount} 张`);
  console.log(`失败：${failCount} 张\n`);
  
  if (successCount > 0) {
    console.log('成功的表:');
    results.filter(r => r.success).forEach(r => {
      console.log(`  ✓ ${r.name} (table_id: ${r.tableId})`);
    });
  }
  
  if (failCount > 0) {
    console.log('\n失败的表:');
    results.filter(r => !r.success).forEach(r => {
      console.log(`  ✗ ${r.name}: ${r.msg || r.error}`);
    });
  }
  
  console.log('\n===========================================');
  console.log('   完成！');
  console.log('===========================================\n');
  
  // 返回退出码
  process.exit(failCount > 0 ? 1 : 0);
}

// 运行主函数
main().catch(err => {
  console.error('程序执行失败:', err.message);
  console.error(err.stack);
  process.exit(1);
});
