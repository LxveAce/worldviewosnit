import urllib.request
import urllib.error
import ssl
import json
import time

ctx = ssl.create_default_context()

USERNAME = "juanes2794"
results = {}

PLATFORMS = [
    ("Twitter/X", f"https://x.com/{USERNAME}"),
    ("Instagram", f"https://www.instagram.com/{USERNAME}/"),
    ("Reddit", f"https://www.reddit.com/user/{USERNAME}"),
    ("TikTok", f"https://www.tiktok.com/@{USERNAME}"),
    ("YouTube", f"https://www.youtube.com/@{USERNAME}"),
    ("Pinterest", f"https://www.pinterest.com/{USERNAME}/"),
    ("Twitch", f"https://www.twitch.tv/{USERNAME}"),
    ("Medium", f"https://medium.com/@{USERNAME}"),
    ("Dev.to", f"https://dev.to/{USERNAME}"),
    ("Keybase", f"https://keybase.io/{USERNAME}"),
    ("Gravatar", f"https://gravatar.com/{USERNAME}"),
    ("About.me", f"https://about.me/{USERNAME}"),
    ("Linktree", f"https://linktr.ee/{USERNAME}"),
    ("DockerHub", f"https://hub.docker.com/u/{USERNAME}"),
    ("PyPI", f"https://pypi.org/user/{USERNAME}/"),
    ("RubyGems", f"https://rubygems.org/profiles/{USERNAME}"),
    ("Hackernews", f"https://news.ycombinator.com/user?id={USERNAME}"),
    ("Kaggle", f"https://www.kaggle.com/{USERNAME}"),
    ("Replit", f"https://replit.com/@{USERNAME}"),
    ("CodePen", f"https://codepen.io/{USERNAME}"),
    ("GitLab", f"https://gitlab.com/{USERNAME}"),
    ("Bitbucket", f"https://bitbucket.org/{USERNAME}/"),
    ("SourceForge", f"https://sourceforge.net/u/{USERNAME}/"),
    ("npm", f"https://www.npmjs.com/~{USERNAME}"),
    ("Patreon", f"https://www.patreon.com/{USERNAME}"),
    ("Behance", f"https://www.behance.net/{USERNAME}"),
    ("Dribbble", f"https://dribbble.com/{USERNAME}"),
    ("Flickr", f"https://www.flickr.com/people/{USERNAME}/"),
    ("Vimeo", f"https://vimeo.com/{USERNAME}"),
    ("SoundCloud", f"https://soundcloud.com/{USERNAME}"),
    ("Spotify", f"https://open.spotify.com/user/{USERNAME}"),
    ("Steam", f"https://steamcommunity.com/id/{USERNAME}"),
    ("Xbox Gamertag", f"https://www.xboxgamertag.com/search/{USERNAME}"),
    ("Telegram", f"https://t.me/{USERNAME}"),
    ("Signal", f"https://signal.me/#{USERNAME}"),
    ("Discord (via search)", f"https://discord.com/users/{USERNAME}"),
    ("Mastodon", f"https://mastodon.social/@{USERNAME}"),
    ("Threads", f"https://www.threads.net/@{USERNAME}"),
    ("Facebook", f"https://www.facebook.com/{USERNAME}"),
    ("LinkedIn", f"https://www.linkedin.com/in/{USERNAME}"),
    ("Crunchbase", f"https://www.crunchbase.com/person/{USERNAME}"),
    ("HackerOne", f"https://hackerone.com/{USERNAME}"),
    ("BugCrowd", f"https://bugcrowd.com/{USERNAME}"),
    ("Tryhackme", f"https://tryhackme.com/p/{USERNAME}"),
    ("HackTheBox", f"https://app.hackthebox.com/users/{USERNAME}"),
]

print(f"=== USERNAME OSINT: {USERNAME} ===")
print(f"Testing {len(PLATFORMS)} platforms...\n")

found = []
not_found = []
errors = []

for platform, url in PLATFORMS:
    try:
        req = urllib.request.Request(url, headers={
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
            "Accept-Language": "en-US,en;q=0.9",
        })
        resp = urllib.request.urlopen(req, timeout=10, context=ctx)
        body = resp.read(10000).decode("utf-8", errors="replace")
        status = resp.status

        # Check if it's a real profile or a redirect/404 page
        is_404_page = any(x in body.lower() for x in [
            "page not found", "user not found", "doesn't exist",
            "this page isn't available", "sorry, this page",
            "no user found", "404", "not found",
            "this account doesn't exist", "hmm...this page",
        ])

        if status == 200 and not is_404_page:
            print(f"  [FOUND]  {platform:20} => {url}")
            found.append({"platform": platform, "url": url, "status": status})
        else:
            not_found.append({"platform": platform, "url": url, "status": status, "soft_404": is_404_page})

    except urllib.error.HTTPError as e:
        if e.code == 404:
            not_found.append({"platform": platform, "url": url, "status": 404})
        elif e.code == 429:
            errors.append({"platform": platform, "url": url, "status": 429, "note": "rate limited"})
            print(f"  [LIMIT] {platform:20} => rate limited")
        else:
            not_found.append({"platform": platform, "url": url, "status": e.code})
    except Exception as e:
        err_str = str(e)[:60]
        errors.append({"platform": platform, "url": url, "error": err_str})
    time.sleep(0.5)

print(f"\n{'='*60}")
print(f"RESULTS: {len(found)} found / {len(not_found)} not found / {len(errors)} errors")
print(f"{'='*60}")

if found:
    print("\n[!!!] ACCOUNTS FOUND:")
    for f in found:
        print(f"  {f['platform']:20} => {f['url']}")

results = {
    "username": USERNAME,
    "total_tested": len(PLATFORMS),
    "found": found,
    "not_found_count": len(not_found),
    "errors": errors,
}

with open(r"C:\Users\mmrla\worldviewosnit\logs\username_osint.json", "w", encoding="utf-8") as f:
    json.dump(results, f, indent=2)
print("\nSaved to logs/username_osint.json")
