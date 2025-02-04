import logging

# 중앙 집중화된 로깅 레벨 매핑
LEVELS = {
    "DEBUG": logging.DEBUG,
    "INFO": logging.INFO,
    "WARNING": logging.WARNING,
    "ERROR": logging.ERROR,
    "CRITICAL": logging.CRITICAL,
}


# 문자열 또는 숫자로 로깅 레벨 변환
def get_log_level(level):
    if isinstance(level, str):
        return LEVELS.get(level.upper(), logging.INFO)
    elif isinstance(level, int):
        return level
    else:
        raise ValueError(f"Invalid log level: {level}")
