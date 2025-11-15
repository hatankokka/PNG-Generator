import streamlit as st
from PIL import Image, ImageDraw, ImageFont
import os, io

st.set_page_config(page_title="外交部ジェネレーター", layout="centered")
st.title("外交部風 画像ジェネレーター（超大型フォント版）")

# ▼ 入力欄
main_text = st.text_area("本文（最大600px、自動縮小）", "")
footer_text = st.text_input("下のヘッダー（署名・日付、フォント200固定）", "")

# ▼ フォント設定
FONT_MAIN_MAX = 600     # ←←← ここ！！
FONT_MAIN_MIN = 150     # ← 最低でもデカい
FONT_FOOTER   = 200     # ←←← ここ！！

font_path = os.path.join("fonts", "BIZUDMincho-Regular.ttf")

# ▼ 背景PNG
bg = Image.open("background.png").convert("RGBA")
W, H = bg.size   # 1601×2048のPNGに自動適応

# ▼ 本文のエリア（背景PNGに合わせて調整）
#   → 今回は「画面中央より少し下」がベスト
CENTER_TOP    = int(H * 0.32)
CENTER_BOTTOM = int(H * 0.72)
CENTER_LEFT   = int(W * 0.10)
CENTER_RIGHT  = int(W * 0.90)

CENTER_W = CENTER_RIGHT - CENTER_LEFT
CENTER_H = CENTER_BOTTOM - CENTER_TOP

# ▼ 自動改行
def wrap_text(text, draw, font, max_width):
    lines, cur = [], ""
    for ch in text:
        t = cur + ch
        w,_ = draw.textbbox((0,0), t, font=font)[2:]
        if w <= max_width:
            cur = t
        else:
            lines.append(cur)
            cur = ch
    if cur:
        lines.append(cur)
    return "\n".join(lines)

# ▼ フォント自動縮小
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

        size -= 15   # ←巨大フォントのときは大胆に減らす

    return ImageFont.truetype(font_path, FONT_MAIN_MIN), text

# ▼ 縁取り
def draw_outline(draw, x, y, text, font, fill="#FFFFFF", outline="#000", width=8):
    for ox in range(-width, width+1):
        for oy in range(-width, width+1):
            draw.multiline_text((x+ox, y+oy), text, font=font, fill=outline)
    draw.multiline_text((x, y), text, font=font, fill=fill)

# ▼ 描画
if main_text:
    img = bg.copy()
    draw = ImageDraw.Draw(img)

    # 本文 shrink
    font_main, wrapped = autoshrink(draw, main_text, CENTER_W, CENTER_H)

    bbox = draw.multiline_textbbox((0,0), wrapped, font=font_main)
    tw = bbox[2] - bbox[0]
    th = bbox[3] - bbox[1]

    # ←本文は中央寄り下に配置（調整済み）
    x_main = CENTER_LEFT + (CENTER_W - tw)//2
    y_main = CENTER_TOP + (CENTER_H - th)//2

    draw_outline(draw, x_main, y_main, wrapped, font_main)

    # ▼ ヘッダー（200px固定）
    if footer_text:
        font_footer = ImageFont.truetype(font_path, FONT_FOOTER)
        fw = draw.textbbox((0,0), footer_text, font=font_footer)[2]

        x_footer = (W - fw)//2
        y_footer = int(H * 0.88)   # ← 横線の上にドンピシャ

        draw_outline(draw, x_footer, y_footer, footer_text, font_footer, width=6)

    st.image(img)

    buf = io.BytesIO()
    img.save(buf, "PNG")
    st.download_button("画像をダウンロード", buf.getvalue(), "output.png", "image/png")
