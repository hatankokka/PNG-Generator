import streamlit as st
from PIL import Image, ImageDraw, ImageFont
import os, io

st.set_page_config(page_title="外交部ジェネレーター", layout="centered")
st.title("中国外交部風 画像ジェネレーター（完全移植版）")

# ▼ 入力欄
main_text = st.text_area("本文（最大フォント130、自動縮小・自動改行）")
source_text = st.text_input("出典（下部左）", "")
date_text   = st.text_input("日付（下部右）", "")

# ▼ フォント
FONT_MAX = 130
FONT_MIN = 20
FONT_FOOTER = 50

font_path = os.path.join("fonts", "BIZUDMincho-Regular.ttf")

# ▼ 背景画像
bg = Image.open("background.png").convert("RGBA")
W, H = bg.size

# ▼ 中央テキストエリア（HTML の .quote に相当）
AREA_LEFT   = 180
AREA_RIGHT  = W - 180
AREA_TOP    = 750     # 紋章の真下
AREA_BOTTOM = 2100    # 下線のずっと上

AREA_W = AREA_RIGHT - AREA_LEFT
AREA_H = AREA_BOTTOM - AREA_TOP

# ▼ 改行なしで収めるための wrap（1文字ずつ判定）
def wrap_to_width(text, draw, font, max_width):
    lines = []
    current = ""
    for ch in text:
        test = current + ch
        w,_ = draw.textbbox((0,0), test, font=font)[2:]
        if w <= max_width:
            current = test
        else:
            lines.append(current)
            current = ch
    lines.append(current)
    return "\n".join(lines)

# ▼ HTML の fitQuoteFont と同じロジック（フォント縮小）
def autoshrink(draw, text, max_w, max_h, font_path, max_size, min_size):
    size = max_size
    while size >= min_size:
        font = ImageFont.truetype(font_path, size)
        wrapped = wrap_to_width(text, draw, font, max_w)

        bbox = draw.multiline_textbbox((0,0), wrapped, font=font)
        w = bbox[2] - bbox[0]
        h = bbox[3] - bbox[1]

        if w <= max_w and h <= max_h:
            return font, wrapped

        size -= 2  # ステップ（HTMLでは0.4pxだがピクセルでは2px単位が妥当）

    return ImageFont.truetype(font_path, min_size), text

# ▼ 描画処理
if main_text:
    img = bg.copy()
    draw = ImageDraw.Draw(img)

    # フォント縮小・wrap
    font_main, wrapped = autoshrink(
        draw, main_text, AREA_W, AREA_H,
        font_path, FONT_MAX, FONT_MIN
    )

    # 中央配置（HTML の flex-center と同じ）
    bbox = draw.multiline_textbbox((0,0), wrapped, font=font_main)
    tw = bbox[2] - bbox[0]
    th = bbox[3] - bbox[1]

    x = AREA_LEFT + (AREA_W - tw) // 2
    y = AREA_TOP  + (AREA_H - th) // 2

    # 縁取り
    def outline(draw, x, y, t, font):
        for ox in range(-4, 5):
            for oy in range(-4, 5):
                draw.multiline_text((x+ox, y+oy), t, font=font, fill="#000")
        draw.multiline_text((x, y), t, font=font, fill="#FFF")

    # 本文描画
    outline(draw, x, y, wrapped, font_main)

    # ▼ 下部フッター（HTML の footer と同じ構造）
    if source_text or date_text:
        font_footer = ImageFont.truetype(font_path, FONT_FOOTER)

        footer_y = 2750  # 背景画像の下線の直上

        # 左（出典）
        if source_text:
            sw = draw.textbbox((0,0), source_text, font=font_footer)[2]
            sx = AREA_LEFT
            outline(draw, sx, footer_y, source_text, font_footer)

        # 右（日付）
        if date_text:
            dw = draw.textbbox((0,0), date_text, font=font_footer)[2]
            dx = AREA_RIGHT - dw
            outline(draw, dx, footer_y, date_text, font_footer)

    st.image(img)

    # ▼ ダウンロード
    buf = io.BytesIO()
    img.save(buf, "PNG")
    st.download_button("画像をダウンロード", buf.getvalue(), "output.png", "image/png")
