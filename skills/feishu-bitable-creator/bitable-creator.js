/**
 * 飞书多维表格创建工具库
 * 
 * 提供创建数据表、字段的核心功能
 */

// 尝试从多个位置加载 SDK
let Lark;
try {
  Lark = require('@larksuiteoapi/node-sdk');
} catch (e) {
  // 如果当前目录没有，尝试从 feishu 扩展加载
  try {
    Lark = require('/home/chando/openclaw/extensions/feishu/node_modules/@larksuiteoapi/node-sdk');
  } catch (e2) {
    console.error('错误：找不到 @larksuiteoapi/node-sdk');
    console.error('请运行：npm install @larksuiteoapi/node-sdk');
    process.exit(1);
  }
}

// 字段类型常量
const FieldType = {
  TEXT: 1,
  NUMBER: 2,
  SINGLE_SELECT: 3,
  MULTI_SELECT: 4,
  DATETIME: 5,
  CHECKBOX: 7,
  USER: 11,
  PHONE: 13,
  URL: 15,
  ATTACHMENT: 17,
  LOOKUP: 19,
  FORMULA: 20,
  DUPLEX_LINK: 21,
  LOCATION: 22,
  GROUP_CHAT: 23,
  CREATED_TIME: 1001,
  MODIFIED_TIME: 1002,
  CREATED_USER: 1003,
  MODIFIED_USER: 1004,
  AUTO_NUMBER: 1005
};

/**
 * 创建飞书客户端
 * @param {Object} config - 配置对象
 * @param {string} config.appId - 应用 ID
 * @param {string} config.appSecret - 应用密钥
 * @param {string} [config.domain='feishu'] - 域名 (feishu|lark)
 * @returns {Lark.Client}
 */
function createClient(config) {
  const domain = config.domain === 'lark' ? Lark.Domain.Lark : Lark.Domain.Feishu;
  
  return new Lark.Client({
    appId: config.appId,
    appSecret: config.appSecret,
    appType: Lark.AppType.SelfBuild,
    domain: domain
  });
}

/**
 * 创建数据表
 * @param {Lark.Client} client - 飞书客户端
 * @param {string} appToken - 多维表格 Token
 * @param {string} tableName - 表名
 * @param {Array} fields - 字段定义数组
 * @param {string} [viewName='默认视图'] - 视图名称
 * @returns {Promise<Object>} 创建结果
 */
async function createTable(client, appToken, tableName, fields, viewName = '默认视图') {
  const res = await client.bitable.appTable.create({
    path: { app_token: appToken },
    data: {
      table: {
        name: tableName,
        default_view_name: viewName,
        fields: fields
      }
    }
  });
  
  return {
    success: res.code === 0,
    code: res.code,
    msg: res.msg,
    tableId: res.data?.table_id,
    viewId: res.data?.default_view_id,
    fieldIds: res.data?.field_id_list,
    fieldCount: res.data?.field_id_list?.length || 0
  };
}

/**
 * 批量创建数据表
 * @param {Lark.Client} client - 飞书客户端
 * @param {string} appToken - 多维表格 Token
 * @param {Array} tables - 表定义数组
 * @returns {Promise<Array>} 创建结果数组
 */
async function createTables(client, appToken, tables) {
  const results = [];
  
  for (let i = 0; i < tables.length; i++) {
    const table = tables[i];
    console.log(`[${i + 1}/${tables.length}] 创建表：${table.name}...`);
    
    try {
      const result = await createTable(client, appToken, table.name, table.fields, table.viewName);
      
      if (result.success) {
        console.log(`  ✓ 成功! table_id: ${result.tableId}, 字段：${result.fieldCount}`);
      } else {
        console.log(`  ❌ 失败：${result.msg}`);
      }
      
      results.push({
        name: table.name,
        ...result
      });
    } catch (err) {
      console.log(`  ❌ 错误：${err.message}`);
      results.push({
        name: table.name,
        success: false,
        error: err.message
      });
    }
  }
  
  return results;
}

/**
 * 辅助函数：创建文本字段
 */
function textField(name) {
  return { field_name: name, type: FieldType.TEXT };
}

/**
 * 辅助函数：创建数字字段
 */
function numberField(name) {
  return { field_name: name, type: FieldType.NUMBER };
}

/**
 * 辅助函数：创建日期字段
 * @param {string} name - 字段名
 * @param {string} [format='yyyy-MM-dd'] - 日期格式
 */
function dateField(name, format = 'yyyy-MM-dd') {
  return { 
    field_name: name, 
    type: FieldType.DATETIME,
    property: { date_formatter: format }
  };
}

/**
 * 辅助函数：创建单选字段
 * @param {string} name - 字段名
 * @param {Array<string>} options - 选项数组
 */
function singleSelectField(name, options) {
  return {
    field_name: name,
    type: FieldType.SINGLE_SELECT,
    property: {
      options: options.map(opt => typeof opt === 'string' ? { name: opt } : opt)
    }
  };
}

/**
 * 辅助函数：创建多选字段
 * @param {string} name - 字段名
 * @param {Array<string>} options - 选项数组
 */
function multiSelectField(name, options) {
  return {
    field_name: name,
    type: FieldType.MULTI_SELECT,
    property: {
      options: options.map(opt => typeof opt === 'string' ? { name: opt } : opt)
    }
  };
}

/**
 * 辅助函数：创建人员字段
 */
function userField(name) {
  return { field_name: name, type: FieldType.USER };
}

/**
 * 辅助函数：创建复选框字段
 */
function checkboxField(name) {
  return { field_name: name, type: FieldType.CHECKBOX };
}

/**
 * 辅助函数：创建关联字段（需要额外配置）
 */
function linkField(name, targetTableId) {
  return {
    field_name: name,
    type: FieldType.DUPLEX_LINK,
    property: {
      linked_table_id: targetTableId
    }
  };
}

module.exports = {
  FieldType,
  createClient,
  createTable,
  createTables,
  // 辅助函数
  textField,
  numberField,
  dateField,
  singleSelectField,
  multiSelectField,
  userField,
  checkboxField,
  linkField
};
