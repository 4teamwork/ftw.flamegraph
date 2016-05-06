import xml.etree.ElementTree as etree


class FlameGraph(object):

    def __init__(self, stacks):
        self.boxes = {}  # (frame, depth, endtime) -> starttime
        self.depth_samples = {}  # depth -> number of samples
        self.stacks = {}
        self.stack_counts = {}
        self.maxdepth = 0

        for stack in stacks:
            frame = map("{0[2]} ({0[0]}:{0[1]})".format, reversed(stack))
            key = ','.join(frame)
            if key not in self.stacks:
                self.stacks[key] = frame
                self.stack_counts[key] = 0
            self.stack_counts[key] += 1

        self.calculate_boxes()

    def calculate_boxes(self):
        # import pdb; pdb.set_trace()
        previous_stack = []
        starts = {}  # (frame, depth) -> starttime
        time = 0

        for key in sorted(self.stacks.keys()):
            frames = self.stacks[key]
            count = self.stack_counts[key]

            # Prepend an empty frame to every stack to represent the "all
            # samples" frame
            frames.insert(0, '')

            if len(frames) - 1 > self.maxdepth:
                self.maxdepth = len(frames) - 1

            # Determine the number of same frames of the current and the
            # previous stack
            same_frames = 0
            for i, frame in enumerate(previous_stack):
                if i > len(frames):
                    break
                if frame == frames[i]:
                    same_frames += 1
                else:
                    break

            # Frames ending here
            for i in reversed(range(same_frames, len(previous_stack))):
                starts_key = (previous_stack[i], i)
                ends_key = (previous_stack[i], i, time)
                self.boxes[ends_key] = starts[starts_key]
                self.depth_samples[i] += (time - starts[starts_key])
                del starts[starts_key]

            # Mark frames not present in previous stack as starting here
            for i in range(same_frames, len(frames)):
                starts[(frames[i], i)] = time

                if i not in self.depth_samples:
                    self.depth_samples[i] = 0

            time += count
            previous_stack = frames

        # Frames ending at the end
        for i in reversed(range(0, len(previous_stack))):
            starts_key = (previous_stack[i], i)
            ends_key = (previous_stack[i], i, time)
            self.boxes[ends_key] = starts[starts_key]
            self.depth_samples[i] += (time - starts[starts_key])

        self.total_time = time

    def draw_svg(self):
        width = 1200
        width_per_sample = width / self.total_time
        frame_height = 16
        height = self.maxdepth * frame_height
        root = etree.Element(
            'svg',
            version='1.1',
            width=str(width),
            height=str(height),
            viewBox='0 0 {} {}'.format(width, height),
            xmlns='http://www.w3.org/2000/svg',
        )
        for (frame, depth, end_time), start_time in self.boxes.items():
            root.append(etree.Element(
                'rect',
                 x=str(start_time * width_per_sample),
                 y=str(height - (depth + 1) * frame_height + 1),
                 width=str((end_time - start_time) * width_per_sample),
                 fill="rgb(224,0,2)",
                 rx='2',
                 ry='2',
            ))

        return etree.tostring(root, encoding='UTF-8')
