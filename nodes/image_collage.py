from PIL import Image


class MultiImageConcatenate:
    @classmethod
    def INPUT_TYPES(s):
        return {
            "required": {
                "image1": ("IMAGE",),
                "direction1": (["right", "down"], {"default": "right"}),
            },
            "optional": {
                "image2": ("IMAGE",),
                "direction2": (["right", "down"], {"default": "right"}),
                "image3": ("IMAGE",),
                "direction3": (["right", "down"], {"default": "right"}),
                "image4": ("IMAGE",),
                "direction4": (["right", "down"], {"default": "right"}),
                "image5": ("IMAGE",),
                "direction5": (["right", "down"], {"default": "right"}),
                "padding": ("INT", {"default": 0, "min": 0, "max": 100, "step": 1}),
            },
        }

    RETURN_TYPES = ("IMAGE",)

    RETURN_NAMES = ("OUTPUT",)

    FUNCTION = "concatenate_images"

    CATEGORY = "InitialB/image/collage"

    def concatenate_images(
        self,
        image1,
        direction1="right",
        image2=None,
        direction2="right",
        image3=None,
        direction3="right",
        image4=None,
        direction4="right",
        image5=None,
        direction5="right",
        padding=0,
    ):
        import torch

        directions = [
            ("image1", direction1),
            ("image2", direction2),
            ("image3", direction3),
            ("image4", direction4),
            ("image5", direction5),
        ]

        images = [image1, image2, image3, image4, image5]
        active_images = [
            (img, dir_name)
            for img, dir_name in zip(images, directions)
            if img is not None
        ]

        if len(active_images) == 0:
            raise ValueError("At least one image is required")

        if len(active_images) == 1:
            return (active_images[0][0],)

        result = self._build_collage(active_images, padding)

        return (result,)

    def _build_collage(self, image_direction_pairs, padding):
        import torch

        if len(image_direction_pairs) == 1:
            return image_direction_pairs[0][0]

        first_img = image_direction_pairs[0][0]
        remaining = image_direction_pairs[1:]

        result = first_img

        for img, dir_name in remaining:
            result = self._merge_two_images(result, img, dir_name, padding)

        return result

    def _merge_two_images(self, img1, img2, direction, padding):
        import torch

        batch1 = img1.shape[0] if len(img1.shape) == 4 else 1
        batch2 = img2.shape[0] if len(img2.shape) == 4 else 1

        h1, w1 = img1.shape[1], img1.shape[2]
        h2, w2 = img2.shape[1], img2.shape[2]

        if direction == "right":
            new_h = max(h1, h2)
            new_w = w1 + w2 + padding
            output = torch.zeros((batch1, new_h, new_w, 3), dtype=torch.float32)
            output[:, :h1, :w1, :] = img1
            output[:, :h2, w1 + padding :, :] = img2
        else:
            new_h = h1 + h2 + padding
            new_w = max(w1, w2)
            output = torch.zeros((batch1, new_h, new_w, 3), dtype=torch.float32)
            output[:, :h1, :w1, :] = img1
            output[:, h1 + padding :, :w2, :] = img2

        return output
