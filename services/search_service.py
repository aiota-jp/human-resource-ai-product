"""RAG検索・FAQチャットの薄いラッパー"""
from services.dify_service import search_knowledge, chat_with_faq


def search_documents(question: str) -> dict:
    if not question.strip():
        return {"records": [], "error": "検索キーワードを入力してください。"}
    return search_knowledge(question)


def send_chat_message(message: str, conversation_id: str = "") -> dict:
    if not message.strip():
        return {"success": False, "answer": "", "conversation_id": conversation_id, "error": "メッセージを入力してください"}
    return chat_with_faq(message, conversation_id)
