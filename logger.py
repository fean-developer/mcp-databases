import logging
import os

import sys

class MCPLogger:
    _logger_cache = {}
    @staticmethod
    def get_logger(name: str):
        if name in MCPLogger._logger_cache:
            return MCPLogger._logger_cache[name]
        # Caminho global: diretório do binário executado
        if hasattr(sys, 'argv') and sys.argv and sys.argv[0]:
            bin_dir = os.path.dirname(os.path.abspath(sys.argv[0]))
        else:
            bin_dir = os.getcwd()
        log_path = os.path.join(bin_dir, 'mcp_databases.log')
        logger = logging.getLogger(name)
        logger.setLevel(logging.DEBUG)
        if not logger.hasHandlers():
            file_handler = logging.FileHandler(log_path)
            formatter = logging.Formatter('%(asctime)s %(levelname)s %(message)s')
            file_handler.setFormatter(formatter)
            logger.addHandler(file_handler)
        MCPLogger._logger_cache[name] = logger
        return logger
