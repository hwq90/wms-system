"""
仓库管理系统 - 报表中心模块
库存报表、出入库报表、批次报表等
"""

from database import get_db
from datetime import datetime, date, timedelta
import calendar


def get_inventory_report():
    """库存报表 - 当前库存汇总"""
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute('''
            SELECT 
                m.id as material_id,
                m.material_code,
                m.material_name,
                m.category,
                m.unit,
                COUNT(b.id) as batch_count,
                SUM(b.quantity) as total_quantity,
                m.safety_stock
            FROM materials m
            LEFT JOIN batches b ON m.id = b.material_id AND b.quantity > 0
            GROUP BY m.id
            ORDER BY m.material_code
        ''')
        return cursor.fetchall()


def get_inventory_alert_report():
    """库存预警报表"""
    with get_db() as conn:
        cursor = conn.cursor()
        
        # 安全库存预警
        cursor.execute('''
            SELECT 
                m.id as material_id,
                m.material_code,
                m.material_name,
                m.safety_stock,
                COALESCE(SUM(b.quantity), 0) as current_stock,
                m.safety_stock - COALESCE(SUM(b.quantity), 0) as shortage
            FROM materials m
            LEFT JOIN batches b ON m.id = b.material_id AND b.quantity > 0
            WHERE m.safety_stock > 0
            GROUP BY m.id
            HAVING COALESCE(SUM(b.quantity), 0) < m.safety_stock
            ORDER BY shortage DESC
        ''')
        safety_alert = cursor.fetchall()
        
        # 过期预警
        today = date.today()
        cursor.execute('''
            SELECT 
                b.id as batch_id,
                b.batch_no,
                m.material_code,
                m.material_name,
                b.expiry_date,
                b.quantity,
                julianday(b.expiry_date) - julianday(?) as days_left
            FROM batches b
            LEFT JOIN materials m ON b.material_id = m.id
            WHERE b.expiry_date IS NOT NULL
            AND b.quantity > 0
            AND b.expiry_date BETWEEN ? AND ?
            ORDER BY b.expiry_date ASC
        ''', (today, today + timedelta(days=30)))
        expiry_alert = cursor.fetchall()
        
        return {
            'safety_alert': safety_alert,
            'expiry_alert': expiry_alert
        }


def get_stock_in_report(start_date=None, end_date=None):
    """入库报表"""
    with get_db() as conn:
        cursor = conn.cursor()
        
        if start_date and end_date:
            cursor.execute('''
                SELECT 
                    si.*,
                    m.material_code,
                    m.material_name,
                    b.batch_no,
                    DATE(si.created_at) as in_date
                FROM stock_in si
                LEFT JOIN materials m ON si.material_id = m.id
                LEFT JOIN batches b ON si.batch_id = b.id
                WHERE DATE(si.created_at) BETWEEN ? AND ?
                ORDER BY si.created_at DESC
            ''', (start_date, end_date))
        else:
            cursor.execute('''
                SELECT 
                    si.*,
                    m.material_code,
                    m.material_name,
                    b.batch_no,
                    DATE(si.created_at) as in_date
                FROM stock_in si
                LEFT JOIN materials m ON si.material_id = m.id
                LEFT JOIN batches b ON si.batch_id = b.id
                ORDER BY si.created_at DESC
                LIMIT 100
            ''')
        
        return cursor.fetchall()


