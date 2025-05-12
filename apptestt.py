from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import StreamingResponse, JSONResponse
from io import BytesIO
import requests
from PIL import Image, ImageDraw, ImageFont, ImageFilter
from pydantic import BaseModel
import uvicorn

app = FastAPI()

class BackgroundGradient(BaseModel):
    primary_color: str
    secondary_color: str

class Price(BaseModel):
    usd: int
    star: int
    ton: int

class Gift(BaseModel):
    name: str
    image: str
    quantity: int

class GiftCardData(BaseModel):
    background_gradient: BackgroundGradient
    price: Price
    gift: Gift
    time_display: str

def hex_to_rgb(hex_color):
    hex_color = hex_color.lstrip('#')
    return tuple(int(hex_color[i:i + 2], 16) for i in (0, 2, 4))

def create_diagonal_gradient(width, height, start_color, end_color):
    gradient = Image.new('RGB', (width, height), start_color)
    draw = ImageDraw.Draw(gradient)

    for x in range(width):
        for y in range(height):
            ratio = ((x + y) / (width + height)) * 1.5
            r = int(start_color[0] + (end_color[0] - start_color[0]) * ratio)
            g = int(start_color[1] + (end_color[1] - start_color[1]) * ratio)
            b = int(start_color[2] + (end_color[2] - start_color[2]) * ratio)
            draw.point((x, y), fill=(r, g, b))

    return gradient

def create_variable_blur_effect(image, max_blur_radius, blur_start_y, blur_end_y):
    width, height = image.size

    blur_start_y = max(0, min(blur_start_y, height))
    blur_end_y = max(0, min(blur_end_y, height))

    if blur_start_y >= blur_end_y:
        return image.copy()

    gradient = Image.new('L', (width, height), 0)
    draw = ImageDraw.Draw(gradient)

    for y in range(height):
        if y < blur_start_y or y > blur_end_y:
            alpha = 0
        else:
            alpha = int(255 * (y - blur_start_y) / (blur_end_y - blur_start_y))
        draw.line([(0, y), (width, y)], fill=alpha)

    blur_steps = 5
    blurred_images = []
    for i in range(blur_steps):
        radius = max_blur_radius * (i / (blur_steps - 1))
        blurred = image.filter(ImageFilter.GaussianBlur(radius))
        blurred_images.append(blurred)

    result = Image.new('RGBA', (width, height))
    for y in range(height):
        alpha = gradient.getpixel((0, y))
        if alpha == 0:
            row = image.crop((0, y, width, y + 1))
        else:
            step = min(blur_steps - 1, int((alpha / 255) * (blur_steps - 1)))
            row = blurred_images[step].crop((0, y, width, y + 1))
        result.paste(row, (0, y))

    return result

