# We Belong Network — UK TikTok trend updater

This repository supplies the website's public JSON feed:

https://raw.githubusercontent.com/danielptmay-boop/webelong-uk-trends/main/data/uk-tiktok-trends.json

The workflow is scheduled daily at 06:00 Europe/London and can also be run manually from GitHub Actions. It collects UK hashtag discoveries and sampled sounds through the third-party Apify actor `parsebird/tiktok-trends-scraper`. Sampled sounds are **not** an official UK music chart.

## Activate

1. Create an Apify account and review the actor's current terms, availability, and charges: https://apify.com/parsebird/tiktok-trends-scraper
2. In this repository, open Settings → Secrets and variables → Actions → New repository secret.
3. Create `APIFY_TOKEN` with your Apify API token. Do not put it in a source file, webpage, or chat.
4. Open Actions → Refresh verified UK TikTok trends → Run workflow.
5. Confirm the run succeeded and the date in `data/uk-tiktok-trends.json` changed.

The website falls back to its previous dated snapshot when a fresh feed is unavailable. A daily run cannot succeed without a working authorised data source and token. Scraping TikTok may be restricted by its terms, and the third-party actor can change or stop working. The run limits are not a monthly spending cap.
