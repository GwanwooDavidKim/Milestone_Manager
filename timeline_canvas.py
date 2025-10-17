"""타임라인 캔버스 모듈 - 라이트 모드 타임라인과 노드 시각화"""

from PyQt6.QtWidgets import QWidget, QGraphicsScene, QGraphicsView, QGraphicsEllipseItem, QGraphicsPolygonItem, QGraphicsTextItem, QGraphicsRectItem, QGraphicsPathItem, QCheckBox, QGraphicsProxyWidget
from PyQt6.QtCore import Qt, QPointF, QRectF
from PyQt6.QtGui import QPen, QBrush, QColor, QPainter, QPolygonF, QPainterPath, QFont
from typing import List, Dict, Optional, Tuple
import math
import os
import platform


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
        """타임라인과 노드를 그립니다 - 연도별 균등 배치"""
        self.scene.clear()
        self.node_items.clear()
        self.node_checkboxes.clear()
        
        width = self.width() - 100
        height = self.height()
        
        if width < 100 or height < 100:
            return
        
        nodes = self.milestone_data.get("nodes", [])
        if not nodes:
            no_data_text = self.scene.addText("노드가 없습니다. 'Node 추가' 버튼을 눌러 이벤트를 추가하세요.")
            no_data_text.setDefaultTextColor(QColor("#86868b"))
            no_data_text.setFont(QFont("Apple SD Gothic Neo", 14))
            no_data_text.setPos(width/2 - 200, height/2 - 20)
            return
        
        sorted_nodes = sorted(nodes, key=lambda n: self._parse_date(n.get("date", "")))
        
        # 연도 추출 (간단하게)
        years = set()
        for node in sorted_nodes:
            date_val = self._parse_date(node.get("date", ""))
            year = date_val // 100
            years.add(year)
        
        years = sorted(list(years))
        
        if not years:
            return
        
        timeline_y = height / 2
        start_x = 80
        end_x = width - 20
        timeline_width = end_x - start_x
        
        # 타임라인 막대 (파란색)
        gradient_rect = self.scene.addRect(
            start_x - 5, timeline_y - 3,
            timeline_width + 10, 6
        )
        gradient_rect.setPen(QPen(Qt.PenStyle.NoPen))
        gradient_rect.setBrush(QBrush(QColor("#007AFF")))
        
        # 연도별 균등 간격 계산
        num_years = len(years)
        year_spacing = timeline_width / num_years if num_years > 1 else timeline_width
        
        # 각 연도에 대해 분기별 눈금 그리기
        for i, year in enumerate(years):
            year_x = start_x + (i * year_spacing)
            
            # 각 분기별 위치 계산
            for quarter in [1, 2, 3, 4]:
                # 분기를 년도 내에서 균등하게 배치
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
            
            # 월별 작은 눈금 (각 연도 내에서 12개월 균등 배치)
            for month in range(1, 13):
                if month not in [3, 6, 9, 12]:  # 분기 시작 월 제외
                    month_offset = (month - 1) * (year_spacing / 12)
                    x_pos = year_x + month_offset
                    tick_line = self.scene.addLine(x_pos, timeline_y - 10, x_pos, timeline_y + 10)
                    tick_line.setPen(QPen(QColor("#d2d2d7"), 1))
        
        # 노드 위치 계산
        node_positions = self._calculate_node_positions(sorted_nodes, years, year_spacing, 
                                                         start_x, timeline_y)
        
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
        """노드 위치 계산 - 연도 기반"""
        layout = []
        occupied_positions = []
        
        for i, node in enumerate(nodes):
            date = node.get("date", "")
            date_val = self._parse_date(date)
            year = date_val // 100
            month = date_val % 100
            
            # 연도 인덱스 찾기
            if year in years:
                year_idx = years.index(year)
                # 연도 시작 위치 + 월별 오프셋
                year_x = start_x + (year_idx * year_spacing)
                month_offset = (month - 1) * (year_spacing / 12)
                x_pos = year_x + month_offset
            else:
                x_pos = start_x
            
            # 마일스톤 근처에 배치
            y_offset = 0
            alternating = i % 2
            base_distance = 50
            
            # 겹침 체크
            for occupied_x, occupied_y in occupied_positions:
                if abs(occupied_x - x_pos) < 80:
                    y_offset = max(y_offset, abs(occupied_y - timeline_y) - base_distance + 40)
            
            if alternating == 0:
                y_pos = timeline_y - base_distance - y_offset
            else:
                y_pos = timeline_y + base_distance + y_offset
            
            layout.append((node, x_pos, y_pos))
            occupied_positions.append((x_pos, y_pos))
        
        return layout
    
    def _draw_node(self, node_data: Dict, x: float, y: float, timeline_y: float):
        """노드를 그립니다 - 체크박스 포함"""
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
        
        if node_item:
            tooltip_text = memo if memo else content
            node_item.setToolTip(tooltip_text)
        
        # 체크박스 추가 (노드 왼쪽)
        checkbox = QCheckBox()
        checkbox.setStyleSheet("""
            QCheckBox::indicator {
                width: 18px;
                height: 18px;
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
        checkbox_proxy.setPos(x - 35, y - 10)
        self.node_checkboxes[node_id] = checkbox
        
        # 날짜와 내용 텍스트
        if y < timeline_y:  # 노드가 위에 있을 때
            # 날짜 (노드 바로 위)
            date_text = self.scene.addText(date)
            date_text.setDefaultTextColor(QColor("#86868b"))
            date_text.setFont(QFont("Apple SD Gothic Neo", 10))
            date_bounds = date_text.boundingRect()
            date_text.setPos(x - date_bounds.width() / 2, y - 35)
            
            # 내용 (날짜 위)
            content_text = self.scene.addText(content)
            content_text.setDefaultTextColor(QColor("#1d1d1f"))
            content_text.setFont(QFont("Apple SD Gothic Neo", 11, QFont.Weight.Bold))
            content_bounds = content_text.boundingRect()
            content_text.setPos(x - content_bounds.width() / 2, y - 50)
        else:  # 노드가 아래에 있을 때
            # 날짜 (노드 바로 아래)
            date_text = self.scene.addText(date)
            date_text.setDefaultTextColor(QColor("#86868b"))
            date_text.setFont(QFont("Apple SD Gothic Neo", 10))
            date_bounds = date_text.boundingRect()
            date_text.setPos(x - date_bounds.width() / 2, y + 20)
            
            # 내용 (날짜 아래)
            content_text = self.scene.addText(content)
            content_text.setDefaultTextColor(QColor("#1d1d1f"))
            content_text.setFont(QFont("Apple SD Gothic Neo", 11, QFont.Weight.Bold))
            content_bounds = content_text.boundingRect()
            content_text.setPos(x - content_bounds.width() / 2, y + 35)
        
        # 첨부파일 아이콘
        if attachment:
            attach_text = self.scene.addText("📎")
            attach_text.setFont(QFont("Apple Color Emoji", 12))
            attach_text.setPos(x + 15, y - 15)
            attach_text.setToolTip(f"파일: {attachment}")
            
            # 첨부파일 클릭 가능하게
            attach_text.setFlag(QGraphicsTextItem.GraphicsItemFlag.ItemIsSelectable)
            attach_text.mousePressEvent = lambda event: self._open_attachment(attachment)
        
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
