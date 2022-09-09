import maya.api.OpenMaya as om
import maya.cmds as cmds


def maya_useNewAPI():
    pass


class SimpleCmd(om.MPxCommand):
    COMMAND_NAME = "SimpleCmd"

    VERSION_FLAG = ["-v", "-version"]
    TRANSLATE_FLAG = ["-t", "-translate", (om.MSyntax.kDouble, om.MSyntax.kDouble, om.MSyntax.kDouble)]

    def __int__(self):
        super(SimpleCmd, self).__init__()



    def doIt(self, arg_list):

        try:
            arg_db = om.MArgDatabase(self.syntax(), arg_list)
        except:
            self.displayError("Error parsing arguments")
            raise

        selection_list = arg_db.getObjectList()

        

        version_flag_enabled = arg_db.isFlagSet(SimpleCmd.VERSION_FLAG[0])
        if version_flag_enabled:
            self.setResult("1.0.0")
        else:
            # name = "SimpleCmd"
            # if arg_db.isFlagSet(SimpleCmd.NAME_FLAG[0]):
            #     name = arg_db.flagArgumentString(SimpleCmd.NAME_FLAG[0], 0)

            first_name = arg_db.commandArgumentString(0)
            last_name = arg_db.commandArgumentString(1)

            self.displayInfo("Hello {0} {1}".format(first_name, last_name))


    def undoIt(self):
        pass

    def redoIt(self):
        pass

    def isUndoable(self):
        return False

    @classmethod
    def creator(cls):
        return SimpleCmd()

    @classmethod
    def create_syntax(cls):

        syntax = om.MSyntax()

        syntax.addFlag(SimpleCmd.VERSION_FLAG[0], SimpleCmd.VERSION_FLAG[1])
        # syntax.addFlag(SimpleCmd.NAME_FLAG[0], SimpleCmd.NAME_FLAG[1], om.MSyntax.kString)
        syntax.addArg(om.MSyntax.kString)
        syntax.addArg(om.MSyntax.kString)
        return syntax


def initializePlugin(plugin):
    vendor = "Scott Woodhams"
    version = "1.0.0"
    plugin_fn = om.MFnPlugin(plugin, vendor, version)
    try:
        plugin_fn.registerCommand(SimpleCmd.COMMAND_NAME, SimpleCmd.creator, SimpleCmd.create_syntax)
    except:
        om.MGlobal.displayError("Failed to register command: {0}".format(SimpleCmd.COMMAND_NAME))


def uninitializePlugin(plugin):
    plugin_fn = om.MFnPlugin(plugin)
    try:
        plugin_fn.deregisterCommand(SimpleCmd.COMMAND_NAME)
    except:
        om.MGlobal.displayError("Failed to deregister command: {0}".format(SimpleCmd.commandString))


if __name__ == "__main__":

    cmds.file(new=True, force=True)

    plugin_name = "simple_cmd.py"

    cmds.evalDeferred('if cmds.pluginInfo("{0}", q=True, loaded=True): cmds.unloadPlugin("{0}")'.format(plugin_name))
    cmds.evalDeferred('if not cmds.pluginInfo("{0}", q=True, loaded=True): cmds.loadPlugin("{0}")'.format(plugin_name))

    # cmds.evalDeferred('cmds.createNode("SimpleCmd")')
