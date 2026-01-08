import discord
from discord.ext import commands
import asyncio
from config import (
    WELCOME_CHANNEL_ID, PUBLIC_WELCOME_MESSAGE, PRIVATE_WELCOME_MESSAGE,
    DELAYED_DM_24H, DELAYED_DM_72H, WELCOME_DELAY_24H, WELCOME_DELAY_72H,
    LOG_CHANNEL_ID
)

async def log_to_channel(bot, message: str):
    """Send a log message to the configured log channel."""
    if LOG_CHANNEL_ID != 0:
        log_channel = bot.get_channel(LOG_CHANNEL_ID)
        if log_channel:
            try:
                await log_channel.send(f"👋 {message}")
            except Exception as e:
                print(f"Failed to send log message: {e}")

class Welcome(commands.Cog):
    """
    Welcome system cog for handling new member greetings and delayed DMs.
    """
    
    def __init__(self, bot):
        self.bot = bot
        self.scheduled_dms = {}  # Store scheduled DM tasks
    
    @commands.Cog.listener()
    async def on_ready(self):
        """Called when the bot is ready."""
        print(f"Welcome cog loaded by {self.bot.user}")
    
    @commands.Cog.listener()
    async def on_member_join(self, member):
        """
        Handle new member joining the server.
        Sends public welcome message and private DM, schedules delayed DMs.
        """
        # Skip if the member is a bot
        if member.bot:
            return
        
        # Log member join
        await log_to_channel(self.bot, f"@{member.name} ({member.display_name}) a rejoint le serveur")
        
        # Send public welcome message
        if WELCOME_CHANNEL_ID != 0:
            welcome_channel = self.bot.get_channel(WELCOME_CHANNEL_ID)
            if welcome_channel:
                try:
                    public_message = PUBLIC_WELCOME_MESSAGE.format(
                        user_mention=member.mention,
                        user_name=member.display_name
                    )
                    await welcome_channel.send(public_message)
                except discord.Forbidden:
                    print(f"Missing permissions to send messages in welcome channel {WELCOME_CHANNEL_ID}")
                except Exception as e:
                    print(f"Error sending welcome message: {e}")
        
        # Send private DM
        try:
            private_message = PRIVATE_WELCOME_MESSAGE.format(
                user_name=member.display_name
            )
            await member.send(private_message)
        except discord.Forbidden:
            print(f"Could not send DM to {member.name} - DMs might be disabled")
        except Exception as e:
            print(f"Error sending welcome DM to {member.name}: {e}")
        
        # Schedule delayed DMs
        await self.schedule_delayed_dms(member)
    
    async def schedule_delayed_dms(self, member):
        """
        Schedule delayed DMs for 24h and 72h after member joins.
        """
        # Schedule 24-hour DM
        task_24h = asyncio.create_task(self.send_delayed_dm(
            member, DELAYED_DM_24H, WELCOME_DELAY_24H, "24h"
        ))
        
        # Schedule 72-hour DM
        task_72h = asyncio.create_task(self.send_delayed_dm(
            member, DELAYED_DM_72H, WELCOME_DELAY_72H, "72h"
        ))
        
        # Store tasks so they don't get garbage collected
        self.scheduled_dms[member.id] = {
            "24h": task_24h,
            "72h": task_72h
        }
    
    async def send_delayed_dm(self, member, message_template, delay, delay_type):
        """
        Send a delayed DM after specified delay.
        """
        await asyncio.sleep(delay)
        
        try:
            # Check if member is still in the server
            if member.guild.get_member(member.id) is None:
                return
            
            message = message_template.format(user_name=member.display_name)
            await member.send(message)
            print(f"Sent {delay_type} delayed DM to {member.name}")
            
        except discord.Forbidden:
            print(f"Could not send {delay_type} DM to {member.name} - DMs might be disabled")
        except discord.NotFound:
            print(f"User {member.name} not found when trying to send {delay_type} DM")
        except Exception as e:
            print(f"Error sending {delay_type} DM to {member.name}: {e}")
        finally:
            # Clean up the task from scheduled_dms
            if member.id in self.scheduled_dms and delay_type in self.scheduled_dms[member.id]:
                del self.scheduled_dms[member.id][delay_type]
    
    @commands.Cog.listener()
    async def on_member_remove(self, member):
        """
        Clean up scheduled DMs when a member leaves the server.
        """
        if member.id in self.scheduled_dms:
            # Cancel any pending tasks
            for task in self.scheduled_dms[member.id].values():
                if not task.done():
                    task.cancel()
            del self.scheduled_dms[member.id]
            print(f"Cleaned up scheduled DMs for {member.name}")

async def setup(bot):
    """Setup function to add the cog to the bot."""
    await bot.add_cog(Welcome(bot))
