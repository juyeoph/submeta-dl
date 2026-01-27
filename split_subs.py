import pysrt
import os
import glob
import shutil

# --- 설정 구간 ---
INPUT_FOLDER = "merged_srt"  # 분할할 원본 자막이 있는 폴더
OUTPUT_FOLDER = "split_srt"  # 결과물을 저장할 폴더
TARGET_LINES = 300  # 목표 라인 수 (이쯤에서 자를 준비)
HARD_LIMIT = 350  # 마침표가 안 나와도 이때는 무조건 자름 (안전장치)


def split_subtitle(input_path, output_folder, target_lines, hard_limit):
    try:
        subs = pysrt.open(input_path, encoding='utf-8')
    except Exception as e:
        print(f"❌ 읽기 실패 ({os.path.basename(input_path)}): {e}")
        return

    if not subs:
        return

    # 파일명 기본 정보 추출
    file_name_only, file_extension = os.path.splitext(os.path.basename(input_path))

    part_num = 1
    current_batch = []

    # 분할 로직 시작
    for i, sub in enumerate(subs):
        current_batch.append(sub)

        # 현재 배치의 길이
        batch_len = len(current_batch)

        # 1. 분할 조건 검사
        # (목표 라인을 넘었고 AND 문장이 끝나는 기호로 끝날 때) OR (강제 제한선 도달 시)
        is_end_of_sentence = sub.text.strip().endswith(('.', '?', '!'))
        is_target_reached = batch_len >= target_lines
        is_hard_limit = batch_len >= hard_limit

        if (is_target_reached and is_end_of_sentence) or is_hard_limit:
            # --- 저장 수행 ---
            save_path = os.path.join(output_folder, f"{file_name_only}_part{part_num}{file_extension}")

            # 인덱스(순번) 재정렬 (각 파일마다 1번부터 시작하도록 깔끔하게)
            for idx, item in enumerate(current_batch):
                item.index = idx + 1

            new_file = pysrt.SubRipFile(current_batch)
            new_file.save(save_path, encoding='utf-8')

            print(f"  💾 저장됨: {os.path.basename(save_path)} (라인 수: {len(current_batch)})")

            # 초기화 및 다음 파트 준비
            current_batch = []
            part_num += 1

    # 반복문이 끝났는데 남은 자투리 자막이 있다면 저장
    if current_batch:
        save_path = os.path.join(output_folder, f"{file_name_only}_part{part_num}{file_extension}")
        for idx, item in enumerate(current_batch):
            item.index = idx + 1
        new_file = pysrt.SubRipFile(current_batch)
        new_file.save(save_path, encoding='utf-8')
        print(f"  💾 저장됨: {os.path.basename(save_path)} (라인 수: {len(current_batch)})")


def main():
    # 1. 입력 폴더 확인
    if not os.path.exists(INPUT_FOLDER):
        print(f"❗ 오류: '{INPUT_FOLDER}' 폴더가 없습니다. 병합된 파일이 있는지 확인해주세요.")
        return

    # 2. 결과 폴더 초기화 (비우고 새로 생성)
    if os.path.exists(OUTPUT_FOLDER):
        shutil.rmtree(OUTPUT_FOLDER)
    os.makedirs(OUTPUT_FOLDER)

    # 3. 파일 목록 가져오기
    srt_files = glob.glob(os.path.join(INPUT_FOLDER, "*.srt"))

    if not srt_files:
        print(f"ℹ️ '{INPUT_FOLDER}' 폴더가 비어있습니다.")
        return

    print(f"총 {len(srt_files)}개의 파일을 분할 처리합니다...\n" + "=" * 40)

    for file_path in srt_files:
        print(f"🔨 처리 중: {os.path.basename(file_path)}")
        split_subtitle(file_path, OUTPUT_FOLDER, TARGET_LINES, HARD_LIMIT)
        print("-" * 30)

    print("🎉 모든 분할 작업이 완료되었습니다!")


if __name__ == "__main__":
    main()