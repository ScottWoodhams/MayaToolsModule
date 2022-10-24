import maya.api.OpenMaya as om
import maya.api.OpenMayaRender as omr
import maya.api.OpenMayaUI as omui

import maya.cmds as cmds


def maya_useNewAPI():
    pass


class ShotMaskLocator(omui.MPxLocatorNode):
    NAME = "ShotMask"
    TYPE_ID = om.MTypeId(0x0007F7FE)

    DRAW_DB_CLASSIFICATION = "drawdb/geometry/shotmask"
    DRAW_REGISTRANT_ID = "ShotMaskLocator"

    TEXT_ATTRS = [("TopLeftText", "tlt"), ("TopCenterLeft", "tct"), ("TopRightText", "trt"), ("BottomLeftText", "blt"),
                  ("BottomCenterText", "bct"), ("BottomRightText", "brt")]

    def __init__(self):
        super(ShotMaskLocator, self).__init__()

    def excludeAsLocator(self):
        return False

    @classmethod
    def creator(cls):
        return ShotMaskLocator()

    @classmethod
    def initialize(cls):
        typed_attr = om.MFnTypedAttribute()
        string_data_fn = om.MFnStringData()
        numeric_attr = om.MFnNumericAttribute()

        obj = string_data_fn.create("")
        camera_name = typed_attr.create("camera", "cam", om.MFnData.kString, obj)
        cls.update_attr_properties(typed_attr)
        cls.addAttribute(camera_name)

        for i in range(0, len(cls.TEXT_ATTRS)):
            obj = string_data_fn.create("Position {0}".format(str(i + 1).zfill(2)))
            position = typed_attr.create(cls.TEXT_ATTRS[i][0], cls.TEXT_ATTRS[i][1], om.MFnData.kString, obj)
            cls.update_attr_properties(typed_attr)
            cls.addAttribute(position)

        text_padding = numeric_attr.create("textPadding", "tp", om.MFnNumericData.kShort, 10)
        cls.update_attr_properties(numeric_attr)
        numeric_attr.setMin(0)
        numeric_attr.setMax(50)
        cls.addAttribute(text_padding)

        obj = string_data_fn.create("Consolas")
        font_name = typed_attr.create("fontName", "fn", om.MFnData.kString, obj)
        cls.update_attr_properties(typed_attr)
        cls.addAttribute(font_name)

        font_color = numeric_attr.createColor("fontColor", "fc")
        cls.update_attr_properties(numeric_attr)
        numeric_attr.default = (1.0, 1.0, 1.0)
        cls.addAttribute(font_color)

        font_alpha = numeric_attr.create("fontAlpha", "fa", om.MFnNumericData.kFloat, 1.0)
        cls.update_attr_properties(numeric_attr)
        numeric_attr.setMin(0.0)
        numeric_attr.setMax(1.0)
        cls.addAttribute(font_alpha)

        font_scale = numeric_attr.create("fontScale", "fs", om.MFnNumericData.kFloat, 1.0)
        cls.update_attr_properties(numeric_attr)
        numeric_attr.setMin(0.1)
        numeric_attr.setMax(2.0)
        cls.addAttribute(font_scale)

        top_border = numeric_attr.create("topBorder", "tbd", om.MFnNumericData.kBoolean, True)
        cls.update_attr_properties(numeric_attr)
        cls.addAttribute(top_border)

        bottom_border = numeric_attr.create("bottomBorder", "bbd", om.MFnNumericData.kBoolean, True)
        cls.update_attr_properties(numeric_attr)
        cls.addAttribute(bottom_border)

        border_color = numeric_attr.createColor("borderColor", "bc")
        cls.update_attr_properties(numeric_attr)
        numeric_attr.default = (0.0, 0.0, 0.0)
        cls.addAttribute(border_color)

        border_alpha = numeric_attr.create("borderAlpha", "ba", om.MFnNumericData.kFloat, 1.0)
        cls.update_attr_properties(numeric_attr)
        numeric_attr.setMin(0.0)
        numeric_attr.setMax(1.0)
        cls.addAttribute(border_alpha)

        border_scale = numeric_attr.create("borderScale", "bs", om.MFnNumericData.kFloat, 1.0)
        cls.update_attr_properties(numeric_attr)
        numeric_attr.setMin(0.5)
        numeric_attr.setMax(2.0)
        cls.addAttribute(border_scale)

        counter_padding = numeric_attr.create("counterPadding", "cpd", om.MFnNumericData.kShort, 4)
        cls.update_attr_properties(numeric_attr)
        numeric_attr.setMin(1)
        numeric_attr.setMax(6)
        cls.addAttribute(counter_padding)

    @classmethod
    def update_attr_properties(cls, attr):
        attr.writable = True
        attr.storable = True
        if attr.type() == om.MFn.kNumericAttribute:
            attr.keyable = True


