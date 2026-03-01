"""
InitialB Util - ComfyUI Custom Node Package

A collection of utility nodes for ComfyUI with various functionality including
logic nodes, sigma manipulation, workflow automation, text utilities, collage tools, and flow control.

Package Structure:
- nodes/custom_spline_sigma.py: Interactive spline-based curve editor
- nodes/sigma_joiner.py: Join multiple sigma schedules
- nodes/sigma_scaler.py: Scale and transform sigma values
- nodes/sigma_analyzer.py: Analyze sigma schedule statistics
- nodes/denoising_modifier.py: Modify denoising strength
- nodes/preset_generator.py: Generate sigma schedules from presets
- nodes/logic_types.py: Data type nodes (Int, Float, String, Bool)
- nodes/logic_compare.py: Comparison nodes
- nodes/logic_conditional.py: Conditional execution nodes
- nodes/logic_debug.py: Debug printing nodes
- nodes/text_multiline.py: Multi-line string input node
- nodes/text_joiner.py: Multiple string joiner with configurable inputs
- nodes/image_collage.py: Multi-image collage concatenation
- nodes/image_batch_concat.py: Batch image to grid concatenation
- nodes/flow_loop.py: For Loop start/end nodes
- nodes/flow_while.py: While Loop start/end nodes
- nodes/utility_math.py: Range generator and math operations

Author: InitialB Team
License: MIT
Version: 2.0.0
"""

import os

# Import all node classes from separate modules
from .nodes.custom_spline_sigma import CustomSplineSigma
from .nodes.sigma_joiner import SigmaJoiner
from .nodes.sigma_scaler import SigmaScaler
from .nodes.sigma_analyzer import SigmaAnalyzer
from .nodes.denoising_modifier import DenoisingStrengthModifier
from .nodes.preset_generator import PresetSigmaGenerator
from .nodes.logic_types import String, Int, Float, Bool
from .nodes.logic_compare import Compare
from .nodes.logic_conditional import IfExecute
from .nodes.logic_debug import DebugPrint
from .nodes.text_multiline import MultiLineString
from .nodes.text_joiner import StringJoiner
from .nodes.image_collage import MultiImageConcatenate
from .nodes.image_batch_concat import ImageConcatFromBatch
from .nodes.flow_loop import ForLoopStart, ForLoopEnd
from .nodes.flow_while import WhileLoopStart, WhileLoopEnd
from .nodes.utility_math import RangeInt, MathInt

# Web directory for JavaScript extensions
WEB_DIRECTORY = os.path.join(os.path.dirname(os.path.realpath(__file__)), "js")

# Node class mappings for ComfyUI registration
NODE_CLASS_MAPPINGS = {
    "CustomSplineSigma": CustomSplineSigma,
    "SigmaJoiner": SigmaJoiner,
    "SigmaScaler": SigmaScaler,
    "SigmaAnalyzer": SigmaAnalyzer,
    "DenoisingStrengthModifier": DenoisingStrengthModifier,
    "PresetSigmaGenerator": PresetSigmaGenerator,
    "Compare-🔬": Compare,
    "Int-🔬": Int,
    "Float-🔬": Float,
    "Bool- 🔬": Bool,
    "String- 🔬": String,
    "If ANY return A else B- 🔬": IfExecute,
    "DebugPrint- 🔬": DebugPrint,
    "MultiLineString": MultiLineString,
    "StringJoiner 🔬": StringJoiner,
    "MultiImageConcatenate": MultiImageConcatenate,
    "ImageConcatFromBatch": ImageConcatFromBatch,
    "InitialBForLoopStart": ForLoopStart,
    "InitialBForLoopEnd": ForLoopEnd,
    "InitialBWhileLoopStart": WhileLoopStart,
    "InitialBWhileLoopEnd": WhileLoopEnd,
    "InitialBRangeInt": RangeInt,
    "InitialBMathInt": MathInt,
}

# Display names for the ComfyUI node menu
NODE_DISPLAY_NAME_MAPPINGS = {
    "CustomSplineSigma": "📈 Custom Graph Sigma",
    "SigmaJoiner": "🔗 Join Sigma Values",
    "SigmaScaler": "📏 Scale Sigma",
    "SigmaAnalyzer": "🔍 Analyze Sigma",
    "DenoisingStrengthModifier": "🎚️ Denoising Strength",
    "PresetSigmaGenerator": "📋 Preset Sigma Generator",
    "Compare- 🔬": "Compare",
    "Int- 🔬": "Int",
    "Float- 🔬": "Float",
    "Bool- 🔬": "Bool",
    "String- 🔬": "String",
    "If ANY return A else B- 🔬": "If ANY return A else B",
    "DebugPrint- 🔬": "DebugPrint",
    "MultiLineString": "📝 Multi-Line String",
    "StringJoiner 🔬": "🔗 String Joiner",
    "MultiImageConcatenate": "🖼️ Multi-Image Collage",
    "ImageConcatFromBatch": "🖼️ Image Batch to Grid",
    "InitialBForLoopStart": "🔄 For Loop Start",
    "InitialBForLoopEnd": "🔄 For Loop End",
    "InitialBWhileLoopStart": "🔁 While Loop Start",
    "InitialBWhileLoopEnd": "🔁 While Loop End",
    "InitialBRangeInt": "📊 Range Int",
    "InitialBMathInt": "🔢 Math Int",
}

__all__ = ["NODE_CLASS_MAPPINGS", "NODE_DISPLAY_NAME_MAPPINGS", "WEB_DIRECTORY"]
