# data/gd1_ocr_optimized.py
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import fitz
import numpy as np
from PIL import Image, ImageEnhance
import io
from tqdm import tqdm
import re
from pathlib import Path
from config import Config

try:
    import easyocr
    EASYOCR_AVAILABLE = True
except ImportError:
    EASYOCR_AVAILABLE = False
    print("EasyOCR chưa được cài. Cài bằng: pip install easyocr")


class PDFOCRProcessor:
    def __init__(self):
        self.cache_dir = Path(Config.CACHE_DIR)
        self.cache_dir.mkdir(exist_ok=True)
        
        if not EASYOCR_AVAILABLE:
            raise ImportError("Cần cài easyocr: pip install easyocr")
        
        self.reader = easyocr.Reader(['vi', 'en'], gpu=False, verbose=False)
    
    def extract_text(self, pdf_path: str, use_cache: bool = True) -> str:
        self.doc = fitz.open(pdf_path)
        all_text = []
        
        for page_num in tqdm(range(len(self.doc)), desc="OCR đang xử lý"):
            cache_file = self.cache_dir / f"page_{page_num:03d}.txt"
            
            if use_cache and cache_file.exists():
                with open(cache_file, "r", encoding="utf-8") as f:
                    all_text.append(f.read())
                continue
            
            page = self.doc.load_page(page_num)
            zoom = 300 / 72
            mat = fitz.Matrix(zoom, zoom)
            pix = page.get_pixmap(matrix=mat)
            img_data = pix.tobytes("png")
            img = Image.open(io.BytesIO(img_data))
            
            if img.mode != 'L':
                img = img.convert('L')
            
            enhancer = ImageEnhance.Contrast(img)
            img = enhancer.enhance(1.3)
            
            result = self.reader.readtext(np.array(img), detail=0, paragraph=False)
            page_text = '\n'.join(result)
            
            if use_cache:
                with open(cache_file, "w", encoding="utf-8") as f:
                    f.write(page_text)
            
            all_text.append(page_text)
        
        full_text = '\n'.join(all_text)
        full_text = self._post_process(full_text)
        
        return full_text
    
    def _post_process(self, text: str) -> str:
        corrections = {
            r'Điêu': 'Điều', r'Diêu': 'Điều',
            r'Khoan': 'Khoản', r'khoan': 'khoản',
            r'Chuong': 'Chương', r'chuong': 'chương',
            r'cac': 'các', r'va': 'và', r'cua': 'của',
            r'Viet Nam': 'Việt Nam',
        }
        for wrong, correct in corrections.items():
            text = re.sub(wrong, correct, text)
        
        lines = [l.strip() for l in text.split('\n') if l.strip()]
        return '\n'.join(lines)