"""評価管理ビジネスロジック"""
from database import get_db


def calc_score(attendance_rate: float, understanding_level: int, report_score: int) -> float:
    """出席率30%、理解度40%、課題30%で総合スコアを計算する。"""
    return round((attendance_rate * 0.3) + (understanding_level * 0.4) + (report_score * 0.3), 1)


def get_evaluation_targets() -> list:
    conn = get_db()
    rows = conn.execute(
        """
        SELECT
            e.id AS employee_id,
            e.employee_no,
            e.name,
            e.department,
            ROUND(AVG(COALESCE(th.attendance_rate, 0)), 1) AS attendance_rate,
            ROUND(AVG(COALESCE(th.understanding_level, 0)), 1) AS understanding_level,
            ROUND(AVG(COALESCE(th.report_score, 0)), 1) AS report_score,
            ev.id AS evaluation_id,
            ev.score,
            ev.ai_comment,
            ev.created_at
        FROM employee e
        LEFT JOIN training_history th ON th.employee_id = e.id
        LEFT JOIN (
            SELECT v1.*
              FROM evaluation v1
              JOIN (
                    SELECT employee_id, MAX(id) AS max_id
                      FROM evaluation
                     GROUP BY employee_id
                   ) v2 ON v1.id = v2.max_id
        ) ev ON ev.employee_id = e.id
        WHERE e.is_active = 1
        GROUP BY e.id
        ORDER BY e.employee_no
        """
    ).fetchall()
    conn.close()

    result = []
    for row in rows:
        item = dict(row)
        item["calculated_score"] = calc_score(
            float(item.get("attendance_rate") or 0),
            int(item.get("understanding_level") or 0),
            int(item.get("report_score") or 0),
        )
        result.append(item)
    return result


def save_evaluation(employee_id: int, score: float, ai_comment: str) -> int:
    conn = get_db()
    cur = conn.execute(
        "INSERT INTO evaluation (employee_id, score, ai_comment) VALUES (?, ?, ?)",
        (employee_id, score, ai_comment),
    )
    conn.commit()
    evaluation_id = cur.lastrowid
    conn.close()
    return evaluation_id


def get_export_rows() -> list:
    return get_evaluation_targets()