def create_gift_card(data: GiftCardData):
    width, height = 512, 512
    radius = 79

    star_image = Image.open("Star 1.png")
    star_image = star_image.convert("RGBA")
    data_image = star_image.getdata()
    new_data = []
    for item in data_image:
        if item[0] > 240 and item[1] > 240 and item[2] > 240:
            new_data.append((255, 255, 255, 210))
        else:
            new_data.append(item)
    star_image.putdata(new_data)

    ton_image = Image.open("Ton 1.png")
    ton_image = ton_image.convert("RGBA")
    ton_data = ton_image.getdata()
    new_ton_data = []
    for item in ton_data:
        if item[0] > 240 and item[1] > 240 and item[2] > 240:
            new_ton_data.append((255, 255, 255, 210))
        else:
            new_ton_data.append(item)
    ton_image.putdata(new_ton_data)

    ellipse_image = Image.open("Ellipse 1.png")
    ellipse_image = ellipse_image.convert("RGBA")
    ellipse_data = ellipse_image.getdata()
    new_ellipse_data = []
    for item in ellipse_data:
        if item[0] > 240 and item[1] > 240 and item[2] > 240:
            new_ellipse_data.append((255, 255, 255, 180))
        else:
            new_ellipse_data.append(item)
    ellipse_image.putdata(new_ellipse_data)

    start_color = hex_to_rgb(data.background_gradient.primary_color)
    end_color = hex_to_rgb(data.background_gradient.secondary_color)

    gradient = create_diagonal_gradient(width, height, start_color, end_color)

    mask = Image.new('L', (width, height), 0)
    draw_mask = ImageDraw.Draw(mask)
    draw_mask.rounded_rectangle([(0, 0), (width, height)], radius, fill=255)

    rounded_gradient = Image.new('RGBA', (width, height), (255, 255, 255, 0))
    rounded_gradient.paste(gradient, mask=mask)

    img = Image.new('RGBA', (width, height), (255, 255, 255, 0))
    img.paste(rounded_gradient, (0, 0))

    try:
        font_large_bold = ImageFont.truetype('Inter-Bold.otf', 75)
        font_medium = ImageFont.truetype('Inter-Regular.otf', 35)
        font_small_thin = ImageFont.truetype('Inter-Regular.otf', 25)
        font_small_bold = ImageFont.truetype('Inter-Bold.otf', 25)
    except IOError:
        raise HTTPException(status_code=500, detail="Font loading error")

    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3'
        }
        response = requests.get(data.gift.image, headers=headers)
        response.raise_for_status()
        gift_img = Image.open(BytesIO(response.content))

        new_size = (385, 385)
        gift_img.thumbnail(new_size, Image.Resampling.LANCZOS)

        max_top_position = 210

        pos_x = (width - gift_img.width) // 2
        pos_y = max_top_position

        rounded_mask = Image.new('L', (width, height), 0)
        draw_mask = ImageDraw.Draw(rounded_mask)
        draw_mask.rounded_rectangle([(0, 0), (width, height)], radius, fill=255)

        cropped_mask = rounded_mask.crop((pos_x, pos_y, pos_x + gift_img.width, pos_y + gift_img.height))

        rounded_gift_img = Image.new('RGBA', gift_img.size, (0, 0, 0, 0))
        rounded_gift_img.paste(gift_img, (0, 0), mask=cropped_mask)

        temp_img = img.copy()
        temp_img.paste(rounded_gift_img, (pos_x, pos_y), rounded_gift_img)

        blur_background = Image.new('RGBA', temp_img.size, (0, 0, 0, 255))
        blur_background.paste(temp_img, (0, 0))

        gift_region = blur_background.crop((pos_x, pos_y, pos_x + gift_img.width, pos_y + gift_img.height))

        blurred_region = create_variable_blur_effect(
            gift_region,
            max_blur_radius=3,
            blur_start_y=0,
            blur_end_y=302
        )

        img.paste(blurred_region, (pos_x, pos_y), blurred_region)

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Image processing error: {str(e)}")

    text_mask = Image.new('RGBA', (width, height), (0, 0, 0, 0))
    draw = ImageDraw.Draw(text_mask)

    formatted_price_usd = f"{data.price.usd:,}".replace(",", " ")
    formatted_price_stars = f"{data.price.star:,}".replace(",", " ")
    formatted_price_ton = f"{data.price.ton:,}".replace(",", " ")
    formatted_quantity = f"{data.gift.quantity:,}".replace(",", " ")

    draw.text((52, 37), f"${formatted_price_usd}", font=font_large_bold, fill=(255, 255, 255, 210))

    new_star_size = (33, 33)
    star_image = star_image.resize(new_star_size, Image.Resampling.LANCZOS)
    star_pos = (58, 134)
    text_mask.paste(star_image, star_pos, star_image)
    draw.text((93, 131), f"{formatted_price_stars}", font=font_medium, fill=(255, 255, 255, 180))

    base_ton_pos = 132
    new_ton_size = (28, 28)
    ton_image = ton_image.resize(new_ton_size, Image.Resampling.LANCZOS)
    star_count_length = len(str(data.price.star))
    additional_offset = (star_count_length - 1) * 23 if star_count_length > 1 else 0
    ton_pos = (base_ton_pos + additional_offset, 138)
    text_mask.paste(ton_image, ton_pos, ton_image)
    draw.text((163 + additional_offset, 131), f"{formatted_price_ton}", font=font_medium, fill=(255, 255, 255, 180))

    new_ellipse_size = (28, 28)
    ellipse_image = ellipse_image.resize(new_ellipse_size, Image.Resampling.LANCZOS)
    ellipse_pos = (56, 182)
    text_mask.paste(ellipse_image, ellipse_pos, ellipse_image)
    draw.text((91, 174), f"{data.time_display}", font=font_medium, fill=(255, 255, 255, 120))

    draw.text((55, 437), f"{data.gift.name}", font=font_small_bold, fill='#FFFFFF')

    text_image = Image.new('RGBA', (width, height), (0, 0, 0, 0))
    text_draw = ImageDraw.Draw(text_image)
    text_draw.text((328, 437), f"{formatted_quantity} pcs", font=font_small_thin, fill='#FFFFFF')

    text_image = text_image.filter(ImageFilter.GaussianBlur(radius=0.5))

    img.paste(text_image, (0, 0), text_image)
    img = Image.alpha_composite(img, text_mask)

    img_io = BytesIO()
    img.save(img_io, 'PNG')
    img_io.seek(0)

    return img_io

@app.post("/generate_gift_card")
async def generate_gift_card(data: GiftCardData):
    try:
        img_io = create_gift_card(data)
        return StreamingResponse(img_io, media_type="image/png")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
uvicorn.run(app)