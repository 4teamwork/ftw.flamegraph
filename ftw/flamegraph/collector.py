from __future__ import with_statement
from ftw.flamegraph import platform
from six.moves import _thread

import collections
import signal
import six
import sys
import time


class Collector(object):
    MODES = {
        'prof': (platform.ITIMER_PROF, signal.SIGPROF),
        'virtual': (platform.ITIMER_VIRTUAL, signal.SIGVTALRM),
        'real': (platform.ITIMER_REAL, signal.SIGALRM),
    }

    def __init__(self, interval=0.01, mode='virtual'):
        self.interval = interval
        self.mode = mode
        assert mode in Collector.MODES
        timer, sig = Collector.MODES[self.mode]
        signal.signal(sig, self.handler)
        signal.siginterrupt(sig, False)
        self.reset()

    def reset(self):
        self.stacks = list()
        self.samples_remaining = 0
        self.stopping = False
        self.stopped = False

        self.samples_taken = 0
        self.sample_time = 0

    def start(self, duration=30.0):
        self.thread_id = _thread.get_ident()
        self.stopping = False
        self.stopped = False
        self.samples_remaining = int(duration / self.interval)
        timer, sig = Collector.MODES[self.mode]
        platform.setitimer(timer, self.interval, self.interval)

    def stop(self):
        self.stopping = True
        self.wait()

    def wait(self):
        while not self.stopped:
            pass  # need busy wait; ITIMER_PROF doesn't proceed while sleeping

    def handler(self, sig, current_frame):
        start = time.time()
        self.samples_remaining -= 1
        if self.samples_remaining <= 0 or self.stopping:
            platform.setitimer(Collector.MODES[self.mode][0], 0, 0)
            self.stopped = True
            return
        current_tid = _thread.get_ident()
        for tid, frame in six.iteritems(sys._current_frames()):
            if tid != self.thread_id:
                continue
            if tid == current_tid:
                frame = current_frame
            frames = []
            while frame is not None:
                code = frame.f_code
                frames.append((code.co_filename, frame.f_lineno, code.co_name))
                frame = frame.f_back
            self.stacks.append(frames)
        end = time.time()
        self.samples_taken += 1
        self.sample_time += (end - start)


class CollectorFormatter(object):
    """
    Abstract class for output formats
    """
    def format(self, collector):
        raise Exception("not implemented")

    def store(self, collector, filename):
        with open(filename, "wb") as f:
            f.write(self.format(collector).encode('utf-8'))


class PlopFormatter(CollectorFormatter):
    """
    Formats stack frames for plop.viewer
    """
    def __init__(self, max_stacks=50):
        self.max_stacks = 50

    def format(self, collector):
        # defaultdict instead of counter for pre-2.7 compatibility
        stack_counts = collections.defaultdict(int)
        for frames in collector.stacks:
            stack_counts[tuple(frames)] += 1
        stack_counts = dict(sorted(six.iteritems(stack_counts),
                                   key=lambda kv: -kv[1])[:self.max_stacks])
        return repr(stack_counts)


class FlamegraphFormatter(CollectorFormatter):
    """
    Creates Flamegraph files
    """
    def format(self, collector):
        output = ""
        previous = None
        previous_count = 1
        for stack in collector.stacks:
            current = self.format_flame(stack)
            if current == previous:
                previous_count += 1
            else:
                output += "%s %d\n" % (previous, previous_count)
                previous_count = 1
                previous = current
        output += "%s %d\n" % (previous, previous_count)
        return output

    def format_flame(self, stack):
        funcs = map("{0[2]} ({0[0]}:{0[1]})".format, reversed(stack))
        return ";".join(funcs)
