"""타임라인 캔버스 모듈 - 라이트 모드 타임라인과 노드 시각화"""

from PyQt6.QtWidgets import (QWidget, QGraphicsScene, QGraphicsView, QGraphicsEllipseItem, 
                              QGraphicsPolygonItem, QGraphicsTextItem, QGraphicsRectItem, 
                              QGraphicsPathItem, QCheckBox, QGraphicsProxyWidget, QMessageBox, 
                              QDialog, QVBoxLayout, QTextEdit, QPushButton)
from PyQt6.QtCore import Qt, QPointF, QRectF
from PyQt6.QtGui import QPen, QBrush, QColor, QPainter, QPolygonF, QPainterPath, QFont
from typing import List, Dict, Optional, Tuple
import math
import os
import platform


class MemoDialog(QDialog):
    """메모 표시 다이얼로그"""
    
    def __init__(self, parent=None, memo: str = ""):
        super().__init__(parent)
        self.setWindowTitle("메모")
        self.setModal(True)
        self.setFixedSize(500, 400)
        
        self.setStyleSheet("""
            QDialog {
                background: white;
            }
            QTextEdit {
                background: #f5f5f7;
                border: 1px solid #d2d2d7;
                border-radius: 8px;
                padding: 12px;
                color: #1d1d1f;
                font-size: 14px;
            }
            QPushButton {
                background: #007AFF;
                color: white;
                border: none;
                border-radius: 8px;
                padding: 10px 20px;
                font-size: 14px;
                font-weight: bold;
            }
            QPushButton:hover {
                background: #1A8CFF;
            }
        """)
        
        layout = QVBoxLayout()
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(15)
        
        memo_text = QTextEdit()
        memo_text.setPlainText(memo)
        memo_text.setReadOnly(True)
        layout.addWidget(memo_text)
        
        close_btn = QPushButton("닫기")
        close_btn.clicked.connect(self.accept)
        layout.addWidget(close_btn)
        
        self.setLayout(layout)


