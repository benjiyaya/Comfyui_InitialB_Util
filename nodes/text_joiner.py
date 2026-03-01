class StringJoiner:
    @classmethod
    def INPUT_TYPES(s):
        return {
            "required": {
                "strings": ("STRING", {"default": "", "multiline": False}),
                "separator": ("STRING", {"default": "", "multiline": False}),
            },
            "optional": {
                "string_1": ("STRING", {"default": ""}),
                "string_2": ("STRING", {"default": ""}),
                "string_3": ("STRING", {"default": ""}),
                "string_4": ("STRING", {"default": ""}),
                "string_5": ("STRING", {"default": ""}),
            },
        }

    RETURN_TYPES = ("STRING",)

    RETURN_NAMES = ("OUTPUT",)

    FUNCTION = "join_strings"

    CATEGORY = "InitialB/text"

    def join_strings(
        self,
        strings,
        separator="",
        string_1="",
        string_2="",
        string_3="",
        string_4="",
        string_5="",
    ):
        parts = [
            s for s in [strings, string_1, string_2, string_3, string_4, string_5] if s
        ]
        result = separator.join(parts)
        return (result,)
