import os
from dotenv import load_dotenv

load_dotenv()

# Bot Configuration
DISCORD_TOKEN = os.getenv('DISCORD_TOKEN')
BOT_PREFIX = "!"

# Server Configuration
WELCOME_CHANNEL_ID = int(os.getenv('WELCOME_CHANNEL_ID', 0))
TICKET_CATEGORY_ID = int(os.getenv('TICKET_CATEGORY_ID', 0))
SUPPORT_ROLE_ID = int(os.getenv('SUPPORT_ROLE_ID', 0))
ADMIN_ROLE_ID = int(os.getenv('ADMIN_ROLE_ID', 1188874087901180012))
CLOSED_TICKET_CATEGORY_ID = int(os.getenv('CLOSED_TICKET_CATEGORY_ID', 1458624700321103995))
LOG_CHANNEL_ID = int(os.getenv('LOG_CHANNEL_ID', 1458628872143765577))

# Welcome Messages
PUBLIC_WELCOME_MESSAGE = os.getenv(
    'PUBLIC_WELCOME_MESSAGE',
    "Welcome {user_mention} to Thumblab 👋"
)

PRIVATE_WELCOME_MESSAGE = os.getenv(
    'PRIVATE_WELCOME_MESSAGE',
    """Hey {user_name},

Welcome to Thumblab 👋  
I’m Aleksnader, the one building Thumblab.

Thumblab is a tool I made because thumbnails were always a pain — either too expensive, too slow, or just not good enough.

You can try it here:
https://thumblab.app

If you want to understand how it works (or what it can / can’t do yet), the docs are here:
https://docs.thumblab.app
https://discord.thumblab.app

If you have any question or feedback, you can just open a ticket on the server. I read everything."""
)

DELAYED_DM_24H = os.getenv(
    'DELAYED_DM_24H',
    """Hey {user_name},

Just checking in.

Did you already try generating a thumbnail on Thumblab, or not yet?

No pressure at all — I’m mostly curious to know if it makes sense for you, or if something feels confusing or missing.

If you run into anything weird, feel free to ping me or open a ticket."""
)

DELAYED_DM_72H = os.getenv(
    'DELAYED_DM_72H',
    """Hey {user_name},

Small follow-up.

Most people who get value from Thumblab usually feel it after a few generations, not just one.  
It’s more about testing ideas quickly than getting a “perfect” image instantly.

If you tried it and something didn’t click, I’d honestly love to know why.  
And if you didn’t try yet, it’s still there whenever you need it."""
)

# Ticket System Messages
TICKET_OPEN_MESSAGE = os.getenv(
    'TICKET_OPEN_MESSAGE',
    "Hey {user_mention}, thanks for reaching out. Someone from the team will be with you shortly."
)

TICKET_CHANNEL_TOPIC = os.getenv(
    'TICKET_CHANNEL_TOPIC',
    "Support ticket — {user_name}"
)

TICKET_CLOSED_MESSAGE = os.getenv(
    'TICKET_CLOSED_MESSAGE',
    "This ticket is now closed. The channel will be deleted in a few seconds."
)

TICKET_BUTTON_LABEL = os.getenv('TICKET_BUTTON_LABEL', "🎫 Open Ticket")
TICKET_CLOSE_BUTTON_LABEL = os.getenv('TICKET_CLOSE_BUTTON_LABEL', "🔒 Close Ticket")

# Bot Status
BOT_ACTIVITY = os.getenv('BOT_ACTIVITY', "https://thumblab.app")

# Time delays (in seconds)
WELCOME_DELAY_24H = 24 * 60 * 60
WELCOME_DELAY_72H = 72 * 60 * 60
TICKET_CLOSE_DELAY = 5