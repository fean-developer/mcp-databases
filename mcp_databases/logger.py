import logging
import os

import sys


class MCPLogger:
    _logger_cache = {}
    _global_handler_added = False
    @staticmethod
    def get_logger(name: str):
        import sys
        if name in MCPLogger._logger_cache:
            return MCPLogger._logger_cache[name]
        # Caminho global: diretório do binário executado
        if hasattr(sys, 'argv') and sys.argv and sys.argv[0]:
            bin_dir = os.path.dirname(os.path.abspath(sys.argv[0]))
        else:
            bin_dir = os.getcwd()
        log_path = os.path.join(bin_dir, 'mcp_databases.log')
        logger = logging.getLogger(name)
        logger.setLevel(logging.INFO)
        # Adiciona apenas UM handler global para todos os loggers
        if not MCPLogger._global_handler_added:
            file_handler = logging.FileHandler(log_path)
            formatter = logging.Formatter('%(asctime)s %(levelname)s %(message)s')
            file_handler.setFormatter(formatter)
            logging.getLogger().addHandler(file_handler)
            MCPLogger._global_handler_added = True
        MCPLogger._logger_cache[name] = logger
        return logger
