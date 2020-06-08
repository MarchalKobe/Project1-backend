from RPi import GPIO
import board
import digitalio
from PIL import Image, ImageDraw, ImageFont
import adafruit_ssd1305
import textwrap
import pathlib
from datetime import datetime

class OLED:
    def __init__(self, width=128, height=64, cs=board.D19, dc=board.D16, reset=board.D20):
        WIDTH = width
        HEIGHT = height

        spi = board.SPI()
        oled_cs = digitalio.DigitalInOut(cs)
        oled_dc = digitalio.DigitalInOut(dc)
        oled_reset = digitalio.DigitalInOut(reset)
        self.oled = adafruit_ssd1305.SSD1305_SPI(WIDTH, HEIGHT, spi, oled_dc, oled_reset, oled_cs)

        self.oled.fill(0)
        self.oled.show()

        image = Image.new('1', (self.oled.width, self.oled.height))
        draw = ImageDraw.Draw(image)

        path = pathlib.Path(__file__).parent.absolute()
        self.font = ImageFont.truetype(f"{path}/fonts/repet.ttf")


    def show_text(self, text):
        image = Image.new('1', (self.oled.width, self.oled.height))
        draw = ImageDraw.Draw(image)

        text = text
        split = textwrap.wrap(text, width=21)

        font_width, font_height = self.font.getsize(text)

        line_height = 0

        for line in split:
            draw.text((0, line_height), line, font=self.font, fill=255)
            line_height += font_height
        
        self.oled.image(image)
        self.oled.show()
    

    def show_calendar_date(self, date):
        image = Image.new('1', (self.oled.width, self.oled.height))
        draw = ImageDraw.Draw(image)

        # Date
        font_width, font_height = self.font.getsize(date)
        draw.text(((self.oled.width - font_width) / 2, (self.oled.height - font_height) / 2), date, font=self.font, fill=255)

        # Arrows
        path = pathlib.Path(__file__).parent.absolute()

        arrow_up = Image.open(f"{path}/img/arrow_up.png")
        arrow_up_size = arrow_up.size
        image.paste(arrow_up, (int(self.oled.width / 2) - int(arrow_up_size[0] / 2), 0))

        arrow_down = Image.open(f"{path}/img/arrow_down.png")
        arrow_down_size = arrow_down.size
        image.paste(arrow_down, (int(self.oled.width / 2) - int(arrow_down_size[0] / 2), self.oled.height - arrow_down_size[1]))
        
        self.oled.image(image)
        self.oled.show()
    

    def show_calendar_event(self, time, event):
        image = Image.new('1', (self.oled.width, self.oled.height))
        draw = ImageDraw.Draw(image)

        # Time
        font_width, font_height = self.font.getsize(time)
        draw.text((0, ((self.oled.height - (font_height * 4)) / 2)), time, font=self.font, fill=255)

        # Event
        text = event
        split = textwrap.wrap(text, width=21)

        font_width, font_height = self.font.getsize(text)

        line_height = 0

        for line in split:
            draw.text((0, ((self.oled.height - (font_height * 2)) / 2) + line_height), line, font=self.font, fill=255)
            line_height += font_height

        # Arrows
        path = pathlib.Path(__file__).parent.absolute()

        arrow_up = Image.open(f"{path}/img/arrow_up.png")
        arrow_up_size = arrow_up.size
        image.paste(arrow_up, (int(self.oled.width / 2) - int(arrow_up_size[0] / 2), 0))

        arrow_down = Image.open(f"{path}/img/arrow_down.png")
        arrow_down_size = arrow_down.size
        image.paste(arrow_down, (int(self.oled.width / 2) - int(arrow_down_size[0] / 2), self.oled.height - arrow_down_size[1]))
        
        self.oled.image(image)
        self.oled.show()
    

    def show_message(self, text):
        image = Image.new('1', (self.oled.width, self.oled.height))
        draw = ImageDraw.Draw(image)

        # Event
        split = textwrap.wrap(text, width=21)

        font_width, font_height = self.font.getsize(text)

        line_height = 0

        for line in split:
            draw.text((0, ((self.oled.height - (font_height * 4)) / 2) + line_height), line, font=self.font, fill=255)
            line_height += font_height

        # Ja / Nee
        text = "Ja"
        text_width, text_height = draw.textsize(text, self.font)
        draw.text((int(self.oled.width - text_width), 0), text, font=self.font, fill=255)

        text = "Nee"
        text_width, text_height = draw.textsize(text, self.font)
        draw.text((int(self.oled.width - text_width), self.oled.height - text_height), text, font=self.font, fill=255)

        self.oled.image(image)
        self.oled.show()
    

    def show_clock(self):
        image = Image.new('1', (self.oled.width, self.oled.height))
        draw = ImageDraw.Draw(image)

        # Time
        now = datetime.now()
        text = now.strftime("%H:%M:%S")

        font_width, font_height = self.font.getsize(text)
        draw.text(((self.oled.width - font_width) / 2, (self.oled.height - font_height) / 2), text, font=self.font, fill=255)
        
        self.oled.image(image)
        self.oled.show()
    

    def clear_screen(self):
        self.oled.fill(0)
        self.oled.show()