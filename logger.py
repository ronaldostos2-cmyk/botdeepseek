# logger.py
import logging
import sys
from datetime import datetime


class SafeStreamHandler(logging.StreamHandler):
    def emit(self, record):
        try:
            msg = self.format(record)
            # Remove emojis para evitar problemas de encoding
            msg = self.remove_emojis(msg)
            stream = self.stream
            stream.write(msg + self.terminator)
            self.flush()
        except Exception:
            pass

    def remove_emojis(self, text):
        """Remove emojis para evitar problemas de encoding no Windows"""
        import re
        # Remove caracteres Unicode problemáticos
        emoji_pattern = re.compile("["
                                   u"\U0001F600-\U0001F64F"  # emoticons
                                   u"\U0001F300-\U0001F5FF"  # symbols & pictographs
                                   u"\U0001F680-\U0001F6FF"  # transport & map symbols
                                   u"\U0001F1E0-\U0001F1FF"  # flags (iOS)
                                   u"\U00002700-\U000027BF"  # dingbats
                                   u"\U0001F900-\U0001F9FF"  # supplemental symbols and pictographs
                                   "]+", flags=re.UNICODE)
        return emoji_pattern.sub(r'', text)


def setup_logging():
    """Configura sistema de logging seguro"""
    logger = logging.getLogger()
    logger.setLevel(logging.INFO)

    # Remove handlers existentes
    for handler in logger.handlers[:]:
        logger.removeHandler(handler)

    # Formato sem emojis
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )

    # File handler
    file_handler = logging.FileHandler(
        f'trading_bot_{datetime.now().strftime("%Y%m%d")}.log',
        encoding='utf-8'
    )
    file_handler.setFormatter(formatter)

    # Stream handler seguro
    stream_handler = SafeStreamHandler(sys.stdout)
    stream_handler.setFormatter(formatter)

    logger.addHandler(file_handler)
    logger.addHandler(stream_handler)