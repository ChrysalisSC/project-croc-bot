import discord
from discord.ext import commands
from discord import app_commands

from PIL import Image, ImageDraw, ImageFont

import utils.helpers as helpers
import data.user_data as user_data
import math
import requests

class Leaderboards(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.env = bot.env
      


    @commands.command(name="leaderboard")
    async def leaderboard(self, ctx, limit: int = 10):
        """Display the XP leaderboard."""
        leaderboard = user_data.get_leaderboard(self.bot.env,limit)
        
        if not leaderboard:
            await ctx.send("No data available for the leaderboard!")
            return
        user_list = []
        i = 0
        for user in leaderboard:
            print(user)
            
            user_data_info, profile_data = user_data.get_all_profile_data(user[0], self.env)

            # Fetch the member from the server (force an API call to get up-to-date data)
            member = await ctx.guild.fetch_member(user[0])
            if member is None:
                print(f"Could not find member with ID {user[0]}")
                continue

            # Check if the member has an avatar
            if member.avatar is None:
                print(f"Member {member.name} does not have a profile picture.")
                # Use a local default image
                profile_picture_path = "images/server_icons/default_profile.png"
            else:
                # Download the profile picture from the URL and save it to a temporary file
                thumbnail_url = str(member.avatar.url)
                profile_picture_path = f"leaderboards/{user_data_info[1]}.png"
                response = requests.get(thumbnail_url)
                
                if response.status_code == 200:
                    with open(profile_picture_path, "wb") as f:
                        f.write(response.content)
                else:
                    print(f"Failed to download avatar for {member.name}. Using default.")
                    profile_picture_path = "images/server_icons/default_profile.png"

            # Save the member's name (display name)
            member_name = member.display_name
            print("Member Name:", member_name)


           
            item = {
                "header_image_path": f"images/customization/{profile_data[3]}.png",
                "name": user_data_info[1],
                "level": user_data_info[4],
                "xp": user_data_info[3],
                "profile_picture_path": profile_picture_path  # Save the profile picture path here
            }
            i += 1
            user_list.append(item)

        output_path = "leaderboard.png"
        create_leaderboard_image(user_list, output_path)
        file = discord.File(output_path, filename="leaderboard.png")
        await ctx.send(file=file)

        

async def setup(bot):
    #name of your log(name of cog, print_info)
    helpers.log("EXAMPLE", "Setting up Example cog...")
    await bot.add_cog(Leaderboards(bot))
   

def create_leaderboard_image(user_data_list, output_path="leaderboard.png"):
        """Create a leaderboard image with a stacked layout and rankings."""
        card_width, card_height = 800, 100
        margin = 5
        title_height = 150
        leaderboard_width = card_width + 100  # Extra space for rankings
        leaderboard_height = title_height + (card_height + margin) * len(user_data_list) - margin

        # Create background
        background = create_gradient_background(leaderboard_width, leaderboard_height)

        draw = ImageDraw.Draw(background)

        # Load fonts
        font_path = "fonts/EBGaramond-Bold.ttf"  # Adjust path
        title_font = ImageFont.truetype(font_path, 80)
        rank_font = ImageFont.truetype(font_path, 50)
        title_text = "LEADERBOARD"

        # Draw leaderboard title
        text_bbox = draw.textbbox((0, 0), title_text, font=title_font)
        text_width = text_bbox[2] - text_bbox[0]
        text_height = text_bbox[3] - text_bbox[1]
        draw.text(
            ((leaderboard_width - text_width) // 2, (title_height - text_height) // 2),
            title_text,
            font=title_font,
            fill=(255, 255, 255)
        )
        print('User Data List:', user_data_list)
        for i, user_data in enumerate(user_data_list):
            print('I:', i, 'User Data:', user_data)
            # Create the user card
            card_image = create_level_card(
                user_data["header_image_path"],
                user_data["name"],
                user_data["level"],
                user_data["xp"],
                user_data["profile_picture_path"]
            )
            y_offset = title_height + i * (card_height + margin)

            # Paste the card
            background.paste(card_image, (100, y_offset))

            # Draw ranking number
            rank_text = f"{i + 1}"
            rank_bbox = draw.textbbox((0, 0), rank_text, font=rank_font)
            rank_width = rank_bbox[2] - rank_bbox[0]
            rank_height = rank_bbox[3] - rank_bbox[1]
            rank_x = (100 - rank_width) // 2
            rank_y = y_offset + (card_height - rank_height) // 2
            draw.text((rank_x, rank_y), rank_text, font=rank_font, fill=(255, 255, 255))

        background.save(output_path)
    
      


def create_level_card(header_image_path, name, level, xp, profile_picture_path):
    """
    Create a single user level card with the requested aspect ratio.

    Args:
        Same as before.

    Returns:
        PIL.Image: The generated level card.
    """
    # Card dimensions
    card_width, card_height = 800, 100
    header_height = 200  # Resize to 200px height before cropping

    # Create a blank card
    card = Image.new("RGB", (card_width, card_height), color=(255, 255, 255))

    # Open and resize the header image to 200x800
    header_img = Image.open(header_image_path).resize((card_width, header_height))
    header_img_cropped = header_img.crop((0, 50, card_width, 150))  # Crop 50px from top and bottom
    card.paste(header_img_cropped, (0, 0))

    draw = ImageDraw.Draw(card)
    font_path = "fonts/EBGaramond-Bold.ttf"  # Adjust path
    font_medium = ImageFont.truetype(font_path, 50)

    # Add profile picture (resize to fit within 100x100)
    profile_pic = Image.open(profile_picture_path).resize((100, 100))
    card.paste(profile_pic, (20, 0))  # Paste it at the top-left corner

    # Draw the name and level on the card
    draw_opacity_box(card, (120,10 ), (570, 80), color=(0, 0, 0), opacity=128)
    create_hexagon_gem(draw, position=(730, 50), color=(22, 22, 22), number=9,  radius=50)
    level_position_center = (730, 20)  # Center position for the level number
    level_text = f"{level}"
    
    # Measure the bounding box of the level text
    level_bbox = font_medium.getbbox(level_text)
    level_text_width = level_bbox[2] - level_bbox[0]  # Width of the text

    # Adjust position to center the text horizontally
    level_position = (level_position_center[0] - level_text_width // 2, level_position_center[1])
    draw.text(level_position, level_text, font=font_medium, fill=(255, 255, 255))

    draw_fitting_text(draw, str(name).upper(), font_path, target_width=500, target_height=50, position=(130, 0), fill=(255, 255, 255))

    return card


def draw_rounded_profile_picture(draw, image_path, position, size=(180, 180)):
    """
    Process a profile picture with rounded corners and a border, then paste it onto the card
    
    Args:
        draw: ImageDraw object to draw on
        image_path: Path to the profile picture
        position: Tuple of (x, y) for where to paste the image
        size: Tuple of (width, height) for the profile picture size
    """
    border_width = 5
    border_color = (255, 255, 255, 230)  # Slightly transparent white
    
    # Load and resize profile picture, making it smaller to accommodate border
    inner_size = (size[0] - 2*border_width, size[1] - 2*border_width)
    profile = Image.open(image_path)
    profile = profile.convert('RGBA')
    profile = profile.resize(inner_size, Image.Resampling.LANCZOS)
    
    # Create the outer mask (for border)
    outer_mask = Image.new('L', size, 0)
    outer_draw = ImageDraw.Draw(outer_mask)
    radius = 20
    outer_draw.rounded_rectangle([(0, 0), size], radius=radius, fill=255)
    
    # Create the inner mask (for profile picture)
    inner_mask = Image.new('L', size, 0)
    inner_draw = ImageDraw.Draw(inner_mask)
    inner_draw.rounded_rectangle(
        [(border_width, border_width), 
         (size[0] - border_width -1, size[1] - border_width-1)],
        radius=radius-border_width,
        fill=255
    )
    # Create final image with border
    final_image = Image.new('RGBA', size, (0, 0, 0, 0))
    
    # Draw the border
    border_image = Image.new('RGBA', size, border_color)
    final_image.paste(border_image, (0, 0), outer_mask)
    
    # Draw the profile picture
    profile_with_transparency = Image.new('RGBA', size, (0, 0, 0, 0))
    profile_with_transparency.paste(profile, (border_width, border_width))
    final_image.paste(profile_with_transparency, (0, 0), inner_mask)
    
    # Get the image we're drawing on from the ImageDraw object
    target_image = draw._image
    
    # Paste the final image onto the target image
    target_image.paste(final_image, position, final_image)


def create_hexagon_gem(draw, position, color, number, radius=80, outline_width=10):
    hex_center_x, hex_center_y = position

    # Generate hexagon points
    angle_step = 60 # Hexagons have 60 degrees between vertices
    hex_points = [
        (hex_center_x + radius * math.cos(math.radians(angle)),
         hex_center_y + radius * math.sin(math.radians(angle)))
        for angle in range(0, 360, angle_step)
    ]

    # White border outline
    border_radius = radius + outline_width
    border_points = [
        (hex_center_x + border_radius * math.cos(math.radians(angle)),
         hex_center_y + border_radius * math.sin(math.radians(angle)))
        for angle in range(0, 360, angle_step)
    ]
    draw.polygon(border_points, fill="white")

    # Draw outer hexagon for the gem outline
    draw.polygon(hex_points, outline=color, width=outline_width)

    # Draw inner hexagon to fill the gem
    inner_radius = radius - outline_width
    inner_hex_points = [
        (hex_center_x + inner_radius * math.cos(math.radians(angle)),
         hex_center_y + inner_radius * math.sin(math.radians(angle)))
        for angle in range(0, 360, angle_step)
    ]
    draw.polygon(inner_hex_points, fill=color)

def draw_opacity_box(image, position, box_size, color=(0, 0, 0), opacity=128):
    """
    Draws a semi-transparent box on an image.

    Parameters:
        image (PIL.Image): The image to draw the box onto.
        position (tuple): The (x, y) coordinates for the top-left corner of the box.
        box_size (tuple): The (width, height) of the box.
        color (tuple): The RGB color of the box. Default is black.
        opacity (int): Opacity level from 0 (transparent) to 255 (opaque). Default is 128.
    """
    # Create a semi-transparent overlay with the specified color and opacity
    overlay = Image.new("RGBA", box_size, color + (opacity,))
    
    # Paste the overlay onto the main image at the specified position
    image.paste(overlay, position, overlay)


def create_gradient_background(width, height):
        """Create a gradient background."""
        gradient = Image.new("RGB", (width, height), color=0)
        draw = ImageDraw.Draw(gradient)
        for i in range(height):
            color = int(30 + 225 * (i / height))
            draw.line((0, i, width, i), fill=(color, color // 2, color // 3))
        return gradient


def draw_fitting_text(draw, text, font_path, target_width, target_height, position, fill=(255, 255, 255)):
    """
    Draws text that fits within a specific width and height by adjusting the font size.

    Args:
        draw (ImageDraw.Draw): ImageDraw object.
        text (str): Text to draw.
        font_path (str): Path to the font file.
        target_width (int): Desired maximum width of the text.
        target_height (int): Desired maximum height of the text.
        position (tuple): (x, y) for the top-left position.
        fill (tuple): Text color.
    """
    # Start with a reasonably large font size 
    font_size = 1
    font = ImageFont.truetype(font_path, font_size)
    temp_img = Image.new('RGBA', (1, 1), (0, 0, 0, 0))
    temp_draw = ImageDraw.Draw(temp_img)
    
    # Increase font size until it exceeds the target dimensions
    while True:
        font = ImageFont.truetype(font_path, font_size)
        bbox = temp_draw.textbbox((0, 0), text, font=font)
        text_width = bbox[2] - bbox[0]
        text_height = bbox[3] - bbox[1]
        
        if text_width > target_width or text_height > target_height:
            font_size -= 1  # Reduce to the previous size that fit
            font = ImageFont.truetype(font_path, font_size)
            bbox = temp_draw.textbbox((0, 0), text, font=font)
            break
            
        font_size += 1
    
    # Calculate the y position to align the text at the bottom of the target box
    y_position = position[1] + target_height - text_height

    # Draw the text onto the target image with the final fitting font size
    draw.text((position[0], y_position), text, font=font, fill=fill)
