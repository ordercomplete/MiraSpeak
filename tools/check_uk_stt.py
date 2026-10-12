import asyncio
import io
import sys

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
sys.path.insert(0, ".")
from app.services import stt_service, tts_service


def main():
    # Real Ukrainian audio via the Ukrainian voice, then transcribe with auto-detect.
    audio = asyncio.run(tts_service.synthesize("Привіт, я вивчаю англійську мову.", "uk"))
    txt = stt_service.transcribe(audio, "auto")
    print("TX:", txt)
    cyr = sum(1 for c in txt if "\u0400" <= c < "\u04ff")
    print("CYRILLIC_CHARS:", cyr)
    if cyr < 10:
        print("FAIL: Ukrainian not recognized (looks like garbage/English)")
        sys.exit(1)
    print("UK STT OK")


if __name__ == "__main__":
    main()
