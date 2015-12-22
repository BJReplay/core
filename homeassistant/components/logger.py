"""
homeassistant.components.logger
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
Component that will help set the level of logging for components.

For more details about this component, please refer to the documentation at
https://home-assistant.io/components/logger/
"""
import logging
from collections import OrderedDict

DOMAIN = 'logger'

LOGSEVERITY = {
    'CRITICAL': 50,
    'FATAL': 50,
    'ERROR': 40,
    'WARNING': 30,
    'WARN': 30,
    'INFO': 20,
    'DEBUG': 10,
    'NOTSET': 0
}

LOGGER_DEFAULT = 'default'
LOGGER_LOGS = 'logs'


class HomeAssistantLogFilter(logging.Filter):
    """ A log filter. """
    # pylint: disable=no-init,too-few-public-methods

    def __init__(self, logfilter):
        super().__init__()

        self.logfilter = logfilter

    def filter(self, record):

        # Log with filtered severity
        if LOGGER_LOGS in self.logfilter:
            for filtername in self.logfilter[LOGGER_LOGS]:
                logseverity = self.logfilter[LOGGER_LOGS][filtername]
                if record.name.startswith(filtername):
                    return record.levelno >= logseverity

        # Log with default severity
        default = self.logfilter[LOGGER_DEFAULT]
        return record.levelno >= default


def setup(hass, config=None):
    """ Setup the logger component. """

    logfilter = dict()

    # Set default log severity
    logfilter[LOGGER_DEFAULT] = LOGSEVERITY['DEBUG']
    if LOGGER_DEFAULT in config.get(DOMAIN):
        logfilter[LOGGER_DEFAULT] = LOGSEVERITY[
            config.get(DOMAIN)[LOGGER_DEFAULT].upper()
        ]

    # Compute log severity for components
    if LOGGER_LOGS in config.get(DOMAIN):
        for key, value in config.get(DOMAIN)[LOGGER_LOGS].items():
            config.get(DOMAIN)[LOGGER_LOGS][key] = LOGSEVERITY[value.upper()]

        logs = OrderedDict(
            sorted(
                config.get(DOMAIN)[LOGGER_LOGS].items(),
                key=lambda t: len(t[0]),
                reverse=True
            )
        )

        logfilter[LOGGER_LOGS] = logs

    # Set log filter for all log handler
    for handler in logging.root.handlers:
        handler.setLevel(logging.NOTSET)
        handler.addFilter(HomeAssistantLogFilter(logfilter))

    return True
