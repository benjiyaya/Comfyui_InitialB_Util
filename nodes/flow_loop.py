from comfy_execution.graph_utils import GraphBuilder, is_link
from comfy_execution.graph import ExecutionBlocker

try:
    from nodes import NODE_CLASS_MAPPINGS as ALL_NODE_CLASS_MAPPINGS
except:
    ALL_NODE_CLASS_MAPPINGS = {}

any_type = "COMBO"
MAX_FLOW_NUM = 20


class ForLoopStart:
    @classmethod
    def INPUT_TYPES(s):
        return {
            "required": {
                "total": ("INT", {"default": 5, "min": 1, "max": 10000, "step": 1}),
            },
            "optional": {f"initial_value{i}": ("*",) for i in range(1, 6)},
            "hidden": {
                "prompt": "PROMPT",
                "extra_pnginfo": "EXTRA_PNGINFO",
                "unique_id": "UNIQUE_ID",
            },
        }

    RETURN_TYPES = ["FLOW_CONTROL", "INT"] + ["*"] * 5
    RETURN_NAMES = ["flow", "index"] + [f"value{i}" for i in range(1, 6)]
    FUNCTION = "for_loop_start"
    CATEGORY = "InitialB/flow/loop"

    def for_loop_start(
        self, total, prompt=None, extra_pnginfo=None, unique_id=None, **kwargs
    ):
        graph = GraphBuilder()

        i = kwargs.get("initial_value0", 0) if "initial_value0" in kwargs else 0

        initial_values = {
            f"initial_value{i}": kwargs.get(f"initial_value{i}", None)
            for i in range(1, 6)
        }

        while_open = graph.node(
            "InitialBWhileLoopStart",
            condition=total,
            initial_value0=i,
            **initial_values,
        )

        outputs = [kwargs.get(f"initial_value{i}", None) for i in range(1, 6)]

        return {
            "result": tuple(["stub", i] + outputs),
            "expand": graph.finalize(),
        }


class ForLoopEnd:
    @classmethod
    def INPUT_TYPES(s):
        return {
            "required": {
                "flow": ("FLOW_CONTROL", {"rawLink": True}),
            },
            "optional": {
                f"initial_value{i}": ("*", {"rawLink": True}) for i in range(1, 6)
            },
            "hidden": {
                "dynprompt": "DYNPROMPT",
                "extra_pnginfo": "EXTRA_PNGINFO",
                "unique_id": "UNIQUE_ID",
            },
        }

    RETURN_TYPES = ["*"] * 5
    RETURN_NAMES = [f"value{i}" for i in range(1, 6)]
    FUNCTION = "for_loop_end"
    CATEGORY = "InitialB/flow/loop"

    def for_loop_end(
        self, flow, dynprompt=None, extra_pnginfo=None, unique_id=None, **kwargs
    ):
        graph = GraphBuilder()
        while_open = flow[0]
        total = None

        forstart_node = dynprompt.get_node(while_open)
        if forstart_node:
            inputs = forstart_node.get("inputs", {})
            total = inputs.get("total", 1)

        sub = graph.node("InitialBMathInt", operation="add", a=[while_open, 1], b=1)
        cond = graph.node("InitialBCompare", a=sub.out(0), b=total, comparison="a < b")

        input_values = {
            f"initial_value{i}": kwargs.get(f"initial_value{i}", None)
            for i in range(1, 6)
        }

        while_close = graph.node(
            "InitialBWhileLoopEnd",
            flow=flow,
            condition=cond.out(0),
            initial_value0=sub.out(0),
            **input_values,
        )

        return {
            "result": tuple([while_close.out(i) for i in range(1, 6)]),
            "expand": graph.finalize(),
        }
