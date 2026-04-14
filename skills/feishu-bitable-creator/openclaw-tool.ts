/**
 * OpenClaw 工具注册 - 飞书多维表格创建器
 * 
 * 将此文件复制到 /home/chando/openclaw/extensions/feishu/src/ 目录
 * 然后在 index.ts 中注册
 */

import type { OpenClawPluginApi } from "openclaw/plugin-sdk";
import { Type } from "@sinclair/typebox";
import type { FeishuConfig } from "./types.js";
import { createFeishuClient } from "./client.js";

// 字段类型映射
const FIELD_TYPES = {
  TEXT: 1,
  NUMBER: 2,
  SINGLE_SELECT: 3,
  MULTI_SELECT: 4,
  DATETIME: 5,
  CHECKBOX: 7,
  USER: 11
};

// 创建数据表的 Schema
const CreateBitableTableSchema = Type.Object({
  app_token: Type.String({
    description: "多维表格 Token（从 URL 获取：https://xxx.feishu.cn/base/XXX）"
  }),
  table_name: Type.String({
    description: "要创建的数据表名称"
  }),
  fields: Type.Array(
    Type.Object({
      field_name: Type.String({ description: "字段名称" }),
      type: Type.Number({ 
        description: "字段类型 ID (1=文本，2=数字，3=单选，4=多选，5=日期，7=复选框，11=人员)",
        enum: [1, 2, 3, 4, 5, 7, 11]
      }),
      property: Type.Optional(Type.Any({
        description: "字段属性（如单选选项、日期格式等）"
      }))
    }),
    { description: "字段定义数组" }
  ),
  view_name: Type.Optional(Type.String({
    description: "视图名称（默认：默认视图）"
  }))
});

// 批量创建数据表的 Schema
const CreateBitableTablesSchema = Type.Object({
  app_token: Type.String({
    description: "多维表格 Token"
  }),
  tables: Type.Array(
    Type.Object({
      name: Type.String({ description: "表名" }),
      fields: Type.Array(Type.Any(), { description: "字段数组" }),
      view_name: Type.Optional(Type.String({ description: "视图名称" }))
    }),
    { description: "表定义数组" }
  )
});

export function registerFeishuBitableCreatorTools(api: OpenClawPluginApi) {
  const feishuCfg = api.config?.channels?.feishu as FeishuConfig | undefined;
  if (!feishuCfg?.appId || !feishuCfg?.appSecret) {
    api.logger.debug?.("feishu_bitable_creator: Feishu credentials not configured, skipping");
    return;
  }

  const getClient = () => createFeishuClient(feishuCfg);

  // 工具 1: 创建单个数据表
  api.registerTool(
    {
      name: "feishu_bitable_create_table",
      label: "Feishu Bitable Create Table",
      description: "Create a new table in a Bitable app with specified fields",
      parameters: CreateBitableTableSchema,
      async execute(_toolCallId, params) {
        const { app_token, table_name, fields, view_name = '默认视图' } = params as {
          app_token: string;
          table_name: string;
          fields: Array<{
            field_name: string;
            type: number;
            property?: Record<string, unknown>;
          }>;
          view_name?: string;
        };

        try {
          const client = getClient();
          const res = await client.bitable.appTable.create({
            path: { app_token: app_token },
            data: {
              table: {
                name: table_name,
                default_view_name: view_name,
                fields: fields as any
              }
            }
          });

          if (res.code === 0) {
            return {
              content: [{ 
                type: "text" as const, 
                text: `✓ 表创建成功!\n\n表名：${table_name}\nTable ID: ${res.data?.table_id}\n字段数：${res.data?.field_id_list?.length}`
              }],
              details: res.data
            };
          } else {
            return {
              content: [{ 
                type: "text" as const, 
                text: `❌ 创建失败：${res.msg}`
              }],
              details: res
            };
          }
        } catch (err) {
          return {
            content: [{ 
              type: "text" as const, 
              text: `❌ 错误：${err instanceof Error ? err.message : String(err)}`
            }],
            details: { error: err }
          };
        }
      }
    },
    { name: "feishu_bitable_create_table" }
  );

  // 工具 2: 批量创建数据表
  api.registerTool(
    {
      name: "feishu_bitable_create_tables",
      label: "Feishu Bitable Create Tables",
      description: "Create multiple tables in a Bitable app at once",
      parameters: CreateBitableTablesSchema,
      async execute(_toolCallId, params) {
        const { app_token, tables } = params as {
          app_token: string;
          tables: Array<{
            name: string;
            fields: Array<any>;
            view_name?: string;
          }>;
        };

        try {
          const client = getClient();
          const results = [];

          for (const table of tables) {
            const res = await client.bitable.appTable.create({
              path: { app_token: app_token },
              data: {
                table: {
                  name: table.name,
                  default_view_name: table.view_name || '默认视图',
                  fields: table.fields as any
                }
              }
            });

            results.push({
              name: table.name,
              success: res.code === 0,
              table_id: res.data?.table_id,
              field_count: res.data?.field_id_list?.length,
              msg: res.msg
            });
          }

          const successCount = results.filter(r => r.success).length;
          const failCount = results.length - successCount;

          return {
            content: [{ 
              type: "text" as const, 
              text: `批量创建完成!\n\n总计：${results.length} 张表\n成功：${successCount} 张\n失败：${failCount} 张\n\n详情见下方`
            }],
            details: { results, summary: { total: results.length, success: successCount, fail: failCount } }
          };
        } catch (err) {
          return {
            content: [{ 
              type: "text" as const, 
              text: `❌ 错误：${err instanceof Error ? err.message : String(err)}`
            }],
            details: { error: err }
          };
        }
      }
    },
    { name: "feishu_bitable_create_tables" }
  );

  api.logger.info?.(`feishu_bitable_creator: Registered 2 tools`);
}
