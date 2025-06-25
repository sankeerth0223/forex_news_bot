import feedparser
import time
import requests

# Telegram bot details
BOT_TOKEN = '7550690596:AAGMeQjI7TDW6thHYwwEXKQc-g4IfsdHV8Y'
CHAT_ID = 1452103376

# Track sent article links to avoid duplicates
sent_links = set()

# RSS feed URLs for financial and forex news
RSS_FEEDS = [
    "https://www.investing.com/rss/news_25.rss",
    "https://www.forexfactory.com/ffcal_week_this.xml",
    "https://feeds.marketwatch.com/marketwatch/topstories/",
    "https://www.reutersagency.com/feed/?best-sectors=markets",
]

# Whitelist keywords
whitelist_keywords = [
    'eurusd', 'gbpusd', 'usdjpy', 'audusd', 'nzdusd', 'usdchf', 'usdcad',
    'xauusd', 'gold price', 'dollar index', 'forex', 'forex trading', 'currency pair',
    'interest rate', 'rate hike', 'rate cut', 'federal reserve', 'powell', 'cpi',
    'ppi', 'inflation', 'central bank', 'ecb', 'boj', 'boc', 'fomc', 'monetary policy',
    'usd', 'dollar strength', 'dollar weakness', 'hawkish', 'dovish'
]

# Blacklist keywords
blacklist_keywords = [
    'olympic', 'medal', 'football', 'biles', 'athlete', 'match', 'goal', 'team',
    'nba', 'nfl', 'wrestling', 'movie', 'actor', 'celeb', 'youtube', 'bitcoin',
    'ethereum', 'altcoin', 'coinbase', 'crypto', 'metaverse', 'instagram'
]

def analyze_sentiment(title):
    title = title.lower()
    bullish_words = ['cut', 'dovish', 'soft', 'falling inflation', 'weaker usd', 'slower cpi', 'ease']
    bearish_words = ['hike', 'hawkish', 'rise', 'strong inflation', 'surging cpi', 'hot jobs report', 'strength']

    bullish = any(word in title for word in bullish_words)
    bearish = any(word in title for word in bearish_words)

    if bullish and not bearish:
        return "🟢 Positive — Market may rise 📈"
    elif bearish and not bullish:
        return "🔴 Negative — Gold or safe havens may rise 🪙"
    elif bullish and bearish:
        return "🟡 Mixed — Uncertain reaction ⚖️"
    else:
        return "⚪ Neutral — Minimal impact"

def send_to_telegram(message):
    url = f'https://api.telegram.org/bot{BOT_TOKEN}/sendMessage'
    data = {'chat_id': CHAT_ID, 'text': message, 'parse_mode': 'HTML'}
    try:
        response = requests.post(url, data=data)
        if response.status_code != 200:
            print(f"Failed to send message: {response.text}")
    except Exception as e:
        print(f"Error sending message: {e}")

def fetch_and_send_rss_news():
    global sent_links
    for feed_url in RSS_FEEDS:
        feed = feedparser.parse(feed_url)

        for entry in feed.entries:
            title = entry.title
            link = entry.link
            description = entry.get('description', '')

            if link in sent_links:
                continue

            combined_text = (title + " " + description).lower()

            if any(bad_word in combined_text for bad_word in blacklist_keywords):
                continue

            if not any(word in combined_text for word in whitelist_keywords):
                continue

            sentiment = analyze_sentiment(title)
            message = f"<b>{title}</b>\n{sentiment}\n\nRead more: {link}"

            send_to_telegram(message)
            sent_links.add(link)
            time.sleep(1)  # short pause to avoid message flood

if __name__ == "__main__":
    while True:
        fetch_and_send_rss_news()
        print("Checked RSS feeds. Sleeping for 15 minutes...")
        time.sleep(900)  # 900 seconds = 15 minutes