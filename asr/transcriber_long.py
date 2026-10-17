"""Tencent Cloud ASR — 录音文件识别（说话人分离支持）.

Usage:
    recognize_long_audio(wav_path, key_profile, speaker_count=2)

File < 3MB  → SourceType=1 (base64, 直传)
File ≥ 3MB  → SourceType=0 (COS URL, 需配 cos_bucket / cos_region)
"""

import json, os, sys, base64, time
from pathlib import Path

S = Path(__file__).parent
COS_SIZE_LIMIT = 3 * 1024 * 1024  # 3MB


def load_keys(key_index: int = 0, key_file: str = None):
    kf = key_file or str(S / 'api_keys.json')
    if not os.path.exists(kf):
        print(f"ERROR: {kf} not found.")
        sys.exit(1)
    with open(kf) as f:
        keys = json.load(f)
    return keys[key_index]


def _upload_to_cos(local_path: str, key_profile: dict) -> str:
    """Upload WAV to Tencent COS, return presigned URL (valid 1h)."""
    from qcloud_cos import CosConfig, CosS3Client

    bucket = key_profile['cos_bucket']
    region = key_profile['cos_region']
    secret_id = key_profile['secret_id']
    secret_key = key_profile['secret_key']

    config = CosConfig(Region=region, SecretId=secret_id,
                       SecretKey=secret_key, Scheme='https')
    client = CosS3Client(config)

    remote_key = f'asr-uploads/{Path(local_path).name}'
    print(f'     ☁  上传到 COS ({bucket}/{remote_key})...', end=' ', flush=True)
    client.upload_file(Bucket=bucket, Key=remote_key,
                       LocalFilePath=local_path, PartSize=1)
    print('✓')

    url = client.get_presigned_url(Method='GET', Bucket=bucket,
                                   Key=remote_key, Expired=3600)
    return url


def recognize_long_audio(wav_path: str, key_profile: dict, speaker_count: int = 2,
                         dialect: str = 'mandarin') -> list:
    """Recognize using 录音文件识别 API with speaker diarization.

    Returns list of dicts: {text, start_ms, end_ms, speaker}.
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

    APP_ID = str(key_profile['app_id'])
    cred = credential.Credential(key_profile['secret_id'], key_profile['secret_key'])
    client = asr_client.AsrClient(cred, 'ap-guangzhou')

    file_size = os.path.getsize(wav_path)

    # Create recognition task
    req = models.CreateRecTaskRequest()
    req.EngineModelType = ENGINE_MAP.get(dialect, '16k_zh')
    req.ChannelNum = 1
    req.ResTextFormat = 3          # detailed JSON with timestamps
    req.SpeakerDiarization = 1
    req.SpeakerNumber = speaker_count

    if file_size > COS_SIZE_LIMIT and key_profile.get('cos_bucket'):
        # ── Large file: upload to COS, use URL ──
        cos_url = _upload_to_cos(wav_path, key_profile)
        req.SourceType = 0          # URL
        req.Url = cos_url
    else:
        # ── Small file (or no COS): use base64 ──
        if file_size > COS_SIZE_LIMIT:
            return [{'text': '', 'error':
                     f'文件 {file_size//1024//1024}MB > 3MB 且 api_keys.json 未配置 cos_bucket/cos_region'}]
        with open(wav_path, 'rb') as f:
            audio_b64 = base64.b64encode(f.read()).decode('utf-8')
        req.SourceType = 1          # raw base64 data
        req.Data = audio_b64
        req.DataLen = len(audio_b64)

    try:
        resp = client.CreateRecTask(req)
    except TencentCloudSDKException as e:
        return [{'text': '', 'error': str(e)}]

    task_id = resp.Data.TaskId
    print(f'    任务ID: {task_id}, 轮询结果...', end=' ', flush=True)

    # Poll for result (max 300s, every 3s)
    for _ in range(100):
        time.sleep(3)
        status_req = models.DescribeTaskStatusRequest()
        status_req.TaskId = task_id
        try:
            status = client.DescribeTaskStatus(status_req)
        except Exception:
            continue

        if status.Data.StatusStr == 'success':
            result = status.Data.Result
            if not result:
                print('✓ (空)')
                return []
            # Try parsing as JSON string first; fall back to model attributes
            if isinstance(result, str):
                if not result.strip():
                    print('✓ (空)')
                    return []
                return _parse_speaker_result(result)
            # Must be a model object — extract fields directly
            try:
                sentences = []
                for s in getattr(result, 'SentenceList', []):
                    sentences.append({
                        'text': getattr(s, 'Text', ''),
                        'start_ms': getattr(s, 'StartTimeMs', 0),
                        'end_ms': getattr(s, 'EndTimeMs', 0),
                        'speaker': getattr(s, 'SpeakerId', 0),
                    })
                print('✓')
                return sentences
            except Exception as e:
                print(f'✗ 解析失败: {e}')
                return []
        elif status.Data.StatusStr == 'failed':
            print(f'✗ {status.Data.ErrorMsg}')
            return [{'text': '', 'error': status.Data.ErrorMsg}]

    print('⏱ 超时')
    return [{'text': '', 'error': 'timeout'}]


def _parse_speaker_result(result_str: str) -> list:
    """Parse the JSON result with speaker labels.

    Result format (ResTextFormat=3):
    {
      "SpeakerNumber": 2,
      "SentenceList": [
        {"Text": "...", "StartTimeMs": 1500, "EndTimeMs": 3800, "SpeakerId": 0},
        ...
      ]
    }
    """
    try:
        result = json.loads(result_str) if isinstance(result_str, str) else result_str
    except (json.JSONDecodeError, TypeError) as e:
        print(f'⚠ JSON解析失败: {repr(result_str[:200])}... {e}')
        return []
    sentences = result.get('SentenceList', [])
    return [
        {
            'text': s.get('Text', ''),
            'start_ms': s.get('StartTimeMs', 0),
            'end_ms':   s.get('EndTimeMs', 0),
            'speaker':  s.get('SpeakerId', 0),
        }
        for s in sentences
    ]