def get_stock_out_report(start_date=None, end_date=None):
    """出库报表"""
    with get_db() as conn:
        cursor = conn.cursor()
        
        if start_date and end_date:
            cursor.execute('''
                SELECT 
                    so.*,
                    m.material_code,
                    m.material_name,
                    b.batch_no,
                    DATE(so.created_at) as out_date
                FROM stock_out so
                LEFT JOIN materials m ON so.material_id = m.id
                LEFT JOIN batches b ON so.batch_id = b.id
                WHERE DATE(so.created_at) BETWEEN ? AND ?
                ORDER BY so.created_at DESC
            ''', (start_date, end_date))
        else:
            cursor.execute('''
                SELECT 
                    so.*,
                    m.material_code,
                    m.material_name,
                    b.batch_no,
                    DATE(so.created_at) as out_date
                FROM stock_out so
                LEFT JOIN materials m ON so.material_id = m.id
                LEFT JOIN batches b ON so.batch_id = b.id
                ORDER BY so.created_at DESC
                LIMIT 100
            ''')
        
        return cursor.fetchall()


def get_stock_flow_report(start_date=None, end_date=None):
    """库存流水报表"""
    with get_db() as conn:
        cursor = conn.cursor()
        
        if start_date and end_date:
            # 入库汇总
            cursor.execute('''
                SELECT 
                    material_id,
                    m.material_code,
                    m.material_name,
                    SUM(quantity) as in_qty,
                    0 as out_qty,
                    '入库' as flow_type,
                    ? as flow_date
                FROM stock_in si
                LEFT JOIN materials m ON si.material_id = m.id
                WHERE DATE(si.created_at) BETWEEN ? AND ?
                GROUP BY material_id
            ''', (start_date, start_date, end_date))
            in_flow = cursor.fetchall()
            
            # 出库汇总
            cursor.execute('''
                SELECT 
                    material_id,
                    m.material_code,
                    m.material_name,
                    0 as in_qty,
                    SUM(quantity) as out_qty,
                    '出库' as flow_type,
                    ? as flow_date
                FROM stock_out so
                LEFT JOIN materials m ON so.material_id = m.id
                WHERE DATE(so.created_at) BETWEEN ? AND ?
                GROUP BY material_id
            ''', (start_date, start_date, end_date))
            out_flow = cursor.fetchall()
        else:
            # 最近30天
            in_flow = []
            out_flow = []
        
        return {
            'in_flow': in_flow,
            'out_flow': out_flow
        }


def get_batch_report():
    """批次报表"""
    with get_db() as conn:
        cursor = conn.cursor()
        
        # 所有批次库存
        cursor.execute('''
            SELECT 
                b.*,
                m.material_code,
                m.material_name,
                m.unit,
                b.production_date,
                b.expiry_date,
                CASE 
                    WHEN b.expiry_date IS NULL THEN '无到期日'
                    WHEN b.expiry_date < DATE('now') THEN '已过期'
                    WHEN b.expiry_date <= DATE('now', '+30 days') THEN '30天内到期'
                    WHEN b.expiry_date <= DATE('now', '+90 days') THEN '90天内到期'
                    ELSE '正常'
                END as expiry_status
            FROM batches b
            LEFT JOIN materials m ON b.material_id = m.id
            WHERE b.quantity > 0
            ORDER BY b.production_date DESC
        ''')
        
        return cursor.fetchall()


