import discord
from discord.ext import commands
import os
from config import DISCORD_TOKEN, BOT_PREFIX, BOT_ACTIVITY, LOG_CHANNEL_ID

# Define bot intents
intents = discord.Intents.default()
intents.message_content = True
intents.members = True  # Required for member join/leave events
intents.guilds = True   # Required for guild operations

# Create bot instance with command prefix
bot = commands.Bot(
    command_prefix=BOT_PREFIX,
    intents=intents,
    help_command=None  # We'll create custom help if needed
)

async def log_to_channel(message: str):
    """Send a log message to the configured log channel."""
    if LOG_CHANNEL_ID != 0:
        log_channel = bot.get_channel(LOG_CHANNEL_ID)
        if log_channel:
            try:
                await log_channel.send(f"📝 {message}")
            except Exception as e:
                print(f"Failed to send log message: {e}")

@bot.event
async def on_ready():
    """
    Called when the bot is fully loaded and ready.
    """
    startup_message = f"🚀 {bot.user} has connected to Discord!"
    print(startup_message)
    
    # Send startup log
    await log_to_channel(startup_message)
    print(f'🤖 Bot is in {len(bot.guilds)} servers')
    
    # Set bot activity
    try:
        await bot.change_presence(
            activity=discord.Activity(
                type=discord.ActivityType.watching,
                name=BOT_ACTIVITY
            )
        )
        print(f'📝 Bot activity set to: {BOT_ACTIVITY}')
    except Exception as e:
        print(f'⚠️ Could not set bot activity: {e}')
    
    # Load cogs
    await load_cogs()
    
    print('✅ Bot is fully ready!')

async def load_cogs():
    """
    Load all cogs from the cogs directory.
    """
    cogs_directory = "cogs"
    
    # List all Python files in the cogs directory
    for filename in os.listdir(cogs_directory):
        if filename.endswith('.py') and filename != '__init__.py':
            cog_name = filename[:-3]  # Remove .py extension
            try:
                await bot.load_extension(f'cogs.{cog_name}')
                print(f'📦 Loaded cog: {cog_name}')
            except Exception as e:
                print(f'❌ Failed to load cog {cog_name}: {e}')

@bot.event
async def on_command_error(ctx, error):
    """
    Handle command errors gracefully.
    """
    # Check if the error is wrapped in CommandInvokeError
    original_error = error.original if hasattr(error, 'original') else error
    
    if isinstance(error, commands.CommandNotFound):
        return  # Ignore command not found errors
    
    # Log the error
    error_message = f"Command error in {ctx.command}: {error}"
    print(f'⚠️ {error_message}')
    await log_to_channel(error_message)
    
    # Delete user's command message
    try:
        await ctx.message.delete()
    except:
        pass  # Ignore if we can't delete the message
    
    # Don't send any message to the user

@bot.command(name='reload')
@commands.is_owner()
async def reload_cogs(ctx):
    """
    Reload all cogs (bot owner only).
    """
    cogs_directory = "cogs"
    reloaded_cogs = []
    failed_cogs = []
    
    for filename in os.listdir(cogs_directory):
        if filename.endswith('.py') and filename != '__init__.py':
            cog_name = filename[:-3]
            try:
                await bot.reload_extension(f'cogs.{cog_name}')
                reloaded_cogs.append(cog_name)
            except Exception as e:
                failed_cogs.append(f'{cog_name}: {e}')
    
    embed = discord.Embed(
        title="🔄 Cogs Reloaded",
        color=discord.Color(int("33D26D", 16))
    )
    
    if reloaded_cogs:
        embed.add_field(
            name="✅ Successfully Reloaded",
            value='\n'.join(reloaded_cogs),
            inline=False
        )
    
    if failed_cogs:
        embed.add_field(
            name="❌ Failed to Reload",
            value='\n'.join(failed_cogs),
            inline=False
        )
        embed.color = discord.Color.red()
    
    await ctx.send(embed=embed)

@bot.command(name='status')
@commands.has_permissions(administrator=True)
async def bot_status(ctx):
    """
    Display bot status and information.
    """
    embed = discord.Embed(
        title="🤖 Bot Status",
        color=discord.Color(int("33D26D", 16))
    )
    
    embed.add_field(name="📡 Latency", value=f"{round(bot.latency * 1000)}ms", inline=True)
    embed.add_field(name="🌐 Servers", value=str(len(bot.guilds)), inline=True)
    embed.add_field(name="👥 Total Users", value=str(len(set(bot.get_all_members()))), inline=True)
    embed.add_field(name="📦 Loaded Cogs", value=str(len(bot.cogs)), inline=True)
    embed.add_field(name="⚡ Uptime", value=f"<t:{int(discord.utils.utcnow().timestamp())}:R>", inline=True)
    
    await ctx.send(embed=embed)

if __name__ == "__main__":
    # Check if Discord token is provided
    if not DISCORD_TOKEN:
        print("❌ Discord token not found! Please set DISCORD_TOKEN in your .env file.")
        exit(1)
    
    # Run the bot
    try:
        bot.run(DISCORD_TOKEN)
    except discord.errors.LoginFailure:
        print("❌ Invalid Discord token! Please check your DISCORD_TOKEN.")
    except Exception as e:
        print(f"❌ Error starting bot: {e}")
