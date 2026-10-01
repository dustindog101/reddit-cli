# reddit-cli

Search and read Reddit from the terminal — no login, no API key.

Powered by the [Arctic Shift](https://github.com/ArthurHeitmann/arctic_shift) archive API: free, unauthenticated, near-live data (usually minutes behind reddit.com) with full history back to 2005. Python 3, standard library only, no dependencies.

## Install

```bash
curl -sL https://raw.githubusercontent.com/<you>/reddit-cli/main/reddit -o /usr/local/bin/reddit
chmod +x /usr/local/bin/reddit
```

## Usage

```bash
# keyword search across subreddits (subreddit scope is required by the API)
reddit search "age of hemp" -s vaporents,drdabberofficial

# newest posts in a subreddit
reddit browse -s drdabberofficial -n 10

# full thread: post body + top comments, score-sorted
reddit thread 1lukz0y
reddit thread https://www.reddit.com/r/vaporents/comments/1qva8r1/...

# search comment bodies
reddit comments "shipping" -s vaporents

# a user's recent posts and comments
reddit user spez -n 10

# date-bounded search
reddit search "switch 2" -s drdabberofficial --after 2025-01-01
```

## Notes

- Keyword search needs `-s subreddit` — the archive has no global keyword index. Pass several subs comma-separated to cover a topic.
- Post scores are unreliable (the archive captures posts before votes settle); comment counts are always accurate.
- Arctic Shift is a volunteer-run service: the tool pauses briefly between requests and backs off on rate limits. Don't hammer it.

## License

MIT — see [LICENSE](LICENSE).