class TimelineCanvas(QWidget):
    """라이트 모드 타임라인 시각화 컴포넌트"""
    
    def __init__(self, parent=None, milestone_data: Dict = None, on_node_click=None):
        super().__init__(parent)
        self.milestone_data = milestone_data or {"nodes": []}
        self.on_node_click = on_node_click
        
        self.scene = QGraphicsScene()
        self.view = QGraphicsView(self.scene, self)
        self.view.setRenderHint(QPainter.RenderHint.Antialiasing)
        self.view.setStyleSheet("""
            QGraphicsView {
                background: #fafafa;
                border: 1px solid #e8e8ed;
                border-radius: 8px;
            }
        """)
        
        self.view.setGeometry(0, 0, self.width(), self.height())
        self.node_items = {}
        self.selected_node_id = None
        self.node_checkboxes = {}
        
        self.draw_timeline()
    
    def resizeEvent(self, event):
        self.view.setGeometry(0, 0, self.width(), self.height())
        self.draw_timeline()
    
    def draw_timeline(self):
        """타임라인과 노드를 그립니다 - 빈 연도 포함"""
        self.scene.clear()
        self.node_items.clear()
        self.node_checkboxes.clear()
        
        width = self.width() - 100
        
        if width < 100:
            return
        
        nodes = self.milestone_data.get("nodes", [])
        
        # 현재 년도는 항상 포함
        from datetime import datetime
        current_year = datetime.now().year % 100  # 2025 -> 25
        
        sorted_nodes = sorted(nodes, key=lambda n: self._parse_date(n.get("date", ""))) if nodes else []
        
        # 연도 추출 (빈 연도 포함 + 현재 년도 기본 포함)
        years_set = set()
        years_set.add(current_year)  # 현재 년도는 항상 포함
        
        for node in sorted_nodes:
            date_val = self._parse_date(node.get("date", ""))
            year = date_val // 100
            years_set.add(year)
        
        if not years_set:
            return
        
        # 최소/최대 연도 사이의 모든 연도 포함
        min_year = min(years_set)
        max_year = max(years_set)
        years = list(range(min_year, max_year + 1))
        
        timeline_y = height / 2
        start_x = 80
        end_x = width - 20
        timeline_width = end_x - start_x
        
        # 타임라인 막대 (다크 블루그레이)
        gradient_rect = self.scene.addRect(
            start_x - 5, timeline_y - 3,
            timeline_width + 10, 6
        )
        gradient_rect.setPen(QPen(Qt.PenStyle.NoPen))
        gradient_rect.setBrush(QBrush(QColor("#2C3E50")))
        
        # 연도별 균등 간격 계산
        num_years = len(years)
        year_spacing = timeline_width / num_years if num_years > 1 else timeline_width
        
        # 각 연도에 대해 분기별 눈금 그리기
        for i, year in enumerate(years):
            year_x = start_x + (i * year_spacing)
            
            # 각 분기별 위치 계산
            for quarter in [1, 2, 3, 4]:
                quarter_offset = (quarter - 1) * (year_spacing / 4)
                x_pos = year_x + quarter_offset
                
                # 큰 눈금선
                tick_line = self.scene.addLine(x_pos, timeline_y - 20, x_pos, timeline_y + 20)
                tick_line.setPen(QPen(QColor("#86868b"), 2))
                
                # 분기 표시
                quarter_text = self.scene.addText(f"{year:02d}.Q{quarter}")
                quarter_text.setDefaultTextColor(QColor("#1d1d1f"))
                quarter_text.setFont(QFont("Apple SD Gothic Neo", 11, QFont.Weight.Bold))
                quarter_text.setPos(x_pos - 25, timeline_y - 45)
            
            # 월별 작은 눈금
            for month in range(1, 13):
                if month not in [3, 6, 9, 12]:
                    month_offset = (month - 1) * (year_spacing / 12)
                    x_pos = year_x + month_offset
                    tick_line = self.scene.addLine(x_pos, timeline_y - 10, x_pos, timeline_y + 10)
                    tick_line.setPen(QPen(QColor("#d2d2d7"), 1))
        
        # 현재 날짜 표시 (빨간 점선)
        today = datetime.now()
        current_month = today.month
        
        # "이번달" 텍스트 (점선은 나중에 그림)
        if current_year in years:
            year_idx = years.index(current_year)
            year_x = start_x + (year_idx * year_spacing)
            month_offset = (current_month - 1) * (year_spacing / 12)
            current_x = year_x + month_offset
            
            # "이번달" 표시 (점선 오른쪽 위)
            month_text = self.scene.addText("이번달")
            month_text.setDefaultTextColor(QColor("#FF3B30"))
            month_text.setFont(QFont("Apple SD Gothic Neo", 10, QFont.Weight.Bold))
            month_text.setPos(current_x + 5, 25)
        
        # 노드 위치 계산
        node_positions = self._calculate_node_positions(sorted_nodes, years, year_spacing, 
                                                         start_x, timeline_y)
        
        # 동적 높이 계산 - 모든 노드가 보이도록
        if node_positions:
            min_y = min(y for _, _, y in node_positions)
            max_y = max(y for _, _, y in node_positions)
            required_height = max(600, max_y - min_y + 300)  # 최소 600, 여유 300
        else:
            required_height = 600
        
        # 이번달 점선 높이 업데이트
        if current_year in years:
            year_idx = years.index(current_year)
            year_x = start_x + (year_idx * year_spacing)
            month_offset = (current_month - 1) * (year_spacing / 12)
            current_x = year_x + month_offset
            
            # 빨간 점선 그리기 (동적 높이에 맞춰)
            pen = QPen(QColor("#FF3B30"), 2, Qt.PenStyle.DashLine)
            current_line = self.scene.addLine(current_x, 20, current_x, required_height - 20)
            current_line.setPen(pen)
        
        # Scene 크기 설정
        self.scene.setSceneRect(0, 0, width + 100, required_height)
        
        # Widget 높이도 동적으로 설정하여 스크롤 제거
        self.setMinimumHeight(int(required_height))
        self.setMaximumHeight(int(required_height))
        
        for node_data, x, y in node_positions:
            self._draw_node(node_data, x, y, timeline_y)
    
    def _parse_date(self, date_str: str) -> int:
        """날짜 문자열을 숫자로 변환"""
        date_str = date_str.strip().upper()
        
        if "Q" in date_str:
            parts = date_str.split("Q")
            if len(parts) == 2:
                try:
                    year = int(parts[0].replace(".", "").strip())
                    quarter = int(parts[1].strip())
                    month = quarter * 3
                    return year * 100 + month
                except:
                    return 2000
        else:
            parts = date_str.split(".")
            if len(parts) == 2:
                try:
                    year = int(parts[0].strip())
                    month = int(parts[1].strip())
                    return year * 100 + month
                except:
                    return 2000
        return 2000
    
    def _calculate_node_positions(self, nodes: List[Dict], years: List[int], 
                                   year_spacing: float, start_x: float, 
                                   timeline_y: float) -> List[Tuple]:
        """노드 위치 계산 - 같은 날짜 노드 겹침 방지"""
        layout = []
        occupied_positions = []
        
        # 1단계: 노드를 date_val로 그룹화
        from collections import defaultdict
        date_groups = defaultdict(list)
        for node in nodes:
            date = node.get("date", "")
            date_val = self._parse_date(date)
            date_groups[date_val].append(node)
        
        # 2단계: 각 날짜 그룹별로 처리
        for date_val, group_nodes in date_groups.items():
            year = date_val // 100
            month = date_val % 100
            
            # 기본 x 좌표 계산
            if year in years:
                year_idx = years.index(year)
                year_x = start_x + (year_idx * year_spacing)
                month_offset = (month - 1) * (year_spacing / 12)
                base_x = year_x + month_offset
            else:
                base_x = start_x
            
            # 3단계: 같은 날짜 그룹 내 노드들 배치
            for group_idx, node in enumerate(group_nodes):
                # x좌표 분산: 0, +50, -50, +100, -100, +150, -150...
                # 겹침 방지를 위해 간격을 크게 설정
                if group_idx == 0:
                    x_offset = 0
                elif group_idx % 2 == 1:
                    x_offset = (group_idx // 2 + 1) * 50
                else:
                    x_offset = -(group_idx // 2) * 50
                
                x_pos = base_x + x_offset
                
                # 같은 날짜 그룹 내에서 위-아래 교대 배치
                # 기본 방향은 date_val % 2로 결정하되, 그룹 내에서 교대
                base_alternating = date_val % 2
                if group_idx % 2 == 1:
                    alternating = 1 - base_alternating  # 반대 방향
                else:
                    alternating = base_alternating  # 같은 방향
                
                # 겹침 체크 - 간격을 충분히 크게 설정
                y_offset = 0
                base_distance = 100  # 기본 거리 증가
                for occupied_x, occupied_y in occupied_positions:
                    if abs(occupied_x - x_pos) < 200:
                        y_offset = max(y_offset, abs(occupied_y - timeline_y) - base_distance + 80)
                
                if alternating == 0:
                    y_pos = timeline_y - base_distance - y_offset
                else:
                    y_pos = timeline_y + base_distance + y_offset
                
                layout.append((node, x_pos, y_pos))
                occupied_positions.append((x_pos, y_pos))
        
        return layout
    
    def _draw_node(self, node_data: Dict, x: float, y: float, timeline_y: float):
        """노드를 그립니다 - 체크박스, 첨부파일, 메모 이모지 포함"""
        shape = node_data.get("shape", "●(동그라미)")
        color = QColor(node_data.get("color", "#FF6B6B"))
        content = node_data.get("content", "")
        memo = node_data.get("memo", "")
        attachment = node_data.get("attachment", "")
        date = node_data.get("date", "")
        node_id = node_data.get("id", "")
        
        # 타임라인과 연결선
        connector_line = self.scene.addLine(x, timeline_y, x, y)
        connector_line.setPen(QPen(QColor("#d2d2d7"), 1, Qt.PenStyle.DashLine))
        
        node_item = None
        node_size = 20
        
        if "●" in shape or "동그라미" in shape:
            node_item = self.scene.addEllipse(x - node_size/2, y - node_size/2, node_size, node_size)
            node_item.setBrush(QBrush(color))
            node_item.setPen(QPen(QColor("white"), 2))
        
        elif "▲" in shape or "세모" in shape:
            polygon = QPolygonF([
                QPointF(x, y - node_size*0.6),
                QPointF(x - node_size*0.5, y + node_size*0.4),
                QPointF(x + node_size*0.5, y + node_size*0.4)
            ])
            node_item = self.scene.addPolygon(polygon)
            node_item.setBrush(QBrush(color))
            node_item.setPen(QPen(QColor("white"), 2))
        
        elif "■" in shape or "네모" in shape:
            node_item = self.scene.addRect(x - node_size/2, y - node_size/2, node_size, node_size)
            node_item.setBrush(QBrush(color))
            node_item.setPen(QPen(QColor("white"), 2))
        
        elif "★" in shape or "별" in shape:
            star_path = self._get_star_path(x, y, node_size*0.6, 5)
            node_item = self.scene.addPath(star_path)
            node_item.setBrush(QBrush(color))
            node_item.setPen(QPen(QColor("white"), 2))
        
        else:  # 마름모
            polygon = QPolygonF([
                QPointF(x, y - node_size/2),
                QPointF(x + node_size/2, y),
                QPointF(x, y + node_size/2),
                QPointF(x - node_size/2, y)
            ])
            node_item = self.scene.addPolygon(polygon)
            node_item.setBrush(QBrush(color))
            node_item.setPen(QPen(QColor("white"), 2))
        
        # 체크박스 추가 (노드 왼쪽, 간격 조정, 중간 맞춤)
        checkbox = QCheckBox()
        checkbox.setStyleSheet("""
            QCheckBox {
                spacing: 0px;
                padding: 0px;
                margin: 0px;
            }
            QCheckBox::indicator {
                width: 16px;
                height: 16px;
                border-radius: 4px;
                border: 2px solid #d2d2d7;
                background: white;
            }
            QCheckBox::indicator:checked {
                background: #007AFF;
                border: 2px solid #007AFF;
            }
            QCheckBox::indicator:hover {
                border: 2px solid #007AFF;
            }
        """)
        checkbox.stateChanged.connect(
            lambda state: self._on_checkbox_changed(node_data, state == Qt.CheckState.Checked.value)
        )
        
        checkbox_proxy = self.scene.addWidget(checkbox)
        checkbox_proxy.setPos(x - 32, y - 8)  # 간격 줄이고 중간 맞춤
        self.node_checkboxes[node_id] = checkbox
        
        # 날짜와 내용 텍스트
        if y < timeline_y:  # 노드가 위에 있을 때
            date_text = self.scene.addText(date)
            date_text.setDefaultTextColor(QColor("#86868b"))
            date_text.setFont(QFont("Apple SD Gothic Neo", 10))
            date_bounds = date_text.boundingRect()
            date_text.setPos(x - date_bounds.width() / 2, y - 35)
            
            content_text = self.scene.addText(content)
            content_text.setDefaultTextColor(QColor("#1d1d1f"))
            content_text.setFont(QFont("Apple SD Gothic Neo", 11, QFont.Weight.Bold))
            content_bounds = content_text.boundingRect()
            content_text.setPos(x - content_bounds.width() / 2, y - 50)
        else:  # 노드가 아래에 있을 때
            date_text = self.scene.addText(date)
            date_text.setDefaultTextColor(QColor("#86868b"))
            date_text.setFont(QFont("Apple SD Gothic Neo", 10))
            date_bounds = date_text.boundingRect()
            date_text.setPos(x - date_bounds.width() / 2, y + 20)
            
            content_text = self.scene.addText(content)
            content_text.setDefaultTextColor(QColor("#1d1d1f"))
            content_text.setFont(QFont("Apple SD Gothic Neo", 11, QFont.Weight.Bold))
            content_bounds = content_text.boundingRect()
            content_text.setPos(x - content_bounds.width() / 2, y + 35)
        
        # 이모지 위치 계산
        emoji_x = x + 15
        
        # 첨부파일 아이콘 (QPushButton 사용)
        if attachment:
            attach_btn = QPushButton("📎")
            attach_btn.setFixedSize(24, 24)
            attach_btn.setStyleSheet("""
                QPushButton {
                    background: transparent;
                    border: none;
                    font-size: 16px;
                    padding: 0px;
                }
                QPushButton:hover {
                    background: rgba(0, 122, 255, 0.1);
                    border-radius: 4px;
                }
            """)
            attach_btn.setToolTip(f"파일: {attachment}")
            attach_btn.clicked.connect(lambda: self._open_attachment(attachment))
            
            attach_proxy = self.scene.addWidget(attach_btn)
            attach_proxy.setPos(emoji_x, y - 15)
            emoji_x += 26
        
        # 메모 아이콘 (QPushButton 사용)
        if memo:
            memo_btn = QPushButton("📝")
            memo_btn.setFixedSize(24, 24)
            memo_btn.setStyleSheet("""
                QPushButton {
                    background: transparent;
                    border: none;
                    font-size: 16px;
                    padding: 0px;
                }
                QPushButton:hover {
                    background: rgba(0, 122, 255, 0.1);
                    border-radius: 4px;
                }
            """)
            memo_btn.setToolTip("메모 보기")
            memo_btn.clicked.connect(lambda: self._show_memo(memo))
            
            memo_proxy = self.scene.addWidget(memo_btn)
            memo_proxy.setPos(emoji_x, y - 15)
        
        self.node_items[node_id] = node_item
    
    def _on_checkbox_changed(self, node_data: Dict, is_checked: bool):
        """체크박스 상태 변경"""
        if is_checked:
            self.selected_node_id = node_data.get("id")
            if self.on_node_click:
                self.on_node_click(node_data)
            
            # 다른 체크박스 해제
            for nid, checkbox in self.node_checkboxes.items():
                if nid != self.selected_node_id:
                    checkbox.setChecked(False)
        else:
            if self.selected_node_id == node_data.get("id"):
                self.selected_node_id = None
                if self.on_node_click:
                    self.on_node_click(None)
    
    def _open_attachment(self, attachment: str):
        """첨부파일 열기"""
        if attachment and os.path.exists(attachment):
            if platform.system() == 'Windows':
                os.startfile(attachment)  # type: ignore
            elif platform.system() == 'Darwin':
                os.system(f'open "{attachment}"')
            else:
                os.system(f'xdg-open "{attachment}"')
    
    def _show_memo(self, memo: str):
        """메모 다이얼로그 표시"""
        dialog = MemoDialog(self, memo)
        dialog.exec()
    
    def _get_star_path(self, cx: float, cy: float, r: float, points: int = 5) -> QPainterPath:
        """별 모양 경로 생성"""
        path = QPainterPath()
        angle = math.pi / 2
        d_angle = 2 * math.pi / (points * 2)
        
        first_point = True
        for i in range(points * 2):
            radius = r if i % 2 == 0 else r / 2
            x = cx + radius * math.cos(angle)
            y = cy - radius * math.sin(angle)
            
            if first_point:
                path.moveTo(x, y)
                first_point = False
            else:
                path.lineTo(x, y)
            
            angle += d_angle
        
        path.closeSubpath()
        return path


class ZoomableTimelineView(QGraphicsView):
    """Zoom/Pan 기능이 있는 타임라인 뷰"""
    
    def __init__(self, scene, parent=None):
        super().__init__(scene, parent)
        self.setRenderHint(QPainter.RenderHint.Antialiasing)
        self.setDragMode(QGraphicsView.DragMode.ScrollHandDrag)  # 드래그로 이동
        self.setTransformationAnchor(QGraphicsView.ViewportAnchor.AnchorUnderMouse)
        self.current_scale = 1.0
        
        self.setStyleSheet("""
            QGraphicsView {
                background: #fafafa;
                border: 1px solid #e8e8ed;
            }
        """)
    
    def wheelEvent(self, event):
        """마우스 휠로 줌 인/아웃"""
        # 줌 팩터 계산
        zoom_in_factor = 1.15
        zoom_out_factor = 1 / zoom_in_factor
        
        # 휠 방향에 따라 줌
        if event.angleDelta().y() > 0:
            zoom_factor = zoom_in_factor
            self.current_scale *= zoom_factor
        else:
            zoom_factor = zoom_out_factor
            self.current_scale *= zoom_factor
        
        # 줌 제한 (50% ~ 300%)
        if self.current_scale < 0.5:
            self.current_scale = 0.5
            return
        if self.current_scale > 3.0:
            self.current_scale = 3.0
            return
        
        self.scale(zoom_factor, zoom_factor)
    
    def zoom_in(self):
        """확대"""
        zoom_factor = 1.25
        self.current_scale *= zoom_factor
        if self.current_scale > 3.0:
            self.current_scale = 3.0
            self.resetTransform()
            self.scale(self.current_scale, self.current_scale)
            return
        self.scale(zoom_factor, zoom_factor)
    
    def zoom_out(self):
        """축소"""
        zoom_factor = 0.8
        self.current_scale *= zoom_factor
        if self.current_scale < 0.5:
            self.current_scale = 0.5
            self.resetTransform()
            self.scale(self.current_scale, self.current_scale)
            return
        self.scale(zoom_factor, zoom_factor)
    
    def fit_in_view(self):
        """전체 보기"""
        self.fitInView(self.sceneRect(), Qt.AspectRatioMode.KeepAspectRatio)
        self.current_scale = self.transform().m11()
