class YtDlpLogger:
    def __init__(self, logger):
        self._logger = logger

    def debug(self, msg):
        # Por si se quieren filtrar
        #    if msg.startswith("[debug]"):
        #        return
        self._logger.debug(msg)

    def warning(self, msg):
        self._logger.warning(msg)

    def error(self, msg):
        self._logger.error(msg)
