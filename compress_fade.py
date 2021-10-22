import argparse
import subprocess
from datetime import timedelta
from pathlib import Path


def get_video_length(filename):
    result = subprocess.run(["ffprobe", "-v", "error", "-show_entries",
                             "format=duration", "-of",
                             "default=noprint_wrappers=1:nokey=1", filename],
                            stdout=subprocess.PIPE,
                            stderr=subprocess.STDOUT)
    return float(result.stdout)


def hms_to_seconds(hms: str):
    h, m, s = map(int, hms.split(':'))
    return timedelta(hours=h, minutes=m, seconds=s).total_seconds()


def main(args):
    video_length = get_video_length(args.input)
    ffmpeg_args = ['ffmpeg', '-i', args.input]
    input_path = Path(args.input)

    out_stem = f'{input_path.stem}_out'

    if args.trim_start is not None:
        ffmpeg_args.extend([
            '-ss', args.trim_start,
        ])
        if args.trim_end is None:
            out_stem += '_trim'
            ffmpeg_args.extend([
                '-t', str(video_length),
            ])
    if args.trim_end is not None:
        out_stem += '_trim'
        ffmpeg_args.extend([
            '-to', args.trim_end,
        ])
    if args.compress:
        out_stem += '_compr'
        ffmpeg_args.extend([
            '-c:v', 'libx265', '-crf', '28'
        ])
    else:
        ffmpeg_args.extend([
            '-c', 'copy'
        ])
    if args.fo_end is not None:
        out_stem += '_fade'
        fo_start = hms_to_seconds(args.fo_start)
        fo_end = hms_to_seconds(args.fo_end)
        fo_duration = fo_end - fo_start

        ffmpeg_args.extend([
            '-vf', f'fade=t=out:st={fo_start}:d={fo_duration}',
            '-af', f'afade=t=out:st={fo_start}:d={fo_duration}',
        ])

    out_path = input_path.parent / f'{out_stem}{input_path.suffix}'
    ffmpeg_args.extend([
        str(out_path)
    ])
    subprocess.run(ffmpeg_args)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description='Compress video and/or add fade and/or cut.')
    parser.add_argument('input', metavar='INPUT', help='The video to edit')
    parser.add_argument('--trim_start', metavar='TIME', default='00:00:00',
                        type=str, help='Start time in HH:MM:SS format')
    parser.add_argument('--trim_end', metavar='TIME',
                        type=str, help='End time in HH:MM:SS format')
    parser.add_argument('--compress', action='store_true',
                        help='Add this flag to compress the video.')
    parser.add_argument('--fo_start', metavar='TIME', type=str, default='00:00:00',
                        help='Start time of the fade out in HH:MM:SS format')
    parser.add_argument('--fo_end', metavar='TIME', type=str,
                        help='End time of the fade out in HH:MM:SS format')

    args = parser.parse_args()
    main(args)
