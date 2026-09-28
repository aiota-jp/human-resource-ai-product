"""研修管理ビジネスロジック"""
from database import get_db


def get_all_trainings() -> list:
    conn = get_db()
    rows = conn.execute("SELECT * FROM training ORDER BY start_date DESC, id DESC").fetchall()
    conn.close()
    return [dict(row) for row in rows]


def get_training_by_id(training_id: int) -> dict | None:
    conn = get_db()
    row = conn.execute("SELECT * FROM training WHERE id = ?", (training_id,)).fetchone()
    conn.close()
    return dict(row) if row else None


def create_training(data: dict) -> int:
    conn = get_db()
    cur = conn.execute(
        """
        INSERT INTO training (training_name, start_date, end_date, description)
        VALUES (?, ?, ?, ?)
        """,
        (
            data.get("training_name"),
            data.get("start_date"),
            data.get("end_date"),
            data.get("description"),
        ),
    )
    conn.commit()
    training_id = cur.lastrowid
    conn.close()
    return training_id


def get_training_histories(training_id: int) -> list:
    conn = get_db()
    rows = conn.execute(
        """
        SELECT
            e.id AS employee_id,
            e.employee_no,
            e.name,
            e.department,
            th.id AS history_id,
            COALESCE(th.attendance_rate, 0) AS attendance_rate,
            COALESCE(th.understanding_level, 0) AS understanding_level,
            COALESCE(th.report_score, 0) AS report_score
        FROM employee e
        LEFT JOIN training_history th
               ON th.employee_id = e.id AND th.training_id = ?
        WHERE e.is_active = 1
        ORDER BY e.employee_no
        """,
        (training_id,),
    ).fetchall()
    conn.close()
    return [dict(row) for row in rows]


def upsert_training_history(employee_id: int, training_id: int, data: dict) -> bool:
    conn = get_db()
    conn.execute(
        """
        INSERT INTO training_history
            (employee_id, training_id, attendance_rate, understanding_level, report_score)
        VALUES (?, ?, ?, ?, ?)
        ON CONFLICT(employee_id, training_id) DO UPDATE SET
            attendance_rate = excluded.attendance_rate,
            understanding_level = excluded.understanding_level,
            report_score = excluded.report_score
        """,
        (
            employee_id,
            training_id,
            float(data.get("attendance_rate") or 0),
            int(data.get("understanding_level") or 0),
            int(data.get("report_score") or 0),
        ),
    )
    conn.commit()
    conn.close()
    return True


def calc_attendance_rate(employee_id: int, training_id: int) -> float:
    conn = get_db()
    row = conn.execute(
        "SELECT attendance_rate FROM training_history WHERE employee_id = ? AND training_id = ?",
        (employee_id, training_id),
    ).fetchone()
    conn.close()
    return float(row["attendance_rate"]) if row else 0.0
