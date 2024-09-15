import nextcord
from nextcord.ext import commands

# Bot token (replace with your actual token)
TOKEN = 'DiscordTokenHere'

# Pre-defined list of games
games = ["Destiny 2", "Among Us", "Valorant", "League of Legends", "Overwatch 2"]

# Channel ID for sending the embed (replace with your channel ID)
embed_channel_id = ChannelIDHERE 

# Dictionary to map game names to their logo URLs (replace with your actual URLs or file paths)
game_logos = {
    "Among Us": "",
    "Valorant": "",
    "League of Legends": "",
    "Overwatch 2": "",
    "Destiny 2": ""
}

# Enable message content intent (optional but recommended)
intents = nextcord.Intents.default()
intents.message_content = True
intents.reactions = True # Enable reaction intents
intents.members = True # Enable member intents

bot = commands.Bot(command_prefix='/', intents=intents)

# Emoji for joining the activity (replace with your desired emoji)
join_emoji = "🎮"

@bot.event
async def on_ready():
    print(f'Logged in as {bot.user} (ID: {bot.user.id})')
    print('------')
    try:
        await bot.sync_application_commands() 
    except Exception as e:
        print(e)

@bot.slash_command(name="findplayers", description="Find players for a game")
async def find_players(
    interaction: nextcord.Interaction, 
    game: str = nextcord.SlashOption(name="game", description="Select a game", choices=games), 
    num_players: int = nextcord.SlashOption(name="num_players", description="Number of players needed"),
    activity: str = nextcord.SlashOption(name="activity", description="What do you want to do?")
):
    if game not in games:
        await interaction.send("Invalid game selected.", ephemeral=True)
        return

    if num_players <= 0:
        await interaction.send("Invalid number of players.", ephemeral=True)
        return

    # Get the category to create the channel in
    category_name = "LFG" 
    category = nextcord.utils.get(interaction.guild.categories, name=category_name)
    if not category:
        await interaction.send(f"Couldn't find the category '{category_name}'. Please make sure it exists.", ephemeral=True)
        return

    # Create a new channel for the group if it doesn't exist, within the specified category
    channel_name = f"{game}-{activity}"
    existing_channel = nextcord.utils.get(interaction.guild.channels, name=channel_name)
    if not existing_channel:
        overwrites = {
            interaction.guild.default_role: nextcord.PermissionOverwrite(read_messages=False),
            interaction.user: nextcord.PermissionOverwrite(read_messages=True)  
  # Allow creator to see
        }
        existing_channel = await interaction.guild.create_text_channel(channel_name, overwrites=overwrites, category=category)

        # Send an initial message to the new channel (optional)
        await existing_channel.send(f"Welcome to the {game} - {activity} group! This channel was created by {interaction.user.mention}.")

    # Create the embed 
    embed = nextcord.Embed(title=f"Looking for players for {game}", color=0x00ff00)
    embed.set_thumbnail(url=game_logos[game])
    embed.description = f"Need {num_players} more players!\n**Activity:** {activity}\n\n**Join this channel:** {existing_channel.mention}" 

    # Get the channel to send the embed to
    channel = bot.get_channel(embed_channel_id)
    if not channel:
        await interaction.send("Failed to send the request. Please check the channel ID.", ephemeral=True)
        return

    # Send the embed and add the join emoji reaction
    message = await channel.send(embed=embed)
    await message.add_reaction(join_emoji)

    # Wait for reactions and add users to the channel
    while num_players > 0:
        reaction, user = await bot.wait_for("reaction_add", check=lambda r, u: r.message == message and str(r.emoji) == join_emoji and u != bot.user)

        # Add the user to the channel
        await existing_channel.set_permissions(user, read_messages=True)
        num_players -= 1

    # Update the embed to indicate the group is full
    embed.description = f"Group for {game} - {activity} is now full!"
    await message.edit(embed=embed)

@bot.slash_command(name="close", description="Closes the current group channel. (Only the group creator can use this)")
async def close(interaction: nextcord.Interaction):
    try:
        # Check if the user is in a group channel
        if not interaction.channel.category or interaction.channel.category.name != "LFG": 
            await interaction.send("You can only close group channels within the LFG category.", ephemeral=True)
            return

        # Check if the user has permission to manage the channel (i.e., they created it)
        permissions = interaction.channel.permissions_for(interaction.user)
        if not permissions.manage_channels:
            await interaction.send("You can only close a group channel that you created.", ephemeral=True)
            return

        # Delete the channel
        await interaction.send("Closing the group channel...", ephemeral=True)
        await interaction.channel.delete()

    except Exception as e:
        print(f"Error in /close command: {e}")
        await interaction.send("An error occurred while closing the channel. Please try again later.", ephemeral=True)


bot.run(TOKEN)
