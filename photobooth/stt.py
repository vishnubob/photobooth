import time
from datetime import datetime
import collections, queue, os, os.path
import deepspeech
import numpy as np
import pyaudio
import webrtcvad
from scipy import signal
from . logger import logger

class Audio(object):
    """Streams raw audio from microphone. Data is received in a separate thread, and stored in a buffer, to be read from."""

    FORMAT = pyaudio.paInt16
    # Network/VAD rate-space
    RATE_PROCESS = 16000
    CHANNELS = 1
    BLOCKS_PER_SECOND = 50

    def __init__(self, callback=None, device=None, input_rate=RATE_PROCESS):
        def proxy_callback(in_data, frame_count, time_info, status):
            callback(in_data)
            return (None, pyaudio.paContinue)
        if callback is None: callback = lambda in_data: self.buffer_queue.put(in_data)
        self.buffer_queue = queue.Queue()
        self.device = device
        self.input_rate = input_rate
        self.sample_rate = self.RATE_PROCESS
        self.block_size = int(self.RATE_PROCESS / float(self.BLOCKS_PER_SECOND))
        self.block_size_input = int(self.input_rate / float(self.BLOCKS_PER_SECOND))
        self.pa = pyaudio.PyAudio()

        kwargs = {
            'format': self.FORMAT,
            'channels': self.CHANNELS,
            'rate': self.input_rate,
            'input': True,
            'frames_per_buffer': self.block_size_input,
            'stream_callback': proxy_callback,
        }

        # if not default device
        if self.device:
            kwargs['input_device_index'] = self.device
        self.kwargs = kwargs

    def resample(self, data, input_rate):
        """
        Microphone may not support our native processing sampling rate, so
        resample from input_rate to RATE_PROCESS here for webrtcvad and
        deepspeech

        Args:
            data (binary): Input audio stream
            input_rate (int): Input audio rate to resample from
        """
        data16 = np.fromstring(string=data, dtype=np.int16)
        resample_size = int(len(data16) / self.input_rate * self.RATE_PROCESS)
        resample = signal.resample(data16, resample_size)
        resample16 = np.array(resample, dtype=np.int16)
        return resample16.tostring()

    def read_resampled(self):
        """Return a block of audio data resampled to 16000hz, blocking if necessary."""
        return self.resample(data=self.buffer_queue.get(),
                             input_rate=self.input_rate)

    def read(self):
        """Return a block of audio data, blocking if necessary."""
        return self.buffer_queue.get()

    def start_stream(self):
        self.stream = self.pa.open(**self.kwargs)
        self.stream.start_stream()

    def stop_stream(self):
        self.stream.stop_stream()
        self.stream.close()

    def destroy(self):
        self.stop_stream()
        self.pa.terminate()

    frame_duration_ms = property(lambda self: 1000 * self.block_size // self.sample_rate)

class VADAudio(Audio):
    """Filter & segment audio with voice activity detection."""

    def __init__(self, aggressiveness=3, device=None, input_rate=None):
        super().__init__(device=device, input_rate=input_rate)
        self.vad = webrtcvad.Vad(aggressiveness)

    def frame_generator(self):
        """Generator that yields all audio frames from microphone."""
        if self.input_rate == self.RATE_PROCESS:
            while True:
                yield self.read()
        else:
            while True:
                yield self.read_resampled()

    def vad_collector(self, padding_ms=300, ratio=0.75, frames=None):
        """Generator that yields series of consecutive audio frames comprising each utterence, separated by yielding a single None.
            Determines voice activity by ratio of frames in padding_ms. Uses a buffer to include padding_ms prior to being triggered.
            Example: (frame, ..., frame, None, frame, ..., frame, None, ...)
                      |---utterence---|        |---utterence---|
        """
        self.start_stream()
        if frames is None: frames = self.frame_generator()
        num_padding_frames = padding_ms // self.frame_duration_ms
        ring_buffer = collections.deque(maxlen=num_padding_frames)
        triggered = False

        for frame in frames:
            is_speech = self.vad.is_speech(frame, self.sample_rate)

            if not triggered:
                ring_buffer.append((frame, is_speech))
                num_voiced = len([f for f, speech in ring_buffer if speech])
                if num_voiced > ratio * ring_buffer.maxlen:
                    triggered = True
                    for f, s in ring_buffer:
                        yield f
                    ring_buffer.clear()

            else:
                yield frame
                ring_buffer.append((frame, is_speech))
                num_unvoiced = len([f for f, speech in ring_buffer if not speech])
                if num_unvoiced > ratio * ring_buffer.maxlen:
                    triggered = False
                    ring_buffer.clear()
                    break
        self.stop_stream()

DefaultConfig = {
    "model_dir": "model",
    "beam_width": 500,
    "sample_rate": 16000,
    "lm_alpha": 0.75,
    "lm_beta": 1.85,
    "n_features": 26,
    "n_context": 9,
    "vad_aggressiveness": 3,
    "device": None,
}

class SpeechToText(object):
    def __init__(self, config=None):
        self.config = config if config is not None else DefaultConfig
        self.init_model()

    def init_model(self):
        model_dir = self.config["model_dir"]
        model = os.path.join(model_dir, 'output_graph.pb')
        alphabet = os.path.join(model_dir, 'alphabet.txt')
        lm = os.path.join(model_dir, "lm.binary")
        trie = os.path.join(model_dir, "trie")

        logger.info('Initializing deepspeech model...')
        self.model = deepspeech.Model(
            model, 
            self.config["n_features"], 
            self.config["n_context"], 
            alphabet, 
            self.config["beam_width"]
        )
        self.model.enableDecoderWithLM(alphabet, lm, trie, self.config["lm_alpha"], self.config["lm_beta"])

    def listen(self):
        vad_audio = VADAudio(aggressiveness=self.config["vad_aggressiveness"],
                             device=self.config["device"],
                             input_rate=self.config["sample_rate"])
        frames = vad_audio.vad_collector()
        stream_context = self.model.setupStream()
        for frame in frames:
            logger.debug("streaming frame")
            self.model.feedAudioContent(stream_context, np.frombuffer(frame, np.int16))
        logger.debug("end utterence")
        text = self.model.finishStream(stream_context)
        logger.debug("Recognized: %s" % text)
        return text
