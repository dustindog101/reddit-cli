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
- **Date-bounded search, browse, and user lookup** (`--after` / `--before`, dates or unix seconds)
- **Agent-friendly** — plain text by default, or JSON lines with global `--json`; no auth tokens to manage, so it drops straight into scripts and AI agent toolchains

## Install

```bash
mkdir -p ~/.local/bin
curl -sL https://raw.githubusercontent.com/dustindog101/reddit-cli/main/reddit -o ~/.local/bin/reddit
chmod +x ~/.local/bin/reddit
```

For a checkout you can update with Git:

```bash
mkdir -p ~/coding/projects ~/.local/bin
git clone https://github.com/dustindog101/reddit-cli.git ~/coding/projects/reddit-cli
ln -s ~/coding/projects/reddit-cli/reddit ~/.local/bin/reddit
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
| `reddit browse -s sub1,sub2 [-n 25] [--after DATE] [--before DATE]` | Newest posts in subreddits |
| `reddit thread <post_id\|url> [-n 30]` | Post body + top comments, score-sorted |
| `reddit comments "query" -s sub [-n 25]` | Search comment bodies |
| `reddit user <username> [-n 25] [--after DATE] [--before DATE]` | Recent posts and comments by a user |

`--after` and `--before` accept UTC dates (`YYYY-MM-DD`, midnight UTC) or
integer unix timestamps in seconds. `user` applies the window to both posts
and comments. Limits and archive coverage still apply; a window does not imply
an exhaustive export.

```bash
# Historical window in r/UMBC
reddit browse -s UMBC --after 2024-01-01 --before 2024-02-01 --json

# Last seven days, using portable Python timestamp calculation
now=$(python3 -c 'import time; print(int(time.time()))')
reddit --json browse -s UMBC --after "$((now - 7 * 86400))" --before "$now"

# The same bounds work for a user's posts AND comments
reddit user spez --after 1704067200 --before 1706745600 --json
```

## JSON lines and errors

Every command accepts `--json`, before or after the command. It emits one JSON
object per post or comment with no headings or blank lines. Empty results produce
no stdout. JSON preserves complete bodies and embedded newlines (escaped on one
line), so callers can process archive records without parsing the text display.

All objects contain `id`, `kind`, `subreddit`, `author`, `title`, `body`,
`created_utc`, `permalink`, `score`, and `num_comments`:

- Posts use `id: "t3_<id>"`, `kind: "post"`, and `body` from `selftext`.
- Comments use `id: "t1_<id>"`, `kind: "comment"`; `title` and `num_comments`
  are `null` because those fields do not apply to comments.
- `created_utc` is unix seconds. Permalinks start with `https://www.reddit.com/`.
  Unavailable archive fields are `null`; missing bodies are empty strings.
- `thread --json` emits the post followed by comments sorted by score.
  `user --json` emits posts followed by comments.

Network, HTTP, and API errors exit with status 1 and a message on stderr. Error
messages never go to stdout. Requests retain bounded retries and rate-limit
backoff. If a later request fails, stdout may already contain earlier records;
check the exit status before treating an export as complete.

## Development checks

The CLI and regression tests use only the Python standard library:

```bash
python3 -B -m unittest discover -s tests -v
reddit browse -s UMBC -n 3 --after 2024-01-01 --before 2024-02-01 --json
```

## Notes and limitations

- **Keyword search requires `-s subreddit`.** The archive has no global keyword index, so pass every subreddit relevant to your topic, comma-separated — the tool fans out and dedupes.
- **Post scores are unreliable.** The archive ingests posts before votes settle, so most scores read 0 or 1. Comment counts are always accurate; use those (and comment scores) to judge traction.
- **Be polite.** Arctic Shift is volunteer-run. The tool pauses briefly between requests and backs off on rate limits — don't raise the limits or parallelize aggressively.
- **Removed content.** The archive captures posts at submission time, so some results may have been removed by moderators since. Cross-check the permalink when it matters.

## Why not just use the Reddit API?

Reddit's API now requires an approved OAuth app for almost everything, and anonymous endpoints are blocked for most IPs. Scraping HTML hits login walls and bot challenges. This tool needs none of that — one file, zero setup, works everywhere.

## License

MIT — see [LICENSE](LICENSE).
