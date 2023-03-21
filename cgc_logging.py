import sys
import logging
import logging.handlers

def setup_logging(logs_file):
	try:
		logger = logging.getLogger(__name__)

		# Set up logging
		# LoggingLevel options: CRITICAL (50), ERROR (40), WARNING (30), INFO (20), DEBUG (10), NOTSET (0)
		logger.setLevel("DEBUG")

		logFileHandler = logging.handlers.RotatingFileHandler(logs_file, maxBytes=102400, backupCount=9)
		#logFileHandler = logging.FileHandler(get_log_file())
		logger.addHandler(logFileHandler)

		logFormatter = logging.Formatter("%(asctime)s %(levelname)s %(message)s")
		logFileHandler.setFormatter(logFormatter)

		logConsoleHandler = logging.StreamHandler(sys.stdout)
		logConsoleHandler.setFormatter(logFormatter)
		logger.addHandler(logConsoleHandler)

		return logger
	except Exception as e:
		error_message = "Error setting up logging! " + str(e)
		print(error_message)
		raise
