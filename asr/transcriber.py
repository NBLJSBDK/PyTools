"""Tencent Cloud ASR — 一句话识别."""

import json, os, sys, base64
from pathlib import Path

S = Path(__file__).parent


def load_keys(key_index: int = 0, key_file: str = None):
    """Load API keys from api_keys.json."""
    kf = key_file or str(S / 'api_keys.json')
    if not os.path.exists(kf):
        print(f"ERROR: {kf} not found. Copy api_keys.json.example and fill in your keys.")
        sys.exit(1)
    with open(kf) as f:
        keys = json.load(f)
    if key_index >= len(keys):
        print(f"ERROR: key index {key_index} out of range (have {len(keys)} keys).")
        sys.exit(1)
    return keys[key_index]


def transcribe_one(wav_path: str, key_profile: dict, dialect: str = 'mandarin', retry: int = 2) -> dict:
    """Transcribe a single audio chunk (≤60s, 16kHz mono WAV).

    Returns dict with keys: text, start_ms, end_ms, error (if any).
    """
    from tencentcloud.common import credential
    from tencentcloud.common.exception.tencent_cloud_sdk_exception import TencentCloudSDKException
    from tencentcloud.asr.v20190614 import asr_client, models

    ENGINE_MAP = {
        'mandarin':  '16k_zh',
        'canton':    '16k_zh_dialect',
        'sichuan':   '16k_zh_dialect',
        'shanghai':  '16k_zh_dialect',
        'nanjing':   '16k_zh_dialect',
        'hakka':     '16k_zh_dialect',
        'minnan':    '16k_zh_dialect',
    }
    DIALECT_ID = {'canton': 1, 'sichuan': 2, 'shanghai': 3, 'nanjing': 4, 'hakka': 5, 'minnan': 6}

    APP_ID = str(key_profile['app_id'])
    cred = credential.Credential(
        key_profile['secret_id'],
        key_profile['secret_key']
    )
    client = asr_client.AsrClient(cred, 'ap-guangzhou')

    # Read and base64-encode audio
    with open(wav_path, 'rb') as f:
        audio_data = base64.b64encode(f.read()).decode('utf-8')
    audio_size = len(audio_data)

    req = models.SentenceRecognitionRequest()
    req.EngSerViceType = ENGINE_MAP.get(dialect, '16k_zh')
    req.SourceType = 1                   # raw base64 data, no URL
    req.VoiceFormat = 'wav'
    req.Data = audio_data
    req.DataLen = audio_size

    # Set dialect type for dialect engines
    if dialect in DIALECT_ID:
        req.HotwordId = None
        # DialectType is set via a separate field
        # Note: SentenceRecognition may not support DialectType directly;
        # if not, fall back to 16k_zh with no dialect

    for attempt in range(retry):
        try:
            resp = client.SentenceRecognition(req)
            text = resp.Result or ''
            return {'text': text.strip(), 'error': None}
        except TencentCloudSDKException as e:
            if attempt < retry - 1:
                continue
            return {'text': '', 'error': str(e)}
        except Exception as e:
            return {'text': '', 'error': str(e)}

    return {'text': '', 'error': 'max retries exceeded'}


def transcribe_all(chunks: list, key_profile: dict, dialect: str = 'mandarin') -> list:
    """Transcribe all chunks, returning list with timing info."""
    results = []
    for i, (chunk_path, start_offset) in enumerate(chunks):
        print(f'  [{i+1}/{len(chunks)}] {Path(chunk_path).name} ...', end=' ', flush=True)
        r = transcribe_one(chunk_path, key_profile, dialect)
        r['start_offset'] = start_offset
        r['chunk_path'] = chunk_path
        if r['error']:
            print(f'✗ {r["error"][:60]}')
        else:
            print(f'✓ {len(r["text"])} chars')
        results.append(r)
    return results
