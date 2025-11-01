# vmt

transcribe and translate discord voice messages

[![Deploy on Railway](https://railway.com/button.svg)](https://railway.com/deploy/LBtckT?referralCode=originoid&utm_medium=integration&utm_source=template&utm_campaign=generic)

if you don't want to self-host, we offer our [own free instance](https://discord.com/oauth2/authorize?client_id=1434011906829455451) you're free to use to add to your servers or as an app.

## features

- transcribes voice messages using google speech recognition
- translates to 30+ languages via deepl api
- works in servers, dms, and group chats
- public/private response options
- context menu support (right-click voice messages)

## setting up your discord app

before deploying or running locally, you need to configure your discord application:

1. go to the [discord developer portal](https://discord.com/developers/applications) and create a new application (or select an existing one)
2. navigate to **installation** in the sidebar
3. under **installation contexts**, enable both:
   - **user install** - allows users to install the app to their account for personal use
   - **guild install** - allows the app to be installed to servers
4. under **default install settings**, make sure `applications.commands` is selected for both **guild install** and **user install**
5. navigate to **bot** in the sidebar
6. under **privileged gateway intents**, enable:
   - **message content intent** - required to read voice message content
   - **server members intent** - required for server functionality
7. copy your **bot token** from this page (you'll need it for the environment variables)
8. copy the **install link** from the installation page to add the bot to your account or server

## deployment

### railway (recommended)

this project is configured to deploy on [Railway](https://railway.com?referralCode=originoid) in 1-click and automatically handles ffmpeg installation.
to setup via railway, hit the "deploy on railway" button at the top of this readme

(you'll also get $20 in railway credits upon signup by using our link :3)

### required environment variables

- `BOT_TOKEN` - your discord bot token (from [discord developer portal](https://discord.com/developers/applications))
- `DEEPL_API_KEY` - your deepl api key (from [deepl](https://www.deepl.com/pro-api))
- `DEEPL_FREE_API` - set to `true` if using deepl's free tier, `false` else.
  - deepl uses different api endpoints for free users (`api-free.deepl.com` vs `api.deepl.com`)
- `MAX_VOICE_MESSAGE_DURATION` - maximum duration in seconds (default: `60`)

### local setup

1. **clone the repo**

```bash
git clone https://github.com/originoidco/vmt.git
cd vmt
```

2. **install dependencies**
   you'll also need python installed, i'm personally using python 3.13.3:

```bash
pip install -r requirements.txt
```

**installing ffmpeg:**

- **macos:** `brew install ffmpeg`
- **ubuntu/debian:** `sudo apt-get install ffmpeg`
- **windows:** download from [ffmpeg.org](https://ffmpeg.org/download.html); you can also use `choco install ffmpeg` if you have [chocolately](https://chocolatey.org/)

3. **create `.env` file**

```bash
cp .env.example .env
```

edit `.env`:

```env
BOT_TOKEN=your_bot_token_here
DEEPL_API_KEY=your_deepl_key_here
DEEPL_FREE_API=true
MAX_VOICE_MESSAGE_DURATION=60
```

4. **run the app**

```bash
cd src
python main.py
# or python ./src/main.py, whatever you prefer
```

## usage

### transcribing voice messages

1. right-click (or long-press on mobile) a voice message
2. select **apps → voice message**
3. use `/transcribe` command
4. optionally add a language code to translate (e.g., `en` for english, `es` for spanish)

### commands

- `/transcribe [language]` - transcribe the selected voice message, optionally translate to specified language
- `/languages` - view all supported languages and their codes
- `/help` - show command help and usage examples

## license

GPL-3.0

## credits

authored by [@dromzeh](https://github.com/dromzeh) <[marcel@originoid.co](mailto:marcel@originoid.co)>
