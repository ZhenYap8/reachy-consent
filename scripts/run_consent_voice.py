#!/usr/bin/env python3
"""Voice consent walkthrough using the state machine + OpenAI TTS/STT + Reachy audio."""

from __future__ import annotations

import argparse
import io
import json
import logging
import os
import sys
import time
import wave
from pathlib import Path

import numpy as np
from openai import OpenAI
from scipy.signal import resample

from engine import VoiceConsentBridge, load_consent_pack
from engine.state_machine import PatientResponse, classify_response
from engine.voice_cues import (
    cue_for_phase,
    nod_confirm,
    set_listening,
    set_ready,
    set_speaking,
    set_thinking,
)

logger = logging.getLogger("consent_voice")

TTS_MODEL = "gpt-4o-mini-tts"
TTS_VOICE = "marin"
WHISPER_MODEL = "whisper-1"
PCM_SAMPLE_RATE = 24_000


def _setup_logging(debug: bool) -> None:
    logging.basicConfig(
        level=logging.DEBUG if debug else logging.INFO,
        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    )


def _load_dotenv(root: Path) -> None:
    env_file = root / ".env"
    if not env_file.exists():
        return
    for line in env_file.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, _, value = line.partition("=")
        key = key.strip()
        value = value.strip().strip('"').strip("'")
        os.environ.setdefault(key, value)


def _pcm_to_wav_bytes(pcm: bytes, sample_rate: int = PCM_SAMPLE_RATE) -> bytes:
    buf = io.BytesIO()
    with wave.open(buf, "wb") as wf:
        wf.setnchannels(1)
        wf.setsampwidth(2)
        wf.setframerate(sample_rate)
        wf.writeframes(pcm)
    return buf.getvalue()


def _float32_mono(chunk: np.ndarray) -> np.ndarray:
    if chunk.ndim == 2:
        if chunk.shape[1] > chunk.shape[0]:
            chunk = chunk.T
        if chunk.shape[1] > 1:
            chunk = chunk[:, 0]
    if chunk.dtype == np.int16:
        return chunk.astype(np.float32) / 32768.0
    return chunk.astype(np.float32)


