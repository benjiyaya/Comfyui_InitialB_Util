class RangeInt:
    @classmethod
    def INPUT_TYPES(s):
        return {
            "required": {
                "start": ("INT", {"default": 0, "min": -99999, "max": 99999}),
                "stop": ("INT", {"default": 10, "min": -99999, "max": 99999}),
                "step": ("INT", {"default": 1, "min": 1, "max": 99999}),
            },
        }

    RETURN_TYPES = ("INT",)
    RETURN_NAMES = ("values",)
    FUNCTION = "generate_range"
    CATEGORY = "InitialB/utility"

    def generate_range(self, start, stop, step):
        return (list(range(start, stop, step)),)


class Compare:
    @classmethod
    def INPUT_TYPES(s):
        return {
            "required": {
                "a": ("*", {}),
                "b": ("*", {}),
                "comparison": (
                    ["a == b", "a != b", "a < b", "a > b", "a <= b", "a >= b"],
                    {"default": "a == b"},
                ),
            },
        }

    RETURN_TYPES = ("BOOLEAN",)
    RETURN_NAMES = ("result",)
    FUNCTION = "compare"
    CATEGORY = "InitialB/logic"

    def compare(self, a, b, comparison):
        ops = {
            "a == b": lambda x, y: x == y,
            "a != b": lambda x, y: x != y,
            "a < b": lambda x, y: x < y,
            "a > b": lambda x, y: x > y,
            "a <= b": lambda x, y: x <= y,
            "a >= b": lambda x, y: x >= y,
        }
        return (ops[comparison](a, b),)


class MathInt:
    @classmethod
    def INPUT_TYPES(s):
        return {
            "required": {
                "a": ("INT", {"default": 0}),
                "b": ("INT", {"default": 0}),
                "operation": (
                    ["add", "subtract", "multiply", "divide", "modulo", "power"],
                    {"default": "add"},
                ),
            },
        }

    RETURN_TYPES = ("INT",)
    RETURN_NAMES = ("result",)
    FUNCTION = "calculate"
    CATEGORY = "InitialB/utility"

    def calculate(self, a, b, operation):
        ops = {
            "add": lambda x, y: x + y,
            "subtract": lambda x, y: x - y,
            "multiply": lambda x, y: x * y,
            "divide": lambda x, y: x // y if y != 0 else 0,
            "modulo": lambda x, y: x % y if y != 0 else 0,
            "power": lambda x, y: x**y,
        }
        return (ops[operation](a, b),)
