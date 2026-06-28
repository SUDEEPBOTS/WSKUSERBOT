<div align="center">

# 🧩 WSKUSERBOT

### ⚡ WordSeek Auto-Solver for Telegram

<p>
  <img src="https://readme-typing-svg.demolab.com?font=Fira+Code&weight=600&size=22&pause=1000&color=6C63FF&center=true&vCenter=true&multiline=true&repeat=true&width=500&height=60&lines=Smart+Entropy-Based+Word+Solver;Wins+WordSeek+in+Fewest+Attempts+🏆" alt="Typing SVG" />
</p>

<p>
  <a href="https://github.com/SUDEEPBOTS/WSKUSERBOT/stargazers"><img src="https://img.shields.io/github/stars/SUDEEPBOTS/WSKUSERBOT?style=for-the-badge&logo=github&color=6C63FF&logoColor=white" alt="Stars"></a>
  <a href="https://github.com/SUDEEPBOTS/WSKUSERBOT/network/members"><img src="https://img.shields.io/github/forks/SUDEEPBOTS/WSKUSERBOT?style=for-the-badge&logo=git&color=FF6B6B&logoColor=white" alt="Forks"></a>
  <a href="https://github.com/SUDEEPBOTS/WSKUSERBOT/issues"><img src="https://img.shields.io/github/issues/SUDEEPBOTS/WSKUSERBOT?style=for-the-badge&logo=github&color=FFC93C&logoColor=white" alt="Issues"></a>
  <a href="https://github.com/SUDEEPBOTS/WSKUSERBOT"><img src="https://img.shields.io/github/repo-size/SUDEEPBOTS/WSKUSERBOT?style=for-the-badge&logo=github&color=1DB954&logoColor=white" alt="Repo Size"></a>
</p>

<p>
  <img src="https://img.shields.io/badge/Python-3.11-3776AB?style=flat-square&logo=python&logoColor=white" alt="Python">
  <img src="https://img.shields.io/badge/Pyrogram-Pyrofork-FF4500?style=flat-square&logo=telegram&logoColor=white" alt="Pyrogram">
  <img src="https://img.shields.io/badge/MongoDB-Atlas-47A248?style=flat-square&logo=mongodb&logoColor=white" alt="MongoDB">
  <img src="https://img.shields.io/badge/Docker-Ready-2496ED?style=flat-square&logo=docker&logoColor=white" alt="Docker">
</p>

---

<img src="https://raw.githubusercontent.com/andreasbm/readme/master/assets/lines/rainbow.png" width="100%">

</div>

## 🎯 What is WSKUSERBOT?

