import bdb
import logging
import multiprocessing as mp


class Debugger(bdb.Bdb):
    """Our custom debugger."""

    def __init__(self, queue, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.logger = logging.getLogger(__name__)
        self.queue = queue

    def user_call(self, frame, arg):
        self.logger.debug("call %s %s", frame, arg)
        self.process_cmd()

    def user_line(self, frame):
        self.logger.debug("line %s", frame)
        self.process_cmd()

    def user_return(self, frame, rvalue):
        self.logger.debug("ret %s %s", frame, rvalue)
        self.process_cmd()

    def user_exception(self, frame, exc):
        self.logger.debug("exc %s %s", frame, exc)
        self.process_cmd()

    def process_cmd(self):
        """Wait until a command is received from the other side."""

        while True:
            cmd = self.queue.get()
            self.logger.debug("cmd '%s'", cmd)

            if cmd == "continue":
                break

            if cmd == "quit":
                self.set_quit()
                break


def bootstrap_debugger(queue, code):
    """Standup the debugging infrastructure before executing the given code."""
    debugger = Debugger(queue)
    debugger.run(code)


class DebugControler:
    """The interface to our debugger instance running in the other process."""

    def __init__(self):
        pass

    def run(self, code):
        self.queue = mp.Queue()

        self.process = mp.Process(target=bootstrap_debugger, args=(self.queue, code))
        self.process.start()

    def continue_(self):
        """Continue program execution."""
        self.queue.put("continue")

    def quit(self):
        """Quit the debugging session."""
        self.queue.put("quit")
        self.process.join()


def run(code):

    debug = DebugControler()
    debug.run(code)

    return debug
