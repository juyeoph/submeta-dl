import pysrt
import os
import glob

# --- 설정 구간 (폴더 경로만 지정하세요) ---
FOLDER_A = "en_kor_srt"  # 번역본(Kor+Eng)이 있는 폴더
FOLDER_B = "en_srt"  # 원본(Eng)이 있는 폴더 (비교 대상)


def get_first_srt_file(folder_path):
    """폴더 내의 첫 번째 .srt 파일 경로를 반환"""
    if not os.path.exists(folder_path):
        print(f"❗ 오류: '{folder_path}' 폴더가 존재하지 않습니다.")
        return None

    files = glob.glob(os.path.join(folder_path, "*.srt"))
    if not files:
        print(f"❗ 오류: '{folder_path}' 폴더 안에 .srt 파일이 없습니다.")
        return None

    return files[0]  # 첫 번째 파일 반환


def normalize_text(text):
    """비교를 위해 줄바꿈과 앞뒤 공백 제거"""
    return text.strip().replace('\r\n', '\n').replace('\n', ' ')


def is_match(sub_a, sub_b):
    """두 자막 블록이 일치하는지 판단하는 로직"""
    # 1. 인덱스 비교
    if sub_a.index != sub_b.index:
        return False

    # 2. 타임스탬프 비교
    if sub_a.start != sub_b.start or sub_a.end != sub_b.end:
        return False

    # 3. 텍스트 포함 여부 비교
    # A(번역본) 안에 B(원본) 텍스트가 들어있어야 함
    text_a = normalize_text(sub_a.text)
    text_b = normalize_text(sub_b.text)

    if text_b not in text_a:
        return False

    return True


def compare_subtitles():
    # 1. 파일 자동 찾기
    path_a = get_first_srt_file(FOLDER_A)
    path_b = get_first_srt_file(FOLDER_B)

    if not path_a or not path_b:
        return

    print(f"🔍 비교 시작...")
    print(f"📁 파일 A: {os.path.basename(path_a)}")
    print(f"📁 파일 B: {os.path.basename(path_b)}")
    print("=" * 60)

    try:
        subs_a = pysrt.open(path_a, encoding='utf-8')
        subs_b = pysrt.open(path_b, encoding='utf-8')
    except Exception as e:
        print(f"❌ 파일 열기 실패: {e}")
        return

    min_len = min(len(subs_a), len(subs_b))
    mismatch_start_index = None  # 불일치가 시작된 지점을 기억하는 변수

    # 반복문 시작
    for i in range(min_len):
        sub_a = subs_a[i]
        sub_b = subs_b[i]

        match = is_match(sub_a, sub_b)

        if mismatch_start_index is None:
            # [상태 1] 현재까지 일치하는 중...
            if not match:
                # 💥 불일치 시작 발견!
                mismatch_start_index = sub_a.index
                print(f"\n🔴 [불일치 구간 시작] Line {sub_a.index} 부터 틀어짐")
                print(f"   ⏰ 시간: {sub_a.start} --> {sub_a.end}")
                print(f"   📜 원본(B): {normalize_text(sub_b.text)}")
                print(f"   📜 번역(A): {normalize_text(sub_a.text)}")
        else:
            # [상태 2] 불일치 진행 중... 다시 맞는지 찾는 중
            if match:
                # 🟢 다시 일치하는 지점 발견!
                print(f"🟢 [일치 회복] Line {sub_a.index} 부터 다시 정상")
                print(
                    f"   📊 결과: Line {mismatch_start_index} ~ {sub_a.index - 1} (총 {sub_a.index - mismatch_start_index}개 라인) 불일치")
                print("-" * 60)
                mismatch_start_index = None  # 상태 초기화

    # 루프가 끝났는데 아직도 불일치 상태라면?
    if mismatch_start_index is not None:
        print(f"⚠️ [주의] Line {mismatch_start_index} 부터 파일 끝까지 계속 불일치함.")

    # 파일 길이 차이 확인
    if len(subs_a) != len(subs_b):
        print(f"\nℹ️ 참고: 전체 파일 길이가 다릅니다. (A: {len(subs_a)}개, B: {len(subs_b)}개)")
    else:
        if mismatch_start_index is None:
            print("\n🎉 축하합니다! 모든 구간이 완벽하게 일치합니다.")


if __name__ == "__main__":
    compare_subtitles()