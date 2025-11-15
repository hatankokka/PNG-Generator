import streamlit as st
from PIL import Image, ImageDraw, ImageFont
import os
import io
import textwrap

st.set_page_config(page_title="画像ジェネレーター", layout="centered")
st.title("🖼 固定背景テキストジェネレーター（PNG版）")

# ▼ 入力欄
text = st.text_area("テキストを入力（自動改行・自動縮小します）")

# ▼ フォント設定（Regular）
font_path = os.path.join("fonts", "BIZUDMincho-Regular.ttf")
font_size_max = 90
font_size_min = 12

# ▼ 背景PNG
bg = Image.open("background.png").convert("RGBA")
W, H = bg.size

# ▼ 最大テキストエリア
MAX_W = int(W * 0.85)
MAX_H = int(H * 0.60)

# ▼ 自動改行（画像幅に合わせる）
def wrap_text_to_width(text, draw, font, max_width):
    words = list(text)
    lines = []
    current = ""
    for ch in words:
        test = current + ch
        w, _ = draw.textbbox((0, 0), test, font=font)[2:]
        if w <= max_width:
            current = test
        else:
            lines.append(current)
            current = ch
    lines.append(current)
    return "\n".join(lines)

# ▼ 自動縮小＋折り返し
def fit_text(draw, text, font_path, max_w, max_h, max_size, min_size):
    size = max_size
    while size >= min_size:
        font = ImageFont.truetype(font_path, size)
        wrapped = wrap_text_to_width(text, draw, font, max_w)

        bbox = draw.multiline_textbbox((0, 0), wrapped, font=font)
        w = bbox[2] - bbox[0]
        h = bbox[3] - bbox[1]

        if w <= max_w and h <= max_h:
            return font, wrapped
        size -= 2

    return ImageFont.truetype(font_path, min_size), text

if text:
    img = bg.copy()
    draw = ImageDraw.Draw(img)

    # 自動縮小＆折り返し
    font, wrapped_text = fit_text(
        draw, text, font_path, MAX_W, MAX_H, font_size_max, font_size_min
    )

    # サイズ計算
    bbox = draw.multiline_textbbox((0, 0), wrapped_text, font=font)
    text_w = bbox[2] - bbox[0]
    text_h = bbox[3] - bbox[1]

    x = (W - text_w) // 2
    y = (H - text_h) // 2

    # ▼ 縁取り描画
    def draw_outline(x, y, text):
        for ox in range(-3, 4):
            for oy in range(-3, 4):
                draw.multiline_text((x + ox, y + oy), text, font=font, fill="#000000")
        draw.multiline_text((x, y), text, font=font, fill="#FFFFFF")

    draw_outline(x, y, wrapped_text)

    st.image(img)

    buf = io.BytesIO()
    img.save(buf, format="PNG")
    st.download_button("画像をダウンロード", buf.getvalue(), "output.png", "image/png")
