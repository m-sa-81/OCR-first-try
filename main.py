#!/usr/bin/python3
import json
from pdf2image import convert_from_path
import pytesseract
import cv2
import numpy as np

PDF = "input.pdf"
DPI = 300

# Felddefinitionen (Pixel-Koordinaten bezogen auf das gerenderte Bild bei DPI=300!)
FIELDS = {
    "absender":        {"page": 0, "roi": [160, 200, 1160, 460], "psm": 6},
    "empfaenger":      {"page": 0, "roi": [160, 545, 1160, 795], "psm": 6},
    "Inhalt":          {"page": 0, "roi": [160, 1560, 1160, 2020], "psm": 6},
    "datum":           {"page": 0, "roi": [160, 1238, 1600, 1312], "psm": 7, "whitelist": "1234567890."},
    "plombe":          {"page": 0, "roi": [1190, 2360, 2223, 2463], "psm": 7},
    "Gewicht":         {"page": 0, "roi": [1182, 1912, 1683, 2000], "psm": 6},
}

def preprocess(pil_img):
    """Robuste Standard-Vorverarbeitung für Scans."""
    img = cv2.cvtColor(np.array(pil_img), cv2.COLOR_RGB2BGR)
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

    # leichtes Entrauschen + Kontrast
    gray = cv2.bilateralFilter(gray, 7, 50, 50)

    # adaptives Thresholding für bessere Zeichen-Trennung
    th = cv2.adaptiveThreshold(
        gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 31, 10
    )
    return th

def ocr_image(img_bin, lang="deu", psm=6, whitelist=None):
    cfg = f"--psm {psm}"
    if whitelist:
        cfg += f" -c tessedit_char_whitelist={whitelist}"
    return pytesseract.image_to_string(img_bin, lang=lang, config=cfg).strip()

def main():
    pages = convert_from_path(PDF, dpi=DPI)

    results = {}
    for name, spec in FIELDS.items():
        page_idx = spec["page"]
        l, t, r, b = spec["roi"]
        psm = spec.get("psm", 6)

        page = pages[page_idx]
        crop = page.crop((l, t, r, b))

        bin_img = preprocess(crop)

        # Beispiel: für IDs/Nummern oft hilfreich:
        whitelist = spec.get("whitelist")  # z.B. "ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789-/."
        text = ocr_image(bin_img, lang="deu", psm=psm, whitelist=whitelist)

        results[name] = text

    print(json.dumps(results, ensure_ascii=False, indent=2))

if __name__ == "__main__":
    main()
