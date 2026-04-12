import requests
from bs4 import BeautifulSoup
from datetime import datetime, timedelta
import json
import time
import re

BASE_URL = "https://mongolia.gov.mn/news/news?page={}"

def get_last_7_days():
    today = datetime.now()
    return [(today - timedelta(days=i)).strftime("%Y.%m.%d") for i in range(7)]

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

        # ✅ 修正 selector
        items = soup.select("div.list-item")

        if not items:
            print("No items found, stop")
            break

        stop_flag = False

        for item in items:
            try:
                title = item.select_one("h3, h4").text.strip()

                link_tag = item.select_one("a")
                link = link_tag["href"]

                # 处理相对路径
                if link.startswith("/"):
                    link = "https://mongolia.gov.mn" + link

                date_text = item.get_text()

                # ✅ 用正则提取日期
                match = re.search(r"\d{4}\.\d{2}\.\d{2}", date_text)

                if not match:
                    continue

                date = match.group()

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
