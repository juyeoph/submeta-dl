import subprocess
import os
import yt_dlp
from yt_dlp.utils import sanitize_filename  # 파일명으로 쓸 수 없는 문자 제거용


def download_video_and_add_metadata(url):
    # 1. 다운로드 전에 영상 정보(제목)만 먼저 추출
    print(f"정보 추출 중...: {url}")

    # 제목 추출을 위한 설정
    # (주의: 이전에 말씀드린 헤더 문제가 있다면 여기에 http_headers를 추가해야 합니다)
    ydl_opts_info = {
        'quiet': True,  # 불필요한 로그 생략
        'no_warnings': True,
    }

    try:
        with yt_dlp.YoutubeDL(ydl_opts_info) as ydl:
            info_dict = ydl.extract_info(url, download=False)  # 다운로드는 안 하고 정보만 가져옴
            video_title = info_dict.get('title', 'Unknown_Title')  # 제목 가져오기

            # 파일명으로 쓸 수 없는 특수문자(:, /, \ 등)를 안전하게 변경
            clean_title = sanitize_filename(video_title)
            print(f"감지된 제목: {clean_title}")

    except Exception as e:
        print(f"정보 추출 실패 (URL 만료 가능성): {e}")
        return

    # 2. 추출한 제목으로 다운로드 설정
    ydl_opts = {
        'format': 'bestvideo+bestaudio/best',
        'outtmpl': f'{clean_title}_temp.%(ext)s'  # 위에서 추출한 clean_title 사용
    }

    # 3. 비디오 다운로드
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([url])
    except Exception as e:
        print(f"다운로드 중 오류 발생: {e}")
        return

    # 4. ffmpeg로 메타데이터 추가 (파일명이 clean_title로 바뀜)
    input_file = f'{clean_title}_temp.mp4'
    output_file = f'{clean_title}.mp4'

    # 다운로드가 정상적으로 되어서 파일이 있을 때만 실행
    if os.path.exists(input_file):
        ffmpeg_cmd = [
            'ffmpeg', '-i', input_file,
            '-metadata', f'description={url}',
            '-codec', 'copy', output_file,
            '-y'  # 이미 파일이 있으면 덮어쓰기 옵션
        ]
        subprocess.run(ffmpeg_cmd)

        # 임시 파일 삭제
        os.remove(input_file)
        print(f"완료: {output_file}")
    else:
        print(f"파일을 찾을 수 없습니다: {input_file}")


def download_videos_from_file(file_path):
    with open(file_path, 'r') as file:
        lines = file.readlines()

    # 이제 홀수/짝수 줄 구분 없이 모든 줄을 URL로 처리
    for line in lines:
        url = line.strip()
        if url:  # 빈 줄이 아닐 때만 실행
            download_video_and_add_metadata(url)


if __name__ == '__main__':
    file_path = 'links_temp.txt'
    download_videos_from_file(file_path)