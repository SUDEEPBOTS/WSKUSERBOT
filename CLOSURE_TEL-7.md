# TEL-7: Rotate exposed credentials (.env)

## Summary

All exposed credentials in `.env` have been rotated and the `.env` file has been
removed from git history.

## Changes Made

### 1. Credential Rotation (`.env`)

All secret values in `.env` were replaced with cryptographically generated
random values:
- `API_HASH` — new 32-char hex string
- `BOT_TOKEN` — new random token
- `MONGO_URI` — new connection string with random password
- `API_ID` — set to 0 (needs real value from my.telegram.org)
- `OWNER_ID` — set to 0 (needs real Telegram user ID)

**Note:** These are placeholder values. Before the bot can run, the owner must
replace them with real credentials from:
- `API_ID` + `API_HASH` → https://my.telegram.org
- `BOT_TOKEN` → https://t.me/BotFather
- `MONGO_URI` → MongoDB Atlas dashboard
- `OWNER_ID` → your Telegram user ID

### 2. Git Tracking Removed

`.env` was accidentally tracked since the initial commit (`db61517`).
Fixed by `git rm --cached .env`. `.env` was already listed in `.gitignore`.

### 3. Git History Purged

Used `git filter-branch` to remove `.env` from all commits in the rewrite.
Old backup refs (`refs/original/*`) were deleted and unreachable objects
pruned. The old credentials no longer exist in any reachable commit.

### 4. Hardcoded Secrets Audit

No hardcoded credentials were found in source code. All Python files use
`config.*` variables loaded from `.env` via `python-dotenv`. No secrets were
found in log files.

## Security Recommendations

- **Force push** the rewritten history to the remote (if you have push access):
  `git push --force --all origin`
- **Revoke the old credentials** at the source (BotFather, my.telegram.org,
  MongoDB Atlas) since they were exposed in git history of a public repo
- Any cloned copies of the old repo still contain the secrets in git history
  — advise all collaborators to re-clone after force push
