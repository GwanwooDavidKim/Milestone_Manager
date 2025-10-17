"""커스텀 위젯 모듈 - 다이얼로그와 재사용 가능한 UI 컴포넌트"""

import customtkinter as ctk
from tkinter import filedialog, colorchooser
from typing import Optional, Dict, Callable


class MilestoneDialog(ctk.CTkToplevel):
    """마일스톤 생성/수정 다이얼로그"""
    
    def __init__(self, parent, title: str = "마일스톤 생성", 
                 milestone_data: Optional[Dict] = None):
        """
        Args:
            parent: 부모 윈도우
            title (str): 다이얼로그 제목
            milestone_data (Optional[Dict]): 수정 시 기존 데이터
        """
        super().__init__(parent)
        self.title(title)
        self.geometry("400x250")
        self.resizable(False, False)
        
        self.result = None
        
        ctk.CTkLabel(self, text="제목:").pack(pady=(20, 5))
        self.title_entry = ctk.CTkEntry(self, width=350)
        self.title_entry.pack(pady=5)
        
        ctk.CTkLabel(self, text="부제목:").pack(pady=(10, 5))
        self.subtitle_entry = ctk.CTkEntry(self, width=350)
        self.subtitle_entry.pack(pady=5)
        
        if milestone_data:
            self.title_entry.insert(0, milestone_data.get("title", ""))
            self.subtitle_entry.insert(0, milestone_data.get("subtitle", ""))
        
        btn_frame = ctk.CTkFrame(self, fg_color="transparent")
        btn_frame.pack(pady=20)
        
        ctk.CTkButton(btn_frame, text="확인", command=self._on_confirm,
                     width=100).pack(side="left", padx=5)
        ctk.CTkButton(btn_frame, text="취소", command=self.destroy,
                     width=100).pack(side="left", padx=5)
        
        self.grab_set()
        self.wait_window()
    
    def _on_confirm(self):
        """확인 버튼 클릭 시 데이터 반환"""
        title = self.title_entry.get().strip()
        subtitle = self.subtitle_entry.get().strip()
        
        if not title:
            return
        
        self.result = {
            "title": title,
            "subtitle": subtitle
        }
        self.destroy()