**WSKUSERBOT** is a powerful Telegram userbot that **automatically plays and wins** the [@WordSeekBot](https://t.me/WordSeekBot) word game. It uses an **entropy-based smart solver algorithm** that picks the optimal guess to split remaining candidates most evenly — winning games in the **fewest possible attempts**.

> 💡 Think of it as **Wordle on autopilot**, but for Telegram's WordSeek game!

<div align="center">
<img src="https://raw.githubusercontent.com/andreasbm/readme/master/assets/lines/colored.png" width="100%">
</div>

## ✨ Features

<table>
<tr>
<td>

### 🧠 Smart Solver
- Entropy-based word elimination algorithm
- Supports **4, 5, and 6 letter** word modes
- Pre-cached word lists for instant solving
- Optimal starter word selection

</td>
<td>

### 🤖 Auto Play
- Auto-starts games with `hupp` command
- Auto-reads WordSeek responses
- Auto-sends optimal guesses
- Configurable delay between guesses

</td>
</tr>
<tr>
<td>

### 📊 Stats & Tracking
- Win/loss tracking per user
- Streak & best streak records
- One-attempt win counter
- Export stats to file

</td>
<td>

### 👥 Multi-User Support
- Multiple user clients simultaneously
- Per-user session management
- MongoDB-powered persistence
- Owner-controlled bot management

</td>
</tr>
</table>

<div align="center">
<img src="https://raw.githubusercontent.com/andreasbm/readme/master/assets/lines/colored.png" width="100%">
</div>

## 🚀 Deployment

### 📋 Prerequisites

| Requirement | Details |
|:-----------:|:--------|
| 🐍 **Python** | `3.11+` |
| 🔑 **Telegram API** | Get from [my.telegram.org](https://my.telegram.org) |
| 🤖 **Bot Token** | Get from [@BotFather](https://t.me/BotFather) |
| 🍃 **MongoDB** | Free cluster at [MongoDB Atlas](https://www.mongodb.com/atlas) |

### ⚡ Quick Setup

```bash
# 1️⃣ Clone the repository
git clone https://github.com/SUDEEPBOTS/WSKUSERBOT.git
cd WSKUSERBOT

# 2️⃣ Install dependencies
pip install -r requirements.txt

# 3️⃣ Configure environment
cp sample.env .env
```

### 🔧 Environment Variables

```env
API_ID=12345                    # Telegram API ID
API_HASH=your_api_hash          # Telegram API Hash
BOT_TOKEN=123456:ABC-xyz        # Bot Token from BotFather
MONGO_URI=mongodb+srv://...     # MongoDB Connection URI
OWNER_ID=123456789              # Your Telegram User ID
```

### ▶️ Run the Bot

```bash
# Run directly
bash start

# Or with Docker 🐳
docker build -t wskuserbot .
docker run -d --env-file .env wskuserbot
```

<div align="center">
<img src="https://raw.githubusercontent.com/andreasbm/readme/master/assets/lines/colored.png" width="100%">
</div>

## 💬 Commands

### 🔒 Private Chat (DM)

| Command | Description |
|:--------|:-----------|
| `/start` | Start the bot & get welcome message |
| `.mode [4/5/6]` | Switch word length mode |
| `.delay [seconds]` | Set delay between guesses |
| `.stats` | View your game statistics |
| `.export` | Export stats as text file |
| `.das` | Show current session info |
| `.total` | View word count per mode |
| `.reset confirm` | Reset all your stats |
| `.id` | Get your Telegram ID |
| `.logout` | Delete session & stop games |

### 👥 Group Chat

| Command | Description |
|:--------|:-----------|
| `hupp` | Start auto-playing in this group |
| `bye` | Stop the current game |

<div align="center">
<img src="https://raw.githubusercontent.com/andreasbm/readme/master/assets/lines/colored.png" width="100%">
</div>

## 🏗️ Project Structure

```
WSKUSERBOT/
├── 📄 config.py              # Environment config loader
├── 🐳 Dockerfile             # Docker container setup
├── 📋 requirements.txt       # Python dependencies
├── 📋 sample.env             # Example environment file
├── ▶️  start                  # Startup script
│
└── WSKUSERBOT/               # Main package
    ├── 🔧 __init__.py        # Pyrogram client init
    ├── 🚀 __main__.py        # Bot entry point
    ├── 📊 logging.py         # Colored logging setup
    ├── 👥 user_manager.py    # Multi-user client manager
    ├── 🖼️ start.jpeg         # Welcome image
    │
    └── plugins/              # Bot plugins
        ├── 🎮 game.py        # Game session handler
        ├── 🧩 solver.py      # Entropy-based word solver
        ├── ⚙️ commands.py     # Command handlers
        └── 👋 start.py       # /start command
```

<div align="center">
<img src="https://raw.githubusercontent.com/andreasbm/readme/master/assets/lines/colored.png" width="100%">
</div>

## 🧠 How the Solver Works

```
┌─────────────────────────────────────────────────┐
│               ENTROPY SOLVER                     │
├─────────────────────────────────────────────────┤
│                                                  │
│  1. 📚 Load word list (4/5/6 letters)           │
│  2. 🎯 Pick optimal starter (letter frequency)  │
│  3. 📨 Send guess to WordSeek                   │
│  4. 📖 Read color-coded feedback                │
│  5. 🧮 Calculate entropy for each candidate     │
│  6. ✂️  Eliminate impossible words               │
│  7. 🔄 Pick next guess (max entropy split)      │
│  8. 🏆 Repeat until solved!                     │
│                                                  │
└─────────────────────────────────────────────────┘
```

> The solver picks the guess that **maximizes information gain** — splitting the remaining word pool as evenly as possible across all possible feedback patterns.

<div align="center">
<img src="https://raw.githubusercontent.com/andreasbm/readme/master/assets/lines/colored.png" width="100%">
</div>

## 🛡️ Tech Stack

<div align="center">
<p>
  <img src="https://skillicons.dev/icons?i=python,docker,mongodb,linux,git&theme=dark" alt="Tech Stack" />
</p>
</div>

| Technology | Purpose |
|:-----------|:--------|
| **Pyrofork** | Telegram MTProto client (Pyrogram fork) |
| **Motor** | Async MongoDB driver |
| **TgCrypto** | Fast Telegram encryption |
| **aiohttp** | Async HTTP requests |
| **Docker** | Containerized deployment |

<div align="center">
<img src="https://raw.githubusercontent.com/andreasbm/readme/master/assets/lines/colored.png" width="100%">
</div>

## 📜 License

This project is open source and available under the [MIT License](LICENSE).

---

<div align="center">

### ⭐ Star this repo if you found it useful!

<p>
  <img src="https://readme-typing-svg.demolab.com?font=Fira+Code&weight=500&size=18&pause=1000&color=6C63FF&center=true&vCenter=true&repeat=true&width=400&height=30&lines=Made+with+%E2%9D%A4%EF%B8%8F+by+SUDEEPBOTS" alt="Footer" />
</p>

<a href="https://github.com/SUDEEPBOTS">
  <img src="https://img.shields.io/badge/GitHub-SUDEEPBOTS-181717?style=for-the-badge&logo=github" alt="GitHub">
</a>
<a href="https://t.me/SUDEEPBOTS">
  <img src="https://img.shields.io/badge/Telegram-SUDEEPBOTS-26A5E4?style=for-the-badge&logo=telegram&logoColor=white" alt="Telegram">
</a>

</div>
