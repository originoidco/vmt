# vmt

transcribe and translate discord voice messages

## setup

1. clone the repo

```bash
git clone https://github.com/originoidco/vmt.git
cd vmt
```

2. install dependencies (and ffmpeg!)

```bash
pip install -r requirements.txt
```

3. create `.env` file

```bash
cp .env.example .env
```

edit `.env`:

```env
BOT_TOKEN=your_bot_token
DEEPL_API_KEY=your_deepl_key
DEEPL_FREE_API=true
MAX_VOICE_MESSAGE_DURATION=60
```

4. run

```bash
cd src
python main.py
```

## deployment

this project is configured to deploy on [Railway](https://railway.app) out of the box. just connect your repository and set the required environment variables in the Railway dashboard.

## usage

1. right-click a voice message → **select voice message**
2. use `/transcribe` to transcribe it
3. add a language code to translate (optional)

### commands

- `/transcribe` - transcribe selected voice message
- `/languages` - view all supported languages
- `/help` - show help

## features

- transcribes voice messages using google speech recognition
- translates via deepl api
- works in servers, dms, and group chats
- public/private responses

## license

GPL-3.0

## credits

[@dromzeh](https://github.com/dromzeh) + [@strazto](https://instagram.com/strazto)
