#!/usr/bin/env python3
"""ASR CLI: drag WAV/MP3 file(s) to transcribe via Tencent Cloud.
Multi-file: --merge or --separate, or will ask interactively."""

import sys, os, time, argparse, io
from pathlib import Path

# ── 诊断：记录原始参数，方便排查拖拽闪退问题 ──
_CRASH_LOG = Path(__file__).parent / 'crash.log'
def _log_raw_args():
    try:
        with open(_CRASH_LOG, 'w', encoding='utf-8') as f:
            f.write(f'cwd: {os.getcwd()}\n')
            f.write(f'args ({len(sys.argv)}):\n')
            for i, a in enumerate(sys.argv):
                f.write(f'  [{i}] {a!r}\n')
    except Exception:
        pass
_log_raw_args()

S = Path(__file__).parent
sys.path.insert(0, str(S))

from splitter    import smart_split
from transcriber import load_keys, transcribe_all
from transcriber_long import recognize_long_audio


def fmt_time(seconds: float) -> str:
    h = int(seconds // 3600)
    m = int((seconds % 3600) // 60)
    s = seconds % 60
    return f'[{h:02d}:{m:02d}:{s:05.2f}]'


def transcribe_one(wav_path: Path, key_profile: dict, args) -> list:
    """Process a single audio file → list of result dicts."""
    print(f'\n🔊 输入: {wav_path.name} ({wav_path.stat().st_size // 1024 // 1024}M)')
    tmp_dir = S / 'output' / wav_path.stem
    chunks = smart_split(str(wav_path), str(tmp_dir))
    print(f'✂  切分为 {len(chunks)} 段:')
    for cp, start in chunks:
        print(f'     [{fmt_time(start)}] {Path(cp).name}')

    if args.speaker > 0:
        print(f'\n🎤 角色分离（{args.speaker}人）...')
        # recognize_long_audio handles size: <3MB base64, ≥3MB COS upload
        all_sentences = []
        for i, (cp, start) in enumerate(chunks):
            print(f'  [{i+1}/{len(chunks)}] {Path(cp).name} ...', flush=True)
            sentences = recognize_long_audio(cp, key_profile, args.speaker, args.dialect)
            for s in sentences:
                s['start_offset'] = start
                s['chunk_path'] = cp
            all_sentences.extend(sentences)
        return all_sentences
    else:
        print(f'\n🎤 识别中 ({len(chunks)} 段, {args.dialect})...')
        return transcribe_all(chunks, key_profile, args.dialect)


def write_output(results: list, out_path: Path, args):
    with open(out_path, 'w', encoding='utf-8') as f:
        for r in results:
            if r.get('error'):
                offset = r.get('start_offset', 0)
                f.write(f'[{fmt_time(offset)}] [ERROR: {r["error"]}]\n\n')
                continue
            if args.speaker > 0:
                spk = r.get('speaker', 0)
                t = (r.get('start_offset', 0) * 1000 + r.get('start_ms', 0)) / 1000
                role = '面试官' if spk == 1 else ('我' if spk == 0 else f'S{spk}')
                if args.no_timestamps:
                    f.write(f'[{role}] {r["text"]}\n')
                else:
                    f.write(f'{fmt_time(t)} [{role}] {r["text"]}\n')
            else:
                offset = r.get('start_offset', 0)
                if args.no_timestamps:
                    f.write(r['text'] + '\n')
                else:
                    f.write(f'{fmt_time(offset)} {r["text"]}\n')


def main():
    parser = argparse.ArgumentParser(description='ASR — 语音转文字（腾讯云）')
    parser.add_argument('files', nargs='*', help='WAV/MP3 文件路径（可拖入多个）')
    parser.add_argument('--key', type=int, default=0,
                        help='使用 api_keys.json 中的第几个密钥（默认 0）')
    parser.add_argument('--key-file', default=None,
                        help='自定义密钥文件路径')
    parser.add_argument('--no-timestamps', action='store_true',
                        help='输出纯文本，不要时间戳')
    parser.add_argument('--speaker', type=int, default=0,
                        help='启用角色分离模式，指定人数（0=自动检测，推荐2）')
    parser.add_argument('--dialect', default='mandarin',
                        choices=['mandarin', 'canton', 'sichuan', 'shanghai',
                                 'nanjing', 'hakka', 'minnan'],
                        help='语言/方言（默认 mandarin 普通话）')
    parser.add_argument('-o', '--output', default=None,
                        help='输出文件路径（默认：第一个文件的同目录同名 .txt）')
    parser.add_argument('--merge', action='store_true', default=None,
                        help='多个文件合并为一份文稿（非交互模式）')
    parser.add_argument('--separate', action='store_true', default=None,
                        help='每个文件各自输出（非交互模式）')
    args = parser.parse_args()

    if not args.files:
        parser.print_help()
        print('\n用法：将 mp3/wav 文件拖到 main.py 上即可')
        if sys.stdin.isatty():
            input('\n按回车退出...')
        sys.exit(0)

    # Validate and sort files
    file_paths = []
    for fp in args.files:
        p = Path(fp).resolve()
        if not p.exists():
            print(f'ERROR: file not found: {fp}')
            sys.exit(1)
        if p.suffix.lower() not in ('.wav', '.mp3'):
            print(f'ERROR: only WAV/MP3 supported (got {p.suffix}): {p.name}')
            sys.exit(1)
        file_paths.append(p)
    file_paths.sort(key=lambda p: p.stem.replace('_01', '_b').replace('_02', '_c'))

    # Load API keys
    key_profile = load_keys(args.key, args.key_file)
    mode = f'角色分离{args.speaker}人' if args.speaker > 0 else '通用模式'
    print(f'API: {key_profile["label"]} | {mode} | {args.dialect}')

    # Decide merge vs separate
    merge = args.merge
    if merge and args.separate:
        print('ERROR: --merge 和 --separate 不能同时指定')
        sys.exit(1)
    if len(file_paths) > 1:
        print(f'\n📂 共 {len(file_paths)} 个文件:')
        for p in file_paths:
            print(f'     {p.name}')
        if merge is None and args.separate is None:
            if sys.stdin.isatty():
                ans = input('\n合并为一份文稿？[Y/n] ').strip().lower()
                merge = ans != 'n'
            else:
                print('  (非交互模式，默认分散输出；用 --merge 可合并)')
                merge = False
        elif args.separate:
            merge = False
        elif merge is None:
            merge = True
    elif len(file_paths) == 1:
        merge = False  # single file: no distinction

    # Process
    t0 = time.time()
    first = file_paths[0]

    if merge:
        out_path = Path(args.output) if args.output else first.with_suffix('.txt')
        all_results = []
        total_dur = 0.0
        for fp in file_paths:
            results = transcribe_one(fp, key_profile, args)
            for r in results:
                r['start_offset'] = r.get('start_offset', 0) + total_dur
            all_results.extend(results)
            # Advance duration offset for next file
            if results:
                last_offset = max((r.get('start_offset', 0) for r in results), default=0)
                total_dur = last_offset + (results[-1].get('end_ms', 0) / 1000 if results[-1].get('end_ms') else 0)
        elapsed = time.time() - t0
        ok = sum(1 for r in all_results if not r.get('error'))
        print(f'✅ {ok}/{len(all_results)} 完成, {elapsed:.1f}s')
        write_output(all_results, out_path, args)
        print(f'\n📝 输出: {out_path}')
        total_chars = sum(len(r.get('text', '')) for r in all_results)
        print(f'   共 {total_chars} 字')
    else:
        # Separate mode: each file → own .txt
        for fp in file_paths:
            results = transcribe_one(fp, key_profile, args)
            elapsed = time.time() - t0
            ok = sum(1 for r in results if not r.get('error'))
            print(f'✅ {ok}/{len(results)} 完成, {elapsed:.1f}s')
            out_path = Path(args.output) if args.output and len(file_paths) == 1 else fp.with_suffix('.txt')
            write_output(results, out_path, args)
            print(f'\n📝 输出: {out_path}')
            total_chars = sum(len(r.get('text', '')) for r in results)
            print(f'   共 {total_chars} 字')


if __name__ == '__main__':
    CRASH_LOG = S / 'crash.log'
    try:
        main()
    except SystemExit:
        raise
    except Exception as e:
        import traceback
        with open(CRASH_LOG, 'a', encoding='utf-8') as f:
            f.write('\n── crash ──\n')
            traceback.print_exc(file=f)
        print(f'FATAL: {e}', file=sys.stderr)
        if sys.stdin.isatty():
            input('\n按回车退出...')
        sys.exit(1)
    else:
        if sys.stdin.isatty():
            input('\n按回车退出...')
