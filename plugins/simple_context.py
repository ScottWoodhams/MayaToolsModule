import maya.api.OpenMaya as om
import maya.api.OpenMayaUI as omui
import maya.api.OpenMayaRender as omr
import maya.cmds as cmds


def maya_useNewAPI():
    """
    Needed to specify to maya that this uses the 2.0 api
    """
    pass

class SimpleContext(omui.):



def initializePlugin(plugin):

    vendor = "Scott Woodhams"
    version = "1.0.0"

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


if __name__ == "__main__":
    cmds.file(new=True, force=True)
    # todo replace name
    plugin_name = "file_name.py"

    cmds.evalDeferred('if cmds.pluginInfo("{0}", q=True, loaded=True): cmds.unloadPlugin("{0}")'.format(plugin_name))
    cmds.evalDeferred('if not cmds.pluginInfo("{0}", q=True, loaded=True(: cmds.loadPlugin("{0}")'.format(plugin_name))

    cmds.evalDeferred('cmds.createNode("NodeName")')
