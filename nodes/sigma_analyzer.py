"""
Sigma Analyzer Node

Node for analyzing sigma schedules and providing insights.
Returns detailed statistics about the sigma schedule.

Features:
- Min, max, mean sigma values
- Standard deviation calculation
- Step count
- Detailed JSON analysis output
"""

import torch
import json
from typing import Tuple, Dict, Any


class SigmaAnalyzer:
    """
    Node for analyzing sigma schedules and providing insights.
    """

    @classmethod
    def INPUT_TYPES(cls) -> Dict[str, Any]:
        return {
            "required": {
                "sigmas": ("SIGMAS",),
            }
        }

    RETURN_TYPES = ("FLOAT", "FLOAT", "FLOAT", "INT", "STRING")
    RETURN_NAMES = ("max_sigma", "min_sigma", "mean_sigma", "num_steps", "analysis")
    FUNCTION = "analyze_sigmas"
    CATEGORY = "InitialB/sigma/custom"

    def analyze_sigmas(self, sigmas: Any) -> Tuple[float, float, float, int, str]:
        """
        Analyze a sigma schedule and return statistics.

        Args:
            sigmas: Input sigma schedule

        Returns:
            Tuple of (max_sigma, min_sigma, mean_sigma, num_steps, analysis_json)
        """
        # Convert to tensor if needed
        if isinstance(sigmas, torch.Tensor):
            tensor = sigmas
        else:
            tensor = torch.tensor(sigmas)

        # Calculate basic statistics
        max_s = tensor.max().item()
        min_s = tensor.min().item()
        mean_s = tensor.mean().item()
        num_steps = len(tensor)

        # Calculate additional statistics
        std_s = tensor.std().item() if len(tensor) > 1 else 0.0
        sigma_range = max_s - min_s

        # Create detailed analysis
        analysis = json.dumps({
            "max": max_s,
            "min": min_s,
            "mean": mean_s,
            "std": std_s,
            "range": sigma_range,
            "steps": num_steps,
            "slope_avg": sigma_range / num_steps if num_steps > 0 else 0,
            "median": tensor.median().item() if len(tensor) > 0 else 0.0,
            "variance": tensor.var().item() if len(tensor) > 1 else 0.0,
        })

        return (max_s, min_s, mean_s, num_steps, analysis)
