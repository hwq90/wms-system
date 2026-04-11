"""
仓库管理系统 - 批次管理模块
批次号管理、批次追溯、保质期管理
"""

from database import get_db
from datetime import datetime, date
import random
import string


def generate_batch_no(prefix='BTH'):
    """生成批次号"""
    timestamp = datetime.now().strftime('%Y%m%d')
    random_str = ''.join(random.choices(string.ascii_uppercase + string.digits, k=4))
    return f"{prefix}{timestamp}{random_str}"


def create_batch(material_id, quantity, warehouse_location, production_date=None, 
                 expiry_date=None, supplier=None):
    """创建新批次"""
    batch_no = generate_batch_no()
    
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO batches 
            (batch_no, material_id, quantity, warehouse_location, 
             production_date, expiry_date, supplier, status)
            VALUES (?, ?, ?, ?, ?, ?, ?, 'normal')
        ''', (batch_no, material_id, quantity, warehouse_location, 
              production_date, expiry_date, supplier))
        conn.commit()
        return batch_no


def get_batch_by_no(batch_no):
    """按批次号查询批次信息"""
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute('''
            SELECT b.*, m.material_name, m.material_code
            FROM batches b
            LEFT JOIN materials m ON b.material_id = m.id
            WHERE b.batch_no = ?
        ''', (batch_no,))
        return cursor.fetchone()


def get_batches_by_material(material_id):
    """按物料查询批次列表"""
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute('''
            SELECT b.*, m.material_name, m.material_code
            FROM batches b
            LEFT JOIN materials m ON b.material_id = m.id
            WHERE b.material_id = ?
            ORDER BY b.production_date DESC
        ''', (material_id,))
        return cursor.fetchall()


def get_all_batches(status=None):
    """获取所有批次"""
    with get_db() as conn:
        cursor = conn.cursor()
        if status:
            cursor.execute('''
                SELECT b.*, m.material_name, m.material_code
                FROM batches b
                LEFT JOIN materials m ON b.material_id = m.id
                WHERE b.status = ?
                ORDER BY b.created_at DESC
            ''', (status,))
        else:
            cursor.execute('''
                SELECT b.*, m.material_name, m.material_code
                FROM batches b
                LEFT JOIN materials m ON b.material_id = m.id
                ORDER BY b.created_at DESC
            ''')
        return cursor.fetchall()


def update_batch_status(batch_id, status):
    """更新批次状态"""
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute('''
            UPDATE batches 
            SET status = ? 
            WHERE id = ?
        ''', (status, batch_id))
        conn.commit()
        return True


def batch_trace(batch_id):
    """
    批次追溯
    查询批次从入库到出库的完整流转记录
    """
    with get_db() as conn:
        cursor = conn.cursor()
        
        # 批次基本信息
        cursor.execute('''
            SELECT b.*, m.material_name, m.material_code
            FROM batches b
            LEFT JOIN materials m ON b.material_id = m.id
            WHERE b.id = ?
        ''', (batch_id,))
        batch_info = cursor.fetchone()
        
        if not batch_info:
            return None
        
        # 入库记录
        cursor.execute('''
            SELECT * FROM stock_in 
            WHERE batch_id = ?
            ORDER BY created_at ASC
        ''', (batch_id,))
        stock_in_records = cursor.fetchall()
        
        # 出库记录
        cursor.execute('''
            SELECT * FROM stock_out 
            WHERE batch_id = ?
            ORDER BY created_at ASC
        ''', (batch_id,))
        stock_out_records = cursor.fetchall()
        
        # 退料记录
        cursor.execute('''
            SELECT * FROM returns_to_warehouse 
            WHERE batch_id = ?
            ORDER BY created_at ASC
        ''', (batch_id,))
        return_records = cursor.fetchall()
        
        return {
            'batch_info': batch_info,
            'stock_in': stock_in_records,
            'stock_out': stock_out_records,
            'returns': return_records
        }


def get_expiry_alerts(days=30):
    """
    获取即将过期的批次预警
    days: 多少天内过期预警
    """
    with get_db() as conn:
        cursor = conn.cursor()
        today = date.today()
        
        cursor.execute('''
            SELECT b.*, m.material_name, m.material_code,
                   julianday(b.expiry_date) - julianday(?) as days_left
            FROM batches b
            LEFT JOIN materials m ON b.material_id = m.id
            WHERE b.expiry_date IS NOT NULL
            AND b.quantity > 0
            AND julianday(b.expiry_date) - julianday(?) <= ?
            AND julianday(b.expiry_date) - julianday(?) >= 0
            ORDER BY b.expiry_date ASC
        ''', (today, today, days, today))
        
        return cursor.fetchall()


def get_expired_batches():
    """获取已过期批次"""
    with get_db() as conn:
        cursor = conn.cursor()
        today = date.today()
        
        cursor.execute('''
            SELECT b.*, m.material_name, m.material_code
            FROM batches b
            LEFT JOIN materials m ON b.material_id = m.id
            WHERE b.expiry_date IS NOT NULL
            AND b.quantity > 0
            AND b.expiry_date < ?
            ORDER BY b.expiry_date ASC
        ''', (today,))
        
        return cursor.fetchall()


def get_batch_inventory_summary():
    """获取批次库存汇总"""
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute('''
            SELECT 
                m.material_code,
                m.material_name,
                COUNT(b.id) as batch_count,
                SUM(b.quantity) as total_quantity,
                MIN(b.production_date) as earliest_date,
                MAX(b.expiry_date) as latest_expiry
            FROM materials m
            LEFT JOIN batches b ON m.id = b.material_id AND b.quantity > 0
            GROUP BY m.id
            ORDER BY m.material_code
        ''')
        return cursor.fetchall()


def transfer_batch(batch_id, new_location):
    """批次移库"""
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute('''
            UPDATE batches 
            SET warehouse_location = ? 
            WHERE id = ?
        ''', (new_location, batch_id))
        conn.commit()
        return True


if __name__ == '__main__':
    print("批次管理模块测试")