class ShotMaskData(om.MUserData):

    def __init__(self):
        super(ShotMaskData, self).__init__(False)

        self.parsed_fields = []

        self.current_time = 0
        self.counter_padding = 4

        self.font_name = "Consolas"
        self.font_color = om.MColor((1.0, 1.0, 1.0))
        self.font_scale = 1.0
        self.text_padding = 10

        self.top_border = True
        self.bottom_border = True
        self.border_color = om.MColor((0.0, 0.0, 0.0))
        self.border_scale = 1.0

        self.vp_width = 0
        self.vp_height = 0

        self.mask_width = 0
        self.mask_height = 0

    def __str__(self):
        output = ""
        output += "Text Fields: {0}\n".format(self.parsed_fields)

        output += "Current Time: {0}\n".format(self.current_time)
        output += "Counter Padding: {0}\n".format(self.counter_padding)

        output += "Font Color: {0}\n".format(self.font_color)
        output += "Font Scale: {0}\n".format(self.font_scale)
        output += "Text Padding: {0}\n".format(self.text_padding)

        output += "Top Border: {0}\n".format(self.border_scale)

        output += "Top Border: {0}\n".format(self.top_border)
        output += "Bottom Border: {0}\n".format(self.bottom_border)
        output += "Border Color: {0}\n".format(self.border_color)

        return output


