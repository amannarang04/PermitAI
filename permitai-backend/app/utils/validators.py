import re

def validate_email(email: str) -> bool:
    email_regex = r"^[\w\.-]+@[\w\.-]+\.\w+$"
    return bool(re.match(email_regex, email))

def validate_phone(phone: str) -> bool:
    phone_regex = r"^\+?1?\d{9,15}$"
    clean = re.sub(r"[\s\-\(\)\+]", "", phone or "")
    return bool(re.match(phone_regex, clean))
