# PEOPLE Festival Participant Tracker

Tracks additions to:
https://peoplefestival.berlin/participants

## Features

- Runs automatically every hour
- Stores participant snapshot in Git
- Only tracks artists (all names start with `+`)
- Records the exact date and time each artist was first spotted
- Creates GitHub Issues when new participants appear
- Manual execution via GitHub Actions

## Snapshot format

Artists are sorted by first seen date, then alphabetically:

```json
{
  "+ Actress": "2026-06-20 08:00 UTC",
  "+ Blawan": "2026-06-22 14:00 UTC",
  "+ Shackleton": "2026-06-24 13:45 UTC",
  "_last_run": "2026-06-24 13:45 UTC"
}
```

## Setup

1. Create a new GitHub repository.
2. Copy all files into the repository.
3. Push to GitHub.

No additional secrets are required. The built-in `GITHUB_TOKEN` is sufficient for committing updates and creating issues.

## Manual run

Actions → Track PEOPLE Festival Participants → Run workflow

## Schedule

Every hour:

```cron
0 * * * *
```
