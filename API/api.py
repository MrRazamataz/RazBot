from flask import Flask, request, abort, jsonify, send_file
import json
from flask_cors import CORS, cross_origin
app = Flask(__name__)
cors = CORS(app, resources={r"/*": {"origins": "*", "allow_headers": "*", "expose_headers": "*"}})
from PIL import Image, ImageDraw, ImageFont
import textwrap
import requests
import os
import urllib.request
import traceback
import random
import string
import yt_dlp
import re


def random_char(y):
    return ''.join(random.choice(string.ascii_letters) for x in range(y))


@app.route('/memegen/impact', methods=['GET'])
def memegen_impact():
    try:
        if request.method == 'GET':
            top_text = request.args.get('top_text')
            bottom_text = request.args.get('bottom_text')
            image_url = request.args.get('image_url')
            if top_text and bottom_text and image_url:
                # download image
                img_data = requests.get(image_url).content
                with open('image_name.jpg', 'wb') as handler:
                    handler.write(img_data)
                # load image
                im = Image.open('image_name.jpg')
                im = im.convert('RGB')
                draw = ImageDraw.Draw(im)
                image_width, image_height = im.size

                # load font
                font_size = 9
                stroke_width = 5
                font = ImageFont.truetype(font="fonts/impact.ttf", size=int(image_height * font_size) // 100)

                # convert text to uppercase
                top_text = top_text.upper()
                bottom_text = bottom_text.upper()

                # text wrapping
                char_width, char_height = font.getsize('A')
                chars_per_line = image_width // char_width
                top_lines = textwrap.wrap(top_text, width=chars_per_line)
                bottom_lines = textwrap.wrap(bottom_text, width=chars_per_line)

                # draw top lines
                y = 10
                for line in top_lines:
                    line_width, line_height = font.getsize(line)
                    x = (image_width - line_width) / 2
                    draw.text((x, y), line, fill='white', font=font, stroke_width=stroke_width, stroke_fill='black')
                    y += line_height

                # draw bottom lines
                y = image_height - char_height * len(bottom_lines) - 15
                for line in bottom_lines:
                    line_width, line_height = font.getsize(line)
                    x = (image_width - line_width) / 2
                    draw.text((x, y), line, fill='white', font=font, stroke_width=stroke_width, stroke_fill='black')
                    y += line_height

                # add razbot.xyz hahahaha L
                minus_x = image_width - 15
                draw.text((image_width - minus_x, image_height - 15), "razbot.xyz", fill='white', stroke_width=2,
                          stroke_fill='black')

                # save meme
                os.remove("image_name.jpg")
                random_file = random_char(10)
                filename = f"images/impact-{random_file}.jpg"
                im.save(filename)

                output = {"url": f"https://api.razbot.xyz/image?file=impact-{random_file}.jpg"}
                return output, 200

            else:
                output = {"error": "Please provide top_text bottom_text image_link"}
                return output
    except Exception as e:
        print(e)
        print(traceback.print_exc())
        abort(500)


@app.route('/memegen/megamind', methods=['GET'])
def memegen_megamind():
    try:
        if request.method == 'GET':
            top_text = request.args.get('top_text')
            bottom_text = request.args.get('bottom_text')
            if top_text and bottom_text:
                # load image
                im = Image.open('templates/megamind.png')
                im = im.convert('RGB')
                draw = ImageDraw.Draw(im)
                image_width, image_height = im.size

                # load font
                font_size = 9
                stroke_width = 5
                font = ImageFont.truetype(font="fonts/impact.ttf", size=int(image_height * font_size) // 100)

                # convert text to uppercase
                top_text = top_text.upper()
                bottom_text = bottom_text.upper()

                # text wrapping
                char_width, char_height = font.getsize('A')
                chars_per_line = image_width // char_width
                top_lines = textwrap.wrap(top_text, width=chars_per_line)
                bottom_lines = textwrap.wrap(bottom_text, width=chars_per_line)

                # draw top lines
                y = 10
                for line in top_lines:
                    line_width, line_height = font.getsize(line)
                    x = (image_width - line_width) / 2
                    draw.text((x, y), line, fill='white', font=font, stroke_width=stroke_width, stroke_fill='black')
                    y += line_height

                # draw bottom lines
                y = image_height - char_height * len(bottom_lines) - 15
                for line in bottom_lines:
                    line_width, line_height = font.getsize(line)
                    x = (image_width - line_width) / 2
                    draw.text((x, y), line, fill='white', font=font, stroke_width=stroke_width, stroke_fill='black')
                    y += line_height

                # add razbot.xyz hahahaha L
                minus_x = image_width - 15
                draw.text((image_width - minus_x, image_height - 15), "razbot.xyz", fill='white', stroke_width=2,
                          stroke_fill='black')

                # save meme
                random_file = random_char(10)
                filename = f"images/megamind-{random_file}.jpg"
                im.save(filename)

                output = {"url": f"https://api.razbot.xyz/image?file=megamind-{random_file}.jpg"}
                return output, 200

            else:
                output = {"error": "Please provide top_text bottom_text"}
                return output
    except Exception as e:
        print(e)
        print(traceback.print_exc())
        abort(500)


@app.route('/image', methods=['GET'])
def get_image():
    if request.method == 'GET':
        file = request.args.get('file')
        file_location = f"images/{file}"
        return send_file(file_location, mimetype='image'), 200


@app.route('/file', methods=['GET'])
def get_file():
    if request.method == 'GET':
        file = request.args.get('file')
        file_location = f"files/{file}"
        return send_file(file_location, as_attachment=True), 200


@app.route('/yt2mp4', methods=['GET'])
def yt2mp4():
    if request.method == 'GET':
        done = False
        link = request.args.get('link')
        video_info = yt_dlp.YoutubeDL().extract_info(
            url=link, download=False
        )
        filename = f"{video_info['title']}.{video_info['ext']}"
        title = re.sub(r"[^a-zA-Z]+", "", video_info['title'])
        mp4_filename = f"{title}.mp4"
        ydl_opts = {
            'format': 'bv*[ext=mp4]+ba[ext=m4a]/b[ext=mp4] / bv*+ba/b',
            'outtmpl': mp4_filename
        }
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            output = ydl.download(link)
            os.rename(mp4_filename, f"files/{mp4_filename}")
            done = True
            output = {"url": f"https://api.razbot.xyz/file?file={mp4_filename}"}
            if done:
                return output, 200
        if not done:
            abort(500)


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=4321)
