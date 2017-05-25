from celery import current_app
from celery.utils.log import get_task_logger


class LoggingTask(current_app.Task):
    abstract = True
    ignore_result = False

    @property
    def log(self):
        logger = get_task_logger(self.name)
        return logger

    def log_msg(self, msg, *msg_args):
        self.log.debug(msg, *msg_args)
