VALIDATION_KEY = None
DEV_PASSWORDS = {} # E.g {"admin": "password"}

if VALIDATION_KEY is None:
    raise ValueError("Please set a VALIDATION_KEY in secret_key.py")
