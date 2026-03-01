class DebugPrint:
    @classmethod
    def INPUT_TYPES(s):
        return {"required": {"ANY": ("*",)}}

    RETURN_TYPES = ()

    OUTPUT_NODE = True

    FUNCTION = "log_input"

    CATEGORY = "InitialB/logic"

    def log_input(self, ANY):
        print(ANY)
        return {}
