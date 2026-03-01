"""
Preset Sigma Generator Node

Node for generating sigma schedules from common presets.
Provides quick access to well-known sampling schedules.

Features:
- 10 preset schedules (Karras, Exponential, VP, VE, etc.)
- Configurable sigma_min, sigma_max, and rho parameters
- Seed support for reproducibility
- Detailed preset information output
"""

import torch
import numpy as np
import json
from typing import Tuple, Dict, Any


class PresetSigmaGenerator:
    """
    Node for generating sigma schedules from common presets.
    Provides quick access to well-known sampling schedules.
    Includes seed support for reproducibility.
    """

    @classmethod
    def INPUT_TYPES(cls) -> Dict[str, Any]:
        return {
            "required": {
                "preset": ([
                    "karras",
                    "exponential",
                    "vp",
                    "ve",
                    "linear",
                    "polyexponential",
                    "lms",
                    "ddim",
                    "euler",
                    "heun"
                ], {"default": "karras"}),
                "steps": ("INT", {"default": 20, "min": 2, "max": 1000}),
                "sigma_min": ("FLOAT", {"default": 0.002, "min": 0.0001, "max": 1.0, "step": 0.0001}),
                "sigma_max": ("FLOAT", {"default": 14.6146, "min": 1.0, "max": 1000.0, "step": 0.1}),
                "rho": ("FLOAT", {"default": 7.0, "min": 1.0, "max": 20.0, "step": 0.1}),
                "seed": ("INT", {"default": 0, "min": 0, "max": 0xffffffffffffffff}),
            }
        }

    RETURN_TYPES = ("SIGMAS", "STRING", "INT")
    RETURN_NAMES = ("sigmas", "preset_info", "seed")
    FUNCTION = "generate_preset"
    CATEGORY = "InitialB/sigma/custom"

    def generate_preset(
        self,
        preset: str,
        steps: int,
        sigma_min: float,
        sigma_max: float,
        rho: float,
        seed: int = 0
    ) -> Tuple[torch.Tensor, str, int]:
        """
        Generate a sigma schedule from a preset.

        Args:
            preset: Name of the preset schedule
            steps: Number of steps
            sigma_min: Minimum sigma value
            sigma_max: Maximum sigma value
            rho: Schedule parameter (used in Karras and similar schedules)
            seed: Random seed for reproducibility

        Returns:
            Tuple of (sigma_tensor, preset_info_json, seed)
        """
        sigmas = self._generate_schedule(preset, steps, sigma_min, sigma_max, rho)

        preset_info = json.dumps({
            "preset": preset,
            "steps": steps,
            "sigma_min": sigma_min,
            "sigma_max": sigma_max,
            "rho": rho,
            "seed": seed,
            "actual_max": float(sigmas.max()),
            "actual_min": float(sigmas.min()),
        })

        return (sigmas, preset_info, seed)

    def _generate_schedule(
        self,
        preset: str,
        steps: int,
        sigma_min: float,
        sigma_max: float,
        rho: float
    ) -> torch.Tensor:
        """
        Generate the actual sigma schedule based on preset type.

        Args:
            preset: Name of the preset schedule
            steps: Number of steps
            sigma_min: Minimum sigma value
            sigma_max: Maximum sigma value
            rho: Schedule parameter

        Returns:
            Tensor of sigma values in descending order
        """
        generators = {
            "karras": self._karras_schedule,
            "exponential": self._exponential_schedule,
            "vp": self._vp_schedule,
            "ve": self._ve_schedule,
            "linear": self._linear_schedule,
            "polyexponential": self._polyexponential_schedule,
            "lms": self._lms_schedule,
            "ddim": self._ddim_schedule,
            "euler": self._euler_schedule,
            "heun": self._heun_schedule,
        }

        generator = generators.get(preset, self._linear_schedule)
        sigmas = generator(steps, sigma_min, sigma_max, rho)

        # Ensure correct ordering (descending)
        sigmas, _ = torch.sort(sigmas, descending=True)

        return sigmas

    def _karras_schedule(
        self,
        steps: int,
        sigma_min: float,
        sigma_max: float,
        rho: float
    ) -> torch.Tensor:
        """
        Karras schedule from "Elucidating the Design Space of Diffusion-Based Generative Models"

        This schedule provides a good balance between detail preservation and creative freedom.
        """
        sigma_min_inv = sigma_min ** (1 / rho)
        sigma_max_inv = sigma_max ** (1 / rho)
        sigmas = []
        for i in range(steps):
            t = i / (steps - 1)
            sigma = (sigma_max_inv + t * (sigma_min_inv - sigma_max_inv)) ** rho
            sigmas.append(sigma)
        return torch.tensor(sigmas, dtype=torch.float32)

    def _exponential_schedule(
        self,
        steps: int,
        sigma_min: float,
        sigma_max: float,
        rho: float
    ) -> torch.Tensor:
        """
        Exponential schedule.

        Provides smooth exponential decay from sigma_max to sigma_min.
        """
        t = torch.linspace(0, 1, steps)
        return sigma_max * (sigma_min / sigma_max) ** t

    def _vp_schedule(
        self,
        steps: int,
        sigma_min: float,
        sigma_max: float,
        rho: float
    ) -> torch.Tensor:
        """
        Variance Preserving (VP) schedule.

        Used in DDPM and related models.
        """
        t = torch.linspace(0, 1, steps)
        alpha_cumprod = torch.exp(-t * 10.0)
        sigmas = torch.sqrt((1 - alpha_cumprod) / alpha_cumprod)
        return sigmas * sigma_max / sigmas.max()

    def _ve_schedule(
        self,
        steps: int,
        sigma_min: float,
        sigma_max: float,
        rho: float
    ) -> torch.Tensor:
        """
        Variance Exploding (VE) schedule.

        Used in Score-Based Generative Models.
        """
        t = torch.linspace(0, 1, steps)
        return sigma_min * (sigma_max / sigma_min) ** t

    def _linear_schedule(
        self,
        steps: int,
        sigma_min: float,
        sigma_max: float,
        rho: float
    ) -> torch.Tensor:
        """
        Linear schedule.

        Simple linear interpolation between sigma_max and sigma_min.
        """
        return torch.linspace(sigma_max, sigma_min, steps)

    def _polyexponential_schedule(
        self,
        steps: int,
        sigma_min: float,
        sigma_max: float,
        rho: float
    ) -> torch.Tensor:
        """
        Polyexponential schedule.

        Combination of polynomial and exponential functions.
        """
        t = torch.linspace(0, 1, steps)
        return sigma_min + (sigma_max - sigma_min) * (t ** (1.0 / rho))

    def _lms_schedule(
        self,
        steps: int,
        sigma_min: float,
        sigma_max: float,
        rho: float
    ) -> torch.Tensor:
        """
        Linear Multistep-like schedule.

        Includes smoothing for more stable sampling.
        """
        sigmas = torch.linspace(sigma_max, sigma_min, steps)
        if steps > 2:
            kernel = torch.tensor([0.25, 0.5, 0.25])
            sigmas = torch.conv1d(
                sigmas.unsqueeze(0).unsqueeze(0),
                kernel.view(1, 1, -1),
                padding=1
            ).squeeze()
        return sigmas

    def _ddim_schedule(
        self,
        steps: int,
        sigma_min: float,
        sigma_max: float,
        rho: float
    ) -> torch.Tensor:
        """
        DDIM-style schedule.

        Based on cosine annealing.
        """
        t = torch.linspace(0, 1, steps)
        alpha_cumprod = torch.cos(t * np.pi / 2) ** 2
        sigmas = torch.sqrt((1 - alpha_cumprod) / alpha_cumprod)
        if sigmas.max() > 0:
            sigmas = sigmas * sigma_max / sigmas.max()
        return sigmas

    def _euler_schedule(
        self,
        steps: int,
        sigma_min: float,
        sigma_max: float,
        rho: float
    ) -> torch.Tensor:
        """
        Euler-like schedule.

        Similar to Karras but with different rho handling.
        """
        sigmas = torch.zeros(steps)
        for i in range(steps):
            t = i / max(1, steps - 1)
            sigmas[i] = sigma_max * (sigma_min / sigma_max) ** (t ** (1.0 / rho))
        return sigmas

    def _heun_schedule(
        self,
        steps: int,
        sigma_min: float,
        sigma_max: float,
        rho: float
    ) -> torch.Tensor:
        """
        Heun's method inspired schedule.

        Provides smoother transitions for Heun's sampler.
        """
        t = torch.linspace(0, 1, steps)
        return sigma_max * torch.exp(-t * np.log(sigma_max / sigma_min))
