## OpenVINO support

On platforms that support [OpenVINO](https://github.com/openvinotoolkit/openvino), the Encoder inference can be executed
on OpenVINO-supported devices including x86 CPUs and Intel GPUs (integrated & discrete).

This can result in significant speedup in encoder performance. Here are the instructions for generating the OpenVINO model and using it with `whisper.cpp`:

- First, setup python virtual env. and install python dependencies. Python 3.10 is recommended.

 Linux and macOS:

  ```bash
  cd models
  python3 -m venv openvino_conv_env
  source openvino_conv_env/bin/activate
  python -m pip install --upgrade pip
  pip install -r requirements-openvino.txt
  ```

- Generate an OpenVINO encoder model. For example, to generate a `base.en` model, use:

  ```
  python convert-whisper-to-openvino.py --model base.en
  ```

  This will produce ggml-base.en-encoder-openvino.xml/.bin IR model files. It's recommended to relocate these to the same folder as `ggml` models, as that
  is the default location that the OpenVINO extension will search at runtime.

- Build `whisper.cpp` with OpenVINO support:

  Download OpenVINO package from [release page](https://github.com/openvinotoolkit/openvino/releases). The recommended version to use is [2024.6.0](https://github.com/openvinotoolkit/openvino/releases/tag/2024.6.0). Ready to use Binaries of the required libraries can be found in the [OpenVino Archives](https://storage.openvinotoolkit.org/repositories/openvino/packages/2024.6/)

  After downloading & extracting package onto your development system, set up required environment by sourcing setupvars script. For example:

  Linux:

  ```bash
  source /path/to/l_openvino_toolkit_ubuntu22_2023.0.0.10926.b4452d56304_x86_64/setupvars.sh
  ```

   And then build the project using cmake:

  ```bash
  cmake -B build -DWHISPER_OPENVINO=1
  cmake --build build -j --config Release
  ```

- Run the examples as usual. For example:

  ```text
  $ ./build/bin/whisper-cli -m models/ggml-base.en.bin -f samples/jfk.wav

  ...

  whisper_ctx_init_openvino_encoder: loading OpenVINO model from 'models/ggml-base.en-encoder-openvino.xml'
  whisper_ctx_init_openvino_encoder: first run on a device may take a while ...
  whisper_openvino_init: path_model = models/ggml-base.en-encoder-openvino.xml, device = GPU, cache_dir = models/ggml-base.en-encoder-openvino-cache
  whisper_ctx_init_openvino_encoder: OpenVINO model loaded

  system_info: n_threads = 4 / 8 | AVX = 1 | AVX2 = 1 | AVX512 = 0 | FMA = 1 | NEON = 0 | ARM_FMA = 0 | F16C = 1 | FP16_VA = 0 | WASM_SIMD = 0 | BLAS = 0 | SSE3 = 1 | VSX = 0 | COREML = 0 | OPENVINO = 1 |

  ...
  ```

  The first time run on an OpenVINO device is slow, since the OpenVINO framework will compile the IR (Intermediate Representation) model to a device-specific 'blob'. This device-specific blob will get
  cached for the next run.

For more information about the OpenVINO implementation please refer to PR [#1037](https://github.com/ggml-org/whisper.cpp/pull/1037).