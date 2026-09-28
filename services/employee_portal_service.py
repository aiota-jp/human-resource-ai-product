"""社員本人用マイページのデータ取得サービス"""
from database import get_db


def get_employee_portal_data(employee_id: int) -> dict | None:
    """社員情報、研修履歴、最新評価、直近の日報をまとめて取得する。"""
    conn = get_db()
    employee = conn.execute(
        "SELECT * FROM employee WHERE id = ? AND is_active = 1",
        (employee_id,),
    ).fetchone()
    if not employee:
        conn.close()
        return None

    histories = conn.execute(
        """
        SELECT t.training_name, t.start_date, t.end_date,
               th.attendance_rate, th.understanding_level, th.report_score
          FROM training_history th
          JOIN training t ON t.id = th.training_id
         WHERE th.employee_id = ?
         ORDER BY t.start_date DESC, t.id DESC
        """,
        (employee_id,),
    ).fetchall()
    evaluation = conn.execute(
        """
        SELECT score, ai_comment, created_at
          FROM evaluation
         WHERE employee_id = ?
         ORDER BY id DESC
         LIMIT 1
        """,
        (employee_id,),
    ).fetchone()
    reports = conn.execute(
        """
        SELECT report_date, content, memo
          FROM daily_report
         WHERE employee_id = ?
         ORDER BY report_date DESC, id DESC
         LIMIT 5
        """,
        (employee_id,),
    ).fetchall()
    conn.close()
    return {
        "employee": dict(employee),
        "histories": [dict(row) for row in histories],
        "evaluation": dict(evaluation) if evaluation else None,
        "reports": [dict(row) for row in reports],
    }
