# Discord Support Bot

A production-ready Discord support bot built with Python and discord.py v2.x. Features welcome messages, delayed DMs, and a complete ticket system with buttons and menus.

## Features

- 🎉 **Welcome System**
  - Public welcome messages in configurable channel
  - Private DM on member join
  - Automated DMs after 24 hours and 72 hours
  - Configurable messages and timing

- 🎫 **Ticket System**
  - Button-based ticket creation
  - Private ticket channels with controlled access
  - Support role permissions
  - One-click ticket closure with channel deletion

- 🛠️ **Bot Management**
  - Modular architecture using cogs
  - Admin commands for bot status and cog reloading
  - Comprehensive error handling
  - Configurable bot activity

## Setup

### 1. Prerequisites

- Python 3.8 or higher
- Discord account with server administrator permissions

### 2. Installation

1. **Clone or download this project**
2. **Create a virtual environment:**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```
3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

### 3. Discord Bot Setup

1. **Create a Discord Application:**
   - Go to the [Discord Developer Portal](https://discord.com/developers/applications)
   - Click "New Application"
   - Give your bot a name

2. **Create the Bot:**
   - Go to the "Bot" tab
   - Click "Add Bot"
   - Enable the following intents:
     - **Message Content Intent**
     - **Server Members Intent**
   - Copy the bot token

3. **Configure Bot Permissions:**
   - Go to the "OAuth2" → "URL Generator" tab
   - Select these scopes:
     - `bot`
     - `applications.commands`
   - Select these bot permissions:
     - `Send Messages`
     - `Embed Links`
     - `Attach Files`
     - `Read Message History`
     - `Use External Emojis`
     - `Add Reactions`
     - `Connect`
     - `Speak`
     - `Read Messages/View Channels`
     - `Manage Channels`
     - `Manage Roles`
   - Copy the generated URL and invite the bot to your server

### 4. Environment Configuration

1. **Create a `.env` file** based on `.env.example`:
   ```bash
   cp .env.example .env
   ```

2. **Edit the `.env` file** with your configuration:
   ```env
   DISCORD_TOKEN=your_discord_bot_token_here
   WELCOME_CHANNEL_ID=123456789012345678
   TICKET_CATEGORY_ID=123456789012345678
   SUPPORT_ROLE_ID=123456789012345678
   ```

### 5. Getting Required IDs

**To get Channel IDs:**
- Right-click on the channel in Discord
- Select "Copy Channel ID" (enable Developer Mode in Discord settings first)

**To get Role IDs:**
- Right-click on the role in Discord
- Select "Copy Role ID" (enable Developer Mode in Discord settings first)

### 6. Running the Bot

```bash
python bot.py
```

## Configuration

### Environment Variables

| Variable | Required | Description |
|----------|----------|-------------|
| `DISCORD_TOKEN` | ✅ | Your Discord bot token |
| `WELCOME_CHANNEL_ID` | ✅ | Channel ID for public welcome messages |
| `TICKET_CATEGORY_ID` | ✅ | Category ID where ticket channels are created |
| `SUPPORT_ROLE_ID` | ✅ | Role ID that can access all tickets |

### Message Customization

All user-facing messages can be customized in `config.py`:

- `PUBLIC_WELCOME_MESSAGE` - Public welcome message
- `PRIVATE_WELCOME_MESSAGE` - DM sent to new members
- `DELAYED_DM_24H` - DM sent after 24 hours
- `DELAYED_DM_72H` - DM sent after 72 hours
- `TICKET_OPEN_MESSAGE` - Message in new ticket channels
- `TICKET_CLOSED_MESSAGE` - Message when ticket is closed

## Commands

### User Commands
- `!ticket` - Display ticket creation button
- `!status` - Show bot status (Admin only)

### Admin Commands
- `!ticketpanel` - Create permanent ticket panel (Admin only)
- `!reload` - Reload all bot cogs (Bot owner only)

## Project Structure

```
.
├── bot.py              # Main bot file with startup and core commands
├── config.py           # Configuration and environment variables
├── requirements.txt    # Python dependencies
├── .env.example       # Environment variables template
├── .gitignore         # Git ignore file
├── README.md          # This file
└── cogs/              # Bot modules directory
    ├── __init__.py    # Cogs package initialization
    ├── welcome.py     # Welcome system and delayed DMs
    └── ticket.py      # Ticket system with buttons
```

## Usage

### Setting Up the Welcome System

1. Create a welcome channel in your Discord server
2. Get the channel ID and add it to `WELCOME_CHANNEL_ID` in your `.env`
3. The bot will automatically:
   - Send public welcome messages when users join
   - Send private DMs to new members
   - Schedule follow-up DMs after 24h and 72h

### Setting Up the Ticket System

1. Create a category for ticket channels
2. Get the category ID and add it to `TICKET_CATEGORY_ID` in your `.env`
3. Create a "Support" role for your support team
4. Get the role ID and add it to `SUPPORT_ROLE_ID` in your `.env`
5. Use `!ticketpanel` in a channel to create a permanent ticket panel

### Ticket Workflow

1. **User clicks "Open Ticket" button**
2. **Bot creates private channel** with user and support role access
3. **Support team assists** in the private channel
4. **User or support clicks "Close Ticket"**
5. **Channel is deleted** after 5 seconds

## Troubleshooting

### Common Issues

**Bot doesn't respond to commands:**
- Check that the bot has the correct permissions
- Ensure the bot token is correct in `.env`
- Verify that Message Content Intent is enabled

**Welcome messages not working:**
- Check `WELCOME_CHANNEL_ID` is correct
- Ensure bot has permission to send messages in the welcome channel
- Verify that Members Intent is enabled

**Ticket system not working:**
- Check `TICKET_CATEGORY_ID` and `SUPPORT_ROLE_ID` are correct
- Ensure bot has "Manage Channels" permission
- Verify the category exists and bot can access it

**Delayed DMs not sending:**
- Users might have DMs disabled
- Check console for error messages
- Ensure the bot is running continuously

### Getting Help

If you encounter issues:
1. Check the console output for error messages
2. Verify all environment variables are set correctly
3. Ensure the bot has all required permissions
4. Make sure Discord intents are properly configured

## Development

### Adding New Features

The bot uses a modular cog system:
1. Create new Python files in the `cogs/` directory
2. Follow the existing cog structure with `setup()` function
3. The bot will automatically load new cogs on startup

### Reloading Cogs

Use `!reload` to reload all cogs without restarting the bot (bot owner only).

## License

This project is open source and available under the MIT License.