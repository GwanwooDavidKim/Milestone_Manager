"""타임라인 캔버스 모듈 - 타임라인과 노드를 시각화하는 컴포넌트"""

import customtkinter as ctk
from tkinter import Canvas, font
from typing import List, Dict, Optional, Tuple, Callable
import os
import platform


class TimelineCanvas(ctk.CTkFrame):
    """타임라인과 노드를 직접 그리는 시각화 컴포넌트"""
    
    def __init__(self, parent, milestone_data: Dict, 
                 on_node_click: Optional[Callable] = None):
        """
        Args:
            parent: 부모 위젯
            milestone_data (Dict): 마일스톤 데이터
            on_node_click (Optional[callable]): 노드 클릭 콜백
        """
        super().__init__(parent, fg_color="transparent")
        
        self.milestone_data = milestone_data
        self.on_node_click = on_node_click
        
        self.zoom_level = 1.0
        self.pan_offset = 0
        self.dragging = False
        self.drag_start_x = 0
        
        self.canvas = Canvas(self, bg="#2B2B2B", highlightthickness=0)
        self.canvas.pack(fill="both", expand=True)
        
        self.canvas.bind("<MouseWheel>", self._on_mousewheel)
        self.canvas.bind("<Button-4>", self._on_mousewheel)
        self.canvas.bind("<Button-5>", self._on_mousewheel)
        self.canvas.bind("<ButtonPress-1>", self._on_drag_start)
        self.canvas.bind("<B1-Motion>", self._on_drag_motion)
        self.canvas.bind("<ButtonRelease-1>", self._on_drag_end)
        self.canvas.bind("<Motion>", self._on_mouse_motion)
        
        self.node_positions = {}
        self.tooltip_id = None
        
        self.bind("<Configure>", lambda e: self.draw_timeline())
        
        self.draw_timeline()
    
    def _on_mousewheel(self, event):
        """마우스 휠로 줌 조절"""
        if event.num == 4 or event.delta > 0:
            self.zoom_level = min(self.zoom_level * 1.2, 5.0)
        elif event.num == 5 or event.delta < 0:
            self.zoom_level = max(self.zoom_level / 1.2, 0.2)
        self.draw_timeline()
    
    def _on_drag_start(self, event):
        """드래그 시작"""
        self.dragging = True
        self.drag_start_x = event.x
    
    def _on_drag_motion(self, event):
        """드래그 중"""
        if self.dragging:
            dx = event.x - self.drag_start_x
            self.pan_offset += dx
            self.drag_start_x = event.x
            self.draw_timeline()
    
    def _on_drag_end(self, event):
        """드래그 종료"""
        self.dragging = False
    
    def _on_mouse_motion(self, event):
        """마우스 이동 시 툴팁 표시"""
        if self.tooltip_id:
            self.canvas.delete(self.tooltip_id)
            self.tooltip_id = None
        
        for node_id, (x, y, node_data) in self.node_positions.items():
            if abs(event.x - x) < 15 and abs(event.y - y) < 15:
                memo = node_data.get("memo", "")
                if memo:
                    self._show_tooltip(event.x, event.y, memo)
                break
    
    def _show_tooltip(self, x: int, y: int, text: str):
        """툴팁 표시"""
        lines = text.split('\n')
        max_width = max(len(line) for line in lines) * 7 + 20
        height = len(lines) * 20 + 10
        
        self.tooltip_id = self.canvas.create_rectangle(
            x + 10, y - height, x + max_width + 10, y,
            fill="#1F1F1F", outline="#3B8ED0", width=2
        )
        
        for i, line in enumerate(lines):
            self.canvas.create_text(
                x + 15, y - height + 15 + i * 20,
                text=line, fill="white", anchor="w", font=("Arial", 10)
            )
    
    def draw_timeline(self):
        """타임라인과 노드를 그립니다"""
        self.canvas.delete("all")
        self.node_positions.clear()
        
        width = self.canvas.winfo_width()
        height = self.canvas.winfo_height()
        
        if width < 10 or height < 10:
            return
        
        timeline_y = 100
        
        self.canvas.create_line(50, timeline_y, width - 50, timeline_y,
                               fill="#3B8ED0", width=3)
        
        nodes = self.milestone_data.get("nodes", [])
        
        if not nodes:
            return
        
        sorted_nodes = sorted(nodes, key=lambda n: self._parse_date(n.get("date", "")))
        
        month_positions = {}
        for year in range(20, 30):
            for month in range(1, 13):
                date_key = f"{year:02d}.{month:02d}"
                x_pos = 50 + (year * 12 + month) * 30 * self.zoom_level + self.pan_offset
                month_positions[date_key] = x_pos
                
                if 0 < x_pos < width:
                    self.canvas.create_line(x_pos, timeline_y - 10, x_pos, timeline_y + 10,
                                          fill="#666666", width=1)
                    
                    if month % 3 == 1:
                        self.canvas.create_text(x_pos, timeline_y - 25,
                                              text=date_key, fill="white",
                                              font=("Arial", 9))
        
        node_layout = self._calculate_node_layout(sorted_nodes, month_positions, timeline_y, width)
        
        for node_data, x, y in node_layout:
            self._draw_node(node_data, x, y, timeline_y)
    
    def _parse_date(self, date_str: str) -> int:
        """날짜 문자열을 정렬 가능한 숫자로 변환"""
        if "Q" in date_str.upper():
            parts = date_str.upper().split("Q")
            if len(parts) == 2:
                year = int(parts[0]) if parts[0] else 20
                quarter = int(parts[1]) if parts[1].isdigit() else 1
                return year * 100 + quarter * 3
        else:
            parts = date_str.split(".")
            if len(parts) == 2:
                year = int(parts[0]) if parts[0].isdigit() else 20
                month = int(parts[1]) if parts[1].isdigit() else 1
                return year * 100 + month
        return 0
    
    def _calculate_node_layout(self, nodes: List[Dict], month_positions: Dict,
                               timeline_y: int, width: int) -> List[Tuple]:
        """겹침 방지 자동 레이아웃 계산"""
        layout = []
        occupied = []
        
        for node in nodes:
            date = node.get("date", "")
            x_pos = self._get_node_x_position(date, month_positions)
            
            if x_pos < 0 or x_pos > width:
                continue
            
            y_offset = 0
            alternating = len(layout) % 2
            
            for occupied_x, occupied_y in occupied:
                if abs(occupied_x - x_pos) < 100:
                    y_offset = max(y_offset, abs(occupied_y - timeline_y) + 40)
            
            if alternating == 0:
                y_pos = timeline_y - 50 - y_offset
            else:
                y_pos = timeline_y + 50 + y_offset
            
            layout.append((node, x_pos, y_pos))
            occupied.append((x_pos, y_pos))
        
        return layout
    
    def _get_node_x_position(self, date: str, month_positions: Dict) -> int:
        """날짜에 해당하는 X 좌표 계산"""
        if "Q" in date.upper():
            parts = date.upper().split("Q")
            if len(parts) == 2:
                year = int(parts[0]) if parts[0].isdigit() else 20
                quarter = int(parts[1]) if parts[1].isdigit() else 1
                month = (quarter - 1) * 3 + 2
                date_key = f"{year:02d}.{month:02d}"
                return month_positions.get(date_key, 100)
        
        return month_positions.get(date, 100)
    
    def _draw_node(self, node_data: Dict, x: int, y: int, timeline_y: int):
        """노드를 그립니다"""
        shape = node_data.get("shape", "●(동그라미)")
        color = node_data.get("color", "#3B8ED0")
        content = node_data.get("content", "")
        attachment = node_data.get("attachment", "")
        
        self.canvas.create_line(x, timeline_y, x, y, fill="#666666", width=1, dash=(2, 2))
        
        if "●" in shape or "동그라미" in shape:
            self.canvas.create_oval(x - 10, y - 10, x + 10, y + 10,
                                   fill=color, outline="white", width=2)
        elif "▲" in shape or "세모" in shape:
            self.canvas.create_polygon(x, y - 12, x - 10, y + 8, x + 10, y + 8,
                                      fill=color, outline="white", width=2)
        elif "■" in shape or "네모" in shape:
            self.canvas.create_rectangle(x - 10, y - 10, x + 10, y + 10,
                                        fill=color, outline="white", width=2)
        elif "★" in shape or "별" in shape:
            points = self._get_star_points(x, y, 12, 5)
            self.canvas.create_polygon(points, fill=color, outline="white", width=2)
        else:
            self.canvas.create_polygon(x, y - 10, x + 10, y, x, y + 10, x - 10, y,
                                      fill=color, outline="white", width=2)
        
        text_y = y - 20 if y < timeline_y else y + 20
        self.canvas.create_text(x, text_y, text=content, fill="white",
                              font=("Arial", 10, "bold"))
        
        if attachment:
            self.canvas.create_text(x + 15, y - 15, text="📎", fill="white",
                                  font=("Arial", 12))
        
        self.node_positions[node_data.get("id", "")] = (x, y, node_data)
        
        node_id = self.canvas.create_oval(x - 15, y - 15, x + 15, y + 15,
                                         fill="", outline="", tags=f"node_{node_data.get('id', '')}")
        self.canvas.tag_bind(node_id, "<Button-1>", 
                           lambda e, nd=node_data: self._on_node_clicked(nd))
    
    def _get_star_points(self, cx: int, cy: int, r: int, points: int = 5) -> List[int]:
        """별 모양 좌표 계산"""
        import math
        coords = []
        angle = math.pi / 2
        d_angle = 2 * math.pi / (points * 2)
        
        for i in range(points * 2):
            radius = r if i % 2 == 0 else r / 2
            x = cx + radius * math.cos(angle)
            y = cy - radius * math.sin(angle)
            coords.extend([x, y])
            angle += d_angle
        
        return coords
    
    def _on_node_clicked(self, node_data: Dict):
        """노드 클릭 이벤트"""
        if self.on_node_click:
            self.on_node_click(node_data)
        
        attachment = node_data.get("attachment", "")
        if attachment and os.path.exists(attachment):
            if platform.system() == 'Windows':
                os.startfile(attachment)  # type: ignore
            elif platform.system() == 'Darwin':
                os.system(f'open "{attachment}"')
            else:
                os.system(f'xdg-open "{attachment}"')
