from PIL import Image, ImageDraw, ImageFont, ImageOps
import datetime
import json
import math

def create_gradient_multiple(size, colors):
    """Create a gradient image with 5 colors"""
    total_colors = len(colors)
    base = Image.new('RGB', size, colors[0])
    
    for i in range(1, total_colors):
        top = Image.new('RGB', size, colors[i])
        mask = Image.new('L', size)
        mask_data = []
        
        for y in range(size[1]):
            for x in range(size[0]):
                progress = (x / size[0] + y / size[1]) / 2
                if progress < i/4:
                    alpha = int(255 * (progress * 4 - (i-1)))
                else:
                    alpha = 255
                mask_data.append(alpha)
        
        mask.putdata(mask_data)
        base.paste(top, (0, 0), mask)
    
    return base



def extract_colors_from_image(image_path, num_points=4):
    """Extract colors from an image along a diagonal line"""
    with Image.open(image_path) as img:
        width, height = img.size
        colors = []
        
        center_y = height // 2
        
        for i in range(num_points):
            x = int(width * i / (num_points - 1))
            y = center_y
            
            # Ensure coordinates are within image bounds
            x = min(max(x, 0), width - 1)
            y = min(max(y, 0), height - 1)
            
            color = img.getpixel((x, y))
            colors.append(color)
        
        # if colors are the same at the start and end, change color 2 to white
        if colors[0] == colors[-1]:
            colors[2] = (255, 255, 255)
            colors[1] = (0, 0, 0)
        
    return colors




def draw_rounded_rectangle(draw, position, size, radius, fill, outline=None):
    """Draw a rounded rectangle"""
    x, y = position
    width, height = size
    diameter = radius * 2

    # Draw main rectangle
    draw.rectangle([x + radius, y, x + width - radius, y + height], fill=fill)
    draw.rectangle([x, y + radius, x + width, y + height - radius], fill=fill)

    # Draw four corners
    draw.pieslice([x, y, x + diameter, y + diameter], 180, 270, fill=fill)
    draw.pieslice([x + width - diameter, y, x + width, y + diameter], 270, 360, fill=fill)
    draw.pieslice([x, y + height - diameter, x + diameter, y + height], 90, 180, fill=fill)
    draw.pieslice([x + width - diameter, y + height - diameter, x + width, y + height], 0, 90, fill=fill)

    # Draw outline
    if outline:
        draw.arc([x, y, x + diameter, y + diameter], 180, 270, fill=outline)
        draw.arc([x + width - diameter, y, x + width, y + diameter], 270, 360, fill=outline)
        draw.arc([x, y + height - diameter, x + diameter, y + height], 90, 180, fill=outline)
        draw.arc([x + width - diameter, y + height - diameter, x + width, y + height], 0, 90, fill=outline)
        draw.line([x + radius, y, x + width - radius, y], fill=outline)
        draw.line([x + radius, y + height, x + width - radius, y + height], fill=outline)
        draw.line([x, y + radius, x, y + height - radius], fill=outline)
        draw.line([x + width, y + radius, x + width, y + height - radius], fill=outline)

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

def draw_opacity_box_rounded(image, position, box_size, color=(0, 0, 0), opacity=128, corner_radius=20):
    overlay = Image.new("RGBA", box_size, (0, 0, 0, 0))

    # Draw a rounded rectangle with the specified color and opacity on the overlay
    overlay_draw = ImageDraw.Draw(overlay)
    overlay_draw.rounded_rectangle(
        (0, 0, box_size[0], box_size[1]),
        radius=corner_radius,
        fill=color + (opacity,)
    )

    # Paste the overlay onto the main image at the specified position
    image.paste(overlay, position, overlay)

