import pysrt
import os
import glob
import shutil
from datetime import timedelta

# --- 설정 구간 ---
INPUT_FOLDER = "srt"  # 원본 자막 폴더 (작업 후 비워짐)
OUTPUT_FOLDER = "merged_srt"  # 결과물 폴더 (시작 전 초기화됨)
MAX_CHAR_LIMIT = 60  # 영어 기준 병합 (60~70 추천)
MAX_GAP_SECONDS = 1.5  # 1.5초 이상 침묵이면 합치지 않음


def merge_subtitles(input_path, output_path, max_chars, max_gap_seconds):
    try:
        subs = pysrt.open(input_path, encoding='utf-8')
    except Exception as e:
        print(f"❌ 읽기 실패 ({os.path.basename(input_path)}): {e}")
        return False  # 실패 시 False 반환

    if not subs:
        print(f"⚠️ 빈 파일: {os.path.basename(input_path)}")
        return False

    new_subs = []
    current_sub = subs[0]

    for i in range(1, len(subs)):
        next_sub = subs[i]

        combined_text = (current_sub.text + " " + next_sub.text).replace('\n', ' ').strip()
        length_ok = len(combined_text) <= max_chars

        gap = next_sub.start - current_sub.end
        gap_seconds = gap.seconds + gap.milliseconds / 1000.0
        gap_ok = gap_seconds <= max_gap_seconds

        if length_ok and gap_ok:
            current_sub.text = combined_text
            current_sub.end = next_sub.end
        else:
            new_subs.append(current_sub)
            current_sub = next_sub

    new_subs.append(current_sub)

    final_file = pysrt.SubRipFile(new_subs)
    final_file.save(output_path, encoding='utf-8')
    print(f"✅ 완료: {os.path.basename(output_path)} (라인 수: {len(subs)} -> {len(new_subs)})")
    return True


def main():
    # 1. 원본 폴더 확인
    if not os.path.exists(INPUT_FOLDER):
        print(f"❗ 오류: '{INPUT_FOLDER}' 폴더가 없습니다.")
        os.makedirs(INPUT_FOLDER, exist_ok=True)
        return

    # 2. 결과물 폴더 초기화 (시작 전 비우기)
    if os.path.exists(OUTPUT_FOLDER):
        shutil.rmtree(OUTPUT_FOLDER)
    os.makedirs(OUTPUT_FOLDER)

    # 3. 파일 찾기
    srt_files = glob.glob(os.path.join(INPUT_FOLDER, "*.srt"))

    if not srt_files:
        print(f"ℹ️ '{INPUT_FOLDER}' 폴더가 비어있습니다. 자막 파일을 넣어주세요.")
        return

    print(f"총 {len(srt_files)}개의 파일을 처리합니다...\n" + "-" * 30)

    # 4. 일괄 처리
    for file_path in srt_files:
        file_name_only, file_extension = os.path.splitext(os.path.basename(file_path))
        new_filename = f"{file_name_only}{file_extension}"
        output_path = os.path.join(OUTPUT_FOLDER, new_filename)

        merge_subtitles(file_path, output_path, MAX_CHAR_LIMIT, MAX_GAP_SECONDS)

    print("-" * 30)

    # 5. 원본 폴더 비우기 (작업 후 삭제)
    print(f"🗑️ 원본 폴더('{INPUT_FOLDER}')를 비우는 중...")
    shutil.rmtree(INPUT_FOLDER)
    os.makedirs(INPUT_FOLDER)  # 빈 폴더 다시 생성 (다음 작업을 위해)

    print("✨ 모든 작업 완료! 원본 폴더가 깨끗해졌습니다.")


if __name__ == "__main__":
    main()