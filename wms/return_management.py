"""
仓库管理系统 - 退货管理模块
客户退货、客户换货处理
"""

from database import get_db
from datetime import datetime
import random
import string


def generate_customer_return_no(prefix='CR'):
    """生成客户退货单号"""
    timestamp = datetime.now().strftime('%Y%m%d')
    random_str = ''.join(random.choices(string.digits, k=6))
    return f"{prefix}{timestamp}{random_str}"


def create_customer_return(customer_name, material_id, quantity, return_type='return', 
                           return_reason=None, original_order_no=None, batch_id=None):
    """创建客户退货记录"""
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO customer_returns 
            (customer_name, material_id, batch_id, quantity, 
             return_type, return_reason, original_order_no, 
             operator, status)
            VALUES (?, ?, ?, ?, ?, ?, ?, 'system', 'pending')
        ''', (customer_name, material_id, batch_id, quantity, 
              return_type, return_reason, original_order_no))
        conn.commit()
        return cursor.lastrowid


def approve_customer_return(return_id, operator='system'):
    """审核通过客户退货"""
    with get_db() as conn:
        cursor = conn.cursor()
        # 获取退货记录
        cursor.execute('SELECT * FROM customer_returns WHERE id = ?', (return_id,))
        record = cursor.fetchone()
        
        if record and record['status'] == 'pending':
            # 如果是退货（return），增加库存
            if record['return_type'] == 'return':
                if record['batch_id']:
                    # 有指定批次，增加该批次库存
                    cursor.execute('''
                        UPDATE batches 
                        SET quantity = quantity + ? 
                        WHERE id = ?
                    ''', (record['quantity'], record['batch_id']))
                else:
                    # 没有指定批次，创建新批次
                    cursor.execute('''
                        SELECT material_code FROM materials WHERE id = ?
                    ''', (record['material_id'],))
                    material = cursor.fetchone()
                    
                    batch_no = f"RET{datetime.now().strftime('%Y%m%d')}"
                    cursor.execute('''
                        INSERT INTO batches 
                        (batch_no, material_id, quantity, warehouse_location, 
                         production_date, expiry_date, supplier, status)
                        VALUES (?, ?, ?, '退货区', ?, ?, ?, 'normal')
                    ''', (batch_no, record['material_id'], record['quantity'], 
                          datetime.now(), None, record['customer_name']))
                    
                    # 获取新批次ID
                    cursor.execute('SELECT id FROM batches WHERE batch_no = ?', (batch_no,))
                    new_batch_id = cursor.fetchone()['id']
                    
                    # 更新退货记录的批次ID
                    cursor.execute('''
                        UPDATE customer_returns 
                        SET batch_id = ? 
                        WHERE id = ?
                    ''', (new_batch_id, return_id))
            
            # 更新退货单状态
            cursor.execute('''
                UPDATE customer_returns 
                SET status = 'approved' 
                WHERE id = ?
            ''', (return_id,))
            
            conn.commit()
            return True
    return False


def reject_customer_return(return_id, operator='system'):
    """拒绝客户退货"""
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute('''
            UPDATE customer_returns 
            SET status = 'rejected' 
            WHERE id = ?
        ''', (return_id,))
        conn.commit()
        return True


def get_customer_returns(status=None):
    """获取客户退货列表"""
    with get_db() as conn:
        cursor = conn.cursor()
        if status:
            cursor.execute('''
                SELECT cr.*, m.material_name, m.material_code, b.batch_no
                FROM customer_returns cr
                LEFT JOIN materials m ON cr.material_id = m.id
                LEFT JOIN batches b ON cr.batch_id = b.id
                WHERE cr.status = ?
                ORDER BY cr.created_at DESC
            ''', (status,))
        else:
            cursor.execute('''
                SELECT cr.*, m.material_name, m.material_code, b.batch_no
                FROM customer_returns cr
                LEFT JOIN materials m ON cr.material_id = m.id
                LEFT JOIN batches b ON cr.batch_id = b.id
                ORDER BY cr.created_at DESC
            ''')
        return cursor.fetchall()


def create_customer_exchange(customer_name, material_id, quantity, 
                             exchange_reason=None, original_order_no=None):
    """创建客户换货记录"""
    return create_customer_return(customer_name, material_id, quantity, 
                                  return_type='exchange', return_reason=exchange_reason, 
                                  original_order_no=original_order_no)


def approve_customer_exchange(exchange_id, operator='system'):
    """审核通过客户换货"""
    with get_db() as conn:
        cursor = conn.cursor()
        # 获取换货记录
        cursor.execute('SELECT * FROM customer_returns WHERE id = ?', (exchange_id,))
        record = cursor.fetchone()
        
        if record and record['status'] == 'pending' and record['return_type'] == 'exchange':
            # 换货处理：减少库存（出库），然后创建新的换货入库
            if record['batch_id']:
                # 减少原批次库存
                cursor.execute('''
                    UPDATE batches 
                    SET quantity = quantity - ? 
                    WHERE id = ?
                ''', (record['quantity'], record['batch_id']))
                
                # 记录出库
                cursor.execute('''
                    INSERT INTO stock_out 
                    (batch_id, material_id, quantity, operator, remark)
                    VALUES (?, ?, ?, ?, '客户换货出库')
                ''', (record['batch_id'], record['material_id'], record['quantity'], operator))
            
            # 更新换货单状态
            cursor.execute('''
                UPDATE customer_returns 
                SET status = 'approved' 
                WHERE id = ?
            ''', (exchange_id,))
            
            conn.commit()
            return True
    return False


def get_return_statistics():
    """获取退货统计"""
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute('''
            SELECT 
                return_type,
                COUNT(*) as count,
                SUM(quantity) as total_quantity,
                AVG(quantity) as avg_quantity
            FROM customer_returns
            WHERE status = 'approved'
            GROUP BY return_type
        ''')
        return cursor.fetchall()


def get_return_by_customer(customer_name):
    """按客户查询退货记录"""
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute('''
            SELECT cr.*, m.material_name, m.material_code, b.batch_no
            FROM customer_returns cr
            LEFT JOIN materials m ON cr.material_id = m.id
            LEFT JOIN batches b ON cr.batch_id = b.id
            WHERE cr.customer_name = ?
            ORDER BY cr.created_at DESC
        ''', (customer_name,))
        return cursor.fetchall()


def get_return_reason_summary():
    """退货原因统计"""
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute('''
            SELECT 
                return_reason,
                COUNT(*) as count,
                SUM(quantity) as total_quantity
            FROM customer_returns
            WHERE status = 'approved'
            GROUP BY return_reason
            ORDER BY count DESC
        ''')
        return cursor.fetchall()


def get_return_analysis(start_date=None, end_date=None):
    """退货分析"""
    with get_db() as conn:
        cursor = conn.cursor()
        
        if start_date and end_date:
            cursor.execute('''
                SELECT 
                    DATE(created_at) as date,
                    return_type,
                    COUNT(*) as count,
                    SUM(quantity) as total_quantity
                FROM customer_returns
                WHERE status = 'approved'
                AND DATE(created_at) BETWEEN ? AND ?
                GROUP BY DATE(created_at), return_type
                ORDER BY DATE(created_at) DESC
            ''', (start_date, end_date))
        else:
            cursor.execute('''
                SELECT 
                    DATE(created_at) as date,
                    return_type,
                    COUNT(*) as count,
                    SUM(quantity) as total_quantity
                FROM customer_returns
                WHERE status = 'approved'
                GROUP BY DATE(created_at), return_type
                ORDER BY DATE(created_at) DESC
            ''')
        
        return cursor.fetchall()


if __name__ == '__main__':
    print("退货管理模块测试")