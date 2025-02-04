from functools import wraps
import inspect

import pandas as pd

from .logger import Logger
from .log_levels import get_log_level


def summarize_data(data):
    """데이터의 요약 정보를 반환하는 함수"""
    if isinstance(data, pd.DataFrame):
        return f"<DataFrame: shape={data.shape}, columns={list(data.columns)}>"
    elif isinstance(data, dict):
        keys = list(data.keys())
        return f"<dict: keys={keys[:5]}{'...' if len(keys) > 5 else ''}, total_keys={len(keys)}>"
    elif isinstance(data, list):
        return f"<list: length={len(data)}, first_item={data[0] if data else 'None'}>"
    elif isinstance(data, str) and len(data) > 100:
        return f"<str: length={len(data)}, preview='{data[:50]}...'>"
    else:
        return repr(data)


def auto_logger(
    logger: Logger, call_level="DEBUG", result_level="INFO", error_level="ERROR"
):
    def decorator(func):
        @wraps(func)
        async def async_wrapper(*args, **kwargs):
            # 함수 호출 시 로깅
            summarized_args = [summarize_data(arg) for arg in args]
            summarized_kwargs = {k: summarize_data(v) for k, v in kwargs.items()}

            logger.log(
                get_log_level(call_level),
                f"Called {func.__name__} with args={summarized_args}, kwargs={summarized_kwargs}",
            )

            try:
                result = await func(*args, **kwargs)  # 비동기 함수 처리
                logger.log(
                    get_log_level(result_level),
                    f"{func.__name__} returned {summarize_data(result)}",
                )
                return result
            except Exception as e:
                logger.log(
                    get_log_level(error_level),
                    f"Error in {func.__name__}: {e}",
                    exc_info=True,
                )
                raise

        @wraps(func)
        def sync_wrapper(*args, **kwargs):
            # 동기 함수 호출 시 로깅
            summarized_args = [summarize_data(arg) for arg in args]
            summarized_kwargs = {k: summarize_data(v) for k, v in kwargs.items()}

            logger.log(
                get_log_level(call_level),
                f"Called {func.__name__} with args={summarized_args}, kwargs={summarized_kwargs}",
            )

            try:
                result = func(*args, **kwargs)
                logger.log(
                    get_log_level(result_level),
                    f"{func.__name__} returned {summarize_data(result)}",
                )
                return result
            except Exception as e:
                logger.log(
                    get_log_level(error_level),
                    f"Error in {func.__name__}: {e}",
                    exc_info=True,
                )
                raise

        # 함수가 비동기인지 확인 후 적절한 래퍼 선택
        return async_wrapper if inspect.iscoroutinefunction(func) else sync_wrapper

    return decorator
