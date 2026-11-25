# -*- coding: utf-8 -*-
"""
PDF 카탈로그에서 '주요 사양' 좌측 보라색 사이드바 글자가 빠져 있던 문제 수정용 빌드 스크립트.

원인: 웹(index.html) 버전은 각 페이지의 사이드바 텍스트를 JS(fillSB())가 그 자리에서
그려 넣는 방식인데, PDF는 배경 사진(pages/pNNN.jpg)만 그대로 이미지로 넣어서 만들었기
때문에 사이드바 자리는 비어 있는 보라색 블록으로만 남아 있었다.

이 스크립트는 index.html에 내장된 META/KEYS/DEFV/NAMES 데이터를 그대로 읽어
(웹 화면과 100% 동일한 내용) 각 페이지 이미지 위에 사이드바 텍스트를 실제로
그려 넣은 "PDF 전용" 이미지 세트(pdf_pages_baked/)를 새로 만들고, 그걸로 PDF를
재생성한다. 웹에서 쓰는 원본 pages/*.jpg는 건드리지 않는다 — 그걸 건드리면
웹 뷰어가 사이드바를 다시 한번 겹쳐 그려서 글자가 두 번 찍히게 된다.
"""
import re, json, os
from PIL import Image, ImageDraw, ImageFont

ROOT = os.path.dirname(os.path.abspath(__file__))
HTML_PATH = os.path.join(ROOT, "index.html")
PAGES_DIR = os.path.join(ROOT, "pages")
OUT_DIR = os.path.join(ROOT, "pdf_pages_baked")
PDF_OUT = os.path.join(ROOT, "대동울타리_제품카탈로그.pdf")
N_PAGES = 103

FONT_VF = r"C:\Windows\Fonts\NotoSansKR-VF.ttf"

PURPLE = (61, 31, 107)
GOLD = (201, 162, 74)
WHITE = (255, 255, 255)
LABEL_LAVENDER = (203, 187, 227)
APP_LAVENDER = (228, 218, 242)
ROW_BORDER = (90, 61, 134)
NOTE_LAVENDER = (203, 187, 227)

PAD_Y, PAD_X, GAP = 22, 18, 4


def load_data():
    with open(HTML_PATH, encoding="utf-8") as f:
        html = f.read()
    meta = json.loads(re.search(r"const META=(\{.*?\});", html, re.S).group(1))
    keys = json.loads(re.search(r"const KEYS=(\[.*?\]);", html).group(1))
    defv = json.loads(re.search(r"const DEFV=(\{.*?\});", html).group(1))
    names = json.loads(re.search(r"const NAMES=(\[.*?\]);", html).group(1))
    return meta, keys, defv, names


_font_cache = {}


def font(size, weight="Regular"):
    key = (size, weight)
    if key not in _font_cache:
        f = ImageFont.truetype(FONT_VF, size)
        try:
            f.set_variation_by_name(weight)
        except Exception:
            pass
        _font_cache[key] = f
    return _font_cache[key]


def text_h(size):
    # Noto Sans KR의 실제 줄 높이는 em박스보다 커서(라틴 폰트보다 큰 상/하 여백),
    # 브라우저 기본 line-height("normal")에 가깝게 1.4배로 근사한다.
    return round(size * 1.4)


def wrap_text(draw, text, f, max_width):
    words = list(text)
    lines, cur = [], ""
    for ch in text:
        test = cur + ch
        if draw.textlength(test, font=f) <= max_width or not cur:
            cur = test
        else:
            lines.append(cur)
            cur = ch
    if cur:
        lines.append(cur)
    return lines


