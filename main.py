import re
import textwrap
import os
import nltk
import markovify
import uuid

from random import randint, choice

from PIL import Image
from PIL import ImageDraw
from PIL import ImageFont


class POSifiedText(markovify.Text):
    def word_split(self, sentence):
        words = re.split(self.word_split_pattern, sentence)
        if words[0] != "":
            words = ["::".join(tag) for tag in nltk.pos_tag(words)]
        else:
            words = list("", )
        return words

    def word_join(self, words):
        sentence = " ".join(word.split("::")[0] for word in words)
        return sentence


def main():
    image = Image.open('images/{}'.format(choice(os.listdir('images')))).convert('RGBA')

    with open("txt/prophecy_to_train.txt", 'r', encoding='latin1') as f:
        text_a = f.read()

    text_model = POSifiedText(text_a, state_size=2)

    for i in range(1):
        output_cima = (text_model.make_short_sentence(randint(55, 90), tires=1000000000))

    for i in range(1):
        output_baixo = (text_model.make_short_sentence(randint(55, 90), tires=1000000000))

    top_string = (output_cima)
    bottom_string = (output_baixo)

    regex = r'\Â'
    subst = "'"
    top_string = re.sub(regex, subst, top_string, 0, re.MULTILINE)
    bottom_string = re.sub(regex, subst, bottom_string, 0, re.MULTILINE)

    top_string = textwrap.wrap(top_string, width=18)
    bottom_string = textwrap.wrap(bottom_string, width=18)

    draw_text(100, top_string, image)

    if len(bottom_string) > 1:
        current_h = 1700 - (90 * len(bottom_string))
    else:
        current_h = 1700

    draw_text(current_h, bottom_string, image)

    image = image.convert('RGB')

    image.save('output_images/{}.jpg'.format(str(uuid.uuid4())))


def draw_text(original_h, text, imag):
    MAX_W, MAX_H = 1080, 1920
    current_h, pad = original_h, 1

    font = ImageFont.truetype("FuturaLT-Bold.ttf", 90)
    draw = ImageDraw.Draw(imag)

    # gambiarra do caralho… o certo é usar cairo:
    # https://stackoverflow.com/questions/8049764/how-can-i-draw-text-with-different-stroke-and-fill-colors-on-images-with-python

    for line in text:
        w, h = draw.textsize(line, font=font)
        draw.text((((MAX_W - w) / 2) + 1, current_h), line, font=font, fill=(0, 0, 0))
        current_h += h + pad

    current_h = original_h
    for line in text:
        w, h = draw.textsize(line, font=font)
        draw.text((((MAX_W - w) / 2) - 1, current_h), line, font=font, fill=(0, 0, 0))
        current_h += h + pad

    current_h = original_h
    for line in text:
        w, h = draw.textsize(line, font=font)
        draw.text(((MAX_W - w) / 2, current_h - 1), line, font=font, fill=(0, 0, 0))
        current_h += h + pad

    current_h = original_h
    for line in text:
        w, h = draw.textsize(line, font=font)
        draw.text(((MAX_W - w) / 2, current_h + 1), line, font=font, fill=(0, 0, 0))
        current_h += h + pad

    current_h = original_h
    for line in text:
        w, h = draw.textsize(line, font=font)
        draw.text(((MAX_W - w) / 2, current_h), line, font=font)
        current_h += h + pad


if __name__ == '__main__':
    main()
