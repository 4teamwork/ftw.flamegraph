import signal
import sys
import thread
import time


class Sampler(object):
    """A call stack sampler
    """
    timer = signal.ITIMER_REAL
    signal = signal.SIGALRM

    def __init__(self, interval=0.001):
        self.interval = interval
        signal.signal(self.signal, self.handler)
        signal.siginterrupt(self.signal, False)
        self.reset()

    def reset(self, interval=None):
        self.stacks = []
        self.stopping = False
        self.stopped = False
        self.samples_taken = 0
        self.sample_time = 0

        if interval is not None:
            self.interval = interval

    def start(self):
        self.thread_id = thread.get_ident()
        self.stopping = False
        self.stopped = False
        signal.setitimer(self.timer, self.interval, self.interval)

    def stop(self):
        self.stopping = True
        self.wait()

    def wait(self):
        while not self.stopped:
            time.sleep(self.interval)

    def handler(self, sig, current_frame):
        start = time.time()
        if self.stopping:
            signal.setitimer(self.timer, 0, 0)
            self.stopped = True
            return
        current_tid = thread.get_ident()
        for tid, frame in sys._current_frames().iteritems():
            # Only collect samples for our thread
            if tid != self.thread_id:
                continue
            if tid == current_tid:
                print "tid == curent_tid"
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

    def folded_stacks(self):
        """Fold stack samples into single lines for flame graph generation"""
        output = ""
        previous = None
        previous_count = 1
        for stack in self.stacks:
            funcs = map("{0[2]} ({0[0]}:{0[1]})".format, reversed(stack))
            current = ";".join(funcs)
            if current == previous:
                previous_count += 1
            else:
                output += "%s %d\n" % (previous, previous_count)
                previous_count = 1
                previous = current
        output += "%s %d\n" % (previous, previous_count)
        return output
