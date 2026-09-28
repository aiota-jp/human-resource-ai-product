"""database.py データベース初期化・接続管理"""
import sqlite3
from config import Config


def get_db():
    conn = sqlite3.connect(Config.DATABASE)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    conn = get_db()
    cur = conn.cursor()
    cur.executescript("""
        PRAGMA foreign_keys = ON;

        CREATE TABLE IF NOT EXISTS user (
            id           INTEGER PRIMARY KEY AUTOINCREMENT,
            username     TEXT    NOT NULL UNIQUE,
            password     TEXT    NOT NULL,
            role         TEXT    NOT NULL DEFAULT 'user',
            created_at   DATETIME DEFAULT CURRENT_TIMESTAMP
        );

        CREATE TABLE IF NOT EXISTS department (
            id            INTEGER PRIMARY KEY AUTOINCREMENT,
            dept_name     TEXT    NOT NULL UNIQUE,
            created_at    DATETIME DEFAULT CURRENT_TIMESTAMP
        );

        CREATE TABLE IF NOT EXISTS employee (
            id            INTEGER PRIMARY KEY AUTOINCREMENT,
            employee_no   TEXT    NOT NULL UNIQUE,
            name          TEXT    NOT NULL,
            department    TEXT,
            position      TEXT,
            hire_date     DATE,
            is_active     INTEGER NOT NULL DEFAULT 1,
            created_at    DATETIME DEFAULT CURRENT_TIMESTAMP,
            updated_at    DATETIME DEFAULT CURRENT_TIMESTAMP
        );

        CREATE TABLE IF NOT EXISTS training (
            id            INTEGER PRIMARY KEY AUTOINCREMENT,
            training_name TEXT    NOT NULL,
            start_date    DATE,
            end_date      DATE,
            description   TEXT,
            created_at    DATETIME DEFAULT CURRENT_TIMESTAMP
        );

        CREATE TABLE IF NOT EXISTS training_enrollment (
            id            INTEGER PRIMARY KEY AUTOINCREMENT,
            employee_id   INTEGER NOT NULL REFERENCES employee(id),
            training_id   INTEGER NOT NULL REFERENCES training(id),
            status        TEXT DEFAULT 'enrolled',
            created_at    DATETIME DEFAULT CURRENT_TIMESTAMP,
            UNIQUE(employee_id, training_id)
        );

        CREATE TABLE IF NOT EXISTS training_history (
            id                  INTEGER PRIMARY KEY AUTOINCREMENT,
            employee_id         INTEGER NOT NULL REFERENCES employee(id),
            training_id         INTEGER NOT NULL REFERENCES training(id),
            attendance_rate     REAL    DEFAULT 0.0,
            understanding_level INTEGER DEFAULT 0,
            report_score        INTEGER DEFAULT 0,
            created_at          DATETIME DEFAULT CURRENT_TIMESTAMP,
            UNIQUE(employee_id, training_id)
        );

        CREATE TABLE IF NOT EXISTS evaluation (
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            employee_id INTEGER NOT NULL REFERENCES employee(id),
            score       REAL,
            ai_comment  TEXT,
            created_at  DATETIME DEFAULT CURRENT_TIMESTAMP
        );

        CREATE TABLE IF NOT EXISTS daily_report (
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            employee_id INTEGER NOT NULL REFERENCES employee(id),
            report_date DATE    NOT NULL,
            content     TEXT,
            memo        TEXT,
            created_at  DATETIME DEFAULT CURRENT_TIMESTAMP
        );
    """)
    cur.executescript("""
        INSERT OR IGNORE INTO department (dept_name) VALUES ('人事部'), ('開発部'), ('営業部');
        INSERT OR IGNORE INTO employee (employee_no, name, department, position, hire_date) VALUES
          ('EMP001', '山田 太郎', '開発部', '一般', '2024-04-01'),
          ('EMP002', '佐藤 花子', '人事部', '主任', '2023-10-01');
        INSERT OR IGNORE INTO training (id, training_name, start_date, end_date, description) VALUES
          (1, 'Python基礎研修', '2026-06-01', '2026-06-05', 'Pythonと業務自動化の基礎を学ぶ研修');
        INSERT OR IGNORE INTO training_history (employee_id, training_id, attendance_rate, understanding_level, report_score) VALUES
          (1, 1, 95, 82, 88),
          (2, 1, 90, 76, 80);
    """)
    conn.commit()
    conn.close()
    print("データベースを初期化しました。")


if __name__ == "__main__":
    init_db()
