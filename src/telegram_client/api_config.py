"""
Конфигурация Telegram API
"""

# Ваши API данные
API_ID = 36543854
API_HASH = "bf8037bc98bf353fc649506562968857"

# Название приложения (можно изменить)
APP_TITLE = "Telegram AutoPosting"
APP_SHORT_NAME = "tgautopost"

# Сервера MTProto
TEST_SERVERS = [
    {
        "ip": "149.154.167.40",
        "port": 443,
        "dc_id": 2,
        "test": True
    }
]

PRODUCTION_SERVERS = [
    {
        "ip": "149.154.167.50",
        "port": 443,
        "dc_id": 2,
        "test": False
    }
]

# Публичные ключи
PUBLIC_KEYS = {
    "test": """-----BEGIN RSA PUBLIC KEY-----
MIIBCgKCAQEAyMEdY1aR+sCR3ZSJrtztKTKqigvO/vBfqACJLZtS7QMgCGXJ6XIR
yy7mx66W0/sOFa7/1mAZtEoIokDP3ShoqF4fVNb6XeqgQfaUHd8wJpDWHcR2OFwv
plUUI1PLTktZ9uW2WE23b+ixNwJjJGwBDJPQEQFBE+vfmH0JP503wr5INS1poWg/
j25sIWeYPHYeOrFp/eXaqhISP6G+q2IeTaWTXpwZj4LzXq5YOpk4bYEQ6mvRq7D1
aHWfYmlEGepfaYR8Q0YqvvhYtMte3ITnuSJs171+GDqpdKcSwHnd6FudwGO4pcCO
j4WcDuXc2CTHgH8gFTNhp/Y8/SpDOhvn9QIDAQAB
-----END RSA PUBLIC KEY-----""",
    
    "production": """-----BEGIN RSA PUBLIC KEY-----
MIIBCgKCAQEA6LszBcC1LGzyr992NzE0ieY+BSaOW622Aa9Bd4ZHLl+TuFQ4lo4g
5nKaMBwK/BIb9xUfg0Q29/2mgIR6Zr9krM7HjuIcCzFvDtr+L0GQjae9H0pRB2OO
62cECs5HKhT5DZ98K33vmWiLowc621dQuwKWSQKjWf50XYFw42h21P2KXUGyp2y/
+aEyZ+uVgLLQbRA1dEjSDZ2iGRy12Mk5gpYc397aYp438fsJoHIgJ2lgMv5h7WY9
t6N/byY9Nw9p21Og3AoXSL2q/2IJ1WRUhebgAdGVMlV1fkuOQoEzR7EdpqtQD9Cs
5+bfo3Nhmcyvk5ftB0WkJ9z6bNZ7yxrP8wIDAQAB
-----END RSA PUBLIC KEY-----"""
}

# Настройки сессий
SESSION_SETTINGS = {
    "device_model": "Desktop",
    "system_version": "Windows 10",
    "app_version": "1.0.0",
    "lang_code": "en",
    "system_lang_code": "en",
    "timezone": "UTC"
}

def get_config():
    """Получить конфигурацию для Pyrogram"""
    return {
        "api_id": API_ID,
        "api_hash": API_HASH,
        "app_version": SESSION_SETTINGS["app_version"],
        "device_model": SESSION_SETTINGS["device_model"],
        "system_version": SESSION_SETTINGS["system_version"],
        "lang_code": SESSION_SETTINGS["lang_code"],
        "system_lang_code": SESSION_SETTINGS["system_lang_code"],
    }