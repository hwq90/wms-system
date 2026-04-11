"""
仓库管理系统 - 主程序
提供命令行界面
"""

from database import init_database
import sys


def main_menu():
    """主菜单"""
    print("\n=== 仓库管理系统 ===")
    print("1. 初始化数据库")
    print("2. 退料/补料模块")
    print("3. FIFO模块")
    print("4. 批次管理模块")
    print("5. 退货管理模块")
    print("6. 盘点管理模块")
    print("7. 报表中心模块")
    print("8. 退出")
    
    choice = input("请选择 (1-8): ")
    
    if choice == '1':
        init_database()
        print("数据库初始化完成")
    elif choice == '2':
        print("退料/补料模块")
        # 这里可以调用退料/补料模块的功能
    elif choice == '3':
        print("FIFO模块")
        # 这里可以调用FIFO模块的功能
    elif choice == '4':
        print("批次管理模块")
        # 这里可以调用批次管理模块的功能
    elif choice == '5':
        print("退货管理模块")
        # 这里可以调用退货管理模块的功能
    elif choice == '6':
        print("盘点管理模块")
        # 这里可以调用盘点管理模块的功能
    elif choice == '7':
        print("报表中心模块")
        # 这里可以调用报表中心模块的功能
    elif choice == '8':
        print("退出系统")
        sys.exit(0)
    else:
        print("无效选择")


def run():
    """运行主程序"""
    print("仓库管理系统启动...")
    
    while True:
        main_menu()


if __name__ == '__main__':
    run()