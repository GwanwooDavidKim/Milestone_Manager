"""메인 UI 윈도우 모듈 - 애플리케이션의 주요 GUI 구성"""

import customtkinter as ctk
from tkinter import messagebox, filedialog
from typing import List, Dict, Optional
from PIL import Image, ImageGrab
import io

from data_manager import DataManager
from custom_widgets import MilestoneDialog, NodeDialog, SearchFilterDialog
from timeline_canvas import TimelineCanvas


class MainWindow(ctk.CTk):
    """메인 GUI 창의 레이아웃과 위젯을 관리하는 클래스"""
    
    def __init__(self):
        super().__init__()
        
        self.title("Milestone Manager")
        self.geometry("1400x800")
        
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("blue")
        
        self.data_manager = DataManager()
        self.milestone_blocks = []
        self.selected_milestone_ids = set()
        self.selected_node = None
        self.current_milestone_id = None
        self.filter_settings = None
        
        self._create_ui()
        
        self.bind("<Control-s>", lambda e: self.save_data())
    
    def _create_ui(self):
        """UI 구성 요소 생성"""
        top_frame = ctk.CTkFrame(self, height=60, fg_color="transparent")
        top_frame.pack(fill="x", padx=10, pady=10)
        top_frame.pack_propagate(False)
        
        ctk.CTkButton(top_frame, text="Data Load", command=self.load_data,
                     width=120, height=40).pack(side="left", padx=5)
        
        ctk.CTkButton(top_frame, text="Data 저장 (Ctrl+S)", command=self.save_data,
                     width=150, height=40).pack(side="left", padx=5)
        
        ctk.CTkButton(top_frame, text="Milestone 생성", command=self.create_milestone,
                     width=140, height=40).pack(side="left", padx=5)
        
        ctk.CTkButton(top_frame, text="선택한 Milestone 삭제", command=self.delete_selected_milestones,
                     width=180, height=40).pack(side="left", padx=5)
        
        ctk.CTkButton(top_frame, text="검색/필터", command=self.open_search_filter,
                     width=120, height=40).pack(side="left", padx=5)
        
        ctk.CTkButton(top_frame, text="이미지 내보내기", command=self.export_image,
                     width=140, height=40).pack(side="left", padx=5)
        
        self.scroll_frame = ctk.CTkScrollableFrame(self, fg_color="transparent")
        self.scroll_frame.pack(fill="both", expand=True, padx=10, pady=10)
    
    def load_data(self):
        """raw.json 데이터 로드"""
        try:
            data = self.data_manager.load_data()
            self._refresh_ui()
            messagebox.showinfo("성공", "데이터를 성공적으로 불러왔습니다.")
        except Exception as e:
            messagebox.showerror("오류", str(e))
    
    def save_data(self):
        """현재 데이터를 raw.json에 저장"""
        try:
            data = {"milestones": self.data_manager.get_milestones()}
            self.data_manager.save_data(data)
            messagebox.showinfo("성공", "데이터가 저장되었습니다.")
        except Exception as e:
            messagebox.showerror("오류", str(e))
    
    def create_milestone(self):
        """새 마일스톤 생성"""
        dialog = MilestoneDialog(self)
        if dialog.result:
            self.data_manager.add_milestone(
                dialog.result["title"],
                dialog.result["subtitle"]
            )
            self._refresh_ui()
    
    def delete_selected_milestones(self):
        """선택된 마일스톤 삭제"""
        if not self.selected_milestone_ids:
            messagebox.showwarning("경고", "삭제할 마일스톤을 선택해주세요.")
            return
        
        count = len(self.selected_milestone_ids)
        if messagebox.askyesno("확인", f"{count}개의 마일스톤을 삭제하시겠습니까?"):
            for milestone_id in self.selected_milestone_ids:
                self.data_manager.delete_milestone(milestone_id)
            self.selected_milestone_ids.clear()
            self._refresh_ui()
    
    def open_search_filter(self):
        """검색 및 필터 다이얼로그 열기"""
        dialog = SearchFilterDialog(self)
        if dialog.result:
            self.filter_settings = dialog.result
            self._refresh_ui()
    
    def export_image(self):
        """마일스톤을 이미지로 내보내기"""
        if not self.milestone_blocks:
            messagebox.showwarning("경고", "내보낼 마일스톤이 없습니다.")
            return
        
        filename = filedialog.asksaveasfilename(
            defaultextension=".png",
            filetypes=[("PNG files", "*.png"), ("JPG files", "*.jpg")]
        )
        
        if filename:
            try:
                if self.milestone_blocks:
                    widget = self.milestone_blocks[0]
                    x = widget.winfo_rootx()
                    y = widget.winfo_rooty()
                    w = widget.winfo_width()
                    h = widget.winfo_height()
                    
                    img = ImageGrab.grab(bbox=(x, y, x + w, y + h))
                    img.save(filename)
                    messagebox.showinfo("성공", f"이미지가 저장되었습니다: {filename}")
            except Exception as e:
                messagebox.showerror("오류", f"이미지 저장 실패: {str(e)}")
    
    def _refresh_ui(self):
        """UI 새로고침"""
        for widget in self.scroll_frame.winfo_children():
            widget.destroy()
        
        self.milestone_blocks.clear()
        
        milestones = self.data_manager.get_milestones()
        
        for milestone in milestones:
            if self._should_show_milestone(milestone):
                self._create_milestone_block(milestone)
    
    def _should_show_milestone(self, milestone: Dict) -> bool:
        """필터링 조건에 따라 마일스톤 표시 여부 결정"""
        if not self.filter_settings:
            return True
        
        keyword = self.filter_settings.get("keyword", "")
        shape_filter = self.filter_settings.get("shape")
        
        if keyword:
            if keyword.lower() not in milestone.get("title", "").lower() and \
               keyword.lower() not in milestone.get("subtitle", "").lower():
                has_keyword = False
                for node in milestone.get("nodes", []):
                    if keyword.lower() in node.get("content", "").lower():
                        has_keyword = True
                        break
                if not has_keyword:
                    return False
        
        if shape_filter:
            has_matching_shape = False
            for node in milestone.get("nodes", []):
                if node.get("shape") == shape_filter:
                    has_matching_shape = True
                    break
            if not has_matching_shape:
                return False
        
        return True
    
    def _create_milestone_block(self, milestone: Dict):
        """Liquid Glass 스타일의 마일스톤 블록 생성"""
        block_frame = ctk.CTkFrame(
            self.scroll_frame,
            fg_color="#1E1E1E",
            border_width=2,
            border_color="#3B8ED0",
            corner_radius=15
        )
        block_frame.pack(fill="x", padx=10, pady=15)
        
        self.milestone_blocks.append(block_frame)
        
        header_frame = ctk.CTkFrame(block_frame, fg_color="transparent")
        header_frame.pack(fill="x", padx=15, pady=10)
        
        checkbox_var = ctk.BooleanVar(
            value=milestone["id"] in self.selected_milestone_ids
        )
        
        checkbox = ctk.CTkCheckBox(
            header_frame,
            text="",
            variable=checkbox_var,
            command=lambda: self._toggle_milestone_selection(milestone["id"], checkbox_var.get()),
            width=30
        )
        checkbox.pack(side="left", padx=(0, 10))
        
        title_frame = ctk.CTkFrame(header_frame, fg_color="transparent")
        title_frame.pack(side="left", fill="x", expand=True)
        
        ctk.CTkLabel(
            title_frame,
            text=milestone.get("title", ""),
            font=("Arial", 18, "bold"),
            text_color="white"
        ).pack(anchor="w")
        
        ctk.CTkLabel(
            title_frame,
            text=milestone.get("subtitle", ""),
            font=("Arial", 12),
            text_color="#AAAAAA"
        ).pack(anchor="w")
        
        btn_frame = ctk.CTkFrame(header_frame, fg_color="transparent")
        btn_frame.pack(side="right")
        
        ctk.CTkButton(
            btn_frame,
            text="Node 추가",
            command=lambda: self._add_node_to_milestone(milestone["id"]),
            width=100,
            height=30
        ).pack(side="left", padx=5)
        
        ctk.CTkButton(
            btn_frame,
            text="Node 수정",
            command=lambda: self._edit_node(milestone["id"]),
            width=100,
            height=30
        ).pack(side="left", padx=5)
        
        ctk.CTkButton(
            btn_frame,
            text="Node 삭제",
            command=lambda: self._delete_node(milestone["id"]),
            width=100,
            height=30
        ).pack(side="left", padx=5)
        
        timeline_frame = ctk.CTkFrame(block_frame, fg_color="#2B2B2B", height=400)
        timeline_frame.pack(fill="both", expand=True, padx=15, pady=(0, 15))
        timeline_frame.pack_propagate(False)
        
        canvas = TimelineCanvas(
            timeline_frame,
            milestone,
            on_node_click=lambda nd: self._on_node_selected(milestone["id"], nd)
        )
        canvas.pack(fill="both", expand=True)
    
    def _toggle_milestone_selection(self, milestone_id: str, is_selected: bool):
        """마일스톤 선택 토글"""
        if is_selected:
            self.selected_milestone_ids.add(milestone_id)
        else:
            self.selected_milestone_ids.discard(milestone_id)
    
    def _add_node_to_milestone(self, milestone_id: str):
        """마일스톤에 노드 추가"""
        self.current_milestone_id = milestone_id
        dialog = NodeDialog(self)
        if dialog.result:
            self.data_manager.add_node(milestone_id, dialog.result)
            self._refresh_ui()
    
    def _on_node_selected(self, milestone_id: str, node_data: Dict):
        """노드 선택 이벤트"""
        self.current_milestone_id = milestone_id
        self.selected_node = node_data
    
    def _edit_node(self, milestone_id: str):
        """노드 수정"""
        if not self.selected_node:
            messagebox.showwarning("경고", "수정할 노드를 먼저 선택해주세요.")
            return
        
        dialog = NodeDialog(self, title="노드 수정", node_data=self.selected_node)
        if dialog.result:
            self.data_manager.update_node(
                milestone_id,
                self.selected_node["id"],
                dialog.result
            )
            self.selected_node = None
            self._refresh_ui()
    
    def _delete_node(self, milestone_id: str):
        """노드 삭제"""
        if not self.selected_node:
            messagebox.showwarning("경고", "삭제할 노드를 먼저 선택해주세요.")
            return
        
        if messagebox.askyesno("확인", "선택한 노드를 삭제하시겠습니까?"):
            self.data_manager.delete_node(milestone_id, self.selected_node["id"])
            self.selected_node = None
            self._refresh_ui()
