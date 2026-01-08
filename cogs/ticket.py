import discord
from discord.ext import commands
from discord.ui import Button, View
import asyncio
from config import (
    TICKET_CATEGORY_ID, SUPPORT_ROLE_ID, TICKET_OPEN_MESSAGE,
    TICKET_CHANNEL_TOPIC, TICKET_CLOSED_MESSAGE, TICKET_BUTTON_LABEL,
    TICKET_CLOSE_BUTTON_LABEL, TICKET_CLOSE_DELAY, ADMIN_ROLE_ID,
    CLOSED_TICKET_CATEGORY_ID, LOG_CHANNEL_ID
)

# Track active tickets per user
active_tickets = {}  # {user_id: channel_id}

async def log_to_channel(bot, message: str):
    """Send a log message to the configured log channel."""
    if LOG_CHANNEL_ID != 0:
        log_channel = bot.get_channel(LOG_CHANNEL_ID)
        if log_channel:
            try:
                await log_channel.send(f"🎫 {message}")
            except Exception as e:
                print(f"Failed to send log message: {e}")

class TicketView(View):
    """
    View containing the "Open Ticket" button.
    """
    def __init__(self, bot):
        super().__init__(timeout=None)  # Persistent view
        self.bot = bot
    
    @discord.ui.button(
        label=TICKET_BUTTON_LABEL,
        style=discord.ButtonStyle.primary,
        custom_id="open_ticket_button"
    )
    async def open_ticket_button(self, interaction: discord.Interaction, button: Button):
        """
        Handle the "Open Ticket" button click.
        """
        try:
            user_id = interaction.user.id
            
            # Check if user already has an active ticket
            if user_id in active_tickets:
                channel_id = active_tickets[user_id]
                channel = self.bot.get_channel(channel_id)
                if channel:
                    await interaction.response.send_message(
                        f"You already have an open ticket: {channel.mention}",
                        ephemeral=True
                    )
                    return
                else:
                    # Channel no longer exists, remove from tracking
                    del active_tickets[user_id]
            
            ticket_channel = await self.create_ticket(interaction.user, interaction.guild)
            
            if ticket_channel:
                # Track active ticket
                active_tickets[user_id] = ticket_channel.id
                
                # Log ticket creation
                await log_to_channel(self.bot, f"Ouverture d'un ticket pour {interaction.user.mention} ({interaction.user.name}) - Canal: {ticket_channel.mention}")
                
                await interaction.response.send_message(
                    f"Ticket created! Here's your channel: {ticket_channel.mention}",
                    ephemeral=True
                )
                
            else:
                await interaction.response.send_message(
                    "Error creating ticket. Please contact an administrator.",
                    ephemeral=True
                )
        except discord.InteractionResponded:
            # Interaction already responded, ignore
            pass
        except discord.HTTPException as e:
            print(f"HTTP error in ticket button: {e}")
            await log_to_channel(self.bot, f"Erreur HTTP dans le bouton ticket: {e}")
        except Exception as e:
            print(f"Unexpected error in ticket button: {e}")
            await log_to_channel(self.bot, f"Erreur inattendue dans le bouton ticket: {e}")
            
            # Try to respond if not already responded
            try:
                await interaction.response.send_message(
                    "An unexpected error occurred. Please try again.",
                    ephemeral=True
                )
            except:
                pass
    
    async def create_ticket(self, user, guild):
        """
        Create a new ticket channel for the user.
        Returns the created channel or None if failed.
        """
        # Get the ticket category
        category = guild.get_channel(TICKET_CATEGORY_ID)
        if not category:
            print(f"Ticket category {TICKET_CATEGORY_ID} not found")
            return None
        
        # Create overwrites for the channel
        overwrites = {
            guild.default_role: discord.PermissionOverwrite(read_messages=False),
            user: discord.PermissionOverwrite(
                read_messages=True,
                send_messages=True,
                attach_files=True,
                embed_links=True
            ),
            guild.me: discord.PermissionOverwrite(
                read_messages=True,
                send_messages=True,
                manage_channels=True
            )
        }
        
        # Add support role if configured
        if SUPPORT_ROLE_ID != 0:
            support_role = guild.get_role(SUPPORT_ROLE_ID)
            if support_role:
                overwrites[support_role] = discord.PermissionOverwrite(
                    read_messages=True,
                    send_messages=True,
                    attach_files=True,
                    embed_links=True
                )
        
        # Create the ticket channel
        channel_name = f"ticket-{user.name.lower().replace(' ', '-')}"
        try:
            ticket_channel = await guild.create_text_channel(
                name=channel_name,
                category=category,
                overwrites=overwrites,
                topic=TICKET_CHANNEL_TOPIC.format(user_name=user.display_name)
            )
            
            # Send welcome message to the ticket channel
            welcome_message = TICKET_OPEN_MESSAGE.format(
                user_mention=user.mention
            )
            
            # Create close button view
            close_view = TicketCloseView(self.bot, ticket_channel)
            
            await ticket_channel.send(welcome_message, view=close_view)
            print(f"Created ticket channel {ticket_channel.name} for {user.name}")
            
            return ticket_channel
            
        except discord.Forbidden:
            print(f"Missing permissions to create ticket channels")
            return None
        except Exception as e:
            print(f"Error creating ticket channel: {e}")
            return None

