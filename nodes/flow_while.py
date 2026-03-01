from comfy_execution.graph_utils import GraphBuilder, is_link
from comfy_execution.graph import ExecutionBlocker

try:
    from nodes import NODE_CLASS_MAPPINGS as ALL_NODE_CLASS_MAPPINGS
except:
    ALL_NODE_CLASS_MAPPINGS = {}

MAX_FLOW_NUM = 5
any_type = "*"


class WhileLoopStart:
    @classmethod
    def INPUT_TYPES(s):
        return {
            "required": {
                "condition": ("BOOLEAN", {"default": True}),
            },
            "optional": {f"initial_value{i}": ("*",) for i in range(MAX_FLOW_NUM)},
        }

    RETURN_TYPES = ["FLOW_CONTROL"] + ["*"] * MAX_FLOW_NUM
    RETURN_NAMES = ["flow"] + [f"value{i}" for i in range(MAX_FLOW_NUM)]
    FUNCTION = "while_loop_start"
    CATEGORY = "InitialB/flow/loop"

    def while_loop_start(self, condition, **kwargs):
        values = []
        for i in range(MAX_FLOW_NUM):
            values.append(
                kwargs.get(f"initial_value{i}", None)
                if condition
                else ExecutionBlocker(None)
            )
        return tuple(["stub"] + values)


class WhileLoopEnd:
    @classmethod
    def INPUT_TYPES(s):
        return {
            "required": {
                "flow": ("FLOW_CONTROL", {"rawLink": True}),
                "condition": ("BOOLEAN", {}),
            },
            "optional": {f"initial_value{i}": ("*",) for i in range(MAX_FLOW_NUM)},
            "hidden": {
                "dynprompt": "DYNPROMPT",
                "unique_id": "UNIQUE_ID",
            },
        }

    RETURN_TYPES = ["*"] * MAX_FLOW_NUM
    RETURN_NAMES = [f"value{i}" for i in range(MAX_FLOW_NUM)]
    FUNCTION = "while_loop_end"
    CATEGORY = "InitialB/flow/loop"

    def explore_dependencies(self, node_id, dynprompt, upstream, parent_ids):
        node_info = dynprompt.get_node(node_id)
        if "inputs" not in node_info:
            return

        for k, v in node_info["inputs"].items():
            if is_link(v):
                parent_id = v[0]
                try:
                    display_id = dynprompt.get_display_node_id(parent_id)
                    display_node = dynprompt.get_node(display_id)
                    class_type = display_node.get("class_type", "")
                    if class_type not in ["InitialBForLoopEnd", "InitialBWhileLoopEnd"]:
                        parent_ids.append(display_id)
                    if parent_id not in upstream:
                        upstream[parent_id] = []
                        self.explore_dependencies(
                            parent_id, dynprompt, upstream, parent_ids
                        )
                    upstream[parent_id].append(node_id)
                except:
                    pass

    def collect_contained(self, node_id, upstream, contained):
        if node_id not in upstream:
            return
        for child_id in upstream[node_id]:
            if child_id not in contained:
                contained[child_id] = True
                self.collect_contained(child_id, upstream, contained)

    def while_loop_end(self, flow, condition, dynprompt=None, unique_id=None, **kwargs):
        if not condition:
            values = []
            for i in range(MAX_FLOW_NUM):
                values.append(kwargs.get(f"initial_value{i}", None))
            return tuple(values)

        this_node = dynprompt.get_node(unique_id)
        upstream = {}
        parent_ids = []
        self.explore_dependencies(unique_id, dynprompt, upstream, parent_ids)
        parent_ids = list(set(parent_ids))

        graph = GraphBuilder()
        contained = {}
        open_node = flow[0]
        self.collect_contained(open_node, upstream, contained)
        contained[unique_id] = True
        contained[open_node] = True

        for node_id in contained:
            original_node = dynprompt.get_node(node_id)
            node = graph.node(
                original_node["class_type"],
                "Recurse" if node_id == unique_id else node_id,
            )

        for node_id in contained:
            original_node = dynprompt.get_node(node_id)
            node = graph.lookup_node("Recurse" if node_id == unique_id else node_id)
            for k, v in original_node["inputs"].items():
                if is_link(v) and v[0] in contained:
                    parent = graph.lookup_node(v[0])
                    node.set_input(k, parent.out(v[1]))
                else:
                    node.set_input(k, v)

        new_open = graph.lookup_node(open_node)
        for i in range(MAX_FLOW_NUM):
            key = f"initial_value{i}"
            new_open.set_input(key, kwargs.get(key, None))

        my_clone = graph.lookup_node("Recurse")
        result = map(lambda x: my_clone.out(x), range(MAX_FLOW_NUM))

        return {
            "result": tuple(result),
            "expand": graph.finalize(),
        }
