"""
仓库管理系统 - 盘点管理模块
库存盘点、盘点差异处理
"""

from database import get_db
from datetime import datetime, date
import random
import string


def generate_stocktaking_no(prefix='ST'):
    """生成盘点单号"""
    timestamp = datetime.now().strftime('%Y%m%d')
    random_str = ''.join(random.choices(string.digits, k=4))
    return f"{prefix}{timestamp}{random_str}"


def create_stocktaking(stocktaking_date, operator, remark=''):
    """创建盘点单"""
    stocktaking_no = generate_stocktaking_no()
    
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO stocktaking 
            (stocktaking_no, stocktaking_date, operator, remark, status)
            VALUES (?, ?, ?, ?, 'pending')
        ''', (stocktaking_no, stocktaking_date, operator, remark))
        conn.commit()
        return stocktaking_no


def add_stocktaking_item(stocktaking_id, batch_id, material_id, actual_qty):
    """添加盘点明细"""
    with get_db() as conn:
        cursor = conn.cursor()
        
        # 获取系统库存数量
        cursor.execute('SELECT quantity FROM batches WHERE id = ?', (batch_id,))
        batch = cursor.fetchone()
        system_qty = batch['quantity'] if batch else 0
        
        # 计算差异
        diff_qty = actual_qty - system_qty
        
        cursor.execute('''
            INSERT INTO stocktaking_items 
            (stocktaking_id, batch_id, material_id, system_qty, actual_qty, diff_qty)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (stocktaking_id, batch_id, material_id, system_qty, actual_qty, diff_qty))
        conn.commit()
        return cursor.lastrowid


def get_stocktaking(stocktaking_no):
    """获取盘点单信息"""
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM stocktaking WHERE stocktaking_no = ?', (stocktaking_no,))
        return cursor.fetchone()


def get_stocktaking_items(stocktaking_id):
    """获取盘点明细"""
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute('''
            SELECT si.*, m.material_name, m.material_code, b.batch_no
            FROM stocktaking_items si
            LEFT JOIN materials m ON si.material_id = m.id
            LEFT JOIN batches b ON si.batch_id = b.id
            WHERE si.stocktaking_id = ?
            ORDER BY si.id
        ''', (stocktaking_id,))
        return cursor.fetchall()


def approve_stocktaking(stocktaking_id, operator='system'):
    """审核通过盘点单，更新库存"""
    with get_db() as conn:
        cursor = conn.cursor()
        
        # 获取盘点明细
        cursor.execute('SELECT * FROM stocktaking_items WHERE stocktaking_id = ?', (stocktaking_id,))
        items = cursor.fetchall()
        
        for item in items:
            # 更新批次库存为实际数量
            cursor.execute('''
                UPDATE batches 
                SET quantity = ? 
                WHERE id = ?
            ''', (item['actual_qty'], item['batch_id']))
            
            # 记录差异原因（可选）
            if item['diff_qty'] != 0:
                cursor.execute('''
                    UPDATE stocktaking_items 
                    SET diff_reason = '盘点调整' 
                    WHERE id = ?
                ''', (item['id'],))
        
        # 更新盘点单状态
        cursor.execute('''
            UPDATE stocktaking 
            SET status = 'approved' 
            WHERE id = ?
        ''', (stocktaking_id,))
        
        conn.commit()
        return True


def reject_stocktaking(stocktaking_id, operator='system'):
    """拒绝盘点单"""
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute('''
            UPDATE stocktaking 
            SET status = 'rejected' 
            WHERE id = ?
        ''', (stocktaking_id,))
        conn.commit()
        return True


def get_all_stocktaking(status=None):
    """获取所有盘点单"""
    with get_db() as conn:
        cursor = conn.cursor()
        if status:
            cursor.execute('SELECT * FROM stocktaking WHERE status = ? ORDER BY created_at DESC', (status,))
        else:
            cursor.execute('SELECT * FROM stocktaking ORDER BY created_at DESC')
        return cursor.fetchall()


def get_stocktaking_summary(stocktaking_id):
    """获取盘点汇总统计"""
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute('''
            SELECT 
                COUNT(*) as item_count,
                SUM(system_qty) as system_total,
                SUM(actual_qty) as actual_total,
                SUM(diff_qty) as diff_total,
                SUM(ABS(diff_qty)) as diff_abs_total,
                COUNT(CASE WHEN diff_qty > 0 THEN 1 END) as over_count,
                COUNT(CASE WHEN diff_qty < 0 THEN 1 END) as short_count
            FROM stocktaking_items
            WHERE stocktaking_id = ?
        ''', (stocktaking_id,))
        return cursor.fetchone()


