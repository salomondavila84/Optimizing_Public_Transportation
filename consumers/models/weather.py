"""Contains functionality related to Weather"""
import logging
import json

logger = logging.getLogger(__name__)


class Weather:
    """Defines the Weather model"""

    def __init__(self):
        """Creates the weather model"""
        self.temperature = 70.0
        self.status = "sunny"

    def process_message(self, message):
        """Handles incoming weather data"""

        #
        #
        # TODO: Process incoming weather messages. Set the temperature and status.
        #
        #
        try:
            value = message.value()
            self.temperature = value['temp']
            self.status = value['status']

        except Exception as e:
            logger.debug("Error while processed weather message")
