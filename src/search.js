'use strict';
const snoowrap = require('snoowrap');
const TelegramBot = require('node-telegram-bot-api');

// required for reading config
const yaml = require('js-yaml');
const fs = require('fs');

// load stuff from env variables
const reddit_clientId = process.env.REDDIT_CLIENT_ID;
const reddit_clientSecret = process.env.REDDIT_CLIENT_SECRET;
const reddit_username = process.env.REDDIT_USERNAME;
const reddit_password = process.env.REDDIT_PASSWORD;

const bot = new TelegramBot(process.env.TELEGRAM_TOKEN);
const telegram_channel = process.env.TELEGRAM_CHANNEL_ID

const interval = process.env.INTERVAL

// configure reddit
const r = new snoowrap({
    userAgent: 'nodeJS',
    clientId: reddit_clientId,
    clientSecret: reddit_clientSecret,
    username: reddit_username,
    password: reddit_password
});
// configure  telegram


async function main() {
    console.log("querying...");
    getConfig().forEach(query => {
        searchRedditAndNotify(query)
    });
}


// search for stuff within the last day using the websites search syntax
// there is a max length to this query, but I don't know what it is
async function searchRedditAndNotify(query, time = "day", syntax = "lucene") {
    var posts = await r.search({ query: query, time: time, syntax: syntax })
    posts.forEach(post => {
        if (!post.hidden) {
            let info = [
                "Title: " + post.title,
                "[Site Url]("+post.url+")",
                "[Reddit link](https://reddit.com"+post.permalink+")"
            ]
            telegramNotify(info)
        }
        // make it so the post doesn't show up in the future if notified about it
        post.hide()
    });
}


async function telegramNotify(info) {
    console.log("Sending message in telegram")
    bot.sendMessage(telegram_channel, info.join("\n"), {"parse_mode": 'Markdown'})
}


function getConfig() {
    try {
        const doc = yaml.load(fs.readFileSync('/config.yaml', 'utf8'));
        let queries = []
        Object.values(doc.queries).forEach(query => {
            queries.push(query)
        });
        console.log(queries);
        return queries
    } catch (e) {
        console.log(e);
    }
}

// this is purely here so it runs asap instead of waiting on the first run
main()
setInterval(function () {
    main()
}, interval * 1000);
