import os
import traceback

from PySide2 import QtCore
import maya.cmds as cmds
import maya.OpenMaya as om


class PlayBlast(QtCore.QObject):
    VERSION = "0.0.1"

    DEFAULT_FFMPEG_PATH = "C:\\Users\Scott\Downloads\\ffmpeg\\ffmpeg\\bin\\ffmpeg.exe"
    output_logged = QtCore.Signal(str)

    def __init__(self, ffmpeg_path=None, log_to_maya=True):
        super(PlayBlast, self).__init__()

        self.log_to_maya = None
        self.ffmpeg_path = None
        self.set_ffmpeg_path(ffmpeg_path)
        self.set_maya_logging_enabled(log_to_maya)

    def set_ffmpeg_path(self, ffmpeg_path):
        if ffmpeg_path:
            self.ffmpeg_path = ffmpeg_path
        else:
            self.ffmpeg_path = PlayBlast.DEFAULT_FFMPEG_PATH

    def get_ffmpeg_path(self):
        return self.ffmpeg_path

    def set_maya_logging_enabled(self, enabled):
        self.log_to_maya = enabled

    def validate_ffmpeg(self):
        if not self.ffmpeg_path:
            self.log_error("ffmpeg executable path not set")
            return False
        elif not os.path.exists(self.ffmpeg_path):
            self.log_error("ffmpeg executable path does not exist: {0}".format(self._ffmpeg_path))
            return False
        elif os.path.isdir(self.ffmpeg_path):
            self.log_error("Invalid ffmpeg path: {0}".format(self._ffmpeg_path))
            return False

        return True

    def resolve_output_directory_path(self, dir_path):
        if "{project}" in dir_path:
            dir_path = dir_path.replace("{project}", self.get_project_dir_path())
        return dir_path

    def resolve_output_filename(self, filename):
        if "{scene}" in filename:
            filename = filename.replace("{scene}", self.get_scene_name())
        return filename

    def get_project_dir_path(self):
        return cmds.workspace(q=True, rootDirectory=True)

    def get_scene_name(self):
        scene_name = cmds.file(q=True, sceneName=True, shortName=True)
        if scene_name:
            scene_name = os.path.splitext(scene_name)[0]
        else:
            scene_name = "untitled"

        return scene_name

    def execute(self, output_dir, filename, padding=4, show_ornaments=True, show_in_viewer=True, overwrite=False):

        if not output_dir:
            self.log_error("Output directory path not set")
            return

        if not filename:
            self.log_error("Output file name not set")
            return

        output_dir = self.resolve_output_directory_path(output_dir)
        filename = self.resolve_output_filename(filename)

        self.log_output("Output dir: {0}".format(output_dir))
        self.log_output("Output filename: {0}".format(filename))

        if self.validate_ffmpeg():
            self.log_output("TODO: execute playblast")

    def log_error(self, text):
        if self.log_to_maya:
            om.MGlobal.displayError("[PlayBlast] {0}".format(text))

        self.output_logged.emit("[ERROR] {0}".format(text))

    def log_warning(self, text):
        if self.log_to_maya:
            om.MGlobal.displayWarning("[PlayBlast] {0}".format(text))

        self.output_logged.emit("[WARNING] {0}".format(text))

    def log_output(self, text):
        if self.log_to_maya:
            om.MGlobal.displayInfo(text)

        self.output_logged.emit(text)


if __name__ == "__main__":
    playblast = PlayBlast()
    playblast.execute("{project}", "{scene}")
