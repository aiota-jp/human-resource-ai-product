"""Flaskアプリケーション エントリーポイント"""
import os
from datetime import date
from flask import Flask, render_template, request, redirect, url_for, session, flash, send_file, jsonify
from werkzeug.utils import secure_filename
from flask_wtf.csrf import CSRFProtect
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from config import Config
from database import init_db
from services.auth_service import authenticate, ensure_default_users, login_required, roles_required
from services.employee_service import get_all_employees, get_employee_by_id, create_employee, update_employee, delete_employee
from services.training_service import get_all_trainings, get_training_by_id, create_training, get_training_histories, upsert_training_history
from services.evaluation_service import get_evaluation_targets, save_evaluation
from services.dify_service import generate_evaluation_comment
from services.excel_service import allowed_file, import_employee_excel, import_training_excel, export_evaluation_excel
from services.report_service import get_reports, create_report
from services.search_service import search_documents, send_chat_message
from services.employee_portal_service import get_employee_portal_data

app = Flask(__name__)
app.config.from_object(Config)

# 公開環境向け保護
csrf = CSRFProtect(app)
limiter = Limiter(key_func=get_remote_address, app=app, default_limits=[])

os.makedirs(app.config["UPLOAD_FOLDER"], exist_ok=True)
os.makedirs(app.config["OUTPUT_FOLDER"], exist_ok=True)
init_db()

# 動作確認用ユーザーは開発環境でのみ自動作成する
if os.getenv("FLASK_ENV", "development") != "production":
    ensure_default_users()


@app.route("/login", methods=["GET", "POST"])
@limiter.limit("10 per minute", methods=["POST"])
def login():
    if request.method == "POST":
        user = authenticate(request.form.get("username", ""), request.form.get("password", ""))
        if user:
            session["user_id"] = user["id"]
            session["username"] = user["username"]
            session["role"] = user["role"]
            session["employee_id"] = user.get("employee_id")
            session["employee_name"] = user.get("employee_name")
            flash("ログインしました", "success")
            if user.get("employee_id"):
                return redirect(url_for("employee_portal"))
            return redirect(url_for("index"))
        flash("ユーザーIDまたはパスワードが違います", "danger")
    return render_template("login.html")


@app.route("/logout")
def logout():
    session.clear()
    flash("ログアウトしました", "info")
    return redirect(url_for("login"))


@app.route("/")
@login_required
def index():
    if session.get("employee_id"):
        return redirect(url_for("employee_portal"))
    dashboard_stats = {
        "employee_count": 0,
        "training_count": 0,
        "evaluation_count": 0,
        "role": session.get("role", "user"),
    }
    if session.get("role") in ("staff", "admin"):
        employees = get_all_employees()
        trainings = get_all_trainings()
        evaluations = get_evaluation_targets()
        dashboard_stats.update({
            "employee_count": len(employees),
            "training_count": len(trainings),
            "evaluation_count": sum(1 for item in evaluations if item.get("ai_comment")),
        })
    return render_template("index.html", dashboard_stats=dashboard_stats)


@app.route("/my-page")
@login_required
def employee_portal():
    """社員番号でログインした社員専用のマイページ。"""
    employee_id = session.get("employee_id")
    if not employee_id:
        flash("社員専用画面を利用できるアカウントではありません", "warning")
        return redirect(url_for("index"))
    portal = get_employee_portal_data(int(employee_id))
    if not portal:
        session.clear()
        flash("社員情報が見つかりません。管理者にお問い合わせください", "danger")
        return redirect(url_for("login"))
    return render_template("employee_portal.html", portal=portal)


@app.route("/employees")
@login_required
@roles_required("staff", "admin")
def employee_list():
    keyword = request.args.get("keyword", "")
    return render_template("employee_list.html", employees=get_all_employees(keyword))


@app.route("/employees/new", methods=["GET", "POST"])
@login_required
@roles_required("staff", "admin")
def employee_new():
    if request.method == "POST":
        create_employee(request.form.to_dict())
        flash("社員を登録しました", "success")
        return redirect(url_for("employee_list"))
    return render_template("employee_form.html", employee=None)


@app.route("/employees/<int:employee_id>/edit", methods=["GET", "POST"])
@login_required
@roles_required("staff", "admin")
def employee_edit(employee_id):
    employee = get_employee_by_id(employee_id)
    if not employee:
        flash("社員が見つかりません", "warning")
        return redirect(url_for("employee_list"))
    if request.method == "POST":
        update_employee(employee_id, request.form.to_dict())
        flash("社員情報を更新しました", "success")
        return redirect(url_for("employee_list"))
    return render_template("employee_form.html", employee=employee)


@app.route("/employees/<int:employee_id>/delete", methods=["POST"])
@login_required
@roles_required("admin")
def employee_delete(employee_id):
    delete_employee(employee_id)
    flash("社員を削除しました", "success")
    return redirect(url_for("employee_list"))


@app.route("/trainings")
@login_required
@roles_required("staff", "admin")
def training_list():
    return render_template("training_list.html", trainings=get_all_trainings())


@app.route("/trainings/new", methods=["GET", "POST"])
@login_required
@roles_required("staff", "admin")
def training_new():
    if request.method == "POST":
        create_training(request.form.to_dict())
        flash("研修を登録しました", "success")
        return redirect(url_for("training_list"))
    return render_template("training_form.html", training=None)


