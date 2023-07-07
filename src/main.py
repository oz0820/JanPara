import json
import os
import re
import time
import requests
import dotenv

from bs4 import BeautifulSoup
from urllib.parse import urlparse, parse_qs, urlencode, urlunparse


def main():
    url = hoge_url(os.environ.get("SEARCH_URL"))
    res = requests.get(url, headers=headers)

    soup = BeautifulSoup(res.content, "html.parser")
    parsed_items = parse_items(soup)

    below_target_items = []
    for item in parsed_items:
        if item["price"] <= int(os.environ.get("TARGET_PRICE")):
            below_target_items.append(item)
            send_discord_webhook([get_embed(item)])


def parse_items(soup: BeautifulSoup):
    items = soup.findAll("div", attrs={"class": "search_item_s"})
    out = []
    for item in items:
        search_itemprice = item.find("div", attrs={"class": "search_itemprice"})
        if search_itemprice.find("div").text == "SOLD OUT":
            continue

        out.append({
            "item_link": "https://www.janpara.co.jp/" + item.find("a", attrs={"class": "search_itemlink"}).get("href"),
            "image_link": item.find("div", attrs={"class": "search_itemimage"}).find("img").get("src"),
            "name": item.find("div", attrs={"class": "search_itemname wordturn"}).text.strip(),
            "price": int("".join(re.findall(r"\d+", search_itemprice.find("div", attrs={"class": "item_amount"}).text.strip()))),
            "item_amount": search_itemprice.find("div", attrs={"class": "item_amount"}).text.strip(),
            "stock": int("".join(re.findall(r"\d+", search_itemprice.find("div").text.strip())))

        })
    return out


def hoge_url(url):
    parsed_url = urlparse(url)
    query_params = parse_qs(parsed_url.query)

    # 表示数増やす
    query_params["LINE"] = ["24"]

    # 安い順
    query_params["ORDER"] = ["3"]

    new_query = urlencode(query_params, doseq=True)
    new_url_parts = list(parsed_url)
    new_url_parts[4] = new_query
    return urlunparse(new_url_parts)


def send_discord_webhook(embeds):
    headers = {"Content-Type": "application/json"}
    data = {"embeds":  embeds}
    response = requests.post(os.environ.get("WEBHOOK_URL"), headers=headers, data=json.dumps(data))
    if response.status_code == 204:
        print("Webhook sent successfully.")
    else:
        print("Failed to send webhook. Status code:", response.status_code)


def get_embed(item: dict):
    embed = \
        {
            "title": item.get("name"),
            "description": item.get("item_amount"),
            "url": item.get("item_link"),
            "color": 0x00ff00,
            "thumbnail": {
                "url_ng": item.get("image_link"),
            },
        }
    return embed


if __name__ == "__main__":
    dotenv.load_dotenv()
    headers = {"User-Agent": os.environ.get("USER_AGENT")}
    while True:
        main()
        time.sleep(int(os.environ.get("INTERVAL")))

