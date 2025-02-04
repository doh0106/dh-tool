from contextlib import contextmanager, asynccontextmanager


@contextmanager
def log_block(logger, name):
    logger.info(f"Start: {name}")
    try:
        yield
    finally:
        logger.info(f"End: {name}")


@asynccontextmanager
async def log_async_block(logger, name):
    logger.info(f"Start: {name}")
    try:
        yield
    finally:
        logger.info(f"End: {name}")
