import logging

class Logger:

    logger = logging.getLogger(__name__)
    logger.setLevel(logging.DEBUG)

    formatter = logging.Formatter('{asctime} - {levelname} - {message}', style='{')

    ch = logging.StreamHandler()
    ch.setLevel(logging.INFO)
    ch.setFormatter(formatter)
    logger.addHandler(ch)

    fh = logging.FileHandler('load_fund_echo.logs')
    fh.setLevel(logging.ERROR)
    formatter_file = logging.Formatter('{asctime} - {name} - {levelname} - {message}', style='{')
    fh.setFormatter(formatter_file)
    logger.addHandler(fh)

    @classmethod
    def info(cls, message):
        cls.logger.info(message)

    @classmethod
    def debug(cls, message):
        cls.logger.debug(message)

    @classmethod
    def warning(cls, message):
        cls.logger.warning(message)

    @classmethod
    def error(cls, message):
        cls.logger.error(message)

    @classmethod
    def exception(cls, message):
        cls.logger.exception(message)