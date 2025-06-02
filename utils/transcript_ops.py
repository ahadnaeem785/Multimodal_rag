from faster_whisper import WhisperModel


def transcribe_audio(audio_path, file_hash, chunk_duration=60):
    model = WhisperModel("base", compute_type="int8")
    segments, _ = model.transcribe(audio_path)
    texts, metadatas, transcript = [], [], []
    current_chunk, current_start, current_end = "", None, None

    def format_timestamp(start, end):
        def sec_to_time(sec):
            m, s = divmod(int(sec), 60)
            return f"{m:02}:{s:02}"
        return f"[{sec_to_time(start)} - {sec_to_time(end)}]"

    for seg in segments:
        transcript.append({"text": seg.text.strip(), "start": seg.start})
        if current_start is None:
            current_start = seg.start
        current_chunk += seg.text.strip() + " "
        current_end = seg.end
        if current_end - current_start >= chunk_duration:
            metadata = {"type": "video", "start": current_start, "end": current_end, "source": audio_path, "hash": file_hash}
            chunk_with_meta = f"{format_timestamp(current_start, current_end)} {current_chunk.strip()}"
            texts.append(chunk_with_meta)
            metadatas.append(metadata)
            current_chunk, current_start = "", None
    if current_chunk:
        metadata = {"type": "video", "start": current_start, "end": current_end, "source": audio_path, "hash": file_hash}
        chunk_with_meta = f"{format_timestamp(current_start, current_end)} {current_chunk.strip()}"
        texts.append(chunk_with_meta)
        metadatas.append(metadata)
    return texts, metadatas, transcript
