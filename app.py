import streamlit as st
from PIL import Image, ImageDraw, ImageFont
import os, io

st.set_page_config(page_title="外交部ジェネレーター", layout="centered")
st.title("外交部風 画像ジェネレーター（巨大文字版）")

# ▼ 入力欄
main_text = st.text_area("本文（最大フォント450、自動調整）", "")
footer_text = st.text_input("下のヘッダー（署名・日付、フォント50固定）", "")

# ▼ フォント設定
FONT_MAIN_MAX = 450   # ←←← 超巨大文字に変更！！
FONT_MAIN_MIN = 50    # ← 最低でもデカくする
FONT_FOOTER = 50
font_path = os.path.join("fonts", "BIZUDMincho-Regular.ttf")

# ▼ 背景PNG読み込み
bg = Image.open("background.png").convert("RGBA")
W, H = bg.size

# ▼ 本文エリア（中央寄りの大きな領域）
CENTER_TOP    = int(H * 0.23)
CENTER_BOTTOM = int(H * 0.73)
CENTER_LEFT   = int(W * 0.12)
CENTER_RIGHT  = int(W * 0.88)

CENTER_W = CENTER_RIGHT - CENTER_LEFT
CENTER_H = CENTER_BOTTOM - CENTER_TOP

# ▼ 自動改行
def wrap_text(text, draw, font, max_width):
    lines = []
    cur = ""
    for ch in text:
        t = cur + ch
        w,_ = draw.textbbox((0,0), t, font=font)[2:]
        if w <= max_width:
            cur = t
        else:
            lines.append(cur)
            cur = ch
    lines.append(cur)
    return "\n".join(lines)

# ▼ フォント自動縮小（最大450 → はみ出したら下げる）
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
        size -= 10  # 大きいフォント向けに落差を増やす

    return ImageFont.truetype(font_path, FONT_MAIN_MIN), text

# ▼ 縁取り描画
def draw_outline(draw, x, y, text, font, fill="#FFFFFF"):
    for ox in range(-6, 7):
        for oy in range(-6, 7):
            draw.multiline_text((x+ox, y+oy), text, font=font, fill="#000000")
    draw.multiline_text((x, y), text, font=font, fill=fill)

# ▼ 描画
if main_text:
    img = bg.copy()
    draw = ImageDraw.Draw(img)

    # 本文フォント決定
    font_main, wrapped = autoshrink(draw, main_text, CENTER_W, CENTER_H)

    bbox = draw.multiline_textbbox((0,0), wrapped, font=font_main)
    tw = bbox[2] - bbox[0]
    th = bbox[3] - bbox[1]

    x_main = CENTER_LEFT + (CENTER_W - tw)//2
    y_main = CENTER_TOP + (CENTER_H - th)//2

    draw_outline(draw, x_main, y_main, wrapped, font_main)

    # ▼ フッター
    if footer_text:
        font_footer = ImageFont.truetype(font_path, FONT_FOOTER)
        fw = draw.textbbox((0,0), footer_text, font=font_footer)[2]
        x_footer = (W - fw)//2
        y_footer = int(H * 0.87)
        draw_outline(draw, x_footer, y_footer, footer_text, font_footer)

    st.image(img)

    buf = io.BytesIO()
    img.save(buf, format="PNG")
    st.download_button("画像をダウンロード", buf.getvalue(), "output.png", "image/png")