class ShotMaskDrawOverride(omr.MPxDrawOverride):
    NAME = "shotmask_draw_override"

    def __init__(self, obj):
        super(ShotMaskDrawOverride, self).__init__(obj, None)

    def supportedDrawAPIs(self):
        return omr.MRenderer.kAllDevices

    def hasUIDrawables(self):
        return True

    def prepareForDraw(self, obj_path, camera_path, frame_context, old_data):

        data = old_data
        if not isinstance(data, ShotMaskData):
            data = ShotMaskData()

        dag_fn = om.MFnDagNode(obj_path)

        camera_name = dag_fn.findPlug("camera", False).asString()
        if camera_name and self.camera_exists(camera_name) and not self.is_camera_match(camera_path, camera_name):
            return None

        data.parsed_fields = []
        for i in range(0, len(ShotMaskLocator.TEXT_ATTRS)):
            orig_text = dag_fn.findPlug(ShotMaskLocator.TEXT_ATTRS[i][0], False).asString()
            parsed_text = self.parse_text(orig_text, camera_path, data)
            data.parsed_fields.append(parsed_text)

        data.current_time = int(cmds.currentTime(q=True))

        data.counter_padding = dag_fn.findPlug("counterPadding", False).asInt()
        data.text_padding = dag_fn.findPlug("textPadding", False).asInt()

        data.font_name = dag_fn.findPlug("fontName", False).asString()

        r = dag_fn.findPlug("fontColorR", False).asFloat()
        g = dag_fn.findPlug("fontColorG", False).asFloat()
        b = dag_fn.findPlug("fontColorB", False).asFloat()
        a = dag_fn.findPlug("fontAlpha", False).asFloat()
        data.font_color = om.MColor((r, g, b, a))

        data.font_scale = dag_fn.findPlug("fontScale", False).asFloat()

        r = dag_fn.findPlug("borderColorR", False).asFloat()
        g = dag_fn.findPlug("borderColorG", False).asFloat()
        b = dag_fn.findPlug("borderColorB", False).asFloat()
        a = dag_fn.findPlug("borderAlpha", False).asFloat()
        data.border_color = om.MColor((r, g, b, a))

        data.border_scale = dag_fn.findPlug("borderScale", False).asFloat()

        data.top_border = dag_fn.findPlug("topBorder", False).asBool()
        data.bottom_border = dag_fn.findPlug("bottomBorder", False).asBool()

        vp_x, vp_y, data.vp_width, data.vp_height = frame_context.getViewportDimensions()
        if not (data.vp_width and data.vp_height):
            return None

        data.mask_width, data.mask_height = self.get_mask_width_height(camera_path, data.vp_width, data.vp_height)
        if not (data.mask_width and data.mask_height):
            return None

        # print(data)

        return data

    def get_mask_width_height(self, camera_path, vp_width, vp_height):
        camera_fn = om.MFnCamera(camera_path)

        device_aspect_ratio = cmds.getAttr("defaultResolution.deviceAspectRatio")

        if camera_fn.filmFit == om.MFnCamera.kHorizontalFilmFit:
            mask_width = vp_width / camera_fn.overscan
            mask_height = mask_width / device_aspect_ratio
        elif camera_fn.filmFit == om.MFnCamera.kVerticalFilmFit:
            mask_height = vp_height / camera_fn.overscan
            mask_width = mask_height * device_aspect_ratio
        else:
            om.MGlobal.displayError("Unsupport film fit type")
            return None, None

        return mask_width, mask_height

    def addUIDrawables(self, obj_path, draw_manager, frame_context, data):
        if not (data and isinstance(data, ShotMaskData)):
            return

        vp_half_width = 0.5 * data.vp_width
        vp_half_height = 0.5 * data.vp_height

        mask_half_width = 0.5 * data.mask_width
        mask_x = vp_half_width - mask_half_width

        mask_half_height = 0.5 * data.mask_height
        mask_bottom_y = vp_half_height - mask_half_height
        mask_top_y = vp_half_height + mask_half_height

        border_height = int(0.05 * data.mask_height * data.border_scale)

        background_size = (int(data.mask_width), border_height)

        font_size = int(0.85 * border_height * data.font_scale)

        draw_manager.beginDrawable()

        if data.top_border:
            self.draw_border(draw_manager, om.MPoint(mask_x, mask_top_y - border_height, 0.1), background_size, data.border_color)
        if data.bottom_border:
            self.draw_border(draw_manager, om.MPoint(mask_x, mask_bottom_y, 0.1), background_size, data.border_color)

        draw_manager.setFontName(data.font_name)
        draw_manager.setFontSize(font_size)
        draw_manager.setColor(data.font_color)

        self.draw_label(draw_manager, om.MPoint(mask_x + data.text_padding, mask_top_y - border_height, 0.0), data, 0, omr.MUIDrawManager.kLeft, background_size)
        self.draw_label(draw_manager, om.MPoint(vp_half_width, mask_top_y - border_height, 0.0), data, 1, omr.MUIDrawManager.kCenter, background_size)
        self.draw_label(draw_manager, om.MPoint(mask_x + data.mask_width - data.text_padding, mask_top_y - border_height, 0.0), data, 2, omr.MUIDrawManager.kRight, background_size)

        self.draw_label(draw_manager, om.MPoint(mask_x + data.text_padding, mask_bottom_y, 0.0), data, 3, omr.MUIDrawManager.kLeft, background_size)
        self.draw_label(draw_manager, om.MPoint(vp_half_width, mask_bottom_y, 0.0), data, 4, omr.MUIDrawManager.kCenter, background_size)
        self.draw_label(draw_manager, om.MPoint(mask_x + data.mask_width - data.text_padding, mask_bottom_y, 0.0), data, 5, omr.MUIDrawManager.kRight, background_size)

        draw_manager.endDrawable()

    def draw_border(self, draw_manager, position, background_size, color):
        draw_manager.text2d(position, " ", alignment=omr.MUIDrawManager.kLeft, backgroundSize=background_size,
                            backgroundColor=color)

    def draw_label(self, draw_manager, position, data, data_index, alignment, background_size):
        text = data.parsed_fields[data_index]["text"]
        if text:
            draw_manager.text2d(position, text, alignment=alignment, backgroundSize=background_size, backgroundColor=om.MColor((0.0, 0.0, 0.0, 0.0)))

    def camera_exists(self, name):
        dg_iter = om.MItDependencyNodes(om.MFn.kCamera)
        while not dg_iter.isDone():
            camera_path = om.MDagPath.getAPathTo(dg_iter.thisNode())
            if self.is_camera_match(camera_path, name):
                return True

            dg_iter.next()

        return False

    def is_camera_match(self, camera_path, name):
        if self.get_camera_transform_name(camera_path) == name or self.get_camera_shape_name(camera_path) == name:
            return True

        return False

    def get_camera_transform_name(self, camera_path):
        camera_transform = camera_path.transform()
        if camera_transform:
            return om.MFnTransform(camera_transform).name()

        return ""

    def get_camera_shape_name(self, camera_path):
        camera_shape = camera_path.node()
        if camera_shape:
            return om.MFnCamera(camera_shape).name()

        return ""

    def parse_text(self, orig_text, camera_path, data):
        text = orig_text

        return {"text": text}

    @staticmethod
    def creator(obj):
        """
        """
        return ShotMaskDrawOverride(obj)