class TicketCloseView(View):
    """
    View containing the "Close Ticket" button for ticket channels.
    """
    def __init__(self, bot, channel):
        super().__init__(timeout=None)  # Persistent view
        self.bot = bot
        self.channel = channel
    
    @discord.ui.button(
        label=TICKET_CLOSE_BUTTON_LABEL,
        style=discord.ButtonStyle.danger,
        custom_id="close_ticket_button"
    )
    async def close_ticket_button(self, interaction: discord.Interaction, button: Button):
        """
        Handle the "Close Ticket" button click.
        """
        # Check if user has permission to close ticket (support role or ticket creator)
        member = interaction.user
        has_permission = False
        
        # Check if user is the ticket creator
        if member in self.channel.overwrites:
            has_permission = True
        
        # Check if user has support role
        if SUPPORT_ROLE_ID != 0:
            support_role = member.guild.get_role(SUPPORT_ROLE_ID)
            if support_role and support_role in member.roles:
                has_permission = True
        
        # Check if user is server admin
        if member.guild_permissions.administrator:
            has_permission = True
        
        if not has_permission:
            await interaction.response.send_message(
                "You don't have permission to close this ticket.",
                ephemeral=True
            )
            return
        
        # Send closing message and move channel
        await interaction.response.send_message(TICKET_CLOSED_MESSAGE)
        
        # Log ticket closure
        await log_to_channel(self.bot, f"Ticket #{self.channel.name} fermé par {interaction.user.mention} ({interaction.user.name})")
        
        # Wait before moving channel
        await asyncio.sleep(TICKET_CLOSE_DELAY)
        
        try:
            # Remove user from active tickets tracking
            user_id_to_remove = None
            for user_id, channel_id in active_tickets.items():
                if channel_id == self.channel.id:
                    user_id_to_remove = user_id
                    break
            if user_id_to_remove:
                del active_tickets[user_id_to_remove]
            
            # Remove user permissions from channel
            for member, overwrite in self.channel.overwrites.items():
                if not isinstance(member, discord.Role) and not member.bot:
                    await self.channel.set_permissions(member, overwrite=None)
            
            # Get closed ticket category
            closed_category = self.bot.get_channel(CLOSED_TICKET_CATEGORY_ID)
            if not closed_category:
                print(f"Closed ticket category {CLOSED_TICKET_CATEGORY_ID} not found")
                await self.channel.delete()
                return
            
            # Check if category is full (50 channels max)
            if len(closed_category.channels) >= 50:
                # Find and delete oldest ticket in closed category
                oldest_channel = None
                oldest_time = None
                
                for channel in closed_category.channels:
                    if channel.name.startswith("ticket-"):
                        channel_created = channel.created_at
                        if oldest_time is None or channel_created < oldest_time:
                            oldest_time = channel_created
                            oldest_channel = channel
                
                if oldest_channel:
                    await oldest_channel.delete()
                    print(f"Deleted oldest ticket {oldest_channel.name} to make space")
                    await log_to_channel(self.bot, f"Suppression du plus ancien ticket #{oldest_channel.name} (catégorie pleine)")
            
            # Move channel to closed category
            await self.channel.edit(category=closed_category)
            print(f"Moved ticket {self.channel.name} to closed category")
            await log_to_channel(self.bot, f"Ticket #{self.channel.name} déplacé vers la catégorie fermée")
            
        except discord.Forbidden:
            print(f"Missing permissions to move/delete ticket channel {self.channel.name}")
        except Exception as e:
            print(f"Error handling ticket closure: {e}")
            await log_to_channel(self.bot, f"Erreur lors de la fermeture du ticket #{self.channel.name}: {e}")

