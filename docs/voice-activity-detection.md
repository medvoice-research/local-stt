## Voice Activity Detection (VAD)
Support for Voice Activity Detection (VAD) can be enabled using the `--vad`
argument to `whisper-cli`. In addition to this option a VAD model is also
required.

The way this works is that first the audio samples are passed through
the VAD model which will detect speech segments. Using this information the
only the speech segments that are detected are extracted from the original audio
input and passed to whisper for processing. This reduces the amount of audio
data that needs to be processed by whisper and can significantly speed up the
transcription process.

The following VAD models are currently supported:

### Silero-VAD
[Silero-vad](https://github.com/snakers4/silero-vad) is a lightweight VAD model
written in Python that is fast and accurate.

This model can be converted to ggml using the following command:
```console
$ python3 -m venv venv && source venv/bin/activate
$ (venv) pip install silero-vad
$ (venv) $ python models/convert-silero-vad-to-ggml.py --output models/silero.bin
Saving GGML Silero-VAD model to models/silero-v5.1.2-ggml.bin
```
And it can then be used with whisper as follows:
```console
$ ./build/bin/whisper-cli \
   --file ./samples/jfk.wav \
   --model ./models/ggml-base.en.bin \
   --vad \
   --vad-model ./models/silero-v5.1.2-ggml.bin
```

### VAD Options

* --vad-threshold: Threshold probability for speech detection. A probability
for a speech segment/frame above this threshold will be considered as speech.

* --vad-min-speech-duration-ms: Minimum speech duration in milliseconds. Speech
segments shorter than this value will be discarded to filter out brief noise or
false positives.

* --vad-min-silence-duration-ms: Minimum silence duration in milliseconds. Silence
periods must be at least this long to end a speech segment. Shorter silence
periods will be ignored and included as part of the speech.

* --vad-max-speech-duration-s: Maximum speech duration in seconds. Speech segments
longer than this will be automatically split into multiple segments at silence
points exceeding 98ms to prevent excessively long segments.

* --vad-speech-pad-ms: Speech padding in milliseconds. Adds this amount of padding
before and after each detected speech segment to avoid cutting off speech edges.

* --vad-samples-overlap: Amount of audio to extend from each speech segment into
the next one, in seconds (e.g., 0.10 = 100ms overlap). This ensures speech isn't
cut off abruptly between segments when they're concatenated together.