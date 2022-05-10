# Send results for a reddit search to telegram

## Usage

To run the image published here:
```
# you'll want to write config.yaml before running

docker run \
  --name=reddit-search-monitor \
  -e REDDIT_CLIENT_ID=XXXXXXXXXXXXXX \
  -e REDDIT_CLIENT_SECRET=XXXXXXXXXXXXXX \
  -e REDDIT_USERNAME=XXXXXXXXXXXXXX \
  -e REDDIT_PASSWORD=XXXXXXXXXXXXXX \
  -e TELEGRAM_TOKEN=XXXXXXXXXXXXXX \
  -e TELEGRAM_CHANNEL_ID=XXXXXXXXXXXXXX \
  -e INTERVAL=30 \
  -v $(pwd)/config.yaml:/config.yaml \
  --restart unless-stopped \
  ghcr.io/vmorganp/reddit-telegram-notifier:main
``` 


To build from source
```

git clone <thisRepo>
cd <this repo>
# Edit the docker-compose.yml environment variables
# Edit config.yaml to have the queries you want
docker-compose up --build

```