#!/usr/bin/env python3
"""
数据库迁移脚本
"""
import sys
import os
import subprocess

# 添加项目根目录到Python路径
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

def main():
    """主函数"""
    print("正在运行数据库迁移...")
    
    try:
        # 运行Alembic迁移
        result = subprocess.run(
            ["alembic", "upgrade", "head"],
            capture_output=True,
            text=True
        )
        
        if result.returncode == 0:
            print("✓ 数据库迁移成功")
            print(result.stdout)
        else:
            print("✗ 数据库迁移失败")
            print(result.stderr)
            sys.exit(1)
            
    except Exception as e:
        print(f"✗ 数据库迁移失败: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main()
