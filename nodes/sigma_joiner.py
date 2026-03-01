"""
Sigma Joiner Node

Node for joining two sigma schedules together using various blend modes.
Useful for creating hybrid schedules that combine different sampling strategies.

Features:
- Multiple blend modes (concatenate, average, max, min)
- Support for tensor and dictionary-like sigma objects
- Automatic sorting for proper sigma ordering
"""

import torch
import copy
from typing import Tuple, Dict, Any


class SigmaJoiner:
    """
    Node for joining two sigma schedules together.
    Useful for creating hybrid schedules that combine different sampling strategies.
    """

    @classmethod
    def INPUT_TYPES(cls) -> Dict[str, Any]:
        return {
            "required": {
                "sigma_1": ("SIGMAS",),
                "sigma_2": ("SIGMAS",),
                "blend_mode": (["concatenate", "average", "max", "min"], {"default": "concatenate"}),
            }
        }

    RETURN_TYPES = ("SIGMAS",)
    FUNCTION = "join_sigmas"
    CATEGORY = "InitialB/sigma/custom"

    def join_sigmas(self, sigma_1: Any, sigma_2: Any, blend_mode: str = "concatenate") -> Tuple[Any]:
        """
        Join two sigma schedules using the specified blend mode.

        Args:
            sigma_1: First sigma schedule
            sigma_2: Second sigma schedule
            blend_mode: How to combine the schedules

        Returns:
            Combined sigma schedule
        """
        # Handle tensor inputs
        if isinstance(sigma_1, torch.Tensor) and isinstance(sigma_2, torch.Tensor):
            return self._join_tensors(sigma_1, sigma_2, blend_mode)

        # Handle dictionary-like sigma objects
        elif hasattr(sigma_1, '__dict__') or isinstance(sigma_1, dict):
            return self._join_objects(sigma_1, sigma_2, blend_mode)

        else:
            return (torch.tensor(sigma_1),)

    def _join_tensors(
        self,
        sigma_1: torch.Tensor,
        sigma_2: torch.Tensor,
        blend_mode: str
    ) -> Tuple[torch.Tensor]:
        """Join two tensor sigma schedules."""

        if blend_mode == "concatenate":
            # Remove first element from second array to avoid duplication
            sigma_2_trimmed = sigma_2[1:] if len(sigma_2) > 0 else sigma_2
            combined = torch.cat([sigma_1, sigma_2_trimmed], dim=0)
            combined, _ = torch.sort(combined, descending=True)

        elif blend_mode == "average":
            # Interpolate both to same length and average
            max_len = max(len(sigma_1), len(sigma_2))
            combined = (sigma_1.mean() + sigma_2.mean()) / 2
            combined = torch.full((max_len,), combined)

        elif blend_mode == "max":
            combined = torch.maximum(sigma_1.max(), sigma_2.max())
            combined = torch.full((max(len(sigma_1), len(sigma_2)),), combined)

        elif blend_mode == "min":
            combined = torch.minimum(sigma_1.min(), sigma_2.min())
            combined = torch.full((max(len(sigma_1), len(sigma_2)),), combined)

        else:
            combined = sigma_1

        return (combined,)

    def _join_objects(self, sigma_1: Any, sigma_2: Any, blend_mode: str) -> Tuple[Any]:
        """Join two dictionary-like sigma objects."""

        if isinstance(sigma_1, dict):
            combined_sigma = sigma_1.copy()
        else:
            combined_sigma = copy.deepcopy(sigma_1)

        # Extract tensor values
        tensor1 = self._extract_tensor(sigma_1)
        tensor2 = self._extract_tensor(sigma_2)

        # Apply blend mode
        if blend_mode == "concatenate":
            tensor2_trimmed = tensor2[1:] if len(tensor2) > 0 else tensor2
            combined_tensor = torch.cat([tensor1, tensor2_trimmed], dim=0)
            combined_tensor, _ = torch.sort(combined_tensor, descending=True)
        else:
            combined_tensor = tensor1  # Fallback

        # Update combined object
        self._set_tensor(combined_sigma, combined_tensor)

        return (combined_sigma,)

    def _extract_tensor(self, sigma_obj: Any) -> torch.Tensor:
        """Extract tensor from sigma object."""
        if hasattr(sigma_obj, 'sigmas'):
            return sigma_obj.sigmas
        elif isinstance(sigma_obj, dict) and 'sigmas' in sigma_obj:
            return sigma_obj['sigmas']
        else:
            return next(
                (v for k, v in vars(sigma_obj).items() if isinstance(v, torch.Tensor)),
                sigma_obj
            )

    def _set_tensor(self, sigma_obj: Any, tensor: torch.Tensor):
        """Set tensor in sigma object."""
        if hasattr(sigma_obj, 'sigmas'):
            sigma_obj.sigmas = tensor
        elif isinstance(sigma_obj, dict) and 'sigmas' in sigma_obj:
            sigma_obj['sigmas'] = tensor

        if hasattr(sigma_obj, 'cfg_sigmas_i'):
            sigma_obj.cfg_sigmas_i = {i: tensor[i].item() for i in range(len(tensor))}
        elif isinstance(sigma_obj, dict) and 'cfg_sigmas_i' in sigma_obj:
            sigma_obj['cfg_sigmas_i'] = {i: tensor[i].item() for i in range(len(tensor))}
