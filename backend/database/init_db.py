"""
資料庫初始化腳本
執行方式：python -m database.init_db
"""

import sqlite3
from pathlib import Path


def get_sql_path(filename: str) -> Path:
    """取得 SQL 檔案路徑"""
    return Path(__file__).parent / filename


def init_database(db_path: str = "attendance.db") -> None:
    """初始化資料庫，建立所有資料表"""
    schema_path = get_sql_path("schema.sql")

    with open(schema_path, encoding="utf-8") as f:
        schema_sql = f.read()

    conn = sqlite3.connect(db_path)
    conn.executescript(schema_sql)
    conn.close()

    print(f"資料庫初始化完成：{db_path}")


def insert_sample_data(db_path: str = "attendance.db") -> None:
    """插入範例資料（測試用）"""
    sample_data_path = get_sql_path("sample_data.sql")

    with open(sample_data_path, encoding="utf-8") as f:
        sample_sql = f.read()

    conn = sqlite3.connect(db_path)
    conn.executescript(sample_sql)
    conn.close()

    print("範例資料插入完成")
    print("  - 部門：IT、HR、FIN")
    print("  - 員工：王小明、李小華、張美玲、陳大文、林志偉")
    print("  - 班表：各部門標準班")
    print("  - 彈性設定：IT(30分)、HR(15分)、FIN(0分)")


def reset_database(db_path: str = "attendance.db") -> None:
    """重置資料庫（刪除後重建）"""
    db_file = Path(db_path)
    if db_file.exists():
        db_file.unlink()
        print(f"已刪除舊資料庫：{db_path}")

    init_database(db_path)


if __name__ == "__main__":
    import sys

    db_file = sys.argv[1] if len(sys.argv) > 1 else "attendance.db"

    # 檢查是否要重置
    if "--reset" in sys.argv:
        reset_database(db_file)
    else:
        init_database(db_file)

    # 詢問是否插入範例資料
    if "--sample" in sys.argv:
        insert_sample_data(db_file)
    else:
        response = input("是否插入範例資料？(y/N): ").strip().lower()
        if response == "y":
            insert_sample_data(db_file)