@app.route("/trainings/<int:training_id>/history", methods=["GET", "POST"])
@login_required
@roles_required("staff", "admin")
def training_history(training_id):
    training = get_training_by_id(training_id)
    if not training:
        flash("研修が見つかりません", "warning")
        return redirect(url_for("training_list"))
    if request.method == "POST":
        for emp_id in request.form.getlist("employee_id"):
            upsert_training_history(int(emp_id), training_id, {
                "attendance_rate": request.form.get(f"attendance_rate_{emp_id}"),
                "understanding_level": request.form.get(f"understanding_level_{emp_id}"),
                "report_score": request.form.get(f"report_score_{emp_id}"),
            })
        flash("研修履歴を保存しました", "success")
        return redirect(url_for("training_history", training_id=training_id))
    return render_template("training_history.html", training=training, histories=get_training_histories(training_id))


@app.route("/evaluations")
@login_required
@roles_required("staff", "admin")
def evaluation_list():
    evaluations = get_evaluation_targets()
    count = len(evaluations)
    evaluation_stats = {
        "target_count": count,
        "attendance_average": round(sum(float(item.get("attendance_rate") or 0) for item in evaluations) / count, 1) if count else 0,
        "understanding_average": round(sum(float(item.get("understanding_level") or 0) for item in evaluations) / count, 1) if count else 0,
        "generated_count": sum(1 for item in evaluations if item.get("ai_comment")),
    }
    return render_template("evaluation.html", evaluations=evaluations, evaluation_stats=evaluation_stats)


@app.route("/evaluations/<int:employee_id>/generate", methods=["POST"])
@login_required
@roles_required("staff", "admin")
def evaluation_generate(employee_id):
    target = next((e for e in get_evaluation_targets() if e["employee_id"] == employee_id), None)
    if not target:
        flash("評価対象が見つかりません", "warning")
        return redirect(url_for("evaluation_list"))
    comment = generate_evaluation_comment(
        target["name"], target["understanding_level"], target["attendance_rate"], target["report_score"]
    )
    save_evaluation(employee_id, target["calculated_score"], comment)
    flash("AI評価コメントを生成しました", "success")
    return redirect(url_for("evaluation_list"))


@app.route("/import", methods=["GET", "POST"])
@login_required
@roles_required("staff", "admin")
def import_excel():
    trainings = get_all_trainings()
    if request.method == "POST":
        file = request.files.get("file")
        import_type = request.form.get("import_type")
        if not file or file.filename == "":
            flash("ファイルを選択してください", "warning")
            return redirect(url_for("import_excel"))
        if not allowed_file(file.filename):
            flash("xlsx または csv を指定してください", "danger")
            return redirect(url_for("import_excel"))
        path = os.path.join(app.config["UPLOAD_FOLDER"], secure_filename(file.filename))
        file.save(path)
        if import_type == "training":
            count, errors = import_training_excel(path, int(request.form.get("training_id") or 0))
        else:
            count, errors = import_employee_excel(path)
        flash(f"{count}件取り込みました", "success")
        for error in errors[:5]:
            flash(error, "warning")
        return redirect(url_for("import_excel"))
    return render_template("import.html", trainings=trainings)


@app.route("/export")
@login_required
@roles_required("staff", "admin")
def export_excel():
    output_path = os.path.join(app.config["OUTPUT_FOLDER"], f"evaluation_{date.today().isoformat()}.xlsx")
    export_evaluation_excel(get_evaluation_targets(), output_path)
    return send_file(output_path, as_attachment=True)


@app.route("/reports", methods=["GET", "POST"])
@login_required
def report_list():
    employee_id = session.get("employee_id")
    if request.method == "POST":
        report_data = request.form.to_dict()
        if employee_id:
            report_data["employee_id"] = str(employee_id)
        create_report(report_data)
        flash("日報を登録しました", "success")
        return redirect(url_for("report_list"))
    employees = [get_employee_by_id(int(employee_id))] if employee_id else get_all_employees()
    return render_template(
        "report.html",
        reports=get_reports(int(employee_id)) if employee_id else get_reports(),
        employees=employees,
        today=date.today().isoformat(),
        employee_mode=bool(employee_id),
    )


@app.route("/reports/new")
@login_required
def report_new():
    return redirect(url_for("report_list"))


@app.route("/search", methods=["GET", "POST"])
@login_required
def search():
    result = None
    question = ""
    if request.method == "POST":
        question = request.form.get("question", "")
        result = search_documents(question)
    return render_template("search.html", result=result, question=question)


@app.route("/chat")
@login_required
def chat():
    """FAQチャット画面"""
    return render_template("chat.html")


@app.route("/chat/send", methods=["POST"])
@login_required
def chat_send():
    """FAQチャットのメッセージ送信API"""
    data = request.get_json(silent=True) or {}
    message = data.get("message", "").strip()
    conversation_id = data.get("conversation_id", "")

    if not message:
        return jsonify({
            "success": False,
            "answer": "",
            "conversation_id": conversation_id,
            "error": "メッセージを入力してください",
        })

    result = send_chat_message(message, conversation_id)
    return jsonify(result)


if __name__ == "__main__":
    app.run(debug=Config.DEBUG, host="0.0.0.0", port=5000)
