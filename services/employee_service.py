"""社員管理ビジネスロジック"""
from database import get_db


def _row_to_dict(row):
    return dict(row) if row else None


def get_all_employees(keyword: str = "") -> list:
    conn = get_db()
    if keyword:
        like = f"%{keyword}%"
        rows = conn.execute(
            """
            SELECT * FROM employee
            WHERE is_active = 1 AND (name LIKE ? OR department LIKE ? OR employee_no LIKE ?)
            ORDER BY employee_no
            """,
            (like, like, like),
        ).fetchall()
    else:
        rows = conn.execute(
            "SELECT * FROM employee WHERE is_active = 1 ORDER BY employee_no"
        ).fetchall()
    conn.close()
    return [dict(row) for row in rows]


def get_employee_by_id(employee_id: int) -> dict | None:
    conn = get_db()
    row = conn.execute("SELECT * FROM employee WHERE id = ?", (employee_id,)).fetchone()
    conn.close()
    return _row_to_dict(row)


def create_employee(data: dict) -> int:
    conn = get_db()
    cur = conn.execute(
        """
        INSERT INTO employee (employee_no, name, department, position, hire_date)
        VALUES (?, ?, ?, ?, ?)
        """,
        (
            data.get("employee_no"),
            data.get("name"),
            data.get("department"),
            data.get("position"),
            data.get("hire_date"),
        ),
    )
    conn.commit()
    employee_id = cur.lastrowid
    conn.close()
    return employee_id


def update_employee(employee_id: int, data: dict) -> bool:
    conn = get_db()
    cur = conn.execute(
        """
        UPDATE employee
           SET employee_no = ?, name = ?, department = ?, position = ?, hire_date = ?,
               updated_at = CURRENT_TIMESTAMP
         WHERE id = ?
        """,
        (
            data.get("employee_no"),
            data.get("name"),
            data.get("department"),
            data.get("position"),
            data.get("hire_date"),
            employee_id,
        ),
    )
    conn.commit()
    ok = cur.rowcount > 0
    conn.close()
    return ok


def delete_employee(employee_id: int) -> bool:
    conn = get_db()
    cur = conn.execute(
        "UPDATE employee SET is_active = 0, updated_at = CURRENT_TIMESTAMP WHERE id = ?",
        (employee_id,),
    )
    conn.commit()
    ok = cur.rowcount > 0
    conn.close()
    return ok
