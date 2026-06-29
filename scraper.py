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
    sorted_data = dict(sorted(artists.items(), key=lambda x: (x[1]["first_seen"], x[0])))
    sorted_data["_last_run"] = last_run
    SNAPSHOT_FILE.write_text(json.dumps(sorted_data, indent=2, ensure_ascii=False))


def create_issue(new_people, removed_people, last_run):
    token = os.environ.get("GITHUB_TOKEN")
    repo = os.environ.get("GITHUB_REPOSITORY")

    if not token or not repo:
        print("GitHub credentials unavailable.")
        return

    sections = []
    if new_people:
        sections.append("**New participants:**\n" + "\n".join(f"- {n}" for n in sorted(new_people)))
    if removed_people:
        sections.append("**Removed participants:**\n" + "\n".join(f"- {n}" for n in sorted(removed_people)))

    body = f"Changes spotted at {last_run}:\n\n" + "\n\n".join(sections)

    title_parts = []
    if new_people:
        title_parts.append(f"+{len(new_people)}")
    if removed_people:
        title_parts.append(f"-{len(removed_people)}")

    requests.post(
        f"https://api.github.com/repos/{repo}/issues",
        headers={
            "Authorization": f"Bearer {token}",
            "Accept": "application/vnd.github+json",
        },
        json={
            "title": f"PEOPLE Festival participants changed ({', '.join(title_parts)}) — {last_run}",
            "body": body,
        },
        timeout=30,
    )


def main():
    last_run = datetime.now().strftime("%Y-%m-%d %H:%M MEST")
    current = extract_participants()
    previous = load_previous()

    known = {k: v for k, v in previous.items() if not k.startswith("_")}

    new_people = sorted(current - set(known.keys()))
    removed_people = sorted(set(known.keys()) - current)

    print(f"Previously known: {len(known)}")
    print(f"Currently on site: {len(current)}")

    if new_people:
        print("New participants:")
        for name in new_people:
            print("-", name)

    if removed_people:
        print("Removed participants:")
        for name in removed_people:
            print("-", name)

    if new_people or removed_people:
        create_issue(new_people, removed_people, last_run)
    else:
        print("No changes found.")

    # Keep all artists, mark removed ones
    updated = dict(known)
    for name in new_people:
        updated[name] = {"first_seen": last_run, "removed": None}
    for name in removed_people:
        updated[name]["removed"] = last_run

    save_snapshot(updated, last_run)


if __name__ == "__main__":
    main()
