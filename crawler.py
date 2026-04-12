from translator import translate_mn_to_zh
import requests
from bs4 import BeautifulSoup
from datetime import datetime, timedelta
import json
import time

BASE_URL = "https://mongolia.gov.mn/news/news?page={}"

def get_last_7_days():
    today = datetime.now()
    return [(today - timedelta(days=i)).strftime("%Y-%m-%d") for i in range(7)]

def parse_news():
    results = []
    target_dates = get_last_7_days()

    page = 1

    while True:
        url = BASE_URL.format(page)
        print(f"Fetching: {url}")

        res = requests.get(url)
        if res.status_code != 200:
            break

        soup = BeautifulSoup(res.text, "html.parser")

        # ✅ 正确 selector
        items = soup.select("article.l-post")

        if not items:
            print("No items found")
            break

        stop_flag = False

        for item in items:
            try:
                # 标题 + 链接
                a_tag = item.select_one("h2 a")
                title = a_tag.text.strip()
                link = a_tag["href"]

                if link.startswith("/"):
                    link = "https://mongolia.gov.mn" + link

                # 日期
                time_tag = item.select_one("time.post-date")
                datetime_str = time_tag["datetime"]

                date = datetime.strptime(datetime_str, "%Y-%m-%d %H:%M:%S").strftime("%Y-%m-%d")

                # 过滤7天
                if date in target_dates:
                    results.append({
                        "title": title,
                        "link": link,
                        "date": date
                    })
                else:
                    stop_flag = True

            except Exception as e:
                print("Error:", e)

        if stop_flag:
            break

        page += 1
        time.sleep(1)

    return results


def save_data(data):
    with open("news.json", "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


if __name__ == "__main__":
    news = parse_news()
    save_data(news)
    print(f"Saved {len(news)} records")
