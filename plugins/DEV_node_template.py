import maya.api.OpenMaya as om
import maya.cmds as cmds


def maya_useNewAPI():
    """
    Needed to specify to maya that this uses the 2.0 api

    """
    pass


def initializePlugin(plugin):
    """
    Needed to initialize the plugin
    Note: name sensitive
    :param plugin: paassed in by maya
    """

    # plugin details
    vendor = "Scott Woodhams"
    version = "1.0.0"

    # create plugin function set
    plugin_fn = om.MFnPlugin(plugin, vendor, version)

    # register node 
    try:
        plugin_fn.registerNode(NodeName.TYPE_NAME,
                               NodeName.TYPE_ID,
                               NodeName.creator,
                               NodeName.initialize,
                               om.MPxNode.kDependNode)

    except:
        om.MGlobal.displayError("Failed to register node: {0}".format(NodeName.TYPE_NAME))


def uninitializePlugin(plugin):
    """
    Needed to uninitialize the plugin
    Note: name sensitive
    :param plugin:
    :return:
    """
    plugin_fn = om.MFnPlugin(plugin)

    try:
        plugin_fn.deregisterNode(NodeName.TYPE_ID)
    except:
        om.MGlobal.displayError("Failed to deregister node: {0}".format(NodeName.TYPE_NAME))


class NodeName(om.MPxNode):

    TYPE_NAME = "NodeName"
    # node need id above 0x0007F7F7 - needs to be unique, may clash with other plugins
    TYPE_ID = om.MTypeId(0x0007F7F8)

    def __int__(self):
        super(NodeName, self).__init__()

    def compute(self, plug, data):
        pass

    @classmethod
    def creator(cls):
        return NodeName()

    @classmethod
    def initialize(cls):
        pass


if __name__ == "__main__":
    cmds.file(new=True, force=True)
    # todo replace name
    plugin_name = "file_name.py"

    cmds.evalDeferred('if cmds.pluginInfo("{0}", q=True, loaded=True): cmds.unloadPlugin("{0}")'.format(plugin_name))
    cmds.evalDeferred('if not cmds.pluginInfo("{0}", q=True, loaded=True(: cmds.loadPlugin("{0}")'.format(plugin_name))

    cmds.evalDeferred('cmds.createNode("NodeName")')
