"""日報管理ビジネスロジック"""
from database import get_db


def get_reports(employee_id: int | None = None) -> list:
    conn = get_db()
    sql = """
        SELECT dr.*, e.name AS employee_name, e.employee_no
          FROM daily_report dr
          JOIN employee e ON e.id = dr.employee_id
    """
    params = ()
    if employee_id is not None:
        sql += " WHERE dr.employee_id = ?"
        params = (employee_id,)
    sql += " ORDER BY dr.report_date DESC, dr.id DESC"
    rows = conn.execute(sql, params).fetchall()
    conn.close()
    return [dict(row) for row in rows]


def create_report(data: dict) -> int:
    conn = get_db()
    cur = conn.execute(
        """
        INSERT INTO daily_report (employee_id, report_date, content, memo)
        VALUES (?, ?, ?, ?)
        """,
        (
            int(data.get("employee_id")),
            data.get("report_date"),
            data.get("content"),
            data.get("memo"),
        ),
    )
    conn.commit()
    report_id = cur.lastrowid
    conn.close()
    return report_id
