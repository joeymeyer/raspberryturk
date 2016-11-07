import logging
import signal
import time
from daemon import runner
import raspberryturk
from raspberryturk.embedded.agent import Agent


class RaspberryTurkDaemon(object):
    def __init__(self):
        self.stdin_path = '/dev/null'
        self.stdout_path = raspberryturk.active_log_path()
        self.stderr_path = raspberryturk.active_log_path()
        self.pidfile_path =  raspberryturk.run_path('raspberryturkd.pid')
        self.pidfile_timeout = 5
        self.logger = logging.getLogger(__name__)
        self._interrupt_signum = None

    def run(self):
        self.logger.info("Starting RaspberryTurkDaemon.")
        time.sleep(1)
        self.agent = Agent()
        while self._interrupt_signum is None:
            self.agent.perception_action_sequence()
        self.logger.warn("Received signal {}.".format(self._interrupt_signum))
        self.logger.info("Stopping RaspberryTurkDaemon.")

    def interrupt_handler(self, signum, frame):
        self._interrupt_signum = signum

def main():
    raspberryturk.setup_file_logging()
    rtd = RaspberryTurkDaemon()
    daemon_runner = runner.DaemonRunner(rtd)
    daemon_runner.daemon_context.files_preserve=[raspberryturk.active_log_stream()]
    daemon_runner.daemon_context.signal_map = {
        signal.SIGINT: rtd.interrupt_handler,
        signal.SIGTERM: rtd.interrupt_handler,
        signal.SIGHUP: 'terminate',
    }
    daemon_runner.do_action()

if __name__ == '__main__':
    main()
