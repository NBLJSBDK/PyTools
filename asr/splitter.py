"""Audio splitter: use ffmpeg silencedetect to find natural break points.

Performance: 2-pass approach for long files.
  Pass 1: decode+resample entire file to 16kHz mono WAV (1 ffmpeg call)
  Pass 2: split the WAV at boundaries (1 ffmpeg call, -c copy)
Previously 77 chunks = 77 ffmpeg calls; now always 2 calls.
"""

import subprocess, os, re, time
from pathlib import Path

FFMPEG  = '/mnt/c/Program Files/FFmpeg/ffmpeg-master-latest-win64-gpl-shared/bin/ffmpeg.exe'
FFPROBE = '/mnt/c/Program Files/FFmpeg/ffmpeg-master-latest-win64-gpl-shared/bin/ffprobe.exe'
FFMPEG  = FFMPEG if os.path.exists(FFMPEG) else 'ffmpeg'
FFPROBE = FFPROBE if os.path.exists(FFPROBE) else 'ffprobe'
MAX_CHUNK_SEC = 55  # leave 5s margin below 60s API limit


def _to_win(path: str) -> str:
    """Convert WSL path to Windows path for ffmpeg."""
    try:
        return subprocess.check_output(['wslpath', '-w', path]).decode().strip()
    except Exception:
        return path


def get_duration(wav_path: str) -> float:
    """Get audio duration in seconds via ffprobe."""
    cmd = [FFPROBE, '-show_entries', 'format=duration',
           '-of', 'default=noprint_wrappers=1:nokey=1', _to_win(wav_path)]
    r = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
    return float(r.stdout.strip())


def _guess_noise_db(wav_path: str) -> int:
    """Estimate a reasonable noise floor based on audio mean volume.

    Returns a dB value suitable for silencedetect.
    Rule of thumb: noise threshold = mean_volume + 15dB, clamped to [-35, -15].
    """
    cmd = [
        FFMPEG, '-i', _to_win(wav_path),
        '-af', 'volumedetect', '-f', 'null', '-'
    ]
    r = subprocess.run(cmd, capture_output=True, text=True, timeout=60)
    mean_db = 0
    for line in r.stderr.split('\n'):
        m = re.search(r'mean_volume:\s*(-?[\d.]+)\s*dB', line)
        if m:
            mean_db = float(m.group(1))
            break
    noise_db = int(mean_db + 15)
    noise_db = max(-35, min(-15, noise_db))
    return noise_db


def detect_silence_points(wav_path: str, min_silence: float = 1.5, db: int = None) -> list:
    """Find silence regions using ffmpeg silencedetect.

    Returns list of (start_sec, end_sec) tuples for each silence region.
    db: noise threshold in dB. If None, auto-detect from audio level.
    """
    if db is None:
        db = _guess_noise_db(wav_path)

    cmd = [
        FFMPEG, '-i', _to_win(wav_path),
        '-af', f'silencedetect=noise={db}dB:d={min_silence}',
        '-f', 'null', '-'
    ]
    r = subprocess.run(cmd, capture_output=True, text=True, timeout=300)

    pairs = []
    for line in r.stderr.split('\n'):
        m_start = re.search(r'silence_start:\s*([\d.]+)', line)
        m_end   = re.search(r'silence_end:\s*([\d.]+)', line)
        if m_start:
            pairs.append([float(m_start.group(1)), None])
        if m_end and pairs:
            for p in reversed(pairs):
                if p[1] is None:
                    p[1] = float(m_end.group(1))
                    break
    return [(s, e) for s, e in pairs if e is not None]


def _transcode_one(src: str, dst: str, t_start: float, duration: float):
    """Transcode a single audio segment (16kHz mono PCM WAV). Used for short files."""
    cmd = [
        FFMPEG, '-y', '-ss', str(t_start), '-t', str(duration),
        '-i', _to_win(src),
        '-ac', '1', '-ar', '16000',
        '-c:a', 'pcm_s16le',
        _to_win(dst)
    ]
    subprocess.run(cmd, capture_output=True, timeout=120)


def _split_full_wav(full_wav: str, output_dir: str, stem: str,
                    seg_times: list, chunks: list) -> list:
    """Split a full 16kHz WAV into segments using ffmpeg segment muxer (-c copy).

    Returns list of (chunk_path, start_offset_sec).
    """
    if not seg_times:
        # Single chunk: just rename/copy the full WAV
        dst = Path(output_dir) / f'{stem}_000.wav'
        if not dst.exists():
            os.rename(full_wav, str(dst))
        else:
            os.remove(full_wav)
        return [(str(dst), chunks[0][0])]

    cmd = [
        FFMPEG, '-y', '-i', _to_win(full_wav),
        '-f', 'segment', '-segment_times', ','.join(seg_times),
        '-c', 'copy', '-reset_timestamps', '1',
        _to_win(str(Path(output_dir) / f'{stem}_%03d.wav'))
    ]
    subprocess.run(cmd, capture_output=True, timeout=300)

    results = []
    for i, (t_start, t_end) in enumerate(chunks):
        dst = Path(output_dir) / f'{stem}_{i:03d}.wav'
        if dst.exists():
            results.append((str(dst), t_start))
        else:
            print(f'  ⚠ 缺失: {dst.name}')
    return results


