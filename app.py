import streamlit as st
from PIL import Image, ImageDraw, ImageFont
import os, io

st.set_page_config(page_title="画像ジェネレーター", layout="centered")
st.title("🖼 外交部風テキストジェネレーター（最適レイアウト版）")

# ▼ 入力欄
main_text = st.text_area("本文テキスト（フォント最大130、自動縮小・自動改行）")
footer_text = st.text_input("ヘッダー（署名・日付など、フォント50固定）", "")

# ▼ フォント設定
FONT_MAIN_MAX = 130
FONT_MAIN_MIN = 20
FONT_FOOTER = 50

font_path = os.path.join("fonts", "BIZUDMincho-Regular.ttf")

# ▼ 背景PNG読み込み
bg = Image.open("background.png").convert("RGBA")
W, H = bg.size

# ▼ 本文の描画領域（背景PNG専用）
TEXT_LEFT   = 200
TEXT_RIGHT  = W - 200
TEXT_TOP    = 700
TEXT_BOTTOM = 2300

TEXT_W = TEXT_RIGHT - TEXT_LEFT
TEXT_H = TEXT_BOTTOM - TEXT_TOP

# ▼ 自動改行
def wrap_text(text, draw, font, max_width):
    lines = []
    cur = ""
    for ch in text:
        test = cur + ch
        w, _ = draw.textbbox((0,0), test, font=font)[2:]
        if w <= max_width:
            cur = test
        else:
            lines.append(cur)
            cur = ch
    lines.append(cur)
    return "\n".join(lines)

# ▼ 自動縮小
def fit_text(draw, text, max_w, max_h, font_path, max_size, min_size):
    size = max_size
    while size >= min_size:
        font = ImageFont.truetype(font_path, size)
        wrapped = wrap_text(text, draw, font, max_w)

        bbox = draw.multiline_textbbox((0,0), wrapped, font=font)
        w = bbox[2] - bbox[0]
        h = bbox[3] - bbox[1]

        if w <= max_w and h <= max_h:
            return font, wrapped

        size -= 3

    return ImageFont.truetype(font_path, min_size), text

# ▼ 描画処理
if main_text:
    img = bg.copy()
    draw = ImageDraw.Draw(img)

    # 本文フォントの調整
    font_main, wrapped_text = fit_text(
        draw, main_text, TEXT_W, TEXT_H, font_path,
        FONT_MAIN_MAX, FONT_MAIN_MIN
    )

    # 本文の描画位置
    bbox = draw.multiline_textbbox((0,0), wrapped_text, font=font_main)
    tw = bbox[2] - bbox[0]
    th = bbox[3] - bbox[1]

    x = TEXT_LEFT + (TEXT_W - tw) // 2
    y = TEXT_TOP  + (TEXT_H - th) // 2

    # 縁取り付き描画
    def draw_outline(draw, x, y, t, font):
        for ox in range(-4, 5):
            for oy in range(-4, 5):
                draw.multiline_text((x+ox, y+oy), t, font=font, fill="#000000")
        draw.multiline_text((x, y), t, font=font, fill="#FFFFFF")

    draw_outline(draw, x, y, wrapped_text, font_main)

    # ▼ フッター（署名・日付）
    if footer_text:
        font_footer = ImageFont.truetype(font_path, FONT_FOOTER)
        fw, fh = draw.textbbox((0,0), footer_text, font=font_footer)[2:]
        fx = (W - fw) // 2
        fy = 2850   # 背景画像専用の位置

        draw_outline(draw, fx, fy, footer_text, font_footer)

    st.image(img)

    # ▼ ダウンロード
    buf = io.BytesIO()
    img.save(buf, "PNG")
    st.download_button("画像をダウンロード", buf.getvalue(), "output.png", "image/png")
