#!/usr/bin/env python3
"""
数据库初始化脚本
"""
import sys
import os

# 添加项目根目录到Python路径
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from app.database import init_database, create_tables, create_initial_data

def main():
    """主函数"""
    print("正在初始化数据库...")
    
    try:
        # 创建表
        create_tables()
        print("✓ 数据库表创建成功")
        
        # 创建初始数据
        create_initial_data()
        print("✓ 初始数据创建成功")
        
        print("数据库初始化完成！")
        
    except Exception as e:
        print(f"✗ 数据库初始化失败: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main()
