# reddit-cli

Search and read Reddit from your terminal. No login, no API key, no scraping headaches.

Reddit blocks most scrapers and shut down free API access. `reddit-cli` sidesteps all of that by querying [Arctic Shift](https://github.com/ArthurHeitmann/arctic_shift), a free, community-run archive mirror of Reddit — near-live data (usually minutes behind reddit.com) with full history back to 2005.

It's a single Python file, standard library only. No dependencies, nothing to configure.

## Features

- **Keyword search** across any subreddits, full history back to 2005
- **Read full threads** — post body plus top comments, score-sorted
- **Search comment bodies**, not just post titles
- **User lookup** — anyone's recent posts and comments
- **Browse** the newest posts in a subreddit
- **Date-bounded search** (`--after` / `--before`)
- **Agent-friendly** — stable, greppable plain-text output; no auth tokens to manage, so it drops straight into scripts and AI agent toolchains

## Install

```bash
curl -sL https://raw.githubusercontent.com/dustindog101/reddit-cli/main/reddit -o ~/.local/bin/reddit
chmod +x ~/.local/bin/reddit
```

(make sure `~/.local/bin` is on your `PATH`. Or `git clone` the repo and symlink `reddit` anywhere on your `PATH`.)

Requires Python 3. That's it.

## Usage

```bash
# keyword search across subreddits
reddit search "standing desk" -s productivity,BIFL

# newest posts in a subreddit
reddit browse -s neovim -n 10

# full thread: post body + top comments
reddit thread k7x2m9p
reddit thread https://www.reddit.com/r/python/comments/k7x2m9p/...

# search comment bodies
reddit comments "battery life" -s thinkpad

# a user's recent posts and comments
reddit user spez -n 10

# date-bounded search
reddit search "rust async" -s rust --after 2024-01-01 --before 2024-06-01
```

## Commands

| Command | What it does |
|---|---|
| `reddit search "query" -s sub1,sub2 [-n 25] [--after DATE] [--before DATE]` | Keyword search inside subreddits |
| `reddit browse -s sub1,sub2 [-n 25]` | Newest posts in subreddits |
| `reddit thread <post_id\|url> [-n 30]` | Post body + top comments, score-sorted |
| `reddit comments "query" -s sub [-n 25]` | Search comment bodies |
| `reddit user <username> [-n 25]` | Recent posts and comments by a user |

Dates use `YYYY-MM-DD` and are UTC.

## Notes and limitations

- **Keyword search requires `-s subreddit`.** The archive has no global keyword index, so pass every subreddit relevant to your topic, comma-separated — the tool fans out and dedupes.
- **Post scores are unreliable.** The archive ingests posts before votes settle, so most scores read 0 or 1. Comment counts are always accurate; use those (and comment scores) to judge traction.
- **Be polite.** Arctic Shift is volunteer-run. The tool pauses briefly between requests and backs off on rate limits — don't raise the limits or parallelize aggressively.
- **Removed content.** The archive captures posts at submission time, so some results may have been removed by moderators since. Cross-check the permalink when it matters.

## Why not just use the Reddit API?

Reddit's API now requires an approved OAuth app for almost everything, and anonymous endpoints are blocked for most IPs. Scraping HTML hits login walls and bot challenges. This tool needs none of that — one file, zero setup, works everywhere.

## License

MIT — see [LICENSE](LICENSE).
