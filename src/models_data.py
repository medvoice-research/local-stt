"""
Model information for whisper.cpp models.

This module contains detailed information about all available whisper.cpp models,
including their sizes, language support, and quantization details.
"""
from typing import Any, Dict

# Define type for model info dictionary
ModelInfoDict = Dict[str, Dict[str, Any]]

# Complete list of available models, their sizes, and capabilities
MODEL_INFO: ModelInfoDict = {
    # Regular models
    "tiny": {"size_mb": 75, "multilingual": True, "params": "39M", "quantized": False},
    "tiny.en": {"size_mb": 75, "multilingual": False, "params": "39M", "quantized": False},
    "base": {"size_mb": 142, "multilingual": True, "params": "74M", "quantized": False},
    "base.en": {"size_mb": 142, "multilingual": False, "params": "74M", "quantized": False},
    "small": {"size_mb": 466, "multilingual": True, "params": "244M", "quantized": False},
    "small.en": {"size_mb": 466, "multilingual": False, "params": "244M", "quantized": False},
    "medium": {"size_mb": 1500, "multilingual": True, "params": "769M", "quantized": False},
    "medium.en": {"size_mb": 1500, "multilingual": False, "params": "769M", "quantized": False},
    "large-v1": {"size_mb": 2900, "multilingual": True, "params": "1550M", "quantized": False},
    "large-v2": {"size_mb": 2900, "multilingual": True, "params": "1550M", "quantized": False},
    "large-v3": {"size_mb": 2900, "multilingual": True, "params": "1550M", "quantized": False},
    "large-v3-turbo": {
        "size_mb": 2900,
        "multilingual": True,
        "params": "1550M",
        "quantized": False,
    },
    # Diarization-capable models
    "small.en-tdrz": {
        "size_mb": 466,
        "multilingual": False,
        "params": "244M",
        "quantized": False,
        "diarization": True,
    },
    # Quantized models - Q5_1 (5-bit quantization)
    "tiny-q5_1": {
        "size_mb": 47,
        "multilingual": True,
        "params": "39M",
        "quantized": True,
        "quantization": "q5_1",
    },
    "tiny.en-q5_1": {
        "size_mb": 47,
        "multilingual": False,
        "params": "39M",
        "quantized": True,
        "quantization": "q5_1",
    },
    "base-q5_1": {
        "size_mb": 89,
        "multilingual": True,
        "params": "74M",
        "quantized": True,
        "quantization": "q5_1",
    },
    "base.en-q5_1": {
        "size_mb": 89,
        "multilingual": False,
        "params": "74M",
        "quantized": True,
        "quantization": "q5_1",
    },
    "small-q5_1": {
        "size_mb": 292,
        "multilingual": True,
        "params": "244M",
        "quantized": True,
        "quantization": "q5_1",
    },
    "small.en-q5_1": {
        "size_mb": 292,
        "multilingual": False,
        "params": "244M",
        "quantized": True,
        "quantization": "q5_1",
    },
    # Quantized models - Q8_0 (8-bit quantization)
    "tiny-q8_0": {
        "size_mb": 75,
        "multilingual": True,
        "params": "39M",
        "quantized": True,
        "quantization": "q8_0",
    },
    "base-q8_0": {
        "size_mb": 142,
        "multilingual": True,
        "params": "74M",
        "quantized": True,
        "quantization": "q8_0",
    },
    "small-q8_0": {
        "size_mb": 466,
        "multilingual": True,
        "params": "244M",
        "quantized": True,
        "quantization": "q8_0",
    },
    "medium-q8_0": {
        "size_mb": 1500,
        "multilingual": True,
        "params": "769M",
        "quantized": True,
        "quantization": "q8_0",
    },
    "medium.en-q8_0": {
        "size_mb": 1500,
        "multilingual": False,
        "params": "769M",
        "quantized": True,
        "quantization": "q8_0",
    },
    "large-v2-q8_0": {
        "size_mb": 2900,
        "multilingual": True,
        "params": "1550M",
        "quantized": True,
        "quantization": "q8_0",
    },
    "large-v3-turbo-q8_0": {
        "size_mb": 2900,
        "multilingual": True,
        "params": "1550M",
        "quantized": True,
        "quantization": "q8_0",
    },
    # Quantized models - Q5_0 (5-bit quantization, different algorithm than Q5_1)
    "medium-q5_0": {
        "size_mb": 938,
        "multilingual": True,
        "params": "769M",
        "quantized": True,
        "quantization": "q5_0",
    },
    "medium.en-q5_0": {
        "size_mb": 938,
        "multilingual": False,
        "params": "769M",
        "quantized": True,
        "quantization": "q5_0",
    },
    "large-v2-q5_0": {
        "size_mb": 1810,
        "multilingual": True,
        "params": "1550M",
        "quantized": True,
        "quantization": "q5_0",
    },
    "large-v3-q5_0": {
        "size_mb": 1810,
        "multilingual": True,
        "params": "1550M",
        "quantized": True,
        "quantization": "q5_0",
    },
    "large-v3-turbo-q5_0": {
        "size_mb": 1810,
        "multilingual": True,
        "params": "1550M",
        "quantized": True,
        "quantization": "q5_0",
    },
}

# Extract just the model names for convenience
AVAILABLE_MODELS = list(MODEL_INFO.keys())

# Group models by quantization for easier lookup
QUANTIZED_MODELS = {name: info for name, info in MODEL_INFO.items() if info["quantized"]}
STANDARD_MODELS = {name: info for name, info in MODEL_INFO.items() if not info["quantized"]}
DIARIZATION_MODELS = {
    name: info for name, info in MODEL_INFO.items() if info.get("diarization", False)
}