def draw_opacity_box_rounded_with_text(image, position, text, font, color=(0, 0, 0), opacity=128, corner_radius=20, outline_color=(255, 255, 255), box_height=50):
    # Calculate the width of the box based on the text
    text_width, text_height = font.getbbox(text)[2:4]  # Get width and height of the text
    box_width = text_width + 20  # Add some padding around the text
    
    # Create a new image for the overlay
    overlay = Image.new("RGBA", (box_width, box_height), (0, 0, 0, 0))

    # Draw the rounded rectangle with the specified color and opacity
    overlay_draw = ImageDraw.Draw(overlay)
    overlay_draw.rounded_rectangle(
        (0, 0, box_width, box_height),
        radius=corner_radius,
        fill=color + (opacity,)
    )

    # Draw a white outline around the rounded rectangle
    overlay_draw.rounded_rectangle(
        (0, 0, box_width, box_height),
        radius=corner_radius,
        outline=outline_color,
        width=3  # Width of the outline
    )

    # Calculate the position to center the text in the box
    text_x = (box_width - text_width) // 2  # X position for centered text
    text_y = (box_height - text_height) // 2  # Y position for centered text

    # Draw the text on the image
    draw = ImageDraw.Draw(overlay)
    draw.text((text_x, text_y), text, font=font, fill="white")

    # Paste the overlay onto the main image at the specified position
    image.paste(overlay, position, overlay)


def create_badge_element(background_img, badge_box_position, badge_box_size, badges, font_path, font_size=20, text_color=(255, 255, 255), padding=5):
    # Create a new transparent image for the badge grid
   
    badge_grid = Image.new('RGBA', badge_box_size, (0, 0, 0, 0))
    draw = ImageDraw.Draw(badge_grid)
    font = ImageFont.truetype(font_path, font_size)

    # Calculate grid dimensions
    grid_cols, grid_rows = 6, 4
    total_badges = grid_cols * grid_rows
    badge_width = badge_box_size[0] // grid_cols
    badge_height = badge_box_size[1] // grid_rows

    for i in range(total_badges):
        row = i // grid_cols
        col = i % grid_cols

        # Determine badge
        if i < len(badges):
            badge = badges[i]
        else:
            badge = {"badge": "default"}

      
        # Load badge image
        try:
            badge_img = Image.open(f"images/badges/{badge[0]}.png").convert("RGBA")
        except KeyError:
            badge_img = Image.open(f"images/badges/default.png").convert("RGBA")

        # Resize badge image while maintaining aspect ratio
        original_width, original_height = badge_img.size
        aspect_ratio = original_width / original_height

        # Calculate new size based on aspect ratio
        target_width = badge_width - 2 * padding
        target_height = badge_height - 2 * padding

        if target_width / aspect_ratio <= target_height:
            new_width = target_width
            new_height = int(target_width / aspect_ratio)
        else:
            new_width = int(target_height * aspect_ratio)
            new_height = target_height

        badge_img = badge_img.resize((new_width, new_height), Image.LANCZOS)

        # Calculate position
        x = col * badge_width + padding + (target_width - new_width) // 2
        y = row * badge_height + padding + (target_height - new_height) // 2

        # Paste badge image onto the badge grid
        badge_grid.paste(badge_img, (x, y), badge_img)

        # Draw badge text
        

    # Paste the badge grid onto the background image
    background_img.paste(badge_grid, badge_box_position, badge_grid)

def create_hexagon_gem(draw, position, color, number, radius=100, outline_width=10):
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
  

