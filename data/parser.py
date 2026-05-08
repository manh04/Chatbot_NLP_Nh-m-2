# data/gd1_parser_smart.py - Cập nhật bắt Chương
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import re
from dataclasses import dataclass, field
from typing import List, Set
from utils import extract_keywords


@dataclass
class LegalChunk:
    id: str
    content: str
    title: str = ""
    chapter: str = ""
    chapter_title: str = ""
    article: int = 0
    clause: int = 0
    point: str = ""
    keywords: List[str] = field(default_factory=list)
    chunk_type: str = "content"
    embedding: List[float] = field(default_factory=list)


class SmartLegalParser:
    """Parser thông minh - bắt đủ 9 Chương"""
    
    # Danh sách số La Mã đầy đủ
    ROMAN_NUMERALS = ['I', 'II', 'III', 'IV', 'V', 'VI', 'VII', 'VIII', 'IX', 'X']
    
    def __init__(self):
        self.current_chapter = "I"
        self.current_chapter_title = ""
        self.current_article = 0
        self.current_article_title = ""
        self.found_chapters: Set[str] = set()
    
    def parse_to_chunks(self, text: str) -> List[LegalChunk]:
        chunks = []
        chunk_id = 0
        
        # Tiền xử lý: chuẩn hóa dòng
        lines = self._normalize_lines(text)
        
        i = 0
        total_lines = len(lines)
        
        while i < total_lines:
            line = lines[i]
            
            # === 1. NHẬN DIỆN CHƯƠNG (mở rộng pattern) ===
            # Pattern cho nhiều định dạng: "Chương I", "CHƯƠNG I", "Chương 1", "I. CHƯƠNG"
            chapter_match = self._match_chapter(line)
            if chapter_match:
                chapter_num, chapter_title = chapter_match
                self.current_chapter = chapter_num
                self.current_chapter_title = chapter_title
                self.found_chapters.add(chapter_num)
                
                # Nếu không có title, lấy dòng tiếp theo
                if not self.current_chapter_title and i + 1 < total_lines:
                    next_line = lines[i + 1]
                    if not self._is_chapter_line(next_line):
                        self.current_chapter_title = next_line.strip()
                        i += 1
                
                chunks.append(LegalChunk(
                    id=f"ch_{chunk_id:04d}",
                    content=f"CHƯƠNG {self.current_chapter}. {self.current_chapter_title}",
                    title=self.current_chapter_title,
                    chapter=self.current_chapter,
                    chapter_title=self.current_chapter_title,
                    keywords=["chapter", f"chuong_{self.current_chapter}"],
                    chunk_type="chapter"
                ))
                chunk_id += 1
                i += 1
                continue
            
            # === 2. NHẬN DIỆN ĐIỀU ===
            article_match = self._match_article(line)
            if article_match and not self._is_inside_clause(line, i, lines):
                self.current_article = article_match[0]
                self.current_article_title = article_match[1]
                
                # Gom title nếu bị xuống dòng
                if len(self.current_article_title) < 20 and i + 1 < total_lines:
                    next_line = lines[i + 1]
                    if not re.match(r'^(?:CHƯƠNG|Chương|Điều|\d+\.|\d+\)|[a-zđ]\)|$)', next_line, re.IGNORECASE):
                        self.current_article_title += " " + next_line.strip()
                        i += 1
                
                chunks.append(LegalChunk(
                    id=f"ch_{chunk_id:04d}",
                    content=f"Điều {self.current_article}. {self.current_article_title}",
                    title=self.current_article_title,
                    chapter=self.current_chapter,
                    chapter_title=self.current_chapter_title,
                    article=self.current_article,
                    keywords=extract_keywords(self.current_article_title),
                    chunk_type="article"
                ))
                chunk_id += 1
                i += 1
                continue
            
            # === 3. NHẬN DIỆN KHOẢN ===
            clause_match = self._match_clause(line)
            if clause_match and self.current_article > 0:
                clause_num, clause_content = clause_match
                
                # Gom nội dung nhiều dòng
                j = i + 1
                while j < total_lines:
                    next_line = lines[j]
                    if self._is_boundary(next_line):
                        break
                    if next_line.strip():
                        clause_content += " " + next_line.strip()
                    j += 1
                
                clause_content = re.sub(r'\s+', ' ', clause_content).strip()
                
                chunks.append(LegalChunk(
                    id=f"ch_{chunk_id:04d}",
                    content=f"{clause_num}. {clause_content}",
                    title=self.current_article_title,
                    chapter=self.current_chapter,
                    chapter_title=self.current_chapter_title,
                    article=self.current_article,
                    clause=clause_num,
                    keywords=extract_keywords(clause_content),
                    chunk_type="clause"
                ))
                chunk_id += 1
                i = j
                continue
            
            # === 4. NHẬN DIỆN ĐIỂM ===
            point_match = self._match_point(line)
            if point_match and self.current_article > 0:
                point_letter, point_content = point_match
                
                # Gom nội dung nhiều dòng
                j = i + 1
                while j < total_lines:
                    next_line = lines[j]
                    if self._is_boundary(next_line):
                        break
                    if next_line.strip():
                        point_content += " " + next_line.strip()
                    j += 1
                
                point_content = re.sub(r'\s+', ' ', point_content).strip()
                
                chunks.append(LegalChunk(
                    id=f"ch_{chunk_id:04d}",
                    content=f"{point_letter}) {point_content}",
                    title=self.current_article_title,
                    chapter=self.current_chapter,
                    chapter_title=self.current_chapter_title,
                    article=self.current_article,
                    point=point_letter,
                    keywords=extract_keywords(point_content),
                    chunk_type="point"
                ))
                chunk_id += 1
                i = j
                continue
            
            i += 1
        
        # In báo cáo
        self._print_report(chunks)
        
        return chunks
    
    def _normalize_lines(self, text: str) -> List[str]:
        """Chuẩn hóa các dòng"""
        lines = text.split('\n')
        # Loại bỏ dòng rỗng và chuẩn hóa khoảng trắng
        normalized = []
        for line in lines:
            line = line.strip()
            if line:
                normalized.append(line)
        return normalized
    
    def _match_chapter(self, line: str) -> tuple:
        """Nhận diện Chương - hỗ trợ nhiều định dạng"""
        patterns = [
            # "Chương I" hoặc "CHƯƠNG I"
            r'^(?:CHƯƠNG|Chương)\s+([IVXLCDM]+|\d+)[\s:.]*\s*(.*)$',
            # "I. CHƯƠNG ..."
            r'^([IVXLCDM]+|\d+)[\s:.]*\s*(?:CHƯƠNG|Chương)\s+(.*)$',
        ]
        
        for pattern in patterns:
            match = re.match(pattern, line, re.IGNORECASE)
            if match:
                chapter_num = match.group(1).upper()
                title = match.group(2).strip() if len(match.groups()) > 1 else ""
                return (chapter_num, title)
        return None
    
    def _match_article(self, line: str) -> tuple:
        """Nhận diện Điều - chỉ khi Điều đứng đầu dòng"""
        # Chỉ match khi bắt đầu dòng, không phải ở giữa
        match = re.match(r'^Điều\s+(\d+)\s*\.?\s*(.*)$', line, re.IGNORECASE)
        if match:
            return (int(match.group(1)), match.group(2).strip())
        return None
    
    def _match_clause(self, line: str) -> tuple:
        """Nhận diện Khoản - số + dấu chấm hoặc ngoặc"""
        match = re.match(r'^(\d+)\s*[\.\)]\s*(.*)$', line)
        if match:
            return (int(match.group(1)), match.group(2).strip())
        return None
    
    def _match_point(self, line: str) -> tuple:
        """Nhận diện Điểm - chữ cái + dấu ngoặc"""
        match = re.match(r'^([a-zđ])\s*[\)\)]\s*(.*)$', line, re.IGNORECASE)
        if match:
            return (match.group(1), match.group(2).strip())
        return None
    
    def _is_boundary(self, line: str) -> bool:
        """Kiểm tra có phải ranh giới (Chương, Điều, Khoản, Điểm mới)"""
        return bool(
            re.match(r'^(?:CHƯƠNG|Chương)', line, re.IGNORECASE) or
            re.match(r'^Điều\s+\d+', line, re.IGNORECASE) or
            re.match(r'^\d+\s*[\.\)]', line) or
            re.match(r'^[a-zđ]\)', line, re.IGNORECASE)
        )
    
    def _is_chapter_line(self, line: str) -> bool:
        """Kiểm tra dòng có phải là dòng Chương không"""
        return bool(re.match(r'^(?:CHƯƠNG|Chương)', line, re.IGNORECASE))
    
    def _is_inside_clause(self, line: str, idx: int, lines: List[str]) -> bool:
        """Kiểm tra dòng có đang nằm trong nội dung Khoản không"""
        look_back = max(0, idx - 3)
        for i in range(idx - 1, look_back - 1, -1):
            prev_line = lines[i]
            if re.match(r'^\d+\s*[\.\)]', prev_line):
                return True
            if re.match(r'^[a-zđ]\)', prev_line):
                return True
        return False
    
    def _print_report(self, chunks: List[LegalChunk]):
        """In báo cáo chi tiết"""
        print("\n" + "=" * 60)
        print("BÁO CÁO PARSER")
        print("=" * 60)
        
        # Thống kê theo loại
        stats = {}
        for chunk in chunks:
            stats[chunk.chunk_type] = stats.get(chunk.chunk_type, 0) + 1
        
        print("\n Thống kê chunks:")
        for chunk_type, count in stats.items():
            print(f"   - {chunk_type}: {count}")
        
        # Thống kê Chương
        chapters = sorted(set(c.chapter for c in chunks if c.chapter), key=self._roman_to_int)
        print(f"\n Chương tìm thấy ({len(chapters)}/9):")
        print(f"   {', '.join(chapters)}")
        
        if len(chapters) < 9:
            missing = [r for r in self.ROMAN_NUMERALS[:9] if r not in chapters]
            print(f"    Thiếu Chương: {', '.join(missing)}")
        
        # Thống kê Điều
        articles = sorted(set(c.article for c in chunks if c.article > 0))
        print(f"\n Số Điều tìm thấy: {len(articles)}/124")
        
        # Hiển thị 10 Điều đầu
        print(f"\n 10 Điều đầu tiên:")
        for article in articles[:10]:
            print(f"   - Điều {article}")
        
        print("=" * 60)
    
    def _roman_to_int(self, roman: str) -> int:
        """Chuyển số La Mã sang số nguyên"""
        roman_map = {
            'I': 1, 'II': 2, 'III': 3, 'IV': 4, 'V': 5,
            'VI': 6, 'VII': 7, 'VIII': 8, 'IX': 9, 'X': 10
        }
        return roman_map.get(roman.upper(), 999)