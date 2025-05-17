import subprocess
import os
import yt_dlp

def download_video_and_add_metadata(url, title):
    # Define download options for yt-dlp
    ydl_opts = {
        'format': 'bestvideo+bestaudio/best',
        'outtmpl': f'{title}_temp.%(ext)s'
    }

    # Download video using yt-dlp
    with yt_dlp. YoutubeDL(ydl_opts) as ydl:
        ydl.download([url])

    # Define ffmpeg command to add metadata
    input_file = f'{title}_temp.mp4'
    output_file = f'{title}.mp4'
    ffmpeg_cmd = [
        'ffmpeg', '-i', input_file,
        '-metadata', f'description={url}',
        '-codec', 'copy', output_file
    ]
    # Run ffmpeg to add metadata
    subprocess.run(ffmpeg_cmd)

    #Delete the temporary file
    if os.path.exists(input_file):
        os.remove(input_file)

def download_videos_from_file(file_path):
    with open(file_path, 'r') as file:
        lines = file.readlines()

    for i in range(0, len(lines), 2):
        title = lines[i].strip()
        url = lines[i + 1].strip()
        download_video_and_add_metadata(url, title)

if __name__ == '__main__':
    file_path = 'links.txt'
    download_videos_from_file(file_path)