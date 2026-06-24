import json
import os
from datetime import date
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


def save_snapshot(data):
    SNAPSHOT_FILE.parent.mkdir(exist_ok=True)
    sorted_data = dict(sorted(data.items(), key=lambda x: (x[1], x[0])))
    SNAPSHOT_FILE.write_text(json.dumps(sorted_data, indent=2, ensure_ascii=False))


def create_issue(new_people, today):
    token = os.environ.get("GITHUB_TOKEN")
    repo = os.environ.get("GITHUB_REPOSITORY")

    if not token or not repo:
        print("GitHub credentials unavailable.")
        return

    body = (
        f"New participants spotted on {today}:\n\n"
        + "\n".join(f"- {name}" for name in sorted(new_people))
    )

    requests.post(
        f"https://api.github.com/repos/{repo}/issues",
        headers={
            "Authorization": f"Bearer {token}",
            "Accept": "application/vnd.github+json",
        },
        json={
            "title": f"New PEOPLE Festival participants ({len(new_people)}) — {today}",
            "body": body,
        },
        timeout=30,
    )


def main():
    today = date.today().isoformat()
    current = extract_participants()
    previous = load_previous()

    new_people = sorted(current - set(previous.keys()))

    print(f"Previously known: {len(previous)}")
    print(f"Currently on site: {len(current)}")

    if new_people:
        print("New participants:")
        for name in new_people:
            print("-", name)
        create_issue(new_people, today)
    else:
        print("No new participants found.")

    updated = {**previous, **{name: today for name in new_people}}
    save_snapshot(updated)


if __name__ == "__main__":
    main()