def get_return_report(start_date=None, end_date=None):
    """退料/补料/退货报表"""
    with get_db() as conn:
        cursor = conn.cursor()
        
        # 退料报表
        if start_date and end_date:
            cursor.execute('''
                SELECT 
                    '退料' as return_type,
                    r.*,
                    m.material_code,
                    m.material_name,
                    b.batch_no,
                    DATE(r.created_at) as return_date
                FROM returns_to_warehouse r
                LEFT JOIN materials m ON r.material_id = m.id
                LEFT JOIN batches b ON r.batch_id = b.id
                WHERE DATE(r.created_at) BETWEEN ? AND ?
                AND r.status = 'approved'
            ''', (start_date, end_date))
        else:
            cursor.execute('''
                SELECT 
                    '退料' as return_type,
                    r.*,
                    m.material_code,
                    m.material_name,
                    b.batch_no,
                    DATE(r.created_at) as return_date
                FROM returns_to_warehouse r
                LEFT JOIN materials m ON r.material_id = m.id
                LEFT JOIN batches b ON r.batch_id = b.id
                WHERE r.status = 'approved'
                ORDER BY r.created_at DESC
                LIMIT 100
            ''')
        returns = cursor.fetchall()
        
        # 补料报表
        if start_date and end_date:
            cursor.execute('''
                SELECT 
                    '补料' as return_type,
                    r.*,
                    m.material_code,
                    m.material_name,
                    b.batch_no,
                    DATE(r.created_at) as return_date
                FROM replenishment r
                LEFT JOIN materials m ON r.material_id = m.id
                LEFT JOIN batches b ON r.batch_id = b.id
                WHERE DATE(r.created_at) BETWEEN ? AND ?
                AND r.status = 'approved'
            ''', (start_date, end_date))
        else:
            cursor.execute('''
                SELECT 
                    '补料' as return_type,
                    r.*,
                    m.material_code,
                    m.material_name,
                    b.batch_no,
                    DATE(r.created_at) as return_date
                FROM replenishment r
                LEFT JOIN materials m ON r.material_id = m.id
                LEFT JOIN batches b ON r.batch_id = b.id
                WHERE r.status = 'approved'
                ORDER BY r.created_at DESC
                LIMIT 100
            ''')
        replenishments = cursor.fetchall()
        
        # 客户退货报表
        if start_date and end_date:
            cursor.execute('''
                SELECT 
                    '客户退货' as return_type,
                    cr.*,
                    m.material_code,
                    m.material_name,
                    b.batch_no,
                    DATE(cr.created_at) as return_date
                FROM customer_returns cr
                LEFT JOIN materials m ON cr.material_id = m.id
                LEFT JOIN batches b ON cr.batch_id = b.id
                WHERE DATE(cr.created_at) BETWEEN ? AND ?
                AND cr.status = 'approved'
            ''', (start_date, end_date))
        else:
            cursor.execute('''
                SELECT 
                    '客户退货' as return_type,
                    cr.*,
                    m.material_code,
                    m.material_name,
                    b.batch_no,
                    DATE(cr.created_at) as return_date
                FROM customer_returns cr
                LEFT JOIN materials m ON cr.material_id = m.id
                LEFT JOIN batches b ON cr.batch_id = b.id
                WHERE cr.status = 'approved'
                ORDER BY cr.created_at DESC
                LIMIT 100
            ''')
        customer_returns = cursor.fetchall()
        
        return {
            'returns': returns,
            'replenishments': replenishments,
            'customer_returns': customer_returns
        }


def get_stocktaking_report(start_date=None, end_date=None):
    """盘点报表"""
    with get_db() as conn:
        cursor = conn.cursor()
        
        if start_date and end_date:
            cursor.execute('''
                SELECT 
                    s.*,
                    COUNT(si.id) as item_count,
                    SUM(si.system_qty) as system_total,
                    SUM(si.actual_qty) as actual_total,
                    SUM(si.diff_qty) as diff_total
                FROM stocktaking s
                LEFT JOIN stocktaking_items si ON s.id = si.stocktaking_id
                WHERE s.stocktaking_date BETWEEN ? AND ?
                GROUP BY s.id
                ORDER BY s.stocktaking_date DESC
            ''', (start_date, end_date))
        else:
            cursor.execute('''
                SELECT 
                    s.*,
                    COUNT(si.id) as item_count,
                    SUM(si.system_qty) as system_total,
                    SUM(si.actual_qty) as actual_total,
                    SUM(si.diff_qty) as diff_total
                FROM stocktaking s
                LEFT JOIN stocktaking_items si ON s.id = si.stocktaking_id
                GROUP BY s.id
                ORDER BY s.stocktaking_date DESC
                LIMIT 50
            ''')
        
        return cursor.fetchall()


