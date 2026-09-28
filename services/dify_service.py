"""Dify API連携（評価コメント生成・RAG検索・FAQチャット）"""
import requests
from config import Config


def _headers(api_key: str | None = None) -> dict:
    key = api_key or Config.DIFY_API_KEY
    return {
        "Authorization": f"Bearer {key}",
        "Content-Type": "application/json",
    }


def _clean_ai_answer(text: str) -> str:
    """画面表示用にDify回答のMarkdown太字記号を除去する。"""
    return (text or "").replace("**", "").strip()


def _fallback_comment(name: str, understanding: float, attendance: float, submission: float) -> str:
    score = round(attendance * 0.3 + understanding * 0.4 + submission * 0.3, 1)
    if score >= 80:
        level = "非常に良好です"
        advice = "今後は周囲への共有や応用課題への挑戦を期待します。"
    elif score >= 60:
        level = "概ね良好です"
        advice = "理解が浅い部分を復習し、課題の精度を高めるとさらに伸びます。"
    else:
        level = "基礎の定着に追加支援が必要です"
        advice = "出席状況と課題提出を確認し、短い単位で復習を進めましょう。"
    return f"{name}さんの研修状況は{level}。出席率{attendance}%、理解度{understanding}%、課題スコア{submission}%です。{advice}"


def generate_evaluation_comment(name: str, understanding: float, attendance: float, submission: float) -> str:
    if not Config.DIFY_API_KEY:
        return _fallback_comment(name, understanding, attendance, submission)

    prompt = (
        "あなたは人事評価の専門家です。以下の研修データをもとに、"
        "200字以内・前向きな表現・具体的な改善点1つを含めた評価コメントを作成してください。\n"
        f"対象者：{name}\n理解度：{understanding}%\n出席率：{attendance}%\n課題スコア：{submission}%"
    )
    payload = {
        "inputs": {},
        "query": prompt,
        "response_mode": "blocking",
        "user": "human-resource-app",
    }
    try:
        res = requests.post(f"{Config.DIFY_API_URL}/chat-messages", headers=_headers(), json=payload, timeout=30)
        res.raise_for_status()
        data = res.json()
        return _clean_ai_answer(data.get("answer", "")) or _fallback_comment(name, understanding, attendance, submission)
    except requests.RequestException:
        return _fallback_comment(name, understanding, attendance, submission)


def search_knowledge(question: str, top_k: int = 3) -> dict:
    if not Config.DIFY_API_KEY:
        return {
            "records": [
                {
                    "title": "ローカル確認用サンプル",
                    "content": "DIFY_API_KEY を .env に設定すると、Dify Knowledge / Chat API に問い合わせます。",
                    "score": 1.0,
                }
            ]
        }
    payload = {
        "inputs": {"top_k": top_k},
        "query": question,
        "response_mode": "blocking",
        "user": "human-resource-app",
    }
    try:
        res = requests.post(f"{Config.DIFY_API_URL}/chat-messages", headers=_headers(), json=payload, timeout=30)
        res.raise_for_status()
        data = res.json()
        answer = _clean_ai_answer(data.get("answer", ""))
        return {"records": [{"title": "Dify回答", "content": answer, "score": 1.0}] if answer else []}
    except requests.RequestException as exc:
        return {"records": [], "error": str(exc)}


def chat_with_faq(message: str, conversation_id: str = "") -> dict:
    """FAQチャットボットへ問い合わせ、回答と会話IDを返す。"""
    if not Config.DIFY_API_KEY:
        return {
            "success": False,
            "answer": "",
            "conversation_id": conversation_id,
            "error": "DIFY_API_KEY が設定されていません（.env を確認してください）",
        }

    payload = {
        "inputs": {},
        "query": message,
        "response_mode": "blocking",
        "user": "human-resource-app",
    }

    # 2回目以降は同じ conversation_id を送り、会話の文脈を保持する
    if conversation_id:
        payload["conversation_id"] = conversation_id

    try:
        res = requests.post(
            f"{Config.DIFY_API_URL}/chat-messages",
            headers=_headers(),
            json=payload,
            timeout=30,
        )
        res.raise_for_status()
        data = res.json()
        answer = _clean_ai_answer(data.get("answer", ""))

        if not answer:
            return {
                "success": False,
                "answer": "",
                "conversation_id": data.get("conversation_id", conversation_id),
                "error": "AIからの回答が空でした",
            }

        return {
            "success": True,
            "answer": answer,
            "conversation_id": data.get("conversation_id", conversation_id),
            "error": "",
        }

    except requests.exceptions.Timeout:
        return {
            "success": False,
            "answer": "",
            "conversation_id": conversation_id,
            "error": "Dify APIへのリクエストがタイムアウトしました",
        }
    except requests.exceptions.ConnectionError:
        return {
            "success": False,
            "answer": "",
            "conversation_id": conversation_id,
            "error": "Dify APIに接続できません",
        }
    except requests.RequestException as exc:
        return {
            "success": False,
            "answer": "",
            "conversation_id": conversation_id,
            "error": f"FAQチャットの呼び出しでエラーが発生しました: {exc}",
        }

