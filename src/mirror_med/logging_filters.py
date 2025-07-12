import logging
from typing import List


class HealthCheckFilter(logging.Filter):
    """
    Filter out successful health check log records from Uvicorn access logs.

    This filter targets uvicorn.access logger records and suppresses logs for
    successful (2xx) health check requests while preserving all error responses.

    Uvicorn access logs pass a LogRecord whose args tuple contains:
    (client_addr, method, path, http_version, status_code)
    """

    def __init__(self, name: str = "", paths: List[str] = None):
        super().__init__(name)
        self.paths = paths or []

    def filter(self, record: logging.LogRecord) -> bool:
        """
        Filter log records.

        Returns:
            bool: True to allow the log record, False to suppress it
        """
        # We only want to filter uvicorn.access logs
        if record.name != "uvicorn.access":
            return True

        try:
            # record.args for uvicorn.access is a tuple like:
            # ('127.0.0.1:53331', 'GET', '/health', '1.1', 200)
            log_args = record.args
            if isinstance(log_args, tuple) and len(log_args) == 5:
                method, path, _, status_code = (
                    log_args[1],
                    log_args[2],
                    log_args[3],
                    log_args[4],
                )

                # Check if the path matches any of the configured health check paths
                # Use exact match for root '/' and startswith for others like '/health'
                path_matches = False
                for p in self.paths:
                    if p == "/" and path == "/":
                        path_matches = True
                        break
                    elif p != "/" and path.startswith(p):
                        path_matches = True
                        break

                if path_matches:
                    # Suppress log if status code is a success (2xx)
                    if 200 <= status_code < 300:
                        return False
        except (ValueError, IndexError, TypeError):
            # If log record format is unexpected, pass it through
            # This ensures we don't break logging if Uvicorn changes format
            pass

        return True
