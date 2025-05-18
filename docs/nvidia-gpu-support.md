## NVIDIA GPU support

With NVIDIA cards the processing of the models is done efficiently on the GPU via cuBLAS and custom CUDA kernels.
First, make sure you have installed `cuda`: https://developer.nvidia.com/cuda-downloads

Now build `whisper.cpp` with CUDA support:

```
cmake -B build -DGGML_CUDA=1
cmake --build build -j --config Release
```

or for newer NVIDIA GPU's (RTX 5000 series):
```
cmake -B build -DGGML_CUDA=1 -DCMAKE_CUDA_ARCHITECTURES="86"
cmake --build build -j --config Release
```