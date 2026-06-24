import json
import os
from datetime import datetime
from pathlib import Path

import requests
from bs4 import BeautifulSoup

URL = "https://peoplefestival.berlin/participants"
SNAPSHOT_FILE = Path("data/participants.json")


def extract_participants():
    response = requests.get(URL, timeout=30)
    response.raise_for_status()
    soup = BeautifulSoup(response.text, "html.parser")

    participants = set()
    for tag in soup.find_all(["li", "a", "div"]):
        text = tag.get_text(strip=True)
        if text.startswith("+") and len(text) < 80:
            participants.add(text)

    return participants


def load_previous():
    if not SNAPSHOT_FILE.exists():
        return {}
    return json.loads(SNAPSHOT_FILE.read_text())


def save_snapshot(data, last_run):
    SNAPSHOT_FILE.parent.mkdir(exist_ok=True)
    artists = {k: v for k, v in data.items() if not k.startswith("_")}
    sorted_data = dict(sorted(artists.items(), key=lambda x: (x[1], x[0])))
    sorted_data["_last_run"] = last_run
    SNAPSHOT_FILE.write_text(json.dumps(sorted_data, indent=2, ensure_ascii=False))


def create_issue(new_people, last_run):
    token = os.environ.get("GITHUB_TOKEN")
    repo = os.environ.get("GITHUB_REPOSITORY")

    if not token or not repo:
        print("GitHub credentials unavailable.")
        return

    body = (
        f"New participants spotted at {last_run}:\n\n"
        + "\n".join(f"- {name}" for name in sorted(new_people))
    )

    requests.post(
        f"https://api.github.com/repos/{repo}/issues",
        headers={
            "Authorization": f"Bearer {token}",
            "Accept": "application/vnd.github+json",
        },
        json={
            "title": f"New PEOPLE Festival participants ({len(new_people)}) — {last_run}",
            "body": body,
        },
        timeout=30,
    )


def main():
    last_run = datetime.utcnow().strftime("%Y-%m-%d %H:%M UTC")
    current = extract_participants()
    previous = load_previous()

    new_people = sorted(current - set(previous.keys()))

    print(f"Previously known: {len(previous)}")
    print(f"Currently on site: {len(current)}")

    if new_people:
        print("New participants:")
        for name in new_people:
            print("-", name)
        create_issue(new_people, last_run)
    else:
        print("No new participants found.")

    updated = {**previous, **{name: last_run for name in new_people}}
    save_snapshot(updated, last_run)


if __name__ == "__main__":
    main()
