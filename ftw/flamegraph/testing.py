from plone.app.testing import PloneSandboxLayer
from plone.app.testing import PLONE_FIXTURE
from plone.app.testing import IntegrationTesting
from plone.testing import z2
from zope.configuration import xmlconfig


class FlamegraphLayer(PloneSandboxLayer):

    defaultBases = (PLONE_FIXTURE,)

    def setUpZope(self, app, configurationContext):
        import ftw.flamegraph
        xmlconfig.file('configure.zcml',
                       ftw.flamegraph,
                       context=configurationContext)
        z2.installProduct(app, 'ftw.flamegraph')


FLAMEGRAPH_LAYER = FlamegraphLayer()

FLAMEGRAPH_INTEGRATION_TESTING = IntegrationTesting(
    bases=(FLAMEGRAPH_LAYER, ), name='ftw.flamegraph:Integration')
