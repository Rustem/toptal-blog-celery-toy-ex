import os
from django.conf import settings
from .utils import join, ts as utils_ts, interval_timestamp, list_files


class Repository(object):
    def __init__(self, obj):
        self._wrapped_obj = obj
        self.language = obj[u'language'] or u'unknown'
        self.name = obj[u'full_name']

    def __getattr__(self, attr):
        if attr in self.__dict__:
            return getattr(self, attr)
        else:
            return getattr(self._wrapped_obj, attr)


class ErrorRecord(object):
    """docstring for ErrorRecord"""
    def __init__(self, subject, message):
        self.subject = subject
        self.message = message


ERROR_MAIL_SEND_INTERVAL = 60 # 60 seconds
ERROR_CHECKPOINT_FILE_DELIMITER = '@@@'


class IntervalCheckpoint(object):

    real_ts = None
    int_ts = None
    interval = None
    file_path = None

    NAME = '.chkpoint'

    def __init__(self, location, ts=None, interval=None):
        interval = interval or ERROR_MAIL_SEND_INTERVAL
        ts = ts or utils_ts()
        self.real_ts = ts
        self.int_ts = interval_timestamp(interval, ts)
        self.file_path = join(location, self.NAME)

    @classmethod
    def from_disk(cls, location):
        ts = cls.read_value(join(location, cls.NAME))
        if ts:
            ts = int(ts)
        return IntervalCheckpoint(location, ts=ts)

    @classmethod
    def update_current(cls, location, interval=None):
        interval = IntervalCheckpoint(location, utils_ts(), interval=interval)
        interval.update()
        return interval

    @classmethod
    def read_value(cls, path):
        try:
            with open(path, 'r') as fd:
                return fd.read().rstrip('\n')
        except IOError:
            return

    def update(self):
        with open(self.file_path, 'w') as fd:
            fd.write(str(self.int_ts))


class CheckpointFile(object):

    filedir = None
    filename = None
    interval_chkpoint = None

    def __init__(self, filedir, filename, interval_chkpoint=None):
        self.filedir = filedir
        if interval_chkpoint:
            self.interval_chkpoint = interval_chkpoint
            self.filename = self.build_fname(filename.replace('/', ' ').rstrip(' '), self.interval_chkpoint.real_ts)
        else:
            self.filename = filename
            self.interval_chkpoint = self.infer_chkpoint(filedir, filename)

    @classmethod
    def error_file(self, filename):
        error_dir = '{media}/errors/'.format(media=settings.MEDIA_ROOT)
        return CheckpointFile(error_dir, filename, interval_chkpoint=IntervalCheckpoint(error_dir))

    @property
    def fullpath(self):
        return join(self.filedir, self.filename)

    @property
    def trashpath(self):
        trashdir = join(self.filedir, '.trash')
        if not os.path.exists(trashdir):
            os.makedirs(trashdir)
        return join(trashdir, self.filename)

    def build_fname(self, fname, ts):
        fname = '{fname}{delim}{ts}.log'.format(
            fname=fname,
            delim=ERROR_CHECKPOINT_FILE_DELIMITER,
            ts=ts)
        return fname

    def infer_chkpoint(self, filedir, filename):
        assert '.log' in filename, 'should end with .log'
        fname, ts = filename.rstrip('.log').rsplit(ERROR_CHECKPOINT_FILE_DELIMITER, 1)
        return IntervalCheckpoint(filedir, ts=int(ts), interval=ERROR_MAIL_SEND_INTERVAL)

    def is_relevant_now(self):
        return self.interval_chkpoint.int_ts == interval_timestamp(ERROR_MAIL_SEND_INTERVAL)

    def trash_me(self):
        os.rename(self.fullpath, self.trashpath)

    def write(self, content):
        if not os.path.exists(self.filedir):
            os.makedirs(self.filedir)
        with open(self.fullpath, 'w') as fd:
            fd.write(content)

    def read(self):
        with open(self.fullpath, 'r') as fd:
            return fd.read()

    @classmethod
    def read_relevant_files(self, location):
        for fdir, fname in list_files(location):
            try:
                cur_file = CheckpointFile(fdir, fname)
            except AssertionError:
                continue
            if cur_file.is_relevant_now():
                yield cur_file
            cur_file.trash_me()
        raise StopIteration()

    @classmethod
    def read_relevant_error_files(self):
        error_dir = '{media}/errors/'.format(media=settings.MEDIA_ROOT)
        return self.read_relevant_files(error_dir)


