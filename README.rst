==============================================================================
ftw.flamegraph
==============================================================================

This package provides a statistical profiler for Plone and creates flame graphs
for visualization of profiled code. It allows you to profile a single request
in Plone.

Because of it's low overhead, it can also be used for profiling Plone sites in
production.


Introduction
------------

In contrast to deterministic profilers that capture all code paths, ftw.flamegraph
samples the call stack periodically (by default 1000 times per second) which
reveals where time is being spent and involves less overhead.

Flame graphs are a way to visualize statistical profile data, allowing hot code-paths
to be identified quickly. For more information about flame graphs see:
http://www.brendangregg.com/flamegraphs.html


Installation
------------

Install ftw.flamegraph by adding it to your buildout::

    [buildout]
    ...
    eggs =
        ftw.flamegraph


and then running ``bin/buildout``


Usage
-----

To profile a request simply add the parameter ``flamegraph=1`` to the URL.

Example::

 http://localhost:8080/Plone?flamegraph=1

This will profile the request and render a SVG containing a flame graph.

You can customize the sampling interval by providing the ``interval`` parameter.

Example::

 http://localhost:8080/Plone?flamegraph=1&interval=0.0005

This will sample the call stack 2000 times per second. Too small intervals will
create more overhead while too large intervals may lead to missing hot code paths.


Use in tests
------------

The flamegraph decorator can be used for wrapping tests (or other functions) and
producing a flamegraph:

.. code:: python

    from ftw.flamegraph import flamegraph

    @flamegraph()
    def test():
        do_things()


Options:

- ``open_svg``: Open the SVG with the systems "open" command (default: ``True``)
- ``interval``: The interval for taking snapshots (default: ``0.001``)



Implementation notes
--------------------

ftw.flamegraph sets an interval timer which decrements in real time (ITIMER_REAL)
and sends a signal (SIGALRM) upon expiration. Every time the signal gets delivered,
the current thread's call stack gets recorded.

While timers that decrement only when the process is executing (ITIMER_PROF and
ITIMER_VIRTUAL) might be more appropriate for profiling, this is not possible with
Zope 2. In Python those timers only decrement when the main thread is
executing, but in Zope 2 the main thread is an asyncore loop that waits for I/O
with a timeout of 30 seconds, making it inappropriate for periodic sampling.

To get meaningful results you should make sure there are no other CPU intensive
processes executing on the same CPU as the profiled process.


Links
-----

- Issue Tracker: https://github.com/4teamwork/ftw.flamegraph/issues
- Source Code: https://github.com/4teamwork/ftw.flamegraph


Copyright
---------

This package is copyright by `4teamwork <http://www.4teamwork.ch/>`_.

``ftw.flamegraph`` is licensed under GNU General Public License, version 2.
