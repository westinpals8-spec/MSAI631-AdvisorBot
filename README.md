# MSAI631 Advisor Bot

A simple traditional (non-LLM) chatbot built on the
[Microsoft Bot Framework](https://dev.botframework.com/) Python SDK.
Submitted for **MSAI631 - Natural Language Processing**, University
of the Cumberlands.

The bot extends the official `EchoBot` sample into a domain-specific
**academic advisor** that answers common questions about the MS in
Artificial Intelligence program. Intent resolution uses keyword scoring
with `difflib` fuzzy matching - no LLM, no external API calls.

## Capabilities

- Program overview and credit-hour summary
- Required-course list and per-course descriptions (`MSAI500`-`MSAI690`)
- Capstone expectations
- Typical career outcomes
- Graceful fallback for malformed, empty, or out-of-domain input
- Built-in `help` command that lists everything the bot can do

## Architecture

```
user text
   |
   v
+-----------------+     +-----------------+     +------------------+
| preprocess      | --> | intent scoring  | --> | response policy  |
| (lowercase,     |     | (keywords +     |     | (canned reply or |
|  strip punct,   |     |  fuzzy match)   |     |  course catalog) |
|  tokenize)      |     +-----------------+     +------------------+
+-----------------+              |
                                  v
                          score < threshold? --> fallback message
```

All NLP logic lives in `bots/advisor_bot.py`. The Bot Framework
plumbing (`app.py`, `config.py`) is unchanged from the EchoBot sample
so the project can be tested with the standard Bot Framework Emulator.

## Setup

```bash
conda create --name MSAI631_MBF python==3.8.2
conda activate MSAI631_MBF
pip install -r requirements.txt
python app.py
```

Then open the [Bot Framework Emulator](https://github.com/microsoft/botframework-emulator/releases),
click **Open Bot**, and connect to:

```
http://localhost:3978/api/messages
```

## Tests

The intent logic is exercised by a small `unittest` suite that runs
without the Bot Framework runtime:

```bash
python tests/test_advisor_bot.py
```

## Project layout

```
MSAI631-AdvisorBot/
  app.py                  # aiohttp web server + Bot Framework adapter
  config.py               # port + app-id config
  requirements.txt
  bots/
    __init__.py
    advisor_bot.py        # intents, scoring, response policy
  tests/
    __init__.py
    test_advisor_bot.py   # unittest suite
  README.md
  .gitignore
```

## License

MIT. See file headers.
