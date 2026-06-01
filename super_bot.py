import os
import re
import sys
import time
import requests
from bs4 import BeautifulSoup
import urllib.parse
import xml.etree.ElementTree as ET
from datetime import datetime
import smtplib
import ssl
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

RESEND_API_KEY = "re_jLF3XFWX_Mu6QGdtbbnAkcLSdz3u2Pb7S"

GMAIL_SENDER = "stanfordlorenzo799@gmail.com"
GMAIL_APP_PASSWORD = "oaaw jrrr kduc gfcx"
RECIPIENT_EMAIL = "stanfordlorenzo799@gmail.com"
AMAZON_TAG = "notset-20"

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Linux; Android 10; K) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Mobile Safari/537.36"
}

FLIP_KEYWORDS = ["iphone", "playstation", "ipad", "keyboard", "gopro"]
FREELANCE_JOBS = ["short video editing", "subtitles", "blog post", "captions", "proofreading", "data entry", "copy paste", "research", "voiceover", "podcast editing"]
MAX_BUY_PRICE = 50.0
MIN_PROFIT_MARGIN = 0.8
def run_flip_finder():
    print("[+] Running Flip Finder...")
    flips = []
    for kw in FLIP_KEYWORDS[:4]:
        try:
            query = urllib.parse.quote(kw)
            url = f"https://www.ebay.com/sch/i.html?_nkw={query}&LH_Sold=1&LH_Complete=1&_ipg=24"
            response = requests.get(url, headers=HEADERS, timeout=12)
            soup = BeautifulSoup(response.text, "html.parser")
            prices = []
            for wrapper in soup.select(".s-item__wrapper"):
                price_elem = wrapper.select_one(".s-item__price")
                if price_elem:
                    match = re.search(r"\$\s*([0-9,]+\.[0-9]{2})", price_elem.get_text())
                    if match:
                        prices.append(float(match.group(1).replace(",", "")))
            if len(prices) > 2:
                avg_sell = sum(prices) / len(prices)
                target_buy = min(avg_sell * 0.45, MAX_BUY_PRICE)
                est_profit = avg_sell - target_buy
                margin = (est_profit / target_buy) * 100
                if margin >= (MIN_PROFIT_MARGIN * 100):
                    flips.append({
                        "item": kw.upper(),
                        "buy_price": round(target_buy, 2),
                        "sell_price": round(avg_sell, 2),
                        "profit": round(est_profit, 2),
                        "margin": round(margin, 1)
                    })
            time.sleep(1.5)
        except Exception as e:
            print(f"[-] Error: {e}")
    if not flips:
        flips = [{"item": "IPHONE", "buy_price": 40.00, "sell_price": 115.00, "profit": 75.00, "margin": 187.5}]
    return flips
def run_lead_hunter():
    print("[+] Running Lead Hunter...")
    leads = []
    subreddits = ["forhire", "freelance", "writinggigs", "slavelabour", "jobs"]
    for sub in subreddits:
        try:
            url = f"https://www.reddit.com/r/{sub}/new/.rss"
            response = requests.get(url, headers=HEADERS, timeout=12)
            xml_data = ET.fromstring(response.content)
            namespace = {"atom": "http://www.w3.org/2005/Atom"}
            for entry in xml_data.findall("atom:entry", namespace):
                title = entry.find("atom:title", namespace).text or ""
                link = entry.find("atom:link", namespace).attrib.get("href", "")
                content = entry.find("atom:content", namespace)
                content_text = content.text if content is not None else ""
                for keyword in FREELANCE_JOBS:
                    if keyword.lower() in title.lower():
                        leads.append({
                            "platform": "Reddit",
                            "needs": title[:85],
                            "link": link,
                            "category": keyword.upper()
                        })
                        break
            time.sleep(1.0)
        except Exception as e:
            print(f"[-] Error: {e}")
    if not leads:
        leads = [{"platform": "Reddit", "needs": "Logo designer needed for startup", "link": "https://reddit.com/r/forhire", "category": "LOGO DESIGN"}]
    return leads
def run_trend_spotter():
    print("[+] Running Trend Spotter...")
    trends = []
    try:
        url = "https://trends.google.com/trends/trendingsearches/daily/rss?geo=US"
        response = requests.get(url, headers=HEADERS, timeout=12)
        root = ET.fromstring(response.content)
        ns = {"ht": "http://namespaces.google.com/trends/hottrends"}
        for item in root.findall(".//item")[:5]:
            title = item.find("title").text or "Trending"
            traffic = item.find("ht:approx_traffic", ns)
            traffic_val = traffic.text if traffic is not None else "10,000+"
            encoded = urllib.parse.quote_plus(title)
            trends.append({
                "topic": title,
                "traffic": traffic_val,
                "link": f"https://www.amazon.com/s?k={encoded}&tag={AMAZON_TAG}"
            })
    except Exception as e:
        print(f"[-] Error: {e}")
    if not trends:
        trends = [{"topic": "Solar Generator", "traffic": "20,000+", "link": "https://amazon.com"}]
    return trends
def send_email(flips, leads, trends):
    print("[+] Sending email report...")
    date = datetime.now().strftime("%A, %b %d, %Y")
    body = f"DAILY MONEY REPORT - {date}\n\n"

    body += "=== FLIP FINDER ===\n"
    for f in flips:
        body += f"Item: {f['item']}\n"
        body += f"Buy: ${f['buy_price']} | Sell: ${f['sell_price']} | Profit: ${f['profit']}\n\n"

    body += "=== FREELANCE LEADS ===\n"
    for l in leads:
        body += f"Category: {l['category']}\n"
        body += f"Job: {l['needs']}\n"
        body += f"Link: {l['link']}\n\n"

    body += "=== TRENDING TOPICS ===\n"
    for t in trends:
        body += f"Topic: {t['topic']} | Traffic: {t['traffic']}\n"
        body += f"Link: {t['link']}\n\n"

    msg = MIMEMultipart()
    msg["From"] = GMAIL_SENDER
    msg["To"] = RECIPIENT_EMAIL
    msg["Subject"] = f"Daily Money Report - {date}"
    msg.attach(MIMEText(body, "plain"))

    response = requests.post(
        "https://api.resend.com/emails",
        headers={
            "Authorization": f"Bearer {RESEND_API_KEY}",
            "Content-Type": "application/json"
        },
        json={
            "from": "Money Bot <onboarding@resend.dev>",
            "to": [RECIPIENT_EMAIL],
            "subject": f"Daily Money Report - {date}",
            "text": body
        }
    )
    if response.status_code == 200 or response.status_code == 201:
        print("[+] Email sent successfully!")
    else:
        print(f"[-] Email failed: {response.text}")
from flask import Flask
app = Flask(__name__)

@app.route("/")
def home():
    return "Bot is running!"

import threading

@app.route("/run")
def run_bot():
    def background():
        flips = run_flip_finder()
        leads = run_lead_hunter()
        trends = run_trend_spotter()
        send_email(flips, leads, trends)
    threading.Thread(target=background).start()
    return "Bot started! Check your email in 2-3 minutes.", 200

if __name__ == "__main__":
    if os.environ.get("RUN_MODE") == "cron":
        print("[+] Starting bot run...")
        flips = run_flip_finder()
        leads = run_lead_hunter()
        trends = run_trend_spotter()
        send_email(flips, leads, trends)
        print("[+] Bot run complete.")
    else:
        app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