def get_dashboard_summary():
    """仪表盘汇总数据"""
    with get_db() as conn:
        cursor = conn.cursor()
        today = date.today()
        
        # 物料种类数
        cursor.execute('SELECT COUNT(*) as count FROM materials')
        material_count = cursor.fetchone()['count']
        
        # 批次数量
        cursor.execute("SELECT COUNT(*) as count FROM batches WHERE quantity > 0")
        batch_count = cursor.fetchone()['count']
        
        # 今日入库
        cursor.execute('''
            SELECT COALESCE(SUM(quantity), 0) as total 
            FROM stock_in 
            WHERE DATE(created_at) = ?
        ''', (today,))
        today_in = cursor.fetchone()['total']
        
        # 今日出库
        cursor.execute('''
            SELECT COALESCE(SUM(quantity), 0) as total 
            FROM stock_out 
            WHERE DATE(created_at) = ?
        ''', (today,))
        today_out = cursor.fetchone()['total']
        
        # 待处理退料
        cursor.execute("SELECT COUNT(*) as count FROM returns_to_warehouse WHERE status = 'pending'")
        pending_returns = cursor.fetchone()['count']
        
        # 待处理补料
        cursor.execute("SELECT COUNT(*) as count FROM replenishment WHERE status = 'pending'")
        pending_replenishments = cursor.fetchone()['count']
        
        # 待处理客户退货
        cursor.execute("SELECT COUNT(*) as count FROM customer_returns WHERE status = 'pending'")
        pending_customer_returns = cursor.fetchone()['count']
        
        # 待审核盘点
        cursor.execute("SELECT COUNT(*) as count FROM stocktaking WHERE status = 'pending'")
        pending_stocktaking = cursor.fetchone()['count']
        
        # 库存总量
        cursor.execute('SELECT COALESCE(SUM(quantity), 0) as total FROM batches WHERE quantity > 0')
        total_stock = cursor.fetchone()['total']
        
        # 过期预警
        cursor.execute('''
            SELECT COUNT(*) as count 
            FROM batches 
            WHERE expiry_date IS NOT NULL 
            AND expiry_date < ?
            AND quantity > 0
        ''', (today + timedelta(days=30),))
        expiry_warning = cursor.fetchone()['count']
        
        return {
            'material_count': material_count,
            'batch_count': batch_count,
            'today_in': today_in,
            'today_out': today_out,
            'total_stock': total_stock,
            'pending_returns': pending_returns,
            'pending_replenishments': pending_replenishments,
            'pending_customer_returns': pending_customer_returns,
            'pending_stocktaking': pending_stocktaking,
            'expiry_warning': expiry_warning
        }


def get_monthly_report(year=None, month=None):
    """月度报表"""
    if year is None:
        today = date.today()
        year = today.year
        month = today.month
    
    start_date = date(year, month, 1)
    end_date = date(year, month, calendar.monthrange(year, month)[1])
    
    with get_db() as conn:
        cursor = conn.cursor()
        
        # 月度入库统计
        cursor.execute('''
            SELECT 
                material_id,
                m.material_name,
                m.material_code,
                SUM(quantity) as total_in
            FROM stock_in si
            LEFT JOIN materials m ON si.material_id = m.id
            WHERE DATE(si.created_at) BETWEEN ? AND ?
            GROUP BY material_id
        ''', (start_date, end_date))
        monthly_in = cursor.fetchall()
        
        # 月度出库统计
        cursor.execute('''
            SELECT 
                material_id,
                m.material_name,
                m.material_code,
                SUM(quantity) as total_out
            FROM stock_out so
            LEFT JOIN materials m ON so.material_id = m.id
            WHERE DATE(so.created_at) BETWEEN ? AND ?
            GROUP BY material_id
        ''', (start_date, end_date))
        monthly_out = cursor.fetchall()
        
        return {
            'year': year,
            'month': month,
            'start_date': start_date,
            'end_date': end_date,
            'monthly_in': monthly_in,
            'monthly_out': monthly_out
        }


if __name__ == '__main__':
    print("报表中心模块测试")