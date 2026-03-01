# InitialB Util for ComfyUI

InitialB Util is a ComfyUI custom node package that provides various utility nodes for workflow automation, logic operations, sigma manipulation, text processing, image collage creation, and flow control.

## ✨ Features

### Core Features
- 🖱️ **Interactive Graph Editor**: Add, move, or delete control points directly on the node's graph
- 🟦 **Smooth Catmull-Rom Spline**: Uses centripetal Catmull-Rom spline for smooth interpolation
- 📤 **Export Schedules as Tensors**: Outputs sigma value tensors for use in sampling pipelines
- 👀 **Visual Feedback**: Live preview of curves and control points
- 🎲 **Seed Support**: Reproducible results with seed input/output
- 🖼️ **Collage Creation**: Combine multiple images with directional control
- 🔄 **Flow Control**: For loops and while loops for iterative workflows

### Node Collection

![2026-03-02 042235](https://github.com/user-attachments/assets/50d10c44-c890-4958-92ec-264f45285c63)

#### Sigma Utilities
- 📈 **Custom Graph Sigma**: Main interactive curve editor with 12+ presets
- 🔗 **Sigma Joiner**: Combine multiple sigma schedules with blend modes
- 📏 **Sigma Scaler**: Scale and transform sigma values
- 🔍 **Sigma Analyzer**: Get detailed statistics about sigma schedules
- 🎚️ **Denoising Strength Modifier**: Control denoising for img2img workflows
- 📋 **Preset Sigma Generator**: Quick access to common schedules

![2026-03-02 042135](https://github.com/user-attachments/assets/ff48c8cb-0f2d-4166-9f2a-3f241045682f)

#### Logic Nodes
- 🔬 **Compare**: Compare two values with various operators (==, !=, <, >, <=, >=)
- 🔬 **Int/Float/String/Bool**: Data type nodes for handling different value types
- 🔬 **If ANY return A else B**: Conditional execution based on boolean
- 🔬 **DebugPrint**: Print any input to console for debugging

![2026-03-02 042217](https://github.com/user-attachments/assets/14ada7ed-3ed3-47fa-9b52-817197a12f6d)

#### Text Tools
- 📝 **Multi-Line String**: Input multiline text and output as single string
- 🔗 **String Joiner**: Join multiple strings with configurable separator

![2026-03-02 042252](https://github.com/user-attachments/assets/5fbc81a2-1fdb-4117-a412-23a2c7f162d2)

#### Flow Control
- 🔄 **For Loop Start/End**: Execute nodes in a loop with iteration counting
- 🔁 **While Loop Start/End**: Execute nodes while condition is true
- 📊 **Range Int**: Generate integer sequences (start, stop, step)
- 🔢 **Math Int**: Integer math operations (add, subtract, multiply, divide, modulo, power)

## 📦 Installation

### Method 1: ComfyUI Manager (Recommended)
1. Open ComfyUI Manager
2. Search for "InitialB Util"
3. Click Install

### Method 2: Manual Installation
```bash
cd ComfyUI/custom_nodes/
git clone https://github.com/yourusername/comfyui_InitialB_Util.git
cd comfyui_InitialB_Util
pip install -r requirements.txt
```

### Method 3: Download ZIP
1. Download the ZIP file from releases
2. Extract to `ComfyUI/custom_nodes/comfyui_InitialB_Util/`
3. Restart ComfyUI

## 🎯 Node Reference

### Sigma Utility Nodes

See earlier sections for sigma utility documentation.

### Logic Nodes

See earlier sections for logic nodes documentation.

### Text Tool Nodes

See earlier sections for text tools documentation.

### Image Collage Nodes

See earlier sections for image collage documentation.

### Flow Control Nodes

#### 🔄 For Loop

Execute a set of nodes multiple times with incrementing index.

**For Loop Start:**
- **Inputs:**
  - `total`: Number of iterations (1-10000)
  - `value1-5`: Optional values to pass through loop
- **Outputs:**
  - `flow`: Flow control connection
  - `index`: Current iteration number (0-based)
  - `value1-5`: Passed-through values

**For Loop End:**
- **Inputs:**
  - `flow`: Connection from For Loop Start
  - `value1-5`: Values from loop body
- **Outputs:**
  - `value1-5`: Final values after loop completion

**Usage:**
```
[For Loop Start: total=5] → [Your Nodes] → [For Loop End]
         ↓                      ↑
      index=0,1,2,3,4          ↓
                           (auto-increments)
```

#### 🔁 While Loop

Execute nodes while a condition is true.

**While Loop Start:**
- **Inputs:**
  - `condition`: Boolean to continue loop
  - `value0-4`: Values to pass through (5 carriers)
- **Outputs:**
  - `flow`: Flow control connection
  - `value0-4`: Passed-through values

**While Loop End:**
- **Inputs:**
  - `flow`: Connection from While Loop Start
  - `condition`: Boolean to continue or exit
  - `value0-4`: Values from loop body
- **Outputs:**
  - `value0-4`: Final values after loop exits

**Usage:**
```
[While Loop Start] → [Your Nodes] → [Compare/Condition] → [While Loop End]
        ↓                                                      ↑
    (pass values)                                          (check condition)
```

#### 📊 Range Int

Generate a sequence of integers.

**Inputs:**
- `start`: Starting value (default: 0)
- `stop`: Ending value (exclusive, default: 10)
- `step`: Step size (default: 1)

**Outputs:**
- `values`: List of integers from start to stop with step

**Example:**
- start=0, stop=10, step=2 → [0, 2, 4, 6, 8]

#### 🔢 Math Int

Perform integer mathematical operations.

**Inputs:**
- `a`: First integer
- `b`: Second integer
- `operation`: Math operation (add, subtract, multiply, divide, modulo, power)

**Outputs:**
- `result`: Result of the operation

**Operations:**
- `add`: a + b
- `subtract`: a - b
- `multiply`: a * b
- `divide`: a // b (integer division)
- `modulo`: a % b
- `power`: a ** b

## 🎨 Usage Guide

### For Loop Example
```
[For Loop Start: total=10]
         ↓
    [index: 0-9]
         ↓
  [Generate Image per iteration]
         ↓
[For Loop End] → [Final Output]
```

### While Loop Example
```
[While Loop Start: condition=True]
         ↓
  [Process Data]
         ↓
[Compare: check if done] → [While Loop End]
                                  ↓
                            (exit when condition=False)
```

### Combining Flow Control
```
[Range Int: 0-100, step=10] → [For Loop Start]
                                      ↓
                                [Process Each]
                                      ↓
                                [For Loop End]
```

## 📝 Requirements
- Python 3.9+
- PyTorch
- NumPy
- SciPy
- Pillow
- ComfyUI (with dynamic execution graph support for loops)

## 📄 License
MIT License

## 🤝 Credits
- InitialB Util package structure and architecture
- Logic nodes based on ComfyUI-Logic by [theUpsider](https://github.com/theUpsider)
- Flow control patterns inspired by ComfyUI-Easy-Use [yolain](https://github.com/yolain/ComfyUI-Easy-Use)
- Sigma functionality from original work by [JoeNavark](https://github.com/JoeNavark)

## 📮 Support
For issues and feature requests, please open an issue on GitHub.