def fill_sidebar(img, box, ci, spec, keys, defv):
    x, y, w, h = box
    draw = ImageDraw.Draw(img)
    draw.rectangle([x, y, x + w, y + h], fill=PURPLE)

    x0, x1 = x + PAD_X, x + w - PAD_X
    cw = x1 - x0
    cy = y + PAD_Y

    def heading(text, color, size=13, weight="Bold", border=True, extra_top=0):
        nonlocal cy
        cy += extra_top
        f = font(size, weight)
        draw.text((x0, cy), text, font=f, fill=color)
        cy += text_h(size)
        if border:
            cy += 8
            draw.line([(x0, cy), (x1, cy)], fill=GOLD, width=2)
            cy += 2
        cy += GAP

    def row(label, value):
        # CSS 실제 동작과 동일하게: 값(value)이 라벨과 겹칠 만큼 길면 값 쪽만
        # 우측정렬 유지한 채 여러 줄로 줄바꿈한다(2026-11-26 실측 발견·수정 —
        # "알루미늄·스틸 프레임+합성목재"처럼 긴 값이 라벨과 겹쳐 보이던 문제).
        nonlocal cy
        f = font(12, "Regular")
        fv = font(12, "Medium")
        label_w = draw.textlength(label, font=f)
        avail_for_value = cw - label_w - 8
        lh = text_h(12)
        if draw.textlength(value, font=fv) <= avail_for_value:
            lines = [value]
        else:
            lines = wrap_text(draw, value, fv, avail_for_value)
        cy += 8
        draw.text((x0, cy), label, font=f, fill=LABEL_LAVENDER)
        for i, ln in enumerate(lines):
            vw = draw.textlength(ln, font=fv)
            draw.text((x1 - vw, cy + i * lh), ln, font=fv, fill=WHITE)
        cy += lh * len(lines)
        cy += 8
        draw.line([(x0, cy), (x1, cy)], fill=ROW_BORDER, width=1)
        cy += GAP

    def app_line(text):
        nonlocal cy
        f = font(12, "Regular")
        full = "· " + text
        lines = wrap_text(draw, full, f, cw)
        lh = round(12 * 1.9)
        for i, ln in enumerate(lines):
            draw.text((x0, cy), ln, font=f, fill=APP_LAVENDER)
            cy += lh
        cy += GAP - (0 if lines else 0)

    heading("주요 사양", WHITE)
    vals = {r[0]: r[1] for r in spec.get("rows", [])}
    for k in keys:
        if k == "기초":
            heading("설치방식", GOLD, size=12, weight="Medium", border=False, extra_top=12 - GAP)
        row(k, vals.get(k) or defv.get(k) or "—")

    heading("납품 분야", GOLD, extra_top=20 - GAP)
    for a in spec.get("apps", []):
        if a:
            app_line(a)

    # note: margin-top:auto → 박스 맨 아래에 고정 배치
    note_lines = ["규격 외 높이·색상은", "현장 조건에 맞춰 제작 가능"]
    nf = font(11, "Regular")
    nlh = round(11 * 1.6)
    note_h = nlh * len(note_lines)
    ny = y + h - PAD_Y - note_h
    for i, ln in enumerate(note_lines):
        draw.text((x0, ny + i * nlh), ln, font=nf, fill=NOTE_LAVENDER)


def main():
    meta, keys, defv, names = load_data()
    os.makedirs(OUT_DIR, exist_ok=True)

    baked = 0
    for n in range(1, N_PAGES + 1):
        src = os.path.join(PAGES_DIR, f"p{n:03d}.jpg")
        img = Image.open(src).convert("RGB")
        m = meta.get(str(n))
        if m:
            ci = m["ci"]
            spec = meta["def"][str(ci)]
            fill_sidebar(img, m["r"], ci, spec, keys, defv)
            baked += 1
        out = os.path.join(OUT_DIR, f"p{n:03d}.jpg")
        img.save(out, quality=92)

    print(f"baked sidebar text on {baked} pages, wrote {N_PAGES} images to {OUT_DIR}")

    # PDF 조립 (기존 PDF와 동일하게 페이지당 풀블리드 이미지 1장, A4 크기)
    import fitz
    doc = fitz.open()
    for n in range(1, N_PAGES + 1):
        img_path = os.path.join(OUT_DIR, f"p{n:03d}.jpg")
        im = Image.open(img_path)
        w_px, h_px = im.size
        w_pt, h_pt = w_px * 72 / 96, h_px * 72 / 96
        page = doc.new_page(width=w_pt, height=h_pt)
        page.insert_image(fitz.Rect(0, 0, w_pt, h_pt), filename=img_path)
    tmp_out = PDF_OUT + ".tmp"
    doc.save(tmp_out)
    doc.close()
    os.replace(tmp_out, PDF_OUT)
    print(f"PDF written: {PDF_OUT}")


if __name__ == "__main__":
    main()
