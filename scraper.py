import json
import os
import re
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

    # Try common patterns: links or list items
    for tag in soup.find_all(["li", "a", "div"]):
        text = tag.get_text(strip=True)

        # filter obvious junk
        if 2 < len(text) < 80:
            participants.add(text)

    return sorted(participants)


def load_previous():
    if not SNAPSHOT_FILE.exists():
        return []

    return json.loads(SNAPSHOT_FILE.read_text())


def save_snapshot(participants):
    SNAPSHOT_FILE.parent.mkdir(exist_ok=True)

    SNAPSHOT_FILE.write_text(
        json.dumps(participants, indent=2, ensure_ascii=False)
    )


def create_issue(new_people):
    token = os.environ.get("GITHUB_TOKEN")
    repo = os.environ.get("GITHUB_REPOSITORY")

    if not token or not repo:
        print("GitHub credentials unavailable.")
        return

    body = (
        "New participants were detected on "
        "https://peoplefestival.berlin/participants\n\n"
        + "\n".join(f"- {name}" for name in new_people)
    )

    requests.post(
        f"https://api.github.com/repos/{repo}/issues",
        headers={
            "Authorization": f"Bearer {token}",
            "Accept": "application/vnd.github+json",
        },
        json={
            "title": f"New PEOPLE Festival participants ({len(new_people)})",
            "body": body,
        },
        timeout=30,
    )


def main():
    current = extract_participants()
    previous = load_previous()

    previous_set = set(previous)
    current_set = set(current)

    new_people = sorted(current_set - previous_set)

    print(f"Previous count: {len(previous)}")
    print(f"Current count: {len(current)}")

    if new_people:
        print("New participants:")
        for name in new_people:
            print("-", name)

        create_issue(new_people)
    else:
        print("No new participants found.")

    save_snapshot(current)


if __name__ == "__main__":
    main()
