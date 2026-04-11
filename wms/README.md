# 仓库管理系统 (WMS)

## 项目概述

一个完整的仓库管理系统，包含以下6个核心模块：

1. **退料、补料模块** - 处理退货到仓库和从仓库补料的业务流程
2. **先进先出(FIFO)模块** - 按批次入库顺序出库的库存管理
3. **批次管理模块** - 批次号管理、批次追溯、保质期管理
4. **退货管理模块** - 客户退货、客户换货处理
5. **盘点管理模块** - 库存盘点、盘点差异处理
6. **报表中心模块** - 库存报表、出入库报表、批次报表等

## 技术栈

- **语言**: Python 3.x
- **数据库**: SQLite
- **架构**: 模块化设计，易于扩展

## 文件结构

```
wms/
├── database.py              # 数据库模块 - 表结构定义
├── returns_replenishment.py # 退料/补料模块
├── fifo_module.py           # FIFO模块
├── batch_management.py      # 批次管理模块
├── return_management.py     # 退货管理模块
├── stocktaking_management.py # 盘点管理模块
├── report_center.py         # 报表中心模块
├── main.py                  # 主程序入口
└── README.md                # 项目说明
```

## 数据库表结构

### 1. materials (物料表)
- id: 物料ID
- material_code: 物料编码
- material_name: 物料名称
- category: 分类
- unit: 单位
- spec: 规格
- safety_stock: 安全库存

### 2. batches (批次表)
- id: 批次ID
- batch_no: 批次号
- material_id: 物料ID
- quantity: 数量
- warehouse_location: 库位
- production_date: 生产日期
- expiry_date: 保质期
- supplier: 供应商
- status: 状态

### 3. stock_in (入库记录表)
- id: 入库ID
- batch_id: 批次ID
- material_id: 物料ID
- quantity: 数量
- operator: 操作人
- remark: 备注

### 4. stock_out (出库记录表)
- id: 出库ID
- batch_id: 批次ID
- material_id: 物料ID
- quantity: 数量
- operator: 操作人
- remark: 备注

### 5. returns_to_warehouse (退料表)
- id: 退料ID
- batch_id: 批次ID
- material_id: 物料ID
- quantity: 数量
- return_reason: 退料原因
- original_out_id: 原出库单ID
- operator: 操作人
- status: 状态

### 6. replenishment (补料表)
- id: 补料ID
- batch_id: 批次ID
- material_id: 物料ID
- quantity: 数量
- replenish_reason: 补料原因
- operator: 操作人
- status: 状态

### 7. customer_returns (客户退货表)
- id: 退货ID
- customer_name: 客户名称
- material_id: 物料ID
- batch_id: 批次ID
- quantity: 数量
- return_type: 退货类型(return/exchange)
- return_reason: 退货原因
- original_order_no: 原订单号
- operator: 操作人
- status: 状态

### 8. stocktaking (盘点表)
- id: 盘点ID
- stocktaking_no: 盘点单号
- stocktaking_date: 盘点日期
- operator: 操作人
- status: 状态
- remark: 备注

### 9. stocktaking_items (盘点明细表)
- id: 明细ID
- stocktaking_id: 盘点单ID
- batch_id: 批次ID
- material_id: 物料ID
- system_qty: 系统数量
- actual_qty: 实际数量
- diff_qty: 差异数量
- diff_reason: 差异原因

## 模块功能说明

### 1. 退料/补料模块 (returns_replenishment.py)

**功能：**
- 退料记录管理
- 补料记录管理
- 审批流程
- 库存自动更新

**主要函数：**
- `add_return_to_warehouse()` - 添加退料记录
- `approve_return_to_warehouse()` - 审核退料单
- `add_replenishment()` - 添加补料记录
- `approve_replenishment()` - 审核补料单

### 2. FIFO模块 (fifo_module.py)

**功能：**
- 按生产日期先进先出出库
- 批次库龄分析
- 保质期预警
- 出库可行性验证

**主要函数：**
- `get_fifo_batches()` - 获取FIFO批次计划
- `fifo_stock_out()` - 执行FIFO出库
- `get_fifo_analysis()` - FIFO分析
- `validate_fifo_out()` - 验证出库可行性

### 3. 批次管理模块 (batch_management.py)

**功能：**
- 批次号自动生成
- 批次追溯
- 保质期管理
- 库存预警

**主要函数：**
- `create_batch()` - 创建批次
- `batch_trace()` - 批次追溯
- `get_expiry_alerts()` - 过期预警
- `get_batch_inventory_summary()` - 批次库存汇总

### 4. 退货管理模块 (return_management.py)

**功能：**
- 客户退货处理
- 客户换货处理
- 退货统计
- 退货原因分析

**主要函数：**
- `create_customer_return()` - 创建客户退货
- `approve_customer_return()` - 审核客户退货
- `create_customer_exchange()` - 创建客户换货
- `get_return_statistics()` - 退货统计

### 5. 盘点管理模块 (stocktaking_management.py)

**功能：**
- 盘点单管理
- 盘点明细录入
- 盘点差异处理
- 盘点报告生成

**主要函数：**
- `create_stocktaking()` - 创建盘点单
- `add_stocktaking_item()` - 添加盘点明细
- `approve_stocktaking()` - 审核盘点单
- `generate_stocktaking_report()` - 生成盘点报告

### 6. 报表中心模块 (report_center.py)

**功能：**
- 库存报表
- 出入库报表
- 批次报表
- 退货报表
- 盘点报表
- 仪表盘汇总

**主要函数：**
- `get_inventory_report()` - 库存报表
- `get_stock_in_report()` - 入库报表
- `get_stock_out_report()` - 出库报表
- `get_dashboard_summary()` - 仪表盘汇总
- `get_monthly_report()` - 月度报表

## 使用方法

### 1. 初始化数据库

```python
from database import init_database
init_database()
```

### 2. 使用各模块

```python
# 退料模块
from returns_replenishment import add_return_to_warehouse, approve_return_to_warehouse

# FIFO模块
from fifo_module import fifo_stock_out, get_fifo_analysis

# 批次管理
from batch_management import create_batch, batch_trace

# 退货管理
from return_management import create_customer_return, approve_customer_return

# 盘点管理
from stocktaking_management import create_stocktaking, approve_stocktaking

# 报表中心
from report_center import get_inventory_report, get_dashboard_summary
```

## 扩展说明

系统采用模块化设计，每个模块独立封装，可以：
1. 单独调用各模块功能
2. 集成到Web框架(如Flask)
3. 开发GUI界面(如Tkinter)
4. 对接ERP系统

## 许可证

MIT License