def speak_text(client: OpenAI, reachy, text: str) -> None:
    """Synthesize text with OpenAI TTS and play through Reachy media."""
    if not text.strip():
        return

    set_speaking(reachy)
    response = client.audio.speech.create(
        model=TTS_MODEL,
        voice=TTS_VOICE,
        input=text.strip(),
        response_format="pcm",
    )
    pcm = response.content
    samples = np.frombuffer(pcm, dtype=np.int16).astype(np.float32) / 32768.0

    output_sr = reachy.media.get_output_audio_samplerate()
    if output_sr != PCM_SAMPLE_RATE:
        n_out = int(len(samples) * output_sr / PCM_SAMPLE_RATE)
        samples = resample(samples, n_out).astype(np.float32)

    chunk_size = max(output_sr // 20, 1)
    for idx in range(0, len(samples), chunk_size):
        reachy.media.push_audio_sample(samples[idx : idx + chunk_size])
        time.sleep(len(samples[idx : idx + chunk_size]) / output_sr * 0.85)


def _chunk_rms(chunk: np.ndarray) -> float:
    mono = _float32_mono(chunk)
    if mono.size == 0:
        return 0.0
    return float(np.sqrt(np.mean(mono.astype(np.float64) ** 2)))


def record_utterance(
    reachy,
    *,
    silence_threshold: float = 0.015,
    silence_seconds: float = 1.2,
    max_seconds: float = 20.0,
    chunk_seconds: float = 0.25,
) -> np.ndarray | None:
    """Record from Reachy mic until the patient stops speaking."""
    input_sr = reachy.media.get_input_audio_samplerate()
    set_listening(reachy)

    chunks: list[np.ndarray] = []
    silent_time = 0.0
    speech_started = False
    elapsed = 0.0

    while elapsed < max_seconds:
        sample = reachy.media.get_audio_sample()
        if sample is None:
            time.sleep(0.05)
            elapsed += 0.05
            continue

        mono = _float32_mono(sample)
        chunks.append(mono)
        rms = _chunk_rms(mono)
        elapsed += chunk_seconds

        if rms >= silence_threshold:
            speech_started = True
            silent_time = 0.0
        elif speech_started:
            silent_time += chunk_seconds
            if silent_time >= silence_seconds:
                break

    if not speech_started or not chunks:
        return None

    audio = np.concatenate(chunks)
    if input_sr != 16_000:
        n_out = int(len(audio) * 16_000 / input_sr)
        audio = resample(audio, n_out).astype(np.float32)
    return audio


def transcribe(client: OpenAI, audio: np.ndarray) -> str:
    """Transcribe float32 mono audio at 16 kHz."""
    pcm = (np.clip(audio, -1.0, 1.0) * 32767).astype(np.int16).tobytes()
    wav_bytes = _pcm_to_wav_bytes(pcm, sample_rate=16_000)
    result = client.audio.transcriptions.create(
        model=WHISPER_MODEL,
        file=("patient.wav", wav_bytes, "audio/wav"),
    )
    return (result.text or "").strip()


def run_voice_session(
    bridge: VoiceConsentBridge,
    client: OpenAI,
    reachy,
    *,
    text_only: bool = False,
) -> None:
    """Main voice loop."""
    events = bridge.start()

    while events:
        for event in events:
            logger.info("[%s] %s", event.phase.name, event.text[:120])
            cue_for_phase(reachy, event.phase)

            if text_only:
                print(f"\n[ROBOT · {event.phase.name}]\n{event.text}\n")
            else:
                speak_text(client, reachy, event.text)

        if bridge.is_finished:
            break

        if bridge.waits_for_patient:
            if text_only:
                transcript = input("[PATIENT] ").strip()
            else:
                set_listening(reachy)
                logger.info("Listening for patient...")
                audio = record_utterance(reachy)
                if audio is None:
                    logger.warning("No speech detected — asking again.")
                    events = bridge.handle_patient_transcript("")
                    continue

                set_thinking(reachy)
                transcript = transcribe(client, audio)
                logger.info("Patient said: %s", transcript)

            response_kind = classify_response(transcript)
            if response_kind == PatientResponse.CONFIRM and not text_only:
                nod_confirm(reachy)

            events = bridge.handle_patient_transcript(transcript)
        else:
            set_ready(reachy)
            events = bridge.events_after_robot_spoke()

    set_ready(reachy)


def run_demo(
    pack_path: Path,
    export_path: Path | None,
    *,
    no_robot: bool = False,
    media_backend: str | None = None,
    debug: bool = False,
) -> None:
    _setup_logging(debug)
    root = pack_path.resolve().parents[1] if pack_path.name.endswith(".yaml") else Path(__file__).resolve().parents[1]
    _load_dotenv(root)

    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        logger.error("OPENAI_API_KEY is required. Set it in the environment or .env file.")
        sys.exit(1)

    client = OpenAI(api_key=api_key)
    pack = load_consent_pack(pack_path)
    bridge = VoiceConsentBridge(pack)

    print(f"\n=== Voice Consent: {pack.title} ===\n")

    if no_robot:
        run_voice_session(bridge, client, reachy=_NullReachy(), text_only=True)
    else:
        from reachy_mini import ReachyMini

        kwargs: dict = {}
        if media_backend:
            kwargs["media_backend"] = media_backend

        with ReachyMini(**kwargs) as reachy:
            reachy.media.start_playing()
            time.sleep(0.3)
            run_voice_session(bridge, client, reachy, text_only=False)
            reachy.media.stop_playing()

    print("\n=== Session summary ===")
    print(json.dumps(bridge.session.to_dict(), indent=2))

    if export_path:
        export_path.parent.mkdir(parents=True, exist_ok=True)
        export_path.write_text(json.dumps(bridge.session.to_dict(), indent=2), encoding="utf-8")
        print(f"\nExported to {export_path}")


class _NullReachy:
    """Stub for --no-robot text-only mode."""

    class media:
        @staticmethod
        def get_output_audio_samplerate() -> int:
            return PCM_SAMPLE_RATE

        @staticmethod
        def get_input_audio_samplerate() -> int:
            return 16_000

        @staticmethod
        def start_playing() -> None:
            pass

        @staticmethod
        def stop_playing() -> None:
            pass

        @staticmethod
        def push_audio_sample(_: np.ndarray) -> None:
            pass

        @staticmethod
        def get_audio_sample() -> None:
            return None


def main() -> None:
    root = Path(__file__).resolve().parents[1]
    parser = argparse.ArgumentParser(description="Run voice consent session with Reachy Mini")
    parser.add_argument(
        "--pack",
        type=Path,
        default=root / "consent_packs" / "lap_chole.yaml",
    )
    parser.add_argument(
        "--export",
        type=Path,
        default=root / "sessions" / "last_voice_session.json",
    )
    parser.add_argument(
        "--no-robot",
        action="store_true",
        help="Text-only mode (no Reachy connection; uses keyboard input)",
    )
    parser.add_argument(
        "--media-backend",
        choices=["default", "no_media", "gstreamer"],
        default=None,
        help="ReachyMini media backend (use no_media for faster sim connect)",
    )
    parser.add_argument("--debug", action="store_true")
    args = parser.parse_args()

    run_demo(
        args.pack,
        args.export,
        no_robot=args.no_robot,
        media_backend=args.media_backend,
        debug=args.debug,
    )


if __name__ == "__main__":
    main()
