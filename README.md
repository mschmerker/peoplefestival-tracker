# PEOPLE Festival Participant Tracker

Tracks additions to:

https://peoplefestival.berlin/participants

## Features

- Runs automatically every 6 hours
- Stores participant snapshot in Git
- Detects newly added participants
- Creates GitHub Issues when new participants appear
- Manual execution via GitHub Actions

## Setup

1. Create a new GitHub repository.
2. Copy all files into the repository.
3. Push to GitHub.

No additional secrets are required.

The built-in `GITHUB_TOKEN` is sufficient for:
- committing updates
- creating issues

## Manual Run

Actions → Track PEOPLE Festival Participants → Run workflow

## Schedule

Every 6 hours:

```cron
0 */6 * * *