def initializePlugin(obj):
    """
    """
    plugin_fn = om.MFnPlugin(obj, "Scott Woodhams ", "1.0.0", "Any")

    try:
        plugin_fn.registerNode(ShotMaskLocator.NAME,
                               ShotMaskLocator.TYPE_ID,
                               ShotMaskLocator.creator,
                               ShotMaskLocator.initialize,
                               om.MPxNode.kLocatorNode,
                               ShotMaskLocator.DRAW_DB_CLASSIFICATION)
    except:
        om.MGlobal.displayError("Failed to register node: {0}".format(ShotMaskLocator.NAME))

    try:
        omr.MDrawRegistry.registerDrawOverrideCreator(ShotMaskLocator.DRAW_DB_CLASSIFICATION,
                                                      ShotMaskLocator.DRAW_REGISTRANT_ID,
                                                      ShotMaskDrawOverride.creator)
    except:
        om.MGlobal.displayError("Failed to register draw override: {0}".format(ShotMaskDrawOverride.NAME))


def uninitializePlugin(obj):
    """
    """
    plugin_fn = om.MFnPlugin(obj)

    try:
        omr.MDrawRegistry.deregisterDrawOverrideCreator(ShotMaskLocator.DRAW_DB_CLASSIFICATION,
                                                        ShotMaskLocator.DRAW_REGISTRANT_ID)
    except:
        om.MGlobal.displayError("Failed to deregister draw override: {0}".format(ShotMaskDrawOverride.NAME))

    try:
        plugin_fn.deregisterNode(ShotMaskLocator.TYPE_ID)
    except:
        om.MGlobal.displayError("Failed to unregister node: {0}".format(ShotMaskLocator.NAME))


if __name__ == "__main__":
    cmds.file(f=True, new=True)

    plugin_name = "shot_mask.py"
    cmds.evalDeferred('if cmds.pluginInfo("{0}", q=True, loaded=True): cmds.unloadPlugin("{0}")'.format(plugin_name))
    cmds.evalDeferred('if not cmds.pluginInfo("{0}", q=True, loaded=True): cmds.loadPlugin("{0}")'.format(plugin_name))

    cmds.evalDeferred('cmds.createNode("ShotMask")')
