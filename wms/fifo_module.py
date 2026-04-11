"""
仓库管理系统 - 先进先出(FIFO)模块
按批次入库顺序出库的库存管理
"""

from database import get_db
from datetime import datetime


def get_fifo_batches(material_id, required_qty):
    """
    获取先进先出的批次列表
    按生产日期排序，出库时优先选择最早的批次
    """
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute('''
            SELECT b.*, m.material_name, m.material_code
            FROM batches b
            LEFT JOIN materials m ON b.material_id = m.id
            WHERE b.material_id = ? 
            AND b.quantity > 0 
            AND b.status = 'normal'
            ORDER BY b.production_date ASC, b.created_at ASC
        ''', (material_id,))
        
        batches = cursor.fetchall()
        
        # 计算需要从每个批次出库的数量
        fifo_plan = []
        remaining_qty = required_qty
        
        for batch in batches:
            if remaining_qty <= 0:
                break
            
            available = batch['quantity']
            if available > 0:
                take_qty = min(available, remaining_qty)
                fifo_plan.append({
                    'batch_id': batch['id'],
                    'batch_no': batch['batch_no'],
                    'available_qty': available,
                    'take_qty': take_qty,
                    'production_date': batch['production_date']
                })
                remaining_qty -= take_qty
        
        return fifo_plan


def fifo_stock_out(material_id, quantity, operator='system', remark=''):
    """
    执行先进先出出库
    返回出库详情和成功状态
    """
    with get_db() as conn:
        cursor = conn.cursor()
        
        # 获取FIFO批次计划
        fifo_plan = get_fifo_batches(material_id, quantity)
        
        if not fifo_plan:
            return {'success': False, 'message': '库存不足或无可用批次'}
        
        total_available = sum(p['available_qty'] for p in fifo_plan)
        if total_available < quantity:
            return {'success': False, 'message': f'库存不足，需要{quantity}，可用{total_available}'}
        
        # 执行出库
        out_records = []
        for plan in fifo_plan:
            if plan['take_qty'] > 0:
                # 减少批次库存
                cursor.execute('''
                    UPDATE batches 
                    SET quantity = quantity - ? 
                    WHERE id = ?
                ''', (plan['take_qty'], plan['batch_id']))
                
                # 记录出库明细
                cursor.execute('''
                    INSERT INTO stock_out 
                    (batch_id, material_id, quantity, operator, remark)
                    VALUES (?, ?, ?, ?, ?)
                ''', (plan['batch_id'], material_id, plan['take_qty'], operator, remark))
                
                out_records.append({
                    'batch_no': plan['batch_no'],
                    'quantity': plan['take_qty']
                })
        
        conn.commit()
        
        return {
            'success': True,
            'message': 'FIFO出库成功',
            'out_records': out_records
        }


def get_material_stock_summary(material_id):
    """获取物料库存汇总（按批次）"""
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute('''
            SELECT b.*, m.material_name, m.material_code
            FROM batches b
            LEFT JOIN materials m ON b.material_id = m.id
            WHERE b.material_id = ?
            AND b.quantity > 0
            ORDER BY b.production_date ASC
        ''', (material_id,))
        return cursor.fetchall()


def get_fifo_analysis(material_id):
    """
    获取FIFO分析报告
    显示每个批次的库龄和即将过期预警
    """
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute('''
            SELECT b.*, m.material_name, m.material_code
            FROM batches b
            LEFT JOIN materials m ON b.material_id = m.id
            WHERE b.material_id = ?
            AND b.quantity > 0
            ORDER BY b.production_date ASC
        ''', (material_id,))
        batches = cursor.fetchall()
        
        analysis = []
        from datetime import date
        today = date.today()
        
        for batch in batches:
            # 计算库龄
            prod_date = batch['production_date']
            if prod_date:
                age_days = (today - prod_date).days
            else:
                age_days = 0
            
            # 计算保质期剩余天数
            exp_date = batch['expiry_date']
            if exp_date:
                days_to_expire = (exp_date - today).days
                exp_warning = days_to_expire <= 30  # 30天内过期预警
            else:
                days_to_expire = None
                exp_warning = False
            
            analysis.append({
                'batch_no': batch['batch_no'],
                'quantity': batch['quantity'],
                'production_date': prod_date,
                'age_days': age_days,
                'expiry_date': exp_date,
                'days_to_expire': days_to_expire,
                'exp_warning': exp_warning
            })
        
        return analysis


def validate_fifo_out(material_id, quantity):
    """
    验证FIFO出库是否可行
    返回是否可行及可用库存
    """
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute('''
            SELECT SUM(quantity) as total_qty
            FROM batches
            WHERE material_id = ? AND status = 'normal'
        ''', (material_id,))
        result = cursor.fetchone()
        
        available = result['total_qty'] if result['total_qty'] else 0
        
        return {
            'can_out': available >= quantity,
            'available': available,
            'required': quantity,
            'shortage': max(0, quantity - available)
        }


if __name__ == '__main__':
    print("FIFO模块测试")