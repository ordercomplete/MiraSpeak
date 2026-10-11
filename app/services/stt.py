import os
import tempfile

from faster_whisper import WhisperModel
from app.core.config import settings


class STTService:
    """Локальний STT на faster-whisper. Працює і на CPU, і на CUDA."""

    def __init__(self):
        self._model: WhisperModel | None = None
        self._active_device: str = self._resolve_device()

    def _resolve_device(self) -> str:
        if settings.stt_device != "auto":
            return settings.stt_device
        try:
            import ctranslate2
            return "cuda" if ctranslate2.get_cuda_device_count() > 0 else "cpu"
        except Exception:
            return "cpu"

    def _resolve_compute_type(self, device: str) -> str:
        if settings.stt_compute_type != "auto":
            return settings.stt_compute_type
        return "float16" if device == "cuda" else "int8"

    @property
    def model(self) -> WhisperModel:
        if self._model is None:
            self._model = self._build_model(self._active_device)
        return self._model

    def _build_model(self, device: str) -> WhisperModel:
        compute = self._resolve_compute_type(device)
        model = WhisperModel(
            settings.whisper_model,
            device=device,
            compute_type=compute,
        )
        self._active_device = device
        return model

    def transcribe(self, audio_bytes: bytes, language: str = "en") -> str:
        with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as tmp:
            tmp.write(audio_bytes)
            tmp_path = tmp.name
        try:
            return self._transcribe_once(tmp_path, language)
        except Exception:
            # CUDA-бібліотеки (cublas/cudnn) можуть бути відсутні — відкочуємось на CPU,
            # щоб застосунок працював на будь-якій машині (включно з 6 GB VRAM / CPU-only).
            if self._active_device == "cuda":
                self._model = self._build_model("cpu")
                return self._transcribe_once(tmp_path, language)
            raise
        finally:
            os.unlink(tmp_path)

    def _transcribe_once(self, tmp_path: str, language: str) -> str:
        segments, _ = self.model.transcribe(
            tmp_path,
            language=language,
            beam_size=5,
            vad_filter=True,
        )
        return " ".join(s.text.strip() for s in segments).strip()


stt_service = STTService()
