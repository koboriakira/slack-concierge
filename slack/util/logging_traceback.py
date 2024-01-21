import traceback
import logging

def logging_traceback(err: Exception, exc_info):
        t, v, tb = exc_info
        formatted_exception = "\n".join(
            traceback.format_exception(t, v, tb))
        logging.error(err)
        logging.error(formatted_exception)
