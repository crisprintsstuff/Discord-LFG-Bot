import nextcord
from nextcord.ext import commands

# Bot token (replace with your actual token)
TOKEN = 'DiscordTokenHere'

# Pre-defined list of games
games = ["Destiny 2", "Among Us", "Valorant", "League of Legends", "Overwatch 2"]

# Channel ID for sending the embed (replace with your channel ID)
embed_channel_id = YourChannelID 

# Dictionary to map game names to their logo URLs (replace with your full URLs or file paths)
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

    # Create the embed 
    embed = nextcord.Embed(title=f"Looking for players for {game}", color=0x00ff00)
    embed.set_thumbnail(url=game_logos[game])
    embed.description = f"Need {num_players} more players!\n**Activity:** {activity}" 

    # Get the channel to send the embed to
    channel = bot.get_channel(embed_channel_id)
    if not channel:
        await interaction.send("Failed to send the request. Please check the channel ID.", ephemeral=True)
        return

    # Send the embed and add the join emoji reaction
    message = await channel.send(embed=embed)
    await message.add_reaction(join_emoji)

    # Wait for reactions and add users to a new channel
    while num_players > 0:
        reaction, user = await bot.wait_for("reaction_add", check=lambda r, u: r.message == message and str(r.emoji) == join_emoji and u != bot.user)

        # Create a new channel for the group if it doesn't exist
        channel_name = f"{game}-{activity}"
        existing_channel = nextcord.utils.get(interaction.guild.channels, name=channel_name)
        if not existing_channel:
            overwrites = {
                interaction.guild.default_role: nextcord.PermissionOverwrite(read_messages=False),
                user: nextcord.PermissionOverwrite(read_messages=True)  

            }
            existing_channel = await interaction.guild.create_text_channel(channel_name, overwrites=overwrites)

        # Add the user to the channel
        await existing_channel.set_permissions(user, read_messages=True)
        num_players -= 1

    # Update the embed to indicate the group is full
    embed.description = f"Group for {game} - {activity} is now full!"
    await message.edit(embed=embed)

bot.run(TOKEN)
