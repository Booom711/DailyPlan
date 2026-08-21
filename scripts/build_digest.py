#!/usr/bin/env python3
import argparse
import html
import json
import sys
from pathlib import Path


def clean_text(text, limit=200):
    if not text:
        return ""
    text = html.unescape(" ".join(str(text).split()))
    if len(text) <= limit:
        return text
    return text[: limit - 1] + "…"


def render_tweets(data, limit):
    tweets = []
    for builder in data.get("x") or []:
        name = builder.get("name", "")
        handle = builder.get("handle", "")
        for tweet in builder.get("tweets") or []:
            tweets.append(
                {
                    "name": name,
                    "handle": handle,
                    "text": tweet.get("text", ""),
                    "url": tweet.get("url", ""),
                    "likes": tweet.get("likes", 0),
                }
            )

    tweets.sort(key=lambda item: item["likes"], reverse=True)
    lines = ["### 推文精选"]
    if not tweets:
        lines.append("暂无推文。")
    for tweet in tweets[:limit]:
        label = f"{tweet['name']} (@{tweet['handle']})"
        if not tweet["handle"]:
            label = tweet["name"]
        lines.append(f"- **{label}**：{clean_text(tweet['text'], 180)}")
        lines.append(f"  {tweet['url']} · {tweet['likes']} 赞")
    return "\n".join(lines)


def render_blogs(data, limit):
    blogs = (data.get("blogs") or [])[:limit]
    lines = ["### 博客文章"]
    if not blogs:
        lines.append("暂无博客。")
    for blog in blogs:
        source = blog.get("name", "")
        title = blog.get("title", "")
        lines.append(f"- **{source}**：{title}")
        lines.append(f"  {blog.get('url', '')}")
        excerpt = clean_text(blog.get("content") or blog.get("description") or "", 160)
        if excerpt:
            lines.append(f"  {excerpt}")
    return "\n".join(lines)


def render_podcasts(data, limit):
    podcasts = (data.get("podcasts") or [])[:limit]
    lines = ["### 播客"]
    if not podcasts:
        lines.append("暂无播客。")
    for podcast in podcasts:
        lines.append(f"- **{podcast.get('name', '')}**：《{podcast.get('title', '')}》")
        lines.append(f"  {podcast.get('url', '')}")
    return "\n".join(lines)


def build_digest(data, tweet_limit=5, blog_limit=3, podcast_limit=2):
    stats = data.get("stats") or {}
    x_builders = stats.get("xBuilders", 0)
    total_tweets = stats.get("totalTweets", 0)
    blog_posts = stats.get("blogPosts", 0)
    podcast_episodes = stats.get("podcastEpisodes", 0)

    sections = [
        "## AI Builders 今日速报",
        "",
        f"今日共 {x_builders} 位创作者、{total_tweets} 条推文、{blog_posts} 篇博客、{podcast_episodes} 期播客。",
        "",
    ]

    has_content = bool(data.get("x")) or bool(data.get("blogs")) or bool(data.get("podcasts"))
    if not has_content:
        sections.append("今天暂时没有新的内容，明天再看。")
    else:
        sections.append(render_tweets(data, tweet_limit))
        sections.append("")
        sections.append(render_blogs(data, blog_limit))
        sections.append("")
        sections.append(render_podcasts(data, podcast_limit))

    return "\n".join(sections)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", required=True, help="Path to prepare-digest.js output JSON")
    parser.add_argument("--output", help="Optional path to write the digest markdown")
    parser.add_argument("--tweet-limit", type=int, default=5)
    parser.add_argument("--blog-limit", type=int, default=3)
    parser.add_argument("--podcast-limit", type=int, default=2)
    args = parser.parse_args()

    data = json.loads(Path(args.input).read_text(encoding="utf-8"))
    digest = build_digest(
        data,
        tweet_limit=args.tweet_limit,
        blog_limit=args.blog_limit,
        podcast_limit=args.podcast_limit,
    )

    if args.output:
        Path(args.output).write_text(digest + "\n", encoding="utf-8")
    else:
        print(digest)


if __name__ == "__main__":
    main()
