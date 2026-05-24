import re


def redact_pii(text):
    if not text:
        return text

    text = re.sub(r'[\w\.-]+@[\w\.-]+\.\w+', '[REDACTED_EMAIL]', text)
    text = re.sub(r'\b\d{10}\b', '[REDACTED_PHONE]', text)
    text = re.sub(r'\b\d{12}\b', '[REDACTED_ID]', text)

    return text