import logging
import ctypes
import sys
import tempfile
from pathlib import Path
import cog
import time

libc = ctypes.CDLL(None)

# test that we can still capture type signature even if we write
# a bunch of stuff at import time.
libc.puts(b"writing some stuff from C at import time\n")
sys.stdout.write("writing to stdout at import time\n")
sys.stderr.write("writing to stderr at import time\n")


class Predictor(cog.Predictor):
    def setup(self):
        print("setting up predictor")
        self.foo = "foo"

    @cog.input("text", type=str, default="")
    def predict(self, text):
        logging.warn("writing log message")
        time.sleep(0.1)
        libc.puts(b"writing from C")
        time.sleep(0.1)
        sys.stderr.write("writing to stderr\n")
        time.sleep(0.1)
        sys.stderr.flush()
        time.sleep(0.1)
        print("writing with print")
        return "output"
