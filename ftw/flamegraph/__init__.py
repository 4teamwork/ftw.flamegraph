# -*- coding: utf-8 -*-
from StringIO import StringIO
from ZPublisher import Publish
from contextlib import contextmanager
from ftw.flamegraph.sampler import Sampler
from urlparse import parse_qs
from functools import wraps

import logging
import os
import shutil
import sys
import tempfile
import time

sampler = None
logger = logging.getLogger("ftw.flamegraph")
flamegraph_script = os.path.join(os.path.dirname(__file__), 'flamegraph.pl')


def flamegraph(open_svg=False, open_command='open {}', interval=0.001):
    """The @flamegraph() decorator wraps a function and produces a flamegraph
    from calls within this function.
    """
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            with profile(interval, print_summary=True) as sampler:
                return_value = func(*args, **kwargs)

            svg_file_path = make_svg(sampler)
            print '@flamegraph(', svg_file_path, ')'
            if open_svg:
                os.system(open_command.format(svg_file_path))

            return return_value

        return wrapper
    return decorator


def publish_module_standard(
    module_name, stdin=sys.stdin, stdout=sys.stdout, stderr=sys.stderr,
        environ=os.environ, debug=0, request=None, response=None):

    if 'flamegraph=1' in request.get('QUERY_STRING', ''):
        qs = parse_qs(request['QUERY_STRING'])
        interval = qs.get('interval', ['0.001'])
        try:
            interval = float(interval[0])
        except ValueError:
            interval = 0.001

        response_stdout = response.stdout
        response.stdout = StringIO()

        with profile(interval):
            ret = publish_module_standard.original(
                module_name, stdin=stdin, stdout=stdout, stderr=stderr,
                environ=environ, debug=debug, request=request,
                response=response)

        response.stdout = response_stdout

        svg_file_path = make_svg(sampler)
        with open(svg_file_path, 'rb') as f:
            response.setBody(f.read())
        response.setHeader('Content-Type', 'image/svg+xml')
        response.stdout.write(str(response))

        shutil.rmtree(os.path.dirname(svg_file_path))
        return ret

    else:
        return publish_module_standard.original(
            module_name, stdin=stdin, stdout=stdout, stderr=stderr,
            environ=environ, debug=debug, request=request,
            response=response)

publish_module_standard.original = Publish.publish_module_standard
Publish.publish_module_standard = publish_module_standard


def make_svg(sampler):
    tempdir = tempfile.mkdtemp()
    flame_file_path = os.path.join(tempdir, 'profile.flame')
    svg_file_path = os.path.join(tempdir, 'profile.svg')

    with open(flame_file_path, "wb") as f:
        f.write(sampler.folded_stacks().encode('utf-8'))

    os.system(
        '%(flamegraph_script)s --egghash --color rainbow %(flame_file)s > '
        '%(svg_file)s' % (dict(
            flamegraph_script=flamegraph_script,
            flame_file=flame_file_path,
            svg_file=svg_file_path)))

    return svg_file_path


@contextmanager
def profile(interval, print_summary=False):
    global sampler
    if sampler is None:
        sampler = Sampler()

    sampler.reset(interval=interval)
    sampler.start()
    start = time.time()
    yield sampler
    end = time.time()
    sampler.stop()

    message = "Samples taken: %s, sample time: %s ms, duration: %s ms" % (
        sampler.samples_taken,
        sampler.sample_time * 1000,
        (end - start) * 1000
    )
    logger.info(message)
    if print_summary:
        print '\n', message


def initialize(context):
    # The sampler needs to be initialized on the main thread
    global sampler
    sampler = Sampler()
