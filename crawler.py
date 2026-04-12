import requests
from bs4 import BeautifulSoup
from datetime import datetime, timedelta
import json
import time

BASE_URL = "https://mongolia.gov.mn/news/news?page={}"


# ====== 日期 ======
def get_last_7_days():
    today = datetime.now()
    return [(today - timedelta(days=i)).strftime("%Y-%m-%d") for i in range(7)]


# ====== 主逻辑 ======
def parse_news():
    results = []
    target_dates = get_last_7_days()

    page = 1

    while True:
        url = BASE_URL.format(page)
        print(f"Fetching: {url}")

        try:
            res = requests.get(url, timeout=10)
        except Exception as e:
            print("Request error:", e)
            break

        if res.status_code != 200:
            print("Bad status:", res.status_code)
            break

        soup = BeautifulSoup(res.text, "html.parser")
        items = soup.select("article.l-post")

        if not items:
            print("No items found")
            break

        stop_flag = False

        for item in items:
            try:
                # ===== 标题 + 链接 =====
                a_tag = item.select_one("a[href*='/news/view']")
                if not a_tag:
                    continue

                title = a_tag.text.strip()
                link = a_tag["href"]

                if link.startswith("/"):
                    link = "https://mongolia.gov.mn" + link

                # ===== 日期 =====
                time_tag = item.select_one("time.post-date")
                if not time_tag:
                    continue

                datetime_str = time_tag.get("datetime", "")
                date = datetime.strptime(datetime_str, "%Y-%m-%d %H:%M:%S").strftime("%Y-%m-%d")

                # ===== 过滤7天 =====
                if date not in target_dates:
                    stop_flag = True
                    continue

                # ===== 保存 =====
                results.append({
                    "title": title,
                    "link": link,
                    "date": date
                })

            except Exception as e:
                print("Parse error:", e)

        if stop_flag:
            break

        page += 1
        time.sleep(1)

    return results


# ====== 输出 ======
def save_data(data):
    with open("news.json", "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


if __name__ == "__main__":
    try:
        news = parse_news()
        save_data(news)
        print(f"Saved {len(news)} records")
    except Exception as e:
        print("FATAL ERROR:", e)
