import maya.api.OpenMaya as om
import maya.cmds as cmds


def maya_useNewAPI():
    pass


class SimpleCmd(om.MPxCommand):
    COMMAND_NAME = "SimpleCmd"

    VERSION_FLAG = ["-v", "-version"]
    TRANSLATE_FLAG = ["-t", "-translate", (om.MSyntax.kDouble, om.MSyntax.kDouble, om.MSyntax.kDouble)]
    undoable = False
    
    def __int__(self):
        super(SimpleCmd, self).__init__()

        self.undoable = False

    def doIt(self, arg_list):

        try:
            arg_db = om.MArgDatabase(self.syntax(), arg_list)
        except:
            self.displayError("Error parsing arguments")
            raise

        selection_list = arg_db.getObjectList()

        self.selected_obj = selection_list.getDependNode(0)

        if self.selected_obj.apiType() != om.MFn.kTransform:
            raise RuntimeError("This commands requires a transform node")

        self.edit = arg_db.isEdit
        self.query = arg_db.isQuery

        self.translate = arg_db.isFlagSet(SimpleCmd.TRANSLATE_FLAG[0])
        if self.translate:
            transform_fn = om.MFnTransform(self.selected_obj)
            self.originalTranslation = transform_fn.translation(om.MSpace.kTransform)

            if self.edit:
                self.newTranslation = [arg_db.flagArgumentDouble(SimpleCmd.TRANSLATE_FLAG[0], 0),
                                       arg_db.flagArgumentDouble(SimpleCmd.TRANSLATE_FLAG[0], 1),
                                       arg_db.flagArgumentDouble(SimpleCmd.TRANSLATE_FLAG[0], 2)]

                self.undoable = True

        self.version = arg_db.isFlagSet(SimpleCmd.VERSION_FLAG[0])

        self.redoIt()

    def undoIt(self):
        transform_fn = om.MFnTransform(self.selected_obj)
        transform_fn.setTranslation(om.MVector(self.originalTranslation), om.MSpace.kTransform)

    def redoIt(self):
        transform_fn = om.MFnTransform(self.selected_obj)

        if self.query:
            if self.translate:
                self.setResult(self.originalTranslation)
            else:
                raise RuntimeError("Flag does not support query")
        elif self.edit:
            if self.translate:
                transform_fn.setTranslation(om.MVector(self.newTranslation), om.MSpace.kTransform)
            else:
                raise RuntimeError("RFlag does not support edit")

        elif self.version:
            self.setResult("1.0.0")
        else:
            self.setResult(transform_fn.name())

    def isUndoable(self):
        return self.undoable

    @classmethod
    def creator(cls):
        return SimpleCmd()

    @classmethod
    def create_syntax(cls):

        syntax = om.MSyntax()

        syntax.enableEdit = True
        syntax.enableQuery = True

        syntax.addFlag(*cls.TRANSLATE_FLAG)
        syntax.addFlag(*cls.VERSION_FLAG)

        syntax.setObjectType(om.MSyntax.kSelectionList, 1, 1)
        syntax.useSelectionAsDefault(True)
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
