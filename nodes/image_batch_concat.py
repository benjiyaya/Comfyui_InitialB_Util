import torch
import comfy.utils


class ImageConcatFromBatch:
    @classmethod
    def INPUT_TYPES(s):
        return {
            "required": {
                "images": ("IMAGE",),
                "num_columns": ("INT", {"default": 3, "min": 1, "max": 255, "step": 1}),
                "match_image_size": ("BOOLEAN", {"default": False}),
                "max_resolution": ("INT", {"default": 4096}),
            },
        }

    RETURN_TYPES = ("IMAGE",)
    FUNCTION = "concat"
    CATEGORY = "InitialB/image/collage"
    DESCRIPTION = "Concatenates images from a batch into a grid with a specified number of columns."

    def concat(self, images, num_columns, match_image_size, max_resolution):
        batch_size = images.shape[0]
        height = images.shape[1]
        width = images.shape[2]
        channels = images.shape[3]

        num_rows = (batch_size + num_columns - 1) // num_columns

        if match_image_size:
            target_shape = images[0].shape

            resized_images = []
            for image in images:
                original_height = image.shape[0]
                original_width = image.shape[1]
                original_aspect_ratio = original_width / original_height

                if original_aspect_ratio > 1:
                    target_height = target_shape[0]
                    target_width = int(target_height * original_aspect_ratio)
                else:
                    target_width = target_shape[1]
                    target_height = int(target_width / original_aspect_ratio)

                resized_image = comfy.utils.common_upscale(
                    image.movedim(-1, 0),
                    target_width,
                    target_height,
                    "lanczos",
                    "disabled",
                )
                resized_image = resized_image.movedim(0, -1)
                resized_images.append(resized_image)

            images = torch.stack(resized_images)
            height, width = target_shape[:2]

        grid_height = num_rows * height
        grid_width = num_columns * width

        scale_factor = min(
            max_resolution / grid_height, max_resolution / grid_width, 1.0
        )

        scaled_height = height * scale_factor
        scaled_width = width * scale_factor

        height = max(1, int(round(scaled_height / 8) * 8))
        width = max(1, int(round(scaled_width / 8) * 8))

        if abs(scaled_height - height) > 4:
            height = max(1, int(round((scaled_height + 4) / 8) * 8))
        if abs(scaled_width - width) > 4:
            width = max(1, int(round((scaled_width + 4) / 8) * 8))

        grid = torch.zeros((grid_height, grid_width, channels), dtype=images.dtype)

        for idx in range(batch_size):
            resized_image = (
                torch.nn.functional.interpolate(
                    images[idx].unsqueeze(0).permute(0, 3, 1, 2),
                    size=(height, width),
                    mode="bilinear",
                )
                .squeeze()
                .permute(1, 2, 0)
            )
            row = idx // num_columns
            col = idx % num_columns
            grid[
                row * height : (row + 1) * height, col * width : (col + 1) * width, :
            ] = resized_image

        return (grid.unsqueeze(0),)
