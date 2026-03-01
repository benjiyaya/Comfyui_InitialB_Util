"""
Sigma Scaler Node

Node for scaling and transforming sigma schedules.
Allows adjusting the noise levels for different effects.

Features:
- Scale multiplier for sigma values
- Offset adjustment
- Power transformation for non-linear scaling
- Output includes max sigma value for monitoring
"""

import torch
from typing import Tuple, Dict, Any


class SigmaScaler:
    """
    Node for scaling and transforming sigma schedules.
    Allows adjusting the noise levels for different effects.
    """

    @classmethod
    def INPUT_TYPES(cls) -> Dict[str, Any]:
        return {
            "required": {
                "sigmas": ("SIGMAS",),
                "scale": ("FLOAT", {"default": 1.0, "min": 0.01, "max": 100.0, "step": 0.01}),
                "offset": ("FLOAT", {"default": 0.0, "min": -10.0, "max": 10.0, "step": 0.01}),
                "power": ("FLOAT", {"default": 1.0, "min": 0.1, "max": 5.0, "step": 0.1}),
            }
        }

    RETURN_TYPES = ("SIGMAS", "FLOAT")
    RETURN_NAMES = ("scaled_sigmas", "max_sigma")
    FUNCTION = "scale_sigmas"
    CATEGORY = "InitialB/sigma/custom"

    def scale_sigmas(
        self,
        sigmas: Any,
        scale: float,
        offset: float,
        power: float
    ) -> Tuple[Any, float]:
        """
        Scale and transform sigma values.

        Formula: sigma_new = ((sigma * scale) + offset) ** power

        Args:
            sigmas: Input sigma schedule
            scale: Scale multiplier
            offset: Value offset
            power: Power transformation

        Returns:
            Tuple of (scaled_sigmas, max_sigma_value)
        """
        # Convert to tensor if needed
        if isinstance(sigmas, torch.Tensor):
            tensor = sigmas
        else:
            tensor = torch.tensor(sigmas, dtype=torch.float32)

        # Apply transformation: ((sigma * scale) + offset) ** power
        scaled = ((tensor * scale) + offset) ** power
        scaled = torch.clamp(scaled, min=0.0)

        return (scaled, scaled.max().item())
