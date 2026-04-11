"""
仓库管理系统 - 退料和补料模块
处理退货到仓库和补料的业务流程
"""

from database import get_db
from datetime import datetime


def add_return_to_warehouse(batch_id, material_id, quantity, return_reason, original_out_id=None, operator='system'):
    """添加退料记录"""
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO returns_to_warehouse 
            (batch_id, material_id, quantity, return_reason, original_out_id, operator, status)
            VALUES (?, ?, ?, ?, ?, ?, 'pending')
        ''', (batch_id, material_id, quantity, return_reason, original_out_id, operator))
        conn.commit()
        return cursor.lastrowid


def approve_return_to_warehouse(return_id, operator='system'):
    """审核通过退料单，增加库存"""
    with get_db() as conn:
        cursor = conn.cursor()
        # 获取退料记录
        cursor.execute('SELECT * FROM returns_to_warehouse WHERE id = ?', (return_id,))
        record = cursor.fetchone()
        
        if record and record['status'] == 'pending':
            # 增加对应批次的库存
            cursor.execute('''
                UPDATE batches 
                SET quantity = quantity + ? 
                WHERE id = ?
            ''', (record['quantity'], record['batch_id']))
            
            # 更新退料单状态
            cursor.execute('''
                UPDATE returns_to_warehouse 
                SET status = 'approved' 
                WHERE id = ?
            ''', (return_id,))
            
            conn.commit()
            return True
    return False


def reject_return_to_warehouse(return_id, operator='system'):
    """拒绝退料单"""
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute('''
            UPDATE returns_to_warehouse 
            SET status = 'rejected' 
            WHERE id = ?
        ''', (return_id,))
        conn.commit()
        return True


def get_returns_to_warehouse(status=None):
    """获取退料列表"""
    with get_db() as conn:
        cursor = conn.cursor()
        if status:
            cursor.execute('''
                SELECT r.*, m.material_name, m.material_code, b.batch_no
                FROM returns_to_warehouse r
                LEFT JOIN materials m ON r.material_id = m.id
                LEFT JOIN batches b ON r.batch_id = b.id
                WHERE r.status = ?
                ORDER BY r.created_at DESC
            ''', (status,))
        else:
            cursor.execute('''
                SELECT r.*, m.material_name, m.material_code, b.batch_no
                FROM returns_to_warehouse r
                LEFT JOIN materials m ON r.material_id = m.id
                LEFT JOIN batches b ON r.batch_id = b.id
                ORDER BY r.created_at DESC
            ''')
        return cursor.fetchall()


def add_replenishment(batch_id, material_id, quantity, replenish_reason, operator='system'):
    """添加补料记录"""
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO replenishment 
            (batch_id, material_id, quantity, replenish_reason, operator, status)
            VALUES (?, ?, ?, ?, ?, 'pending')
        ''', (batch_id, material_id, quantity, replenish_reason, operator))
        conn.commit()
        return cursor.lastrowid


def approve_replenishment(replenish_id, operator='system'):
    """审核通过补料单，减少库存"""
    with get_db() as conn:
        cursor = conn.cursor()
        # 获取补��记录
        cursor.execute('SELECT * FROM replenishment WHERE id = ?', (replenish_id,))
        record = cursor.fetchone()
        
        if record and record['status'] == 'pending':
            # 减少对应批次的库存
            cursor.execute('''
                UPDATE batches 
                SET quantity = quantity - ? 
                WHERE id = ?
            ''', (record['quantity'], record['batch_id']))
            
            # 更新补料单状态
            cursor.execute('''
                UPDATE replenishment 
                SET status = 'approved' 
                WHERE id = ?
            ''', (replenish_id,))
            
            conn.commit()
            return True
    return False


def reject_replenishment(replenish_id, operator='system'):
    """拒绝补料单"""
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute('''
            UPDATE replenishment 
            SET status = 'rejected' 
            WHERE id = ?
        ''', (replenish_id,))
        conn.commit()
        return True


def get_replenishments(status=None):
    """获取补料列表"""
    with get_db() as conn:
        cursor = conn.cursor()
        if status:
            cursor.execute('''
                SELECT r.*, m.material_name, m.material_code, b.batch_no
                FROM replenishment r
                LEFT JOIN materials m ON r.material_id = m.id
                LEFT JOIN batches b ON r.batch_id = b.id
                WHERE r.status = ?
                ORDER BY r.created_at DESC
            ''', (status,))
        else:
            cursor.execute('''
                SELECT r.*, m.material_name, m.material_code, b.batch_no
                FROM replenishment r
                LEFT JOIN materials m ON r.material_id = m.id
                LEFT JOIN batches b ON r.batch_id = b.id
                ORDER BY r.created_at DESC
            ''')
        return cursor.fetchall()


if __name__ == '__main__':
    # 测试代码
    print("退料补料模块测试")