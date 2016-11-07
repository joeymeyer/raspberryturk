import time
import logging

class Agent(object):
    def __init__(self):
        self._logger = logging.getLogger(__name__)

    def perception_action_sequence(self):
        self._logger.info("Time: {}".format(time.time()))
        time.sleep(2)
