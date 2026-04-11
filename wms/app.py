"""
仓库管理系统 - Flask Web 应用
部署到 Vercel
"""

from flask import Flask, request, jsonify, render_template_string
from flask_cors import CORS
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from database import init_database, get_db
from returns_replenishment import get_returns_to_warehouse, get_replenishments
from fifo_module import get_fifo_batches, fifo_stock_out, get_fifo_analysis
from batch_management import create_batch, get_batch_by_no, get_all_batches, batch_trace
from return_management import get_customer_returns
from stocktaking_management import get_all_stocktaking
from report_center import get_dashboard_summary, get_inventory_report

app = Flask(__name__)
CORS(app)

# 初始化数据库
init_database()

INDEX_HTML = '''
<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>仓库管理系统 (WMS)</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body { font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); min-height: 100vh; padding: 20px; }
        .container { max-width: 1200px; margin: 0 auto; }
        h1 { text-align: center; color: white; margin-bottom: 30px; font-size: 2.5rem; }
        .dashboard { display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 20px; margin-bottom: 30px; }
        .card { background: white; border-radius: 15px; padding: 25px; box-shadow: 0 10px 30px rgba(0,0,0,0.2); }
        .card h3 { color: #666; font-size: 0.9rem; margin-bottom: 10px; }
        .card .value { font-size: 2.5rem; font-weight: bold; color: #667eea; }
        .modules { display: grid; grid-template-columns: repeat(auto-fit, minmax(280px, 1fr)); gap: 20px; }
        .module-card { background: white; border-radius: 15px; padding: 25px; box-shadow: 0 10px 30px rgba(0,0,0,0.2); }
        .module-card h2 { color: #333; margin-bottom: 15px; padding-bottom: 10px; border-bottom: 3px solid #667eea; }
        .module-card ul { list-style: none; }
        .module-card li { padding: 8px 0; color: #666; border-bottom: 1px solid #eee; }
        .footer { text-align: center; color: white; margin-top: 30px; }
    </style>
</head>
<body>
    <div class="container">
        <h1>🏭 仓库管理系统 (WMS)</h1>
        <div class="dashboard">
            <div class="card"><h3>物料种类</h3><div class="value" id="m1">-</div></div>
            <div class="card"><h3>库存批次</h3><div class="value" id="m2">-</div></div>
            <div class="card"><h3>今日入库</h3><div class="value" id="m3">-</div></div>
            <div class="card"><h3>今日出库</h3><div class="value" id="m4">-</div></div>
        </div>
        <div class="modules">
            <div class="module-card"><h2>📦 退料/补料</h2><ul><li>退料记录管理</li><li>补料记录管理</li><li>审批流程</li></ul></div>
            <div class="module-card"><h2>🔄 FIFO</h2><ul><li>先进先出出库</li><li>批次库龄分析</li><li>保质期预警</li></ul></div>
            <div class="module-card"><h2>🏷️ 批次管理</h2><ul><li>批次号生成</li><li>批次追溯</li><li>保质期管理</li></ul></div>
            <div class="module-card"><h2>↩️ 退货管理</h2><ul><li>客户退货</li><li>客户换货</li><li>统计</li></ul></div>
            <div class="module-card"><h2>📋 盘点管理</h2><ul><li>盘点单</li><li>差异处理</li><li>报告</li></ul></div>
            <div class="module-card"><h2>📊 报表中心</h2><ul><li>库存报表</li><li>出入库报表</li><li>仪表盘</li></ul></div>
        </div>
        <div class="footer"><p>WMS 仓库管理系统</p></div>
    </div>
    <script>
        fetch('/api/dashboard').then(r=>r.json()).then(d=>{
            document.getElementById('m1').textContent=d.material_count||0;
            document.getElementById('m2').textContent=d.batch_count||0;
            document.getElementById('m3').textContent=d.today_in||0;
            document.getElementById('m4').textContent=d.today_out||0;
        });
    </script>
</body>
</html>
'''

@app.route('/')
def index():
    return render_template_string(INDEX_HTML)

@app.route('/api/dashboard')
def api_dashboard():
    try:
        return jsonify(get_dashboard_summary())
    except:
        return jsonify({'material_count':0,'batch_count':0,'today_in':0,'today_out':0})

@app.route('/api/materials', methods=['GET', 'POST'])
def api_materials():
    with get_db() as conn:
        cursor = conn.cursor()
        if request.method == 'POST':
            data = request.get_json()
            cursor.execute('INSERT INTO materials (material_code, material_name, category, unit) VALUES (?,?,?,?)',
                        (data['material_code'], data['material_name'], data.get('category',''), data.get('unit','个')))
            conn.commit()
            return jsonify({'id': cursor.lastrowid})
        cursor.execute('SELECT * FROM materials ORDER BY id')
        return jsonify([dict(row) for row in cursor.fetchall()])

@app.route('/api/batches', methods=['GET', 'POST'])
def api_batches():
    with get_db() as conn:
        cursor = conn.cursor()
        if request.method == 'POST':
            data = request.get_json()
            batch_no = f"BTH{data.get('material_id','')}{data.get('quantity',0)}"
            cursor.execute('INSERT INTO batches (batch_no, material_id, quantity, warehouse_location) VALUES (?,?,?,?)',
                        (batch_no, data['material_id'], data['quantity'], data.get('location','A区')))
            conn.commit()
            return jsonify({'batch_no': batch_no})
        cursor.execute('SELECT b.*, m.material_name FROM batches b LEFT JOIN materials m ON b.material_id=m.id WHERE b.quantity>0 ORDER BY b.id')
        return jsonify([dict(row) for row in cursor.fetchall()])

@app.route('/api/stock_in', methods=['POST'])
def api_stock_in():
    with get_db() as conn:
        cursor = conn.cursor()
        data = request.get_json()
        cursor.execute('INSERT INTO stock_in (batch_id, material_id, quantity, operator) VALUES (?,?,?,?)',
                    (data['batch_id'], data['material_id'], data['quantity'], data.get('operator','system')))
        cursor.execute('UPDATE batches SET quantity = quantity + ? WHERE id = ?', (data['quantity'], data['batch_id']))
        conn.commit()
        return jsonify({'success': True})

@app.route('/api/stock_out', methods=['POST'])
def api_stock_out():
    with get_db() as conn:
        cursor = conn.cursor()
        data = request.get_json()
        cursor.execute('INSERT INTO stock_out (batch_id, material_id, quantity, operator) VALUES (?,?,?,?)',
                    (data['batch_id'], data['material_id'], data['quantity'], data.get('operator','system')))
        cursor.execute('UPDATE batches SET quantity = quantity - ? WHERE id = ?', (data['quantity'], data['batch_id']))
        conn.commit()
        return jsonify({'success': True})

@app.route('/api/reports/inventory')
def api_inventory():
    return jsonify(get_inventory_report())

# Vercel 入口 - 只在本地开发时运行
if __name__ == '__main__':
    app.run(debug=True)