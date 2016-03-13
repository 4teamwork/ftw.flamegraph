import signal
import sys
import thread
import time


class Sampler(object):
    """A call stack sampler
    """
    MODES = {
        'prof': (signal.ITIMER_PROF, signal.SIGPROF),
        'virtual': (signal.ITIMER_VIRTUAL, signal.SIGVTALRM),
        'real': (signal.ITIMER_REAL, signal.SIGALRM),
    }

    def __init__(self, interval=0.001, mode='real'):
        self.interval = interval
        self.mode = mode
        timer, sig = Sampler.MODES[self.mode]
        signal.signal(sig, self.handler)
        signal.siginterrupt(sig, False)
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
        timer, sig = Sampler.MODES[self.mode]
        signal.setitimer(timer, self.interval, self.interval)

    def stop(self):
        self.stopping = True
        self.wait()

    def wait(self):
        while not self.stopped:
            pass  # need busy wait; ITIMER_PROF doesn't proceed while sleeping

    def handler(self, sig, current_frame):
        start = time.time()
        if self.stopping:
            signal.setitimer(Sampler.MODES[self.mode][0], 0, 0)
            self.stopped = True
            return
        current_tid = thread.get_ident()
        for tid, frame in sys._current_frames().iteritems():
            # Only collect samples for our thread
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


class FlamegraphFormatter(object):
    """Creates Flamegraph files
    """
    def format(self, stacks):
        output = ""
        previous = None
        previous_count = 1
        for stack in stacks:
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

    def store(self, stacks, filename):
        with open(filename, "wb") as f:
            f.write(self.format(stacks).encode('utf-8'))
