## Quantization

`whisper.cpp` supports integer quantization of the Whisper `ggml` models.
Quantized models require less memory and disk space and depending on the hardware can be processed more efficiently.

### Benefits of Quantization

- **Reduced Disk Space**: Quantized models are significantly smaller than their full-precision counterparts, requiring less storage.
- **Lower Memory Requirements**: Quantized models use less RAM during inference.
- **Faster Processing**: Depending on the hardware, quantized models can often be processed more efficiently, resulting in faster transcription.
- **Mobile Compatibility**: Smaller, quantized models are more suitable for mobile and edge devices.

### Available Quantization Methods

`whisper.cpp` supports different quantization methods:

- **q5_0**: A 5-bit quantization method optimizing for model performance.
  - File size reduction: ~40% of original size
  - Good balance between accuracy and size
  - Recommended for large models (medium, large-v2, large-v3)
  
- **q5_1**: A 5-bit quantization method with slightly higher precision than q5_0.
  - File size reduction: ~40% of original size
  - Offers improved accuracy compared to q5_0
  - Good for all model sizes
  
- **q8_0**: An 8-bit quantization that preserves more accuracy at the cost of larger size.
  - File size reduction: ~65% of original size
  - Highest accuracy among quantized models
  - Recommended when accuracy is most important

### Pre-quantized Models

The following pre-quantized models are available for download:

| Model                 | Size (MB) | Languages     | Details |
|-----------------------|-----------|---------------|---------|
| tiny-q5_1             | 47        | Multilingual  | 39M parameters, q5_1 quantization |
| tiny.en-q5_1          | 47        | English only  | 39M parameters, q5_1 quantization |
| tiny-q8_0             | 75        | Multilingual  | 39M parameters, q8_0 quantization |
| base-q5_1             | 89        | Multilingual  | 74M parameters, q5_1 quantization |
| base.en-q5_1          | 89        | English only  | 74M parameters, q5_1 quantization |
| base-q8_0             | 142       | Multilingual  | 74M parameters, q8_0 quantization |
| small-q5_1            | 292       | Multilingual  | 244M parameters, q5_1 quantization |
| small.en-q5_1         | 292       | English only  | 244M parameters, q5_1 quantization |
| small-q8_0            | 466       | Multilingual  | 244M parameters, q8_0 quantization |
| medium-q5_0           | 938       | Multilingual  | 769M parameters, q5_0 quantization |
| medium.en-q5_0        | 938       | English only  | 769M parameters, q5_0 quantization |
| medium-q8_0           | 1500      | Multilingual  | 769M parameters, q8_0 quantization |
| medium.en-q8_0        | 1500      | English only  | 769M parameters, q8_0 quantization |
| large-v2-q5_0         | 1810      | Multilingual  | 1550M parameters, q5_0 quantization |
| large-v3-q5_0         | 1810      | Multilingual  | 1550M parameters, q5_0 quantization |
| large-v2-q8_0         | 2900      | Multilingual  | 1550M parameters, q8_0 quantization |
| large-v3-turbo-q5_0   | 1810      | Multilingual  | 1550M parameters, q5_0 quantization |
| large-v3-turbo-q8_0   | 2900      | Multilingual  | 1550M parameters, q8_0 quantization |

These pre-quantized models can be downloaded using the provided download script:

```bash
# Download a pre-quantized model (e.g., base.en-q5_1)
./models/download-ggml-model.sh base.en-q5_1
```

### Creating Your Own Quantized Models

If you prefer to quantize a model yourself, follow these steps:

```bash
# Build the quantize tool
cmake -B build
cmake --build build --config Release

# Quantize a model with Q5_0 method
./build/bin/quantize models/ggml-base.en.bin models/ggml-base.en-q5_0.bin q5_0

# Run the examples as usual, specifying the quantized model file
./build/bin/whisper-cli -m models/ggml-base.en-q5_0.bin ./samples/gb0.wav
```

### Choosing the Right Quantized Model

When selecting a quantized model, consider the following factors:

1. **Device Constraints**: For devices with limited resources, smaller models with higher quantization (e.g., tiny-q5_1) may be more appropriate.
   
2. **Accuracy Requirements**: If transcription accuracy is critical, consider using larger models or models with less aggressive quantization (e.g., medium-q8_0).

3. **Language Support**: Choose ".en" models for English-only applications for better performance, or multilingual models for other languages.

4. **Inference Speed**: Smaller, more heavily quantized models will generally offer faster inference times, which can be important for real-time applications.
