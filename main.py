from telegram import Update, Bot
from telegram.ext import Application, CommandHandler, ContextTypes, MessageHandler, filters
from sqlalchemy import create_engine, Column, Integer, String
from sqlalchemy.orm import sessionmaker, declarative_base
import praw
import asyncio
from multiprocessing import Process

import os
import time


SEARCH_INTEVAL = os.getenv("INTERVAL", 300)


################################################################################
################################################################## Reddit Config
################################################################################

reddit = praw.Reddit(
    client_id=os.environ["REDDIT_CLIENT_ID"],
    client_secret=os.environ["REDDIT_CLIENT_SECRET"],
    user_agent="python monitor",
    check_for_async=False,
)

################################################################################
############################################################### SQLAlchemy setup
################################################################################

DATABASE_URL = "sqlite:///queries.db"
engine = create_engine(DATABASE_URL)
# engine = create_engine(DATABASE_URL, echo=True) # use this for debugging
Base = declarative_base()


class UserQuery(Base):
    __tablename__ = "queries"
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, nullable=False)
    query = Column(String, nullable=False)
    last_id = Column(String)


# Create tables
Base.metadata.create_all(engine)

Session = sessionmaker(bind=engine)
session = Session()


################################################################################
################################################################### Telegram Bot
################################################################################

TELEGRAM_TOKEN = os.environ["TELEGRAM_TOKEN"]


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    helptext = """
`/start`

Displays this text
This bot is used for monitoring a search on [reddit](https://old.reddit.com/search)
The best way to do this is to go to reddit, and type in a search. Refine your search here to include only things you care about.

`/add`

Once you're done refining your search, come back here and use the `/add` command to add the query. From then on, the bot will send you new results for that query.
Be sure to put your search between single quotes like so:
```text
/add 'puppies subreddit:awww'
```

`/list`

List the queries you've saved. This is also shown after each /add or /remove command

`/remove`

remove a query from the search. Start with running the /remove command and pick the query you don't want anymore
    """
    await update.message.reply_markdown(
        helptext,
    )


async def listQueries(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user_id = update.message.from_user.id
    users_queries = (
        session.query(UserQuery.id, UserQuery.query).filter(UserQuery.user_id == user_id).order_by(UserQuery.id).all()
    )
    response = ""
    for i, item in enumerate(users_queries):
        response += f"{i}. `{item[1]}`\n"

    await update.message.reply_markdown(
        response,
    )


async def addQuery(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user_id = update.message.from_user.id
    query = update.message.text.split("'")[1]
    user_query = UserQuery(user_id=user_id, query=query)
    session.add(user_query)
    session.commit()
    await listQueries(update=update, context=context)


async def removeQuery(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user_id = update.message.from_user.id
    query_id_to_remove = int(update.message.text.split(" ", 1)[1])
    users_queries = session.query(UserQuery).filter(UserQuery.user_id == user_id).order_by(UserQuery.id).all()

    if len(users_queries) >= query_id_to_remove:
        session.delete(users_queries[query_id_to_remove])
        session.commit()
        await update.message.reply_markdown(
            f"Removed `{users_queries[query_id_to_remove].query}`",
        )
        await listQueries(update=update, context=context)
    else:
        await update.message.reply_markdown(
            "Didn't find that query",
        )


# Function to search Reddit and notify users
def search_reddit():
    async def async_wrapper():
        while True:
            async with Bot(TELEGRAM_TOKEN) as bot:
                queries = (
                    session.query(UserQuery.id, UserQuery.user_id, UserQuery.query, UserQuery.last_id)
                    .order_by(UserQuery.id)
                    .all()
                )
                for my_query in queries:
                    try:
                        query_id, user, query, last = my_query
                        results = reddit.subreddit("all").search(query, sort="new", limit=20, time_filter="day")
                        # Keep the first (newest) response from each search, so that we can stop showing more after that one
                        first = True
                        for submission in results:
                            if submission.id == last:
                                break
                            message = f"{submission.title}\nFound by query: `{query}`\n[Site Url]({submission.url})\n[Reddit Link]({submission.shortlink})"
                            await bot.send_message(chat_id=user, text=message, parse_mode="Markdown")
                            if first:
                                session.query(UserQuery).filter(UserQuery.id == query_id).update(
                                    {"last_id": submission.id}
                                )
                                session.commit()
                                first = False

                    except Exception as e:
                        # raise (e)
                        print(e)
            time.sleep(int(SEARCH_INTEVAL))

    asyncio.run(async_wrapper())


def telegram_bot():
    application = Application.builder().token(TELEGRAM_TOKEN).build()
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", start))
    application.add_handler(CommandHandler("list", listQueries))
    application.add_handler(CommandHandler("add", addQuery))
    application.add_handler(CommandHandler("remove", removeQuery))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, start))

    # Run bot and notifier
    print("Starting Telegram bot")
    application.run_polling(allowed_updates=Update.ALL_TYPES)


def main():
    p1 = Process(target=telegram_bot)
    p2 = Process(target=search_reddit)
    p1.start()
    p2.start()


if __name__ == "__main__":
    main()
