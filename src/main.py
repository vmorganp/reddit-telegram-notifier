import os
import time

import praw
import telegram
import yaml

r = praw.Reddit(
    client_id=os.environ['REDDIT_CLIENT_ID'],
    client_secret=os.environ['REDDIT_CLIENT_SECRET'],
    password=os.environ['REDDIT_PASSWORD'],
    username=os.environ['REDDIT_USERNAME'],
    user_agent="python monitor",
)

bot = telegram.Bot(os.environ['TELEGRAM_TOKEN'])

def main():
    while True:
        queries = get_config()
        for query in queries:
            print(f"getting posts for {query}")
            posts = r.subreddit("all").search(query, sort="new", time_filter="day")
            for post in posts:
                if not post.hidden:
                    try:
                        notify(post)
                        post.hide()
                    except Exception as err:
                        print(err)

        time.sleep(1*int(os.environ['INTERVAL']))


def notify(post):
    text =  "```Title: {}\n```".format(post.title)
    text += "[Site Url]({})\n".format(post.url)
    text += "[Reddit link]({})".format(post.shortlink)
    bot.send_message(text=text, chat_id=os.environ['TELEGRAM_CHANNEL_ID'], parse_mode="markdown" )


def get_config():
    with open("/config.yaml", "r") as config:
        return yaml.safe_load(config)['queries'].values()


main()
