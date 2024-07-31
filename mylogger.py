# myLogger.py

from logging import getLogger, handlers, Formatter, DEBUG


def set_logger():

    # 全体のログ設定
   # ファイルに書き出す。ログが100KB溜まったらバックアップにして新しいファイルを作る。
    root_logger = getLogger()
    root_logger.setLevel(DEBUG)
    rotating_handler = handlers.RotatingFileHandler(
        r'./log/app.log',
        mode="a",
        maxBytes=100 * 1024,
        backupCount=3,
        encoding="utf-8"
    )
    format = Formatter(
        '%(asctime)s : %(levelname)s : %(filename)s - %(message)s')
    rotating_handler.setFormatter(format)
    root_logger.addHandler(rotating_handler)
