class IfExecute:
    @classmethod
    def INPUT_TYPES(s):
        return {
            "required": {
                "ANY": ("*",),
                "IF_TRUE": ("*",),
                "IF_FALSE": ("*",),
            },
        }

    RETURN_TYPES = ("*",)

    RETURN_NAMES = ("OUTPUT",)

    FUNCTION = "return_based_on_bool"

    CATEGORY = "InitialB/logic"

    def return_based_on_bool(self, ANY, IF_TRUE, IF_FALSE):
        return (IF_TRUE if ANY else IF_FALSE,)
