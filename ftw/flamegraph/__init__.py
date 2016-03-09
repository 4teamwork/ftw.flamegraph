# -*- coding: utf-8 -*-
from StringIO import StringIO
from ZPublisher import Publish
from contextlib import contextmanager
from ftw.flamegraph.collector import Collector
from ftw.flamegraph.collector import FlamegraphFormatter
from urlparse import parse_qs

import os
import shutil
import sys
import tempfile

collector = None
flamegraph_script = os.path.join(os.path.dirname(__file__), 'flamegraph.pl')


def publish_module_standard(
    module_name, stdin=sys.stdin, stdout=sys.stdout, stderr=sys.stderr,
        environ=os.environ, debug=0, request=None, response=None):

    qs = parse_qs(request.get('QUERY_STRING', ''))
    if qs.get('profile') == ['1']:
        interval = qs.get('interval', ['0.0005'])
        try:
            interval = float(interval[0])
        except ValueError:
            interval = 0.0005
        response_stdout = response.stdout
        response.stdout = StringIO()
        tempdir = tempfile.mkdtemp()
        with profile(tempdir, interval=interval):
            ret = publish_module_standard.original(
                module_name, stdin=stdin, stdout=stdout, stderr=stderr,
                environ=environ, debug=debug, request=request,
                response=response)
        response.stdout = response_stdout
        response.setBody(
            open(os.path.join(tempdir, 'profile.svg'), 'rb').read())
        response.setHeader('Content-Type', 'image/svg+xml')
        response_stdout.write(str(response))
        shutil.rmtree(tempdir)
        return ret

    else:
        return publish_module_standard.original(
                module_name, stdin=stdin, stdout=stdout, stderr=stderr,
                environ=environ, debug=debug, request=request,
                response=response)

publish_module_standard.original = Publish.publish_module_standard
Publish.publish_module_standard = publish_module_standard


@contextmanager
def profile(tempdir, interval=0.0005):
    collector.reset()
    collector.interval = interval
    collector.start()
    yield
    collector.stop()
    flame_file = os.path.join(tempdir, 'profile.flame')
    svg_file = os.path.join(tempdir, 'profile.svg')
    formatter = FlamegraphFormatter()
    formatter.store(collector, flame_file)
    os.system('%(flamegraph_script)s --egghash --color rainbow %(flame_file)s'
              ' > %(svg_file)s' % (dict(
                  flamegraph_script=flamegraph_script,
                  flame_file=flame_file,
                  svg_file=svg_file)))


def initialize(context):
    global collector
    collector = Collector(interval=0.0005)