class Ticket(commands.Cog):
    """
    Ticket system cog for managing support tickets.
    """
    
    def __init__(self, bot):
        self.bot = bot
    
    @commands.Cog.listener()
    async def on_ready(self):
        """Called when the bot is ready."""
        print(f"Ticket cog loaded by {self.bot.user}")
        
        # Add persistent views for buttons to work after restart
        self.bot.add_view(TicketView(self.bot))
        print("Added persistent view for ticket buttons")
        
        # Also add persistent views for any existing ticket close buttons
        for guild in self.bot.guilds:
            category = guild.get_channel(TICKET_CATEGORY_ID)
            if category:
                for channel in category.text_channels:
                    if channel.name.startswith("ticket-"):
                        # Add close button view to existing ticket channels
                        close_view = TicketCloseView(self.bot, channel)
                        self.bot.add_view(close_view)
                        print(f"Added persistent view for existing ticket: {channel.name}")
    
    @commands.Cog.listener()
    async def on_guild_channel_delete(self, channel):
        """
        Clean up active tickets when channels are deleted.
        """
        # Remove from active tickets if this was a ticket channel
        user_id_to_remove = None
        for user_id, channel_id in active_tickets.items():
            if channel_id == channel.id:
                user_id_to_remove = user_id
                break
        if user_id_to_remove:
            del active_tickets[user_id_to_remove]
            print(f"Cleaned up active ticket for user {user_id_to_remove} due to channel deletion")

    @commands.command(name='ticket')
    @commands.has_role(ADMIN_ROLE_ID)
    async def ticket_command(self, ctx):
        """
        Display ticket creation button (Admin only).
        """
        # Check if command is used in an appropriate channel
        if TICKET_CATEGORY_ID == 0:
            await ctx.send("Ticket system is not configured properly. Please contact an admin.", ephemeral=True)
            return

        # Delete user's command message
        try:
            await ctx.message.delete()
        except:
            pass

        view = TicketView(self.bot)
        embed = discord.Embed(
            title="Support Tickets",
            description="Click the button below to create a new support ticket.",
            color=discord.Color(int("33D26D", 16))
        )

        await ctx.send(embed=embed, view=view)

        # Log command usage
        await log_to_channel(self.bot, f"Commande !ticket utilisée par {ctx.author.mention} ({ctx.author.name}) dans {ctx.channel.mention}")

    @commands.command(name='ticketpanel')
    @commands.has_permissions(administrator=True)
    async def ticket_panel_command(self, ctx):
        """
        Create a permanent ticket panel in the current channel.
        """
        view = TicketView(self.bot)
        embed = discord.Embed(
            title="🎫 Support Tickets",
            description="Need help? Click the button below to create a support ticket.\n\n"
                       "Our support team will assist you as soon as possible!",
            color=discord.Color(int("33D26D", 16))
        )
        
        message = await ctx.send(embed=embed, view=view)
        
        # Make the message persistent
        await ctx.send(
            f"Ticket panel created! Message ID: {message.id}\n"
            "Use this message ID to reference the panel if needed.",
            delete_after=10
        )

async def setup(bot):
    """Setup function to add the cog to the bot."""
    await bot.add_cog(Ticket(bot))
    
    # Wait a bit for the bot to be fully ready
    await asyncio.sleep(2)
    
    # Manually register persistent views for existing messages
    for guild in bot.guilds:
        for channel in guild.text_channels:
            try:
                async for message in channel.history(limit=50):
                    if message.components:
                        for component in message.components:
                            for child in component.children:
                                if hasattr(child, 'custom_id'):
                                    if child.custom_id == "open_ticket_button":
                                        view = TicketView(bot)
                                        bot.add_view(view)
                                        print(f"Registered persistent view for ticket button in {channel.name}")
                                    elif child.custom_id == "close_ticket_button":
                                        # Find the channel for this close button
                                        ticket_channel = channel if channel.name.startswith("ticket-") else None
                                        if ticket_channel:
                                            view = TicketCloseView(bot, ticket_channel)
                                            bot.add_view(view)
                                            print(f"Registered persistent view for close button in {channel.name}")
            except discord.Forbidden:
                continue  # Skip channels we can't read
            except Exception as e:
                print(f"Error checking channel {channel.name}: {e}")
        
        # Also specifically scan the ticket category for existing tickets
        ticket_category = guild.get_channel(TICKET_CATEGORY_ID)
        if ticket_category:
            for channel in ticket_category.text_channels:
                if channel.name.startswith("ticket-"):
                    try:
                        # Look for close button messages in this ticket channel
                        async for message in channel.history(limit=10):
                            if message.components:
                                for component in message.components:
                                    for child in component.children:
                                        if hasattr(child, 'custom_id') and child.custom_id == "close_ticket_button":
                                            view = TicketCloseView(bot, channel)
                                            bot.add_view(view)
                                            print(f"Registered persistent view for close button in ticket channel {channel.name}")
                    except Exception as e:
                        print(f"Error checking ticket channel {channel.name}: {e}")