def get_difference_items(stocktaking_id, threshold=0):
    """获取差异明细"""
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute('''
            SELECT si.*, m.material_name, m.material_code, b.batch_no
            FROM stocktaking_items si
            LEFT JOIN materials m ON si.material_id = m.id
            LEFT JOIN batches b ON si.batch_id = b.id
            WHERE si.stocktaking_id = ?
            AND ABS(si.diff_qty) >= ?
            ORDER BY ABS(si.diff_qty) DESC
        ''', (stocktaking_id, threshold))
        return cursor.fetchall()


def generate_stocktaking_report(stocktaking_id):
    """生成盘点报告"""
    with get_db() as conn:
        cursor = conn.cursor()
        
        # 盘点单基本信息
        cursor.execute('SELECT * FROM stocktaking WHERE id = ?', (stocktaking_id,))
        stocktaking = cursor.fetchone()
        
        # 盘点明细
        cursor.execute('''
            SELECT si.*, m.material_name, m.material_code, b.batch_no
            FROM stocktaking_items si
            LEFT JOIN materials m ON si.material_id = m.id
            LEFT JOIN batches b ON si.batch_id = b.id
            WHERE si.stocktaking_id = ?
            ORDER BY si.id
        ''', (stocktaking_id,))
        items = cursor.fetchall()
        
        # 汇总统计
        cursor.execute('''
            SELECT 
                COUNT(*) as item_count,
                SUM(system_qty) as system_total,
                SUM(actual_qty) as actual_total,
                SUM(diff_qty) as diff_total,
                SUM(ABS(diff_qty)) as diff_abs_total
            FROM stocktaking_items
            WHERE stocktaking_id = ?
        ''', (stocktaking_id,))
        summary = cursor.fetchone()
        
        return {
            'stocktaking': stocktaking,
            'items': items,
1            'summary': summary
        }


def auto_stocktaking():
    """自动盘点：生成所有批次的盘点单"""
    with get_db() as conn:
        cursor = conn.cursor()
        
        # 获取所有批次
        cursor.execute('''
            SELECT b.id as batch_id, b.material_id, b.quantity as system_qty
            FROM batches b
            WHERE b.quantity > 0
        ''')
        batches = cursor.fetchall()
        
        if not batches:
            return None
        
        # 创建盘点单
        stocktaking_no = generate_stocktaking_no('AST')
        cursor.execute('''
            INSERT INTO stocktaking 
            (stocktaking_no, stocktaking_date, operator, remark, status)
            VALUES (?, ?, 'system', '自动盘点', 'pending')
        ''', (stocktaking_no, datetime.now()))
        
        cursor.execute('SELECT id FROM stocktaking WHERE stocktaking_no = ?', (stocktaking_no,))
        stocktaking_id = cursor.fetchone()['id']
        
        # 添加盘点明细（系统数量作为实际数量）
        for batch in batches:
            cursor.execute('''
                INSERT INTO stocktaking_items 
                (stocktaking_id, batch_id, material_id, system_qty, actual_qty, diff_qty)
                VALUES (?, ?, ?, ?, ?, 0)
            ''', (stocktaking_id, batch['batch_id'], batch['material_id'], 
                  batch['system_qty'], batch['system_qty']))
        
        conn.commit()
        return stocktaking_no


def get_stocktaking_history(start_date=None, end_date=None):
    """获取盘点历史"""
    with get_db() as conn:
        cursor = conn.cursor()
        
        if start_date and end_date:
            cursor.execute('''
                SELECT s.*,
                       COUNT(si.id) as item_count,
                       SUM(si.diff_qty) as total_diff
                FROM stocktaking s
                LEFT JOIN stocktaking_items si ON s.id = si.stocktaking_id
                WHERE s.stocktaking_date BETWEEN ? AND ?
                GROUP BY s.id
                ORDER BY s.stocktaking_date DESC
            ''', (start_date, end_date))
        else:
            cursor.execute('''
                SELECT s.*,
                       COUNT(si.id) as item_count,
                       SUM(si.diff_qty) as total_diff
                FROM stocktaking s
                LEFT JOIN stocktaking_items si ON s.id = si.stocktaking_id
                GROUP BY s.id
                ORDER BY s.stocktaking_date DESC
            ''')
        
        return cursor.fetchall()


if __name__ == '__main__':
    print("盘点管理模块测试")