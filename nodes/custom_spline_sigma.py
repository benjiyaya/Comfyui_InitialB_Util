"""
Custom Spline Sigma Node

Main node for creating custom sigma schedules using an interactive spline editor.
Supports multiple preset curves, custom control point editing, and seed-based
random curve generation.

Features:
- Interactive graph-based curve editing
- Centripetal Catmull-Rom spline interpolation
- 12+ preset sigma schedules
- Seed support for reproducibility
- Random curve generation modes
"""

import torch
import numpy as np
import json
from scipy.interpolate import interp1d
from typing import Tuple, Dict, Any


class CustomSplineSigma:
    """
    Main node for creating custom sigma schedules using an interactive spline editor.
    Supports multiple preset curves and custom control point editing.
    Includes seed support for reproducibility and random curve generation.
    """

    CATEGORY = "InitialB/sigma/custom"
    RETURN_TYPES = ("STRING", "SIGMAS", "INT")
    RETURN_NAMES = ("curve_data", "sigmas", "seed")
    FUNCTION = "render"

    @classmethod
    def INPUT_TYPES(cls) -> Dict[str, Any]:
        return {
            "required": {
                "steps": ("INT", {"default": 20, "min": 2, "max": 4096}),
                "start_y": ("FLOAT", {"default": 1.0, "min": 0.0, "max": 20.0, "step": 0.01}),
                "end_y": ("FLOAT", {"default": 0.0, "min": 0.0, "max": 20.0, "step": 0.01}),
                "curve_data": ("STRING", {"default": "", "forceInput": True}),
                "seed": ("INT", {"default": 0, "min": 0, "max": 0xffffffffffffffff}),
                "random_curve": (["disabled", "add_noise", "random_points"], {"default": "disabled"}),
                "noise_strength": ("FLOAT", {"default": 0.1, "min": 0.0, "max": 1.0, "step": 0.01}),
            }
        }

    def __init__(self):
        pass

    def render(
        self,
        steps: int,
        curve_data: str = "",
        start_y: float = 1.0,
        end_y: float = 0.0,
        seed: int = 0,
        random_curve: str = "disabled",
        noise_strength: float = 0.1
    ) -> Tuple[str, torch.Tensor, int]:
        """
        Generate sigma schedule from curve data with seed support.

        Args:
            steps: Number of sigma values to generate
            curve_data: JSON string containing control points and samples
            start_y: Starting Y value (noise level)
            end_y: Ending Y value (noise level)
            seed: Random seed for reproducibility
            random_curve: Mode for random curve generation
                - disabled: Use curve data as-is
                - add_noise: Add random noise to existing curve
                - random_points: Generate random control points
            noise_strength: Strength of noise/randomization (0.0-1.0)

        Returns:
            Tuple of (curve_data_json, sigma_tensor, seed)
        """
        # Set random seed for reproducibility
        rng = np.random.RandomState(seed)

        # Parse curve data
        try:
            data = json.loads(curve_data) if curve_data else {}
            points = data.get(
                "control_points",
                [
                    {"x": 0.0, "y": start_y},
                    {"x": 1.0, "y": end_y}
                ]
            )
            samples = data.get("samples", None)
        except Exception as e:
            print(f"[CustomSplineSigma] Parse error: {str(e)}")
            samples = None
            points = [
                {"x": 0.0, "y": start_y},
                {"x": 1.0, "y": end_y}
            ]

        # Apply random curve modifications if enabled
        if random_curve == "random_points":
            # Generate random control points based on seed
            num_points = rng.randint(3, 8)  # Random number of control points
            x_positions = np.sort(rng.rand(num_points))
            x_positions[0] = 0.0  # Fix start
            x_positions[-1] = 1.0  # Fix end

            # Generate Y values with a general downward trend
            points = []
            for i, x in enumerate(x_positions):
                # Base trend: high to low
                base_y = start_y - (start_y - end_y) * (i / (num_points - 1))
                # Add random variation
                noise = rng.uniform(-noise_strength, noise_strength) * (start_y - end_y)
                y = np.clip(base_y + noise, 0.0, max(start_y, end_y) + 5.0)
                points.append({"x": float(x), "y": float(y)})

            samples = None  # Force recalculation

        elif random_curve == "add_noise" and samples:
            # Add noise to existing samples
            samples_array = np.array(samples)
            noise = rng.randn(len(samples_array)) * noise_strength * (start_y - end_y)
            samples_array[:, 1] = np.clip(samples_array[:, 1] + noise, 0.0, max(start_y, end_y) + 5.0)
            samples = samples_array.tolist()
            # Update control points to match
            points = [
                {"x": samples[0][0], "y": samples[0][1]},
                {"x": samples[-1][0], "y": samples[-1][1]}
            ]

        # Use JS samples if available (pixel-perfect match)
        if samples and isinstance(samples, list) and len(samples) > 1:
            curve_points = samples
        else:
            # Fallback: Python interpolation
            curve_points = self._interpolate_points(points)

        # Compose output
        out_data = {
            "control_points": points,
            "spline_points": curve_points,
            "seed": seed,
            "random_mode": random_curve,
            "noise_strength": noise_strength,
        }

        # Generate sigma tensor
        sigmas = self._generate_sigma_tensor(curve_points, steps, start_y, end_y)

        return (json.dumps(out_data), sigmas, seed)

    def _interpolate_points(self, points: list) -> list:
        """
        Interpolate control points using scipy.

        Args:
            points: List of control point dictionaries with x, y keys

        Returns:
            List of interpolated [x, y] coordinate pairs
        """
        ctrl_x = np.array([p["x"] for p in points])
        ctrl_y = np.array([p["y"] for p in points])

        # Sort by x
        sort_idx = np.argsort(ctrl_x)
        ctrl_x = ctrl_x[sort_idx]
        ctrl_y = ctrl_y[sort_idx]

        # Ensure unique x values
        unique_x, unique_indices = np.unique(ctrl_x, return_index=True)
        unique_y = ctrl_y[unique_indices]

        n_points = len(unique_x)
        if n_points >= 4:
            kind = 'cubic'
        elif n_points == 3:
            kind = 'quadratic'
        elif n_points == 2:
            kind = 'linear'
        else:
            kind = None

        if kind:
            interpolator = interp1d(unique_x, unique_y, kind=kind, fill_value="extrapolate", bounds_error=False)
            dense_x = np.linspace(0, 1, 200)
            dense_y = interpolator(dense_x)
            curve_points = np.stack([dense_x, dense_y], axis=1).tolist()
        else:
            dense_x = np.linspace(0, 1, 200)
            dense_y = np.full_like(dense_x, unique_y[0] if len(unique_y) > 0 else 0.0)
            curve_points = np.stack([dense_x, dense_y], axis=1).tolist()

        return curve_points

    def _generate_sigma_tensor(
        self,
        curve_points: list,
        steps: int,
        start_y: float,
        end_y: float
    ) -> torch.Tensor:
        """
        Generate sigma tensor from curve points.

        Args:
            curve_points: List of [x, y] coordinate pairs
            steps: Number of sigma values to generate
            start_y: Starting Y value for scaling
            end_y: Ending Y value for scaling

        Returns:
            Tensor of sigma values
        """
        curve_points_arr = np.array(curve_points)
        curve_x = curve_points_arr[:, 0]
        curve_y = curve_points_arr[:, 1]
        sort_idx = np.argsort(curve_x)
        curve_x = curve_x[sort_idx]
        curve_y = curve_y[sort_idx]

        sigma_interp = interp1d(curve_x, curve_y, kind="linear", fill_value="extrapolate", bounds_error=False)
        sigma_x = np.linspace(0, 1, steps)
        sigma_y = sigma_interp(sigma_x)
        sigmas = torch.tensor(sigma_y, dtype=torch.float32)

        # Scale and shift to match start_y and end_y
        if steps >= 2:
            src_start = sigmas[0].item()
            src_end = sigmas[-1].item()
            if abs(src_end - src_start) > 1e-8:
                scale = (end_y - start_y) / (src_end - src_start)
                shift = start_y - src_start * scale
                sigmas = sigmas * scale + shift
            else:
                sigmas = torch.full((steps,), start_y, dtype=torch.float32)

        return sigmas
