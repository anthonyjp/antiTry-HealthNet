from django.db import models
from django.utils import timezone as tz

from .options import LogLevel, LogAction


class HNLogEntry(models.Model):
    """
    A simple data entry to allow for persistent log data, this class should remain fairly generic in it's content,
    getting too specific will just lead to more complexity.

    Consists of a timestamp, url created for (where), a log level, a log action and a message.
    """

    timestamp = models.DateTimeField(auto_now_add=True)
    where = models.CharField(max_length=100)
    level = models.SmallIntegerField(choices=LogLevel.choices(), default=LogLevel.INFO)
    action = models.SmallIntegerField(choices=LogAction.choices(), default=LogAction.GENERIC)
    message = models.CharField(max_length=500)

    def __str__(self):
        return "{!s} | [{!s}] at {} doing {!s}: {}".format(self.level, self.timestamp, self.where, self.action,
                                                           self.message)


class HNLogger(object):
    """
    A simple facade to make creating HNLogEntrys simple and providing conveniences like message formatting and None
    handling with a consistent logger format.

    Supports info, debug, warn, verbose and error logging as well as "action" logging designed specifically to log
    actions to a HNLogEntry. All support formatted messages. This means you can specify a string with format specifiers
    as per python's string#format function.
    i.e.

    logger.info(..., 'This is an {1} message {0!s}! How {coolness}!', ashKetchumObject, 'example', coolness='awesome')

    would print "This is an example message Ash Ketchum! How awesome!"
    """

    # Consistent formats for creating messages, this can be modified by set_message_format and set_time_format
    format = "({0}) [ {1} | {2} ]: {3}"
    time_format = "%H:%M:%S %x"

    def log(self, level, action, where, msg, *args, **kwargs):
        """
        The most flexible logging option, allows yo to designate a log level, log action, location and message with
        formatting. This is used by all other methods and should generally be avoided unless you need to specify an
        exact message.

        :param level: Log Level of entry
        :param action: Log Action of entry
        :param where: URL Location entry was created for
        :param msg: A string message or a string with format specifiers
        """

        if not action:
            action = LogAction.GENERIC

        msg = msg.format(*args, **kwargs)
        lvl = LogLevel.label(level)
        timestamp = tz.now()
        time = timestamp.strftime(self.time_format)

        HNLogEntry.objects.create(timestamp=timestamp, where=where, level=level, action=action,
                                  message=self.format.format(time, lvl, where, msg)).save()

    def debug(self, request, msg, *args, action=LogAction.GENERIC, **kwargs):
        """
        Logs a Debug LogEntry with the given message at the location specified in the request object.
        :param request: Request object with path property (request.path)
        :param msg: Message string or format string
        :param action: Keyword argument to specify associated log action, default is LogAction.GENERIC
        """

        self.log(LogLevel.DEBUG, action, request.path, msg, *args, **kwargs)

    def info(self, request, msg, *args, action=LogAction.GENERIC, **kwargs):
        """
        Logs an Info LogEntry with the given message at the location specified in the request object.
        :param request: Request object with path property (request.path)
        :param msg: Message string or format string
        :param action: Keyword argument to specify associated log action, default is LogAction.GENERIC
        """

        self.log(LogLevel.INFO, action, request.path, msg, *args, **kwargs)

    def warn(self, request, msg, *args, action=LogAction.GENERIC, **kwargs):
        """
        Logs a Warning LogEntry with the given message at the location specified in the request object.
        :param request: Request object with path property (request.path)
        :param msg: Message string or format string
        :param action: Keyword argument to specify associated log action, default is LogAction.GENERIC
        """

        self.log(LogLevel.WARN, action, request.path, msg, *args, **kwargs)

    def error(self, request, msg, *args, action=LogAction.GENERIC, **kwargs):
        """
        Logs an Error LogEntry with the given message at the location specified in the request object.
        :param request: Request object with path property (request.path)
        :param msg: Message string or format string
        :param action: Keyword argument to specify associated log action, default is LogAction.GENERIC
        """

        self.log(LogLevel.ERROR, action, request.path, msg, *args, **kwargs)

    def action(self, request, action, msg='', *args, **kwargs):
        """
        Specifically logs a LogEntry with a log message containing the specified action. Unlike the others this forces
        a specific action to be chosen and the LogLevel defaults to INFO.

        :param request: Request object with path property (request.path)
        :param action: LogAction to associate wit hthis log entry, the associated LogAction label is sued in the message
        :param msg: Either a message clarifying the log entry or a format string
        """

        self.log(LogLevel.INFO, action, request.path, "<{0}> {1}", LogAction.label(action), msg.format(*args, **kwargs))

    def set_message_format(self, fmt):
        """
        Set the general log message format for the logger. Should expect at most 4 arguments. A time string, a log level
        string, a location string and the message itself.
        :param fmt: New message format
        """
        self.format = fmt

    def set_time_format(self, fmt):
        """
        Change the time format for all log entrys after this point. This is the printed timestamp on every entry
        message.
        :param fmt: New time format
        """
        self.time_format = fmt

    @staticmethod
    def get_logs(start=None, end=None, level_filter=LogLevel.VERBOSE, ordered=False):
        """
        Gets every log entry created by all HNLoggersm, optionally filtered to fit in a time range and/or specific log
        levels. The level filter accepts all entrys at, or above that level. e.g. LogLevel.INFO means all entries
        at LogLevel.INFO, LogLevel.WARN and LogLevel.ERROR, but not LogLevel.DEBUG or LogLevel.VERBOSE.

        :param start: Start time of time range, defaults to None
        :param end: End time of time range, defaults to None
        :param level_filter: Level to accept at or above, defaults to LogLevel.VERBOSE to accept all entries
        :return: A Python List of all LogEntry objects matched to the filters
        """

        logs = HNLogEntry.objects
        if start:
            if end:  # If we have a time range (a start and an end
                logs = logs.filter(timestamp__range=(start, end), level__gte=level_filter)
            else:  # Only a start time
                logs = logs.filter(timestamp__gte=start, level__gte=level_filter)
        else:
            if end:  # Only an end time
                logs = logs.filter(timestamp__lte=end, level__gte=level_filter)
            else:  # All LogEntrys, No time range provided
                logs = logs.filter(level__gte=level_filter)

        if ordered:
            logs = logs.order_by('-timestamp')

        return [x for x in logs.all()]
