import streamlit as st
from PIL import Image, ImageDraw, ImageFont
import os
import io

st.set_page_config(page_title="外交部ジェネレーター", layout="centered")
st.title("外交部風 画像ジェネレーター（安定版）")

# ▼ ファイル存在チェック（最重要）
if not os.path.exists("background.png"):
    st.error("❌ background.png が見つかりません。\n\n"
             "レポジトリ直下に background.png を置いてください。")
    st.stop()

if not os.path.exists("fonts/BIZUDMincho-Regular.ttf"):
    st.error("❌ BIZUDMincho-Regular.ttf が見つかりません。\n\n"
             "fonts フォルダに置いてください。")
    st.stop()

# ▼ 背景画像読み込み
bg = Image.open("background.png").convert("RGBA")
W, H = bg.size

# ▼ 入力欄
main_text = st.text_area("本文テキスト（最大600px）", "")
footer_text = st.text_input("ヘッダー（署名・日付、200px固定）", "")

# ▼ フォント設定
FONT_MAIN_MAX = 600
FONT_MAIN_MIN = 150
FONT_FOOTER = 200
FONT_PATH = "fonts/BIZUDMincho-Regular.ttf"

# ▼ 中央テキストボックス
CENTER_TOP = int(H * 0.28)
CENTER_BOTTOM = int(H * 0.70)
CENTER_LEFT = int(W * 0.10)
CENTER_RIGHT = int(W * 0.90)

CENTER_W = CENTER_RIGHT - CENTER_LEFT
CENTER_H = CENTER_BOTTOM - CENTER_TOP

# ---------- テキスト折り返し ----------
def wrap_text(text, draw, font, max_width):
    result = []
    line = ""
    for ch in text:
        test = line + ch
        w, _ = draw.textbbox((0,0), test, font=font)[2:]
        if w <= max_width:
            line = test
        else:
            result.append(line)
            line = ch
    if line:
        result.append(line)
    return "\n".join(result)

# ---------- フォント自動縮小 ----------
def auto_font(draw, text, max_w, max_h):
    size = FONT_MAIN_MAX
    while size >= FONT_MAIN_MIN:
        font = ImageFont.truetype(FONT_PATH, size)
        wrapped = wrap_text(text, draw, font, max_w)
        bbox = draw.multiline_textbbox((0,0), wrapped, font=font)
        w = bbox[2] - bbox[0]
        h = bbox[3] - bbox[1]
        if w <= max_w and h <= max_h:
            return font, wrapped
        size -= 12
    return ImageFont.truetype(FONT_PATH, FONT_MAIN_MIN), text

# ---------- 縁取り ----------
def draw_outline(draw, x, y, text, font, fill="#FFF", outline="#000", w=8):
    for ox in range(-w, w+1):
        for oy in range(-w, w+1):
            draw.multiline_text((x+ox, y+oy), text, font=font, fill=outline)
    draw.multiline_text((x, y), text, font=font, fill=fill)

# ---------- 描画 ----------
if main_text:
    img = bg.copy()
    draw = ImageDraw.Draw(img)

    # 本文
    font_main, wrapped = auto_font(draw, main_text, CENTER_W, CENTER_H)
    bbox = draw.multiline_textbbox((0,0), wrapped, font=font_main)
    tw = bbox[2] - bbox[0]
    th = bbox[3] - bbox[1]

    x = CENTER_LEFT + (CENTER_W - tw) // 2
    y = CENTER_TOP + (CENTER_H - th) // 2

    draw_outline(draw, x, y, wrapped, font_main)

    # ヘッダー 200px、画面の 0.90 の位置
    if footer_text:
        font_footer = ImageFont.truetype(FONT_PATH, FONT_FOOTER)
        fw = draw.textbbox((0,0), footer_text, font=font_footer)[2]
        x_footer = (W - fw) // 2
        y_footer = int(H * 0.90)
        draw_outline(draw, x_footer, y_footer, footer_text, font_footer, w=5)

    st.image(img)

    buf = io.BytesIO()
    img.save(buf, format="PNG")
    st.download_button("画像をダウンロード", buf.getvalue(),
                       "output.png", "image/png")
