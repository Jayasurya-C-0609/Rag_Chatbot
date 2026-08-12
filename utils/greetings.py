import re

GREETINGS = {
    "hi",
    "hello",
    "hey",
    "good morning",
    "good afternoon",
    "good evening",
    "how are you",
    "whats up",
    "what's up",
    "thanks",
    "thank you",
    "bye",
    "goodbye",
    "see you"
}

def normalize(text):
    if text is None:
        return ""
    text = str(text).lower().strip()
    text = re.sub(r"[^\w\s]", "", text)
    return text

def is_greeting(text):
    text = normalize(text)
    return text in GREETINGS

def greeting_response(text):
    text = normalize(text)

    if text in {"hi", "hello", "hey"}:
        return "Hello! I'm your PDF RAG assistant. Ask me anything about your uploaded documents."

    if text == "good morning":
        return "Good morning! How can I help you with your PDF documents today?"

    if text == "good afternoon":
        return "Good afternoon! What would you like to know from your documents?"

    if text == "good evening":
        return "Good evening! I'm ready to help with your uploaded PDFs."

    if text == "how are you":
        return "I'm doing well, thank you! I'm ready to help you explore your PDF documents."

    if text in {"thanks", "thank you"}:
        return "You're welcome! Let me know if you have any questions about your documents."

    if text in {"bye", "goodbye", "see you"}:
        return "Goodbye! Have a great day, and feel free to come back anytime."

    return "Hello! How can I help you with your PDF documents?"