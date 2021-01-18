"""
autor: Valentina Garrido
"""

import transformations2 as _tr


class Command:
    TRANSLATE = "translate"
    SCALE = "scale"
    UNIFORM_SCALE = "uniformScale"
    ROTATION_X = "rotationX"
    ROTATION_Y = "rotationY"
    ROTATION_Z = "rotationZ"
    ROTATION_A = "rotationA"
    SHEARING = "shearing"


command_dictionary = {
    Command.TRANSLATE : _tr.translate,
    Command.SCALE : _tr.scale,
    Command.UNIFORM_SCALE: _tr.uniformScale,
    Command.ROTATION_X : _tr.rotationX,
    Command.ROTATION_Y : _tr.rotationY,
    Command.ROTATION_Z : _tr.rotationZ,
    Command.ROTATION_A : _tr.rotationA,
    Command.SHEARING : _tr.shearing
}