import yt_dlp
import os
import subprocess

def extract_subtitles_only(url, title):
    ydl_opts = {
        'skip_download': True,
        'writesubtitles': True,
        'writeautomaticsub': True,
        'subtitleslangs': ['ko', 'en'],
        'postprocessors': [{
            'key': 'FFmpegSubtitlesConvertor',
            'format': 'srt',
        }],
        'ffmpeg_location': '/opt/homebrew/bin/ffmpeg',
        'outtmpl': f'{title}.%(ext)s',
        'quiet': False,
    }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            print(f"\n--- Processing: {title} ---")
            ydl.download([url])

        for lang in ['ko', 'en']:
            vtt_file = f"{title}.{lang}.vtt"
            srt_file = f"{title}.{lang}.srt"

            if os.path.exists(vtt_file):
                print(f"Converting {vtt_file} to {srt_file}...")

                ffmpeg_cmd = [
                    'ffmpeg', '-i', vtt_file,
                    srt_file,
                    '-y'
                ]

                result = subprocess.run(ffmpeg_cmd, capture_output=True)

                if result.returncode == 0:
                    os.remove(vtt_file)
                    print(f"Successfully converted: {srt_file}")
                else:
                    print(f"FFmpeg Error for {lang}: {result.stderr.decode()}")

    except Exception as e:
        print(f"Error for {title}: {e}")

def run_subtitle_extraction(file_path):
    if not os.path.exists(file_path):
        print(f"Error: {file_path} 파일이 없습니다.")
        return

    with open(file_path, 'r', encoding='utf-8') as file:
        lines = [line.strip() for line in file.readlines() if line.strip()]

    for i in range(0, len(lines), 2):
        if i + 1 < len(lines):
            title = lines[i]
            url = lines[i + 1]
            extract_subtitles_only(url, title)

if __name__ == '__main__':
    run_subtitle_extraction('links.txt')