def smart_split(wav_path: str, output_dir: str, max_sec: int = MAX_CHUNK_SEC) -> list:
    """Split audio at natural pauses, each chunk ≤ max_sec.

    Returns list of (chunk_path, start_offset_sec).
    Long files: 2-pass (decode full → segment copy).
    Short files: single transcode.
    """
    duration = get_duration(wav_path)
    os.makedirs(output_dir, exist_ok=True)
    stem = Path(wav_path).stem

    if duration <= max_sec:
        print(f'  🔇 ≤{max_sec}s, 直接转码...')
        dst = Path(output_dir) / f'{stem}_000.wav'
        if not dst.exists():
            _transcode_one(wav_path, str(dst), 0, duration)
        return [(str(dst), 0.0)]

    # ── Phase 0: detect silence ──
    print(f'  🔇 分析静音点 (总长 {duration:.0f}s)...', end=' ', flush=True)
    t0 = time.time()
    silences = detect_silence_points(wav_path, min_silence=1.5)
    print(f'{len(silences)} 个静音区 ({time.time()-t0:.1f}s)')

    if not silences:
        print('  ⚠ 未检测到静音，使用固定切分')
        return _fixed_split(wav_path, output_dir, max_sec)

    # ── Phase 1: build chunk boundaries ──
    boundaries = [0.0]
    for s_start, s_end in silences:
        mid = (s_start + s_end) / 2
        if mid - boundaries[-1] >= 15:
            boundaries.append(mid)
    boundaries.append(duration)

    chunks = []
    start = boundaries[0]
    for i in range(1, len(boundaries)):
        end = boundaries[i]
        if end - start > max_sec:
            sub_boundaries = [start]
            t = start + max_sec
            while t < end:
                sub_boundaries.append(t)
                t += max_sec
            sub_boundaries.append(end)
            for j in range(len(sub_boundaries) - 1):
                chunks.append((sub_boundaries[j], sub_boundaries[j+1]))
        else:
            if chunks and (end - chunks[-1][0]) <= max_sec:
                chunks[-1] = (chunks[-1][0], end)
            else:
                chunks.append((start, end))
        start = end

    seg_times = [f'{chunks[i][1]:.3f}' for i in range(len(chunks) - 1)]
    total_dur = sum(e - s for s, e in chunks)
    print(f'  ✂ 切分为 {len(chunks)} 段 (累计 {total_dur:.0f}s)')

    # ── Phase 2: decode full file to 16kHz mono WAV ──
    tmp_wav = str(Path(output_dir) / f'{stem}_full.wav')
    print(f'  🎶 解码+重采样 (16kHz mono)...', end=' ', flush=True)
    t0 = time.time()
    cmd_decode = [
        FFMPEG, '-y', '-i', _to_win(wav_path),
        '-ac', '1', '-ar', '16000',
        '-c:a', 'pcm_s16le',
        _to_win(tmp_wav)
    ]
    subprocess.run(cmd_decode, capture_output=True, timeout=600)
    print(f'{time.time()-t0:.1f}s')

    # ── Phase 3: split the WAV at boundaries ──
    print(f'  ✂ 按静音点切分 (segment muxer)...', end=' ', flush=True)
    t0 = time.time()
    results = _split_full_wav(tmp_wav, output_dir, stem, seg_times, chunks)
    print(f'{time.time()-t0:.1f}s')

    # Clean up temp full WAV
    Path(tmp_wav).unlink(missing_ok=True)

    return results


def _fixed_split(wav_path: str, output_dir: str, max_sec: int) -> list:
    """Fallback: split into fixed-size chunks (2-pass: decode → segment)."""
    duration = get_duration(wav_path)
    stem = Path(wav_path).stem
    n_chunks = int(duration / max_sec) + (1 if duration % max_sec > 0 else 0)
    print(f'  ✂ 固定切分 {n_chunks} 段 (每段≤{max_sec}s)')

    # Decode full file
    tmp_wav = str(Path(output_dir) / f'{stem}_full.wav')
    cmd_decode = [
        FFMPEG, '-y', '-i', _to_win(wav_path),
        '-ac', '1', '-ar', '16000',
        '-c:a', 'pcm_s16le',
        _to_win(tmp_wav)
    ]
    subprocess.run(cmd_decode, capture_output=True, timeout=600)

    # Split via segment muxer
    cmd_split = [
        FFMPEG, '-y', '-i', _to_win(tmp_wav),
        '-f', 'segment', '-segment_time', str(max_sec),
        '-c', 'copy', '-reset_timestamps', '1',
        _to_win(str(Path(output_dir) / f'{stem}_%03d.wav'))
    ]
    subprocess.run(cmd_split, capture_output=True, timeout=300)

    results = []
    t = 0.0
    i = 0
    while t < duration:
        dst = Path(output_dir) / f'{stem}_{i:03d}.wav'
        if dst.exists():
            results.append((str(dst), t))
            t += max_sec
            i += 1
        else:
            break

    Path(tmp_wav).unlink(missing_ok=True)
    return results
