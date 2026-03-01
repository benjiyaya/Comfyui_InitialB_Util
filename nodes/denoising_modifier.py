"""
Denoising Strength Modifier Node

Node for modifying denoising strength based on sigma schedule.
Useful for img2img and in-painting workflows.

Features:
- Truncate mode: Cut sigma schedule at denoising point
- Scale mode: Scale all sigma values by strength
- Interpolate mode: Smooth interpolation to zero
- Returns effective number of steps used
"""

import torch
from typing import Tuple, Dict, Any


class DenoisingStrengthModifier:
    """
    Node for modifying denoising strength based on sigma schedule.
    Useful for img2img and in-painting workflows.
    """

    @classmethod
    def INPUT_TYPES(cls) -> Dict[str, Any]:
        return {
            "required": {
                "sigmas": ("SIGMAS",),
                "denoising_strength": ("FLOAT", {"default": 1.0, "min": 0.0, "max": 1.0, "step": 0.01}),
                "mode": (["truncate", "scale", "interpolate"], {"default": "truncate"}),
            }
        }

    RETURN_TYPES = ("SIGMAS", "INT")
    RETURN_NAMES = ("modified_sigmas", "effective_steps")
    FUNCTION = "modify_denoising"
    CATEGORY = "InitialB/sigma/custom"

    def modify_denoising(
        self,
        sigmas: Any,
        denoising_strength: float,
        mode: str
    ) -> Tuple[Any, int]:
        """
        Modify sigma schedule based on denoising strength.

        Args:
            sigmas: Input sigma schedule
            denoising_strength: Strength of denoising (0.0 to 1.0)
            mode: How to apply the denoising strength
                - truncate: Truncate schedule at denoising point
                - scale: Scale all values by strength
                - interpolate: Interpolate between original and zero

        Returns:
            Tuple of (modified_sigmas, effective_steps)
        """
        # Convert to tensor if needed
        if isinstance(sigmas, torch.Tensor):
            tensor = sigmas.clone()
        else:
            tensor = torch.tensor(sigmas, dtype=torch.float32)

        if mode == "truncate":
            modified, effective_steps = self._truncate_mode(tensor, denoising_strength)

        elif mode == "scale":
            modified, effective_steps = self._scale_mode(tensor, denoising_strength)

        elif mode == "interpolate":
            modified, effective_steps = self._interpolate_mode(tensor, denoising_strength)

        else:
            modified = tensor
            effective_steps = len(tensor)

        return (modified, effective_steps)

    def _truncate_mode(
        self,
        tensor: torch.Tensor,
        denoising_strength: float
    ) -> Tuple[torch.Tensor, int]:
        """
        Truncate sigma schedule at denoising strength point.

        This mode is useful for img2img where you want to start
        from a partially noised image.
        """
        total_steps = len(tensor)
        effective_steps = max(1, int(total_steps * denoising_strength))

        if denoising_strength < 1.0:
            # Find the sigma value at the truncation point
            truncation_idx = int(total_steps * (1 - denoising_strength))
            truncation_sigma = tensor[truncation_idx]

            # Truncate from the high-noise end
            modified = tensor[tensor >= truncation_sigma]
            if len(modified) == 0:
                modified = tensor[:effective_steps]
        else:
            modified = tensor

        return modified, len(modified)

    def _scale_mode(
        self,
        tensor: torch.Tensor,
        denoising_strength: float
    ) -> Tuple[torch.Tensor, int]:
        """
        Scale sigma values by denoising strength.

        This reduces the overall noise level proportionally.
        """
        modified = tensor * denoising_strength
        return modified, len(modified)

    def _interpolate_mode(
        self,
        tensor: torch.Tensor,
        denoising_strength: float
    ) -> Tuple[torch.Tensor, int]:
        """
        Interpolate between original sigma and zero.

        Creates a smooth transition based on denoising strength.
        """
        # Create interpolation weights
        weights = torch.linspace(denoising_strength, 0.0, len(tensor))
        modified = tensor * weights

        return modified, len(modified)
