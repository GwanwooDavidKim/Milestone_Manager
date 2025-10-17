"""타임라인 캔버스 모듈 - 개선된 타임라인과 노드 시각화"""

from PyQt6.QtWidgets import QWidget, QGraphicsScene, QGraphicsView, QGraphicsEllipseItem, QGraphicsPolygonItem, QGraphicsTextItem, QGraphicsRectItem, QGraphicsPathItem
from PyQt6.QtCore import Qt, QPointF, QRectF
from PyQt6.QtGui import QPen, QBrush, QColor, QPainter, QPolygonF, QPainterPath, QFont
from typing import List, Dict, Optional, Tuple
import math
import os
import platform


class TimelineCanvas(QWidget):
    """개선된 타임라인 시각화 컴포넌트"""
    
    def __init__(self, parent=None, milestone_data: Dict = None, on_node_click=None):
        super().__init__(parent)
        self.milestone_data = milestone_data or {"nodes": []}
        self.on_node_click = on_node_click
        
        self.scene = QGraphicsScene()
        self.view = QGraphicsView(self.scene, self)
        self.view.setRenderHint(QPainter.RenderHint.Antialiasing)
        self.view.setStyleSheet("""
            QGraphicsView {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #1a1a1a, stop:1 #252525);
                border: none;
                border-radius: 8px;
            }
        """)
        
        self.view.setGeometry(0, 0, self.width(), self.height())
        self.node_items = {}
        
        self.draw_timeline()
    
    def resizeEvent(self, event):
        self.view.setGeometry(0, 0, self.width(), self.height())
        self.draw_timeline()
    
    def draw_timeline(self):
        """타임라인과 노드를 그립니다 - 개선된 버전"""
        self.scene.clear()
        self.node_items.clear()
        
        width = self.width() - 100
        height = self.height()
        
        if width < 100 or height < 100:
            return
        
        nodes = self.milestone_data.get("nodes", [])
        if not nodes:
            no_data_text = self.scene.addText("노드가 없습니다. 'Node 추가' 버튼을 눌러 이벤트를 추가하세요.")
            no_data_text.setDefaultTextColor(QColor("#666666"))
            no_data_text.setFont(QFont("Apple SD Gothic Neo", 14))
            no_data_text.setPos(width/2 - 200, height/2 - 20)
            return
        
        sorted_nodes = sorted(nodes, key=lambda n: self._parse_date(n.get("date", "")))
        
        min_date = self._parse_date(sorted_nodes[0].get("date", ""))
        max_date = self._parse_date(sorted_nodes[-1].get("date", ""))
        
        start_date = min_date - 12
        end_date = max_date + 12
        
        timeline_y = height / 2
        start_x = 80
        end_x = width - 20
        timeline_width = end_x - start_x
        
        gradient_rect = self.scene.addRect(
            start_x - 5, timeline_y - 3,
            timeline_width + 10, 6
        )
        gradient_rect.setPen(QPen(Qt.PenStyle.NoPen))
        gradient_rect.setBrush(QBrush(QColor("#4A9EFF")))
        
        date_range = end_date - start_date
        
        for date_val in range(start_date, end_date + 1):
            if date_val % 12 == 0:
                year = date_val // 100
                x_pos = start_x + ((date_val - start_date) / date_range) * timeline_width
                
                tick_line = self.scene.addLine(x_pos, timeline_y - 15, x_pos, timeline_y + 15)
                tick_line.setPen(QPen(QColor("#666666"), 2))
                
                year_text = self.scene.addText(f"{year:02d}")
                year_text.setDefaultTextColor(QColor("#999999"))
                year_text.setFont(QFont("Apple SD Gothic Neo", 11))
                year_text.setPos(x_pos - 15, timeline_y - 40)
            
            elif date_val % 3 == 0:
                x_pos = start_x + ((date_val - start_date) / date_range) * timeline_width
                tick_line = self.scene.addLine(x_pos, timeline_y - 8, x_pos, timeline_y + 8)
                tick_line.setPen(QPen(QColor("#444444"), 1))
        
        node_positions = self._calculate_node_positions(sorted_nodes, start_date, end_date, 
                                                         start_x, timeline_width, timeline_y)
        
        for node_data, x, y in node_positions:
            self._draw_node(node_data, x, y, timeline_y)
    
    def _parse_date(self, date_str: str) -> int:
        """날짜 문자열을 숫자로 변환"""
        if "Q" in date_str.upper():
            parts = date_str.upper().split("Q")
            if len(parts) == 2:
                year = int(parts[0]) if parts[0].isdigit() else 20
                quarter = int(parts[1]) if parts[1].isdigit() else 1
                return year * 100 + quarter * 3
        else:
            parts = date_str.split(".")
            if len(parts) == 2:
                year = int(parts[0]) if parts[0].isdigit() else 20
                month = int(parts[1]) if parts[1].isdigit() else 1
                return year * 100 + month
        return 2000
    
    def _calculate_node_positions(self, nodes: List[Dict], start_date: int, end_date: int,
                                   start_x: float, timeline_width: float, timeline_y: float) -> List[Tuple]:
        """노드 위치 계산 - 겹침 방지"""
        layout = []
        date_range = end_date - start_date
        occupied_positions = []
        
        for i, node in enumerate(nodes):
            date = node.get("date", "")
            date_val = self._parse_date(date)
            
            x_pos = start_x + ((date_val - start_date) / date_range) * timeline_width
            
            y_offset = 0
            alternating = i % 2
            
            for occupied_x, occupied_y in occupied_positions:
                if abs(occupied_x - x_pos) < 120:
                    y_offset = max(y_offset, abs(occupied_y - timeline_y) + 60)
            
            if alternating == 0:
                y_pos = timeline_y - 80 - y_offset
            else:
                y_pos = timeline_y + 80 + y_offset
            
            layout.append((node, x_pos, y_pos))
            occupied_positions.append((x_pos, y_pos))
        
        return layout
    
    def _draw_node(self, node_data: Dict, x: float, y: float, timeline_y: float):
        """노드를 그립니다"""
        shape = node_data.get("shape", "●(동그라미)")
        color = QColor(node_data.get("color", "#FF6B6B"))
        content = node_data.get("content", "")
        memo = node_data.get("memo", "")
        attachment = node_data.get("attachment", "")
        
        connector_line = self.scene.addLine(x, timeline_y, x, y)
        connector_line.setPen(QPen(QColor("#555555"), 1, Qt.PenStyle.DashLine))
        
        node_item = None
        
        if "●" in shape or "동그라미" in shape:
            node_item = self.scene.addEllipse(x - 15, y - 15, 30, 30)
            node_item.setBrush(QBrush(color))
            node_item.setPen(QPen(QColor("white"), 3))
        
        elif "▲" in shape or "세모" in shape:
            polygon = QPolygonF([
                QPointF(x, y - 18),
                QPointF(x - 15, y + 12),
                QPointF(x + 15, y + 12)
            ])
            node_item = self.scene.addPolygon(polygon)
            node_item.setBrush(QBrush(color))
            node_item.setPen(QPen(QColor("white"), 3))
        
        elif "■" in shape or "네모" in shape:
            node_item = self.scene.addRect(x - 15, y - 15, 30, 30)
            node_item.setBrush(QBrush(color))
            node_item.setPen(QPen(QColor("white"), 3))
        
        elif "★" in shape or "별" in shape:
            star_path = self._get_star_path(x, y, 18, 5)
            node_item = self.scene.addPath(star_path)
            node_item.setBrush(QBrush(color))
            node_item.setPen(QPen(QColor("white"), 3))
        
        else:
            polygon = QPolygonF([
                QPointF(x, y - 15),
                QPointF(x + 15, y),
                QPointF(x, y + 15),
                QPointF(x - 15, y)
            ])
            node_item = self.scene.addPolygon(polygon)
            node_item.setBrush(QBrush(color))
            node_item.setPen(QPen(QColor("white"), 3))
        
        if node_item:
            node_item.setToolTip(memo if memo else content)
            node_item.setFlag(QGraphicsEllipseItem.GraphicsItemFlag.ItemIsSelectable)
        
        text_y = y - 35 if y < timeline_y else y + 25
        text_item = self.scene.addText(content)
        text_item.setDefaultTextColor(QColor("white"))
        text_item.setFont(QFont("Apple SD Gothic Neo", 12, QFont.Weight.Bold))
        text_bounds = text_item.boundingRect()
        text_item.setPos(x - text_bounds.width() / 2, text_y)
        
        if attachment:
            attach_text = self.scene.addText("📎")
            attach_text.setFont(QFont("Apple Color Emoji", 14))
            attach_text.setPos(x + 18, y - 20)
            attach_text.setToolTip(f"파일: {attachment}")
        
        self.node_items[node_data.get("id", "")] = node_item
    
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
    
    def mousePressEvent(self, event):
        """마우스 클릭 이벤트"""
        scene_pos = self.view.mapToScene(event.pos())
        item = self.scene.itemAt(scene_pos, self.view.transform())
        
        for node_id, node_item in self.node_items.items():
            if item == node_item:
                for node in self.milestone_data.get("nodes", []):
                    if node.get("id") == node_id:
                        if self.on_node_click:
                            self.on_node_click(node)
                        
                        attachment = node.get("attachment", "")
                        if attachment and os.path.exists(attachment):
                            if platform.system() == 'Windows':
                                os.startfile(attachment)  # type: ignore
                            elif platform.system() == 'Darwin':
                                os.system(f'open "{attachment}"')
                            else:
                                os.system(f'xdg-open "{attachment}"')
                        break
                break