def create_profile_card(header_image_path, name, title, level, badges, timespent,  currency, xp, interests, booster, profile_picture_path = "temp_profile_picture.png"):
    # Card dimensions
    print("Creating profile card for user: ", name)
    card_width, card_height = 800 , 600
    header_height = 500
    xp_bar_size = (589, 30)
    xp_bar_position = (200, 158)

    font_path = "fonts/EBGaramond-Bold.ttf"  # Example path
    font_large = ImageFont.truetype(font_path, 80)
    font_medium = ImageFont.truetype(font_path, 50)
    font_small = ImageFont.truetype(font_path, 35)
    font_small_2 = ImageFont.truetype(font_path, 30)
    font_small_3 = ImageFont.truetype(font_path, 20)


    # Extract gradient colors from header image
    colors = extract_colors_from_image(header_image_path)
    
    # Create gradient background using the extracted colors
    gradient_background = create_gradient_multiple((card_width, card_height), colors)

    # Create a new blank image for the profile card
    profile_card = Image.new('RGB', (card_width, card_height), color=(255, 255, 255))

    # Paste gradient onto the profile card
    profile_card.paste(gradient_background, (0, 0))

    # Open and paste the header image
    header_img = Image.open(header_image_path).resize((card_width, header_height))
    header_image = header_img.resize((800, 200))
    profile_card.paste(header_image, (0, 0))

    #draw_opacity_box(profile_card, (170,30), (470, 140), (0, 0, 0), opacity=128)
    draw_opacity_box_rounded(profile_card, (140,10), (650, 179), (0, 0, 0), opacity=128, corner_radius=30)
    #draw_opacity_box_rounded(profile_card, (590,1), (200, 40), (0, 0, 0), opacity=128, corner_radius=30)
    draw_opacity_box_rounded(profile_card, (10,210), (780, 380), (0, 0, 0), opacity=128, corner_radius=30)
  
    create_badge_element(
        profile_card,
        (330, 255),
        (550, 325),
        badges,
        font_path,
        font_size=30,
        text_color=(255,255,255),
        padding=5
    )

    arcanum_img = Image.open("images/server_icons/arcanum_box.png").convert("RGBA")
    arcanum_img = arcanum_img.resize((150, 150))
    profile_card.paste(arcanum_img, (0, 430), arcanum_img)

    draw = ImageDraw.Draw(profile_card)

    currency_position = (110, 450)
    currency_text = f"{currency}"
    draw.text(currency_position, currency_text, font=font_large, fill=(255, 255, 255))

    create_hexagon_gem(draw, position=(700, 80), color=(22, 22, 22), number=9, radius=60)
    # Define text and font (adjust font path as needed)
   
    

    max_width = 300     # Maximum width for the text boxes
    current_x_text = 20
    current_y_text = 265

    #sort text based on lengh smallest first
    interests = sorted(interests, key=lambda x: len(x['item_name']))

  
    for text in interests:
        # Calculate the text width using the font
        text = text['item_name']
        text_width, _ = font_small_2.getbbox(text)[2:4]
        
        # Check if adding the current box would exceed the maximum width
        if current_x_text + text_width > max_width:
            # Move to the next line
            current_x_text = 20
            current_y_text += 55  # Adjust this value for vertical spacing between rows
        
        # Draw the box with text
        draw_opacity_box_rounded_with_text(profile_card, (current_x_text, current_y_text), text, font_small_2)
        
        # Update current_x_text to position the next box
        current_x_text += text_width + 25  # Add spacing between boxes

    intrests_position = (25, 220)
    intrests_text = f"Interests:"
    draw.text(intrests_position, intrests_text, font=font_small, fill=(255, 255, 255))


    font_large = ImageFont.truetype(font_path, 80)
    font_medium = ImageFont.truetype(font_path, 50)
    font_small = ImageFont.truetype(font_path, 35)
    
    # Draw XP bar
    xp = max(6, min(xp, 100)) #needs to be atleast 6 to draw pixels incircle of start of bar
 
    xp_percentage = xp / 100
    filled_width = max(1, int(xp_bar_size[0] * xp_percentage))  # Ensure at least 1px width
    bar_radius = xp_bar_size[1] // 2  # Half the height for rounded ends
  
    # Draw background bar
    draw_rounded_rectangle(draw, 
                           xp_bar_position, 
                           xp_bar_size, 
                           bar_radius, 
                           fill="white", 
                           #outline=img_config['xp_bar_border_color'])
    )

    # Draw filled portion of the bar
    draw_rounded_rectangle(draw, 
                           xp_bar_position, 
                           (filled_width , xp_bar_size[1]), 
                           bar_radius, 
                           fill=(96, 239, 255))

    #draw profile picture
    draw_rounded_profile_picture(draw,
                                profile_picture_path,
                                (10,10)
                               
                                )
  
    draw_fitting_text(draw, str(name).upper(), font_path, target_width=420, target_height=50, position=(200, 75), fill=(255, 255, 255))

   
   
    level_position_center = (700, 25)  # Center position for the level number
    level_text = f"{level}"
    
    # Measure the bounding box of the level text
    level_bbox = font_large.getbbox(level_text)
    level_text_width = level_bbox[2] - level_bbox[0]  # Width of the text

    # Adjust position to center the text horizontally
    level_position = (level_position_center[0] - level_text_width // 2, level_position_center[1])
    draw.text(level_position, level_text, font=font_large, fill=(255, 255, 255))

    #title
    title_position = (200,50)
    title_text = title
    draw.text(title_position, title_text, font=font_small, fill=(255, 255, 255))

    #Accolades
    accolades_position = (450, 200)
    accolades_text = "Accolades"
    draw.text(accolades_position, accolades_text, font=font_medium, fill=(255, 255, 255))
   
    #statistics
    #stats_position = (20, 400)
    #stats_text = "Statistics"
    #draw.text(stats_position, stats_text, font=font_medium, fill=(255, 255, 255))

    #beta
    #draw.text((20, 350), , font=font_large, fill=(255, 255, 255))

  
 
    '''
    #currency
    currency_position = (335, 530)
    currency_text = f"Currency: {currency}"
    draw.text(currency_position, currency_text, font=font_small, fill=(255, 255, 255))

    #chats
    chats_position = (335, 470)
    chats_text = "Chats: 0"
    draw.text(chats_position, chats_text, font=font_small, fill=(255, 255, 255))

    #time spent
    time_position = (335, 500)
    time_text = f"Time Spent: {timespent}"
    draw.text(time_position, time_text, font=font_small, fill=(255, 255, 255))
    '''


    # Save or show the profile card
    profile_card.save("profile_card.png")

def create_level_card(header_image_path, name, title, level, xp , profile_picture_path = "temp_profile_picture.png"):
   
     # Card dimensions
    card_width, card_height = 800 , 200
    header_height = 500
    xp_bar_size = (589, 30)
    xp_bar_position = (200, 158)

    font_path = "fonts/EBGaramond-Bold.ttf"  # Example path
    ont_large = ImageFont.truetype(font_path, 80)
    font_medium = ImageFont.truetype(font_path, 50)
    font_small = ImageFont.truetype(font_path, 35)
    font_small_2 = ImageFont.truetype(font_path, 30)
    font_small_3 = ImageFont.truetype(font_path, 20)


 
    # Create a new blank image for the profile card
    profile_card = Image.new('RGB', (card_width, card_height), color=(255, 255, 255))

    # Open and paste the header image
    header_img = Image.open(header_image_path).resize((card_width, header_height))
    header_image = header_img.resize((800, 200))
    profile_card.paste(header_image, (0, 0))

    #draw_opacity_box(profile_card, (170,30), (470, 140), (0, 0, 0), opacity=128)
    draw_opacity_box_rounded(profile_card, (140,10), (650, 179), (0, 0, 0), opacity=128, corner_radius=30)
    #draw_opacity_box_rounded(profile_card, (590,1), (200, 40), (0, 0, 0), opacity=128, corner_radius=30)
    draw_opacity_box_rounded(profile_card, (10,210), (780, 380), (0, 0, 0), opacity=128, corner_radius=30)


    font_large = ImageFont.truetype(font_path, 80)
    font_medium = ImageFont.truetype(font_path, 50)
    font_small = ImageFont.truetype(font_path, 35)
    

   
    xp = max(6, min(int(xp), 100)) #needs to be atleast 6 to draw pixels incircle of start of bar
 
    xp_percentage = xp / 100
    filled_width = max(1, int(xp_bar_size[0] * xp_percentage))  # Ensure at least 1px width
    bar_radius = xp_bar_size[1] // 2  # Half the height for rounded ends
  

    draw = ImageDraw.Draw(profile_card)

    create_hexagon_gem(draw, position=(700, 80), color=(22, 22, 22), number=9, radius=60)

      # Draw background bar
    draw_rounded_rectangle(draw, 
                           xp_bar_position, 
                           xp_bar_size, 
                           bar_radius, 
                           fill="white", 
                           #outline=img_config['xp_bar_border_color'])
    )


    draw_rounded_rectangle(draw, 
                        xp_bar_position, 
                        (filled_width , xp_bar_size[1]), 
                        bar_radius, 
                        fill=(96, 239, 255))

    #draw profile picture
    draw_rounded_profile_picture(draw,
                                profile_picture_path,
                                (10,10)
                               
                                )
  

    draw_fitting_text(draw, str(name).upper(), font_path, target_width=570, target_height=50, position=(200, 75), fill=(255, 255, 255))

   
    level_position_center = (700, 25)  # Center position for the level number
    level_text = f"{level}"
    
    # Measure the bounding box of the level text
    level_bbox = font_large.getbbox(level_text)
    level_text_width = level_bbox[2] - level_bbox[0]  # Width of the text

    # Adjust position to center the text horizontally
    level_position = (level_position_center[0] - level_text_width // 2, level_position_center[1])
    draw.text(level_position, level_text, font=font_large, fill=(255, 255, 255))

    title_position = (200,50)
    title_text = title
    draw.text(title_position, title_text, font=font_small, fill=(255, 255, 255))

    profile_card.save("level_card.png")