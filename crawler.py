from translator import translate_mn_to_zh
import requests
from bs4 import BeautifulSoup
from datetime import datetime, timedelta
import json
import time
import os

BASE_URL = "https://mongolia.gov.mn/news/news?page={}"
CACHE_FILE = "translation_cache.json"


# ====== 加载翻译缓存 ======
def load_cache():
    if os.path.exists(CACHE_FILE):
        with open(CACHE_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}


def save_cache(cache):
    with open(CACHE_FILE, "w", encoding="utf-8") as f:
        json.dump(cache, f, ensure_ascii=False, indent=2)


# ====== 日期 ======
def get_last_7_days():
    today = datetime.now()
    return [(today - timedelta(days=i)).strftime("%Y-%m-%d") for i in range(7)]


# ====== 主逻辑 ======
def parse_news():
    results = []
    target_dates = get_last_7_days()

    translation_cache = load_cache()

    page = 1

    while True:
        url = BASE_URL.format(page)
        print(f"Fetching: {url}")

        res = requests.get(url)
        if res.status_code != 200:
            break

        soup = BeautifulSoup(res.text, "html.parser")
        items = soup.select("article.l-post")

        if not items:
            print("No items found")
            break

        stop_flag = False

        for item in items:
            try:
                # ===== 标题 =====
                a_tag = item.select_one("a[href*='/news/view']")
                title = a_tag.text.strip()
                link = a_tag["href"]

                if link.startswith("/"):
                    link = "https://mongolia.gov.mn" + link

                # ===== 日期 =====
                time_tag = item.select_one("time.post-date")
                datetime_str = time_tag["datetime"]

                date = datetime.strptime(datetime_str, "%Y-%m-%d %H:%M:%S").strftime("%Y-%m-%d")

                # ===== 过滤 =====
                if date not in target_dates:
                    stop_flag = True
                    continue

                # ===== 翻译（带缓存）=====
                if title in translation_cache:
                    zh_title = translation_cache[title]
                else:
                    print(f"Translating: {title[:30]}...")
                    zh_title = translate_mn_to_zh(title)
                    translation_cache[title] = zh_title

                    # 防止API/模型压力
                    time.sleep(0.5)

                # ===== 保存 =====
                results.append({
                    "title": title,
                    "title_zh": zh_title,
                    "link": link,
                    "date": date
                })

            except Exception as e:
                print("Error:", e)

        if stop_flag:
            break

        page += 1
        time.sleep(1)

    save_cache(translation_cache)
    return results


# ====== 输出 ======
def save_data(data):
    with open("news.json", "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


if __name__ == "__main__":
    news = parse_news()
    save_data(news)
    print(f"Saved {len(news)} records")
