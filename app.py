import streamlit as st
from PIL import Image, ImageDraw, ImageFont
import os, io

st.set_page_config(page_title="外交部ジェネレーター", layout="centered")
st.title("中国外交部ジェネレーター（完全再現版）")

# 入力欄
main_text = st.text_area("本文", "")
source_text = st.text_input("出典（下左）", "")
date_text   = st.text_input("日付（下右）", "")

# フォント
FONT_MAIN_MAX = 130
FONT_MAIN_MIN = 20
FONT_FOOTER = 50
font_path = os.path.join("fonts", "BIZUDMincho-Regular.ttf")

# 背景読み込み
bg = Image.open("background.png").convert("RGBA")
W, H = bg.size
CENTER_TOP = 550
CENTER_BOTTOM = 2550
CENTER_LEFT = 180
CENTER_RIGHT = W - 180

CENTER_W = CENTER_RIGHT - CENTER_LEFT
CENTER_H = CENTER_BOTTOM - CENTER_TOP

# 自動改行
def wrap_text(text, draw, font, max_width):
    out = []
    cur = ""
    for ch in text:
        t = cur + ch
        w,_ = draw.textbbox((0,0), t, font=font)[2:]
        if w <= max_width:
            cur = t
        else:
            out.append(cur)
            cur = ch
    out.append(cur)
    return "\n".join(out)

# 自動縮小（HTML の fitQuoteFont 相当）
def autoshrink(draw, text, max_w, max_h):
    size = FONT_MAIN_MAX
    while size >= FONT_MAIN_MIN:
        font = ImageFont.truetype(font_path, size)
        wrapped = wrap_text(text, draw, font, max_w)

        bbox = draw.multiline_textbbox((0,0), wrapped, font=font)
        w = bbox[2] - bbox[0]
        h = bbox[3] - bbox[1]

        if w <= max_w and h <= max_h:
            return font, wrapped

        size -= 2

    return ImageFont.truetype(font_path, FONT_MAIN_MIN), text

if main_text:
    img = bg.copy()
    draw = ImageDraw.Draw(img)

    # 本文 shrink
    font_main, wrapped = autoshrink(draw, main_text, CENTER_W, CENTER_H)

    # 中央揃え（HTML の flex-center）
    bbox = draw.multiline_textbbox((0,0), wrapped, font=font_main)
    tw = bbox[2] - bbox[0]
    th = bbox[3] - bbox[1]

    x = CENTER_LEFT + (CENTER_W - tw)//2
    y = CENTER_TOP  + (CENTER_H - th)//2

    # 縁取り
    def outline(x, y, t, font):
        for ox in range(-4,5):
            for oy in range(-4,5):
                draw.multiline_text((x+ox, y+oy), t, font=font, fill="#000")
        draw.multiline_text((x, y), t, font=font, fill="#FFF")

    outline(x, y, wrapped, font_main)

    # フッター
    if source_text or date_text:
        font_footer = ImageFont.truetype(font_path, FONT_FOOTER)

        FOOTER_Y = 2800  # 横線の直上
        # 左
        if source_text:
            sw = draw.textbbox((0,0), source_text, font=font_footer)[2]
            outline(200, FOOTER_Y, source_text, font_footer)

        # 右
        if date_text:
            dw = draw.textbbox((0,0), date_text, font=font_footer)[2]
            outline(W - 200 - dw, FOOTER_Y, date_text, font_footer)

    st.image(img)

    buf = io.BytesIO()
    img.save(buf, "PNG")
    st.download_button("画像をダウンロード", buf.getvalue(), "output.png", "image/png")
