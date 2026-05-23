# Copyright (c) Westin Pals. Course: MSAI631, University of the Cumberlands.
# Licensed under the MIT License.

import os


class DefaultConfig:
    """Bot configuration. PORT defaults to 3978 (the port the Bot
    Framework Emulator looks for at http://localhost:3978/api/messages).
    APP_ID / APP_PASSWORD can stay empty for local development; they are
    only required when the bot is registered with Azure Bot Service."""

    PORT = int(os.environ.get("PORT", 3978))
    APP_ID = os.environ.get("MicrosoftAppId", "")
    APP_PASSWORD = os.environ.get("MicrosoftAppPassword", "")
