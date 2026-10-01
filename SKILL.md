# reddit skill

Search and read Reddit without logging in, via the Arctic Shift archive API
(`https://arctic-shift.photon-reddit.com/api`). Free, no key, no account.
Data is near-live (usually minutes behind reddit.com) with history back to 2005.

The CLI lives at `~/workspace/bin/reddit` (Python 3, stdlib only).

## Commands

```bash
reddit search "keywords" -s sub1,sub2 [-n 25] [--after YYYY-MM-DD] [--before YYYY-MM-DD]
reddit browse -s sub1,sub2 [-n 25]
reddit thread <post_id|full reddit url> [-n 30]
reddit comments "keywords" -s sub [-n 25]
reddit user <username> [-n 25]
```

## Rules that matter

- **Keyword search REQUIRES `-s subreddit`.** The archive has no global keyword
  index (`query` without `subreddit`/`author` returns a 400). To cover a topic,
  pass several relevant subs comma-separated; the CLI fans out one request per
  sub and dedupes.
- **Scores are unreliable.** The archive captures posts before votes settle, so
  most scores read 0/1. Use `num_comments` (always accurate) and comment scores
  for signal, not post scores.
- **Be polite.** It's a volunteer-run service. The CLI already sleeps 0.5s
  between subreddits and backs off on 422/429. Don't parallelize or raise
  limits aggressively.
- **Deleted/removed content:** the archive ingests at submission time, so some
  results may be posts later removed by mods. If a result matters, cross-check
  the permalink.

## When to use this vs web search

- Use `reddit` for: owner opinions, troubleshooting threads, "is X legit"
  checks, subreddit consensus, user histories.
- Use `browser.search` for: breaking news, or when you need Google's/Brave's
  index of Reddit (sometimes finds threads the archive's keyword search
  misses due to phrasing).
- If `reddit search` returns nothing, try alternate phrasings and neighboring
  subreddits before concluding nothing exists.

## Output

One block per result: date, subreddit, score, comment count, author, title,
selftext snippet, and a constructed permalink
(`https://reddit.com/r/<sub>/comments/<id>/`). `thread` prints the post body
plus top comments score-sorted. Dates are UTC.