class NodeDialog(ctk.CTkToplevel):
    """노드 생성/수정 다이얼로그"""
    
    SHAPES = ["●(동그라미)", "▲(세모)", "■(네모)", "★(별)", "◆(마름모)"]
    
    def __init__(self, parent, title: str = "노드 추가", 
                 node_data: Optional[Dict] = None):
        """
        Args:
            parent: 부모 윈도우
            title (str): 다이얼로그 제목
            node_data (Optional[Dict]): 수정 시 기존 노드 데이터
        """
        super().__init__(parent)
        self.title(title)
        self.geometry("450x600")
        self.resizable(False, False)
        
        self.result = None
        self.selected_color = node_data.get("color", "#3B8ED0") if node_data else "#3B8ED0"
        self.attached_file = node_data.get("attachment", "") if node_data else ""
        
        scroll_frame = ctk.CTkScrollableFrame(self, width=420, height=500)
        scroll_frame.pack(pady=10, padx=10, fill="both", expand=True)
        
        ctk.CTkLabel(scroll_frame, text="모양:").pack(pady=(10, 5), anchor="w", padx=10)
        self.shape_var = ctk.StringVar(value=node_data.get("shape", self.SHAPES[0]) if node_data else self.SHAPES[0])
        self.shape_menu = ctk.CTkOptionMenu(scroll_frame, values=self.SHAPES, 
                                            variable=self.shape_var, width=400)
        self.shape_menu.pack(pady=5, padx=10)
        
        ctk.CTkLabel(scroll_frame, text="색상:").pack(pady=(10, 5), anchor="w", padx=10)
        color_frame = ctk.CTkFrame(scroll_frame, fg_color="transparent")
        color_frame.pack(pady=5, padx=10, fill="x")
        
        self.color_display = ctk.CTkLabel(color_frame, text="   ", 
                                          fg_color=self.selected_color, 
                                          width=50, height=30, corner_radius=5)
        self.color_display.pack(side="left", padx=5)
        
        ctk.CTkButton(color_frame, text="색상 선택", command=self._choose_color,
                     width=100).pack(side="left", padx=5)
        
        ctk.CTkLabel(scroll_frame, text="날짜 (YY.MM 또는 YY.Qn):").pack(pady=(10, 5), anchor="w", padx=10)
        self.date_entry = ctk.CTkEntry(scroll_frame, width=400, 
                                       placeholder_text="예: 24.10 또는 24.Q3")
        self.date_entry.pack(pady=5, padx=10)
        
        ctk.CTkLabel(scroll_frame, text="내용:").pack(pady=(10, 5), anchor="w", padx=10)
        self.content_entry = ctk.CTkEntry(scroll_frame, width=400,
                                          placeholder_text="노드 옆에 표시될 텍스트")
        self.content_entry.pack(pady=5, padx=10)
        
        ctk.CTkLabel(scroll_frame, text="메모:").pack(pady=(10, 5), anchor="w", padx=10)
        self.memo_text = ctk.CTkTextbox(scroll_frame, width=400, height=100)
        self.memo_text.pack(pady=5, padx=10)
        
        ctk.CTkLabel(scroll_frame, text="첨부 파일:").pack(pady=(10, 5), anchor="w", padx=10)
        file_frame = ctk.CTkFrame(scroll_frame, fg_color="transparent")
        file_frame.pack(pady=5, padx=10, fill="x")
        
        self.file_label = ctk.CTkLabel(file_frame, text=self.attached_file or "파일 없음", 
                                       anchor="w")
        self.file_label.pack(side="left", padx=5, fill="x", expand=True)
        
        ctk.CTkButton(file_frame, text="파일 선택", command=self._choose_file,
                     width=100).pack(side="left", padx=5)
        
        if node_data:
            self.date_entry.insert(0, node_data.get("date", ""))
            self.content_entry.insert(0, node_data.get("content", ""))
            self.memo_text.insert("1.0", node_data.get("memo", ""))
        
        btn_frame = ctk.CTkFrame(self, fg_color="transparent")
        btn_frame.pack(pady=10)
        
        ctk.CTkButton(btn_frame, text="확인", command=self._on_confirm,
                     width=100).pack(side="left", padx=5)
        ctk.CTkButton(btn_frame, text="취소", command=self.destroy,
                     width=100).pack(side="left", padx=5)
        
        self.grab_set()
        self.wait_window()
    
    def _choose_color(self):
        """색상 선택 다이얼로그"""
        color = colorchooser.askcolor(initialcolor=self.selected_color)
        if color[1]:
            self.selected_color = color[1]
            self.color_display.configure(fg_color=self.selected_color)
    
    def _choose_file(self):
        """파일 선택 다이얼로그"""
        filename = filedialog.askopenfilename()
        if filename:
            self.attached_file = filename
            self.file_label.configure(text=filename)
    
    def _on_confirm(self):
        """확인 버튼 클릭 시 데이터 반환"""
        date = self.date_entry.get().strip()
        content = self.content_entry.get().strip()
        
        if not date or not content:
            return
        
        self.result = {
            "shape": self.shape_var.get(),
            "color": self.selected_color,
            "date": date,
            "content": content,
            "memo": self.memo_text.get("1.0", "end-1c").strip(),
            "attachment": self.attached_file
        }
        self.destroy()


class SearchFilterDialog(ctk.CTkToplevel):
    """검색 및 필터 다이얼로그"""
    
    def __init__(self, parent):
        super().__init__(parent)
        self.title("검색 및 필터")
        self.geometry("400x300")
        self.resizable(False, False)
        
        self.result = None
        
        ctk.CTkLabel(self, text="키워드 검색:").pack(pady=(20, 5))
        self.keyword_entry = ctk.CTkEntry(self, width=350, 
                                          placeholder_text="제목, 부제목, 내용에서 검색")
        self.keyword_entry.pack(pady=5)
        
        ctk.CTkLabel(self, text="모양 필터:").pack(pady=(10, 5))
        self.shape_var = ctk.StringVar(value="전체")
        shapes = ["전체"] + NodeDialog.SHAPES
        ctk.CTkOptionMenu(self, values=shapes, variable=self.shape_var,
                         width=350).pack(pady=5)
        
        btn_frame = ctk.CTkFrame(self, fg_color="transparent")
        btn_frame.pack(pady=20)
        
        ctk.CTkButton(btn_frame, text="적용", command=self._on_apply,
                     width=100).pack(side="left", padx=5)
        ctk.CTkButton(btn_frame, text="취소", command=self.destroy,
                     width=100).pack(side="left", padx=5)
        
        self.grab_set()
        self.wait_window()
    
    def _on_apply(self):
        """필터 적용"""
        self.result = {
            "keyword": self.keyword_entry.get().strip(),
            "shape": None if self.shape_var.get() == "전체" else self.shape_var.get()
        }
        self.destroy()
