from bs4 import BeautifulSoup


def parse_course_toc(html_content):
    soup = BeautifulSoup(html_content, 'html.parser')
    results = []

    chapters = soup.find_all('li', class_=lambda x: x and 'chapter' in x and 'CourseCoverTOC' in x)

    for i, chapter in enumerate(chapters, 1):
        label = chapter.find('label')
        chapter_title = "Unknown Chapter"
        if label:
            title_span = label.find('span')
            if title_span:
                chapter_title = title_span.get_text(strip=True)

        video_ul = chapter.find('ul')
        if video_ul:
            videos = video_ul.find_all('li')

            for j, video in enumerate(videos, 1):
                content_cell = video.find('div', class_=lambda x: x and 'content-cell' in x)
                video_title = "Unknown Video"
                if content_cell:
                    video_title_span = content_cell.find('span')
                    if video_title_span:
                        video_title = video_title_span.get_text(strip=True)

                formatted_str = f"{i}. {chapter_title}/{j}. {video_title}"
                results.append(formatted_str)

    return results


if __name__ == "__main__":
    try:
        with open('extract.txt', 'r', encoding='utf-8') as f:
            data = f.read()
            results = parse_course_toc(data)

            for line in results:
                print(line)

            with open('result.txt', 'w', encoding='utf-8') as outfile:
                for line in results:
                    outfile.write(line + '\n\n')

            print("-" * 30)
            print("✅ 변환 완료! 'result.txt' 파일을 확인해보세요.")

    except FileNotFoundError:
        print("❌ 'extract.txt' 파일을 찾을 수 없습니다.")