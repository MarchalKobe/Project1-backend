from RPi import GPIO
import board
import digitalio
from PIL import Image, ImageDraw, ImageFont
import adafruit_ssd1305
import textwrap
import pathlib

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