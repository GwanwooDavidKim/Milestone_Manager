"""커스텀 위젯 모듈 - 라이트 모드 다이얼로그"""

from PyQt6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLabel, 
                              QLineEdit, QPushButton, QComboBox, QTextEdit,
                              QFileDialog, QColorDialog, QMessageBox)
from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtGui import QColor
from typing import Optional, Dict
import re


class ModernDialog(QDialog):
    """라이트 모드 현대적인 다이얼로그 베이스 클래스"""
    
    def __init__(self, parent=None, title: str = ""):
        super().__init__(parent)
        self.setWindowTitle(title)
        self.setModal(True)
        self.setStyleSheet("""
            QDialog {
                background: white;
                border: 1px solid #d2d2d7;
                border-radius: 12px;
            }
            QLabel {
                color: #1d1d1f;
                font-size: 14px;
            }
            QLineEdit, QTextEdit {
                background-color: white;
                border: 1px solid #d2d2d7;
                border-radius: 8px;
                padding: 12px;
                color: #1d1d1f;
                font-size: 14px;
                min-height: 24px;
            }
            QLineEdit:focus, QTextEdit:focus {
                border: 2px solid #007AFF;
            }
            QPushButton {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #007AFF, stop:1 #0051D5);
                border: none;
                border-radius: 8px;
                color: white;
                padding: 10px 20px;
                font-size: 14px;
                font-weight: bold;
            }
            QPushButton:hover {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #1A8CFF, stop:1 #0062E6);
            }
            QPushButton:pressed {
                background: #0051D5;
            }
            QPushButton#secondary {
                background: #e8e8ed;
                color: #1d1d1f;
                border: 1px solid #d2d2d7;
            }
            QPushButton#secondary:hover {
                background: #d2d2d7;
            }
            QComboBox {
                background-color: white;
                border: 1px solid #d2d2d7;
                border-radius: 8px;
                padding: 8px 12px;
                color: #1d1d1f;
                font-size: 14px;
            }
            QComboBox:focus {
                border: 2px solid #007AFF;
            }
            QComboBox::drop-down {
                border: none;
            }
            QComboBox QAbstractItemView {
                background-color: white;
                border: 1px solid #d2d2d7;
                selection-background-color: #007AFF;
                color: #1d1d1f;
            }
        """)


class MilestoneDialog(ModernDialog):
    """마일스톤 생성/수정 다이얼로그"""
    
    def __init__(self, parent=None, milestone_data: Optional[Dict] = None):
        super().__init__(parent, "마일스톤 생성" if not milestone_data else "마일스톤 수정")
        self.setFixedSize(500, 300)
        self.result = None
        
        layout = QVBoxLayout()
        layout.setSpacing(10)
        layout.setContentsMargins(30, 30, 30, 30)
        
        title_label = QLabel("제목")
        title_label.setStyleSheet("margin-top: 5px;")
        layout.addWidget(title_label)
        self.title_input = QLineEdit()
        self.title_input.setPlaceholderText("마일스톤 제목을 입력하세요")
        self.title_input.setMinimumHeight(45)
        if milestone_data:
            self.title_input.setText(milestone_data.get("title", ""))
        layout.addWidget(self.title_input)
        
        subtitle_label = QLabel("부제목")
        subtitle_label.setStyleSheet("margin-top: 15px;")
        layout.addWidget(subtitle_label)
        self.subtitle_input = QLineEdit()
        self.subtitle_input.setPlaceholderText("부제목을 입력하세요 (선택사항)")
        self.subtitle_input.setMinimumHeight(45)
        if milestone_data:
            self.subtitle_input.setText(milestone_data.get("subtitle", ""))
        layout.addWidget(self.subtitle_input)
        
        layout.addSpacing(20)  # 버튼과 간격 추가
        
        btn_layout = QHBoxLayout()
        btn_layout.addStretch()
        
        cancel_btn = QPushButton("취소")
        cancel_btn.setObjectName("secondary")
        cancel_btn.setFixedWidth(100)
        cancel_btn.clicked.connect(self.reject)
        btn_layout.addWidget(cancel_btn)
        
        ok_btn = QPushButton("확인")
        ok_btn.setFixedWidth(100)
        ok_btn.setDefault(True)  # 엔터키로 클릭 가능
        ok_btn.clicked.connect(self._on_confirm)
        btn_layout.addWidget(ok_btn)
        
        layout.addLayout(btn_layout)
        self.setLayout(layout)
    
    def _on_confirm(self):
        title = self.title_input.text().strip()
        if not title:
            return
        self.result = {
            "title": title,
            "subtitle": self.subtitle_input.text().strip()
        }
        self.accept()


class NodeDialog(ModernDialog):
    """노드 생성/수정 다이얼로그 - 날짜 양식 검증 추가"""
    
    SHAPES = ["●(동그라미)", "▲(세모)", "■(네모)", "★(별)", "◆(마름모)"]
    
    def __init__(self, parent=None, node_data: Optional[Dict] = None):
        super().__init__(parent, "노드 추가" if not node_data else "노드 수정")
        self.setFixedSize(550, 650)
        self.result = None
        self.selected_color = node_data.get("color", "#FF6B6B") if node_data else "#FF6B6B"
        self.attached_file = node_data.get("attachment", "") if node_data else ""
        
        layout = QVBoxLayout()
        layout.setSpacing(12)
        layout.setContentsMargins(30, 30, 30, 30)
        
        layout.addWidget(QLabel("모양"))
        self.shape_combo = QComboBox()
        self.shape_combo.addItems(self.SHAPES)
        if node_data:
            idx = self.SHAPES.index(node_data.get("shape", self.SHAPES[0]))
            self.shape_combo.setCurrentIndex(idx)
        layout.addWidget(self.shape_combo)
        
        layout.addWidget(QLabel("색상"))
        color_layout = QHBoxLayout()
        self.color_btn = QPushButton(f"선택된 색상: {self.selected_color}")
        self.color_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {self.selected_color};
                border: 2px solid #d2d2d7;
                border-radius: 8px;
                color: white;
                font-weight: bold;
            }}
        """)
        self.color_btn.clicked.connect(self._choose_color)
        color_layout.addWidget(self.color_btn)
        layout.addLayout(color_layout)
        
        layout.addWidget(QLabel("날짜 (YY.MM 또는 YY.Qn 형식만 허용)"))
        self.date_input = QLineEdit()
        self.date_input.setPlaceholderText("예: 24.10 또는 24.Q3")
        if node_data:
            self.date_input.setText(node_data.get("date", ""))
        layout.addWidget(self.date_input)
        
        layout.addWidget(QLabel("내용"))
        self.content_input = QLineEdit()
        self.content_input.setPlaceholderText("노드 옆에 표시될 텍스트")
        if node_data:
            self.content_input.setText(node_data.get("content", ""))
        layout.addWidget(self.content_input)
        
        layout.addWidget(QLabel("메모 (마우스 오버 시 툴팁으로 표시)"))
        self.memo_input = QTextEdit()
        self.memo_input.setPlaceholderText("상세 메모를 입력하세요")
        self.memo_input.setMaximumHeight(100)
        if node_data:
            self.memo_input.setPlainText(node_data.get("memo", ""))
        layout.addWidget(self.memo_input)
        
        layout.addWidget(QLabel("첨부 파일"))
        file_layout = QHBoxLayout()
        self.file_label = QLabel(self.attached_file if self.attached_file else "파일 없음")
        self.file_label.setStyleSheet("color: #86868b;")
        file_layout.addWidget(self.file_label, 1)
        file_btn = QPushButton("파일 선택")
        file_btn.setObjectName("secondary")
        file_btn.setFixedWidth(100)
        file_btn.clicked.connect(self._choose_file)
        file_layout.addWidget(file_btn)
        layout.addLayout(file_layout)
        
        btn_layout = QHBoxLayout()
        btn_layout.addStretch()
        
        cancel_btn = QPushButton("취소")
        cancel_btn.setObjectName("secondary")
        cancel_btn.setFixedWidth(100)
        cancel_btn.clicked.connect(self.reject)
        btn_layout.addWidget(cancel_btn)
        
        ok_btn = QPushButton("확인")
        ok_btn.setFixedWidth(100)
        ok_btn.setDefault(True)  # 엔터키로 클릭 가능
        ok_btn.clicked.connect(self._on_confirm)
        btn_layout.addWidget(ok_btn)
        
        layout.addLayout(btn_layout)
        self.setLayout(layout)
    
    def _choose_color(self):
        color = QColorDialog.getColor(QColor(self.selected_color), self)
        if color.isValid():
            self.selected_color = color.name()
            self.color_btn.setText(f"선택된 색상: {self.selected_color}")
            self.color_btn.setStyleSheet(f"""
                QPushButton {{
                    background-color: {self.selected_color};
                    border: 2px solid #d2d2d7;
                    border-radius: 8px;
                    color: white;
                    font-weight: bold;
                }}
            """)
    
    def _choose_file(self):
        filename, _ = QFileDialog.getOpenFileName(self, "파일 선택")
        if filename:
            self.attached_file = filename
            self.file_label.setText(filename)
    
    def _validate_date(self, date_str: str) -> bool:
        """날짜 양식 검증: YY.MM 또는 YY.Qn 형식만 허용"""
        date_str = date_str.strip().upper()
        
        # YY.Qn 형식 검증 (예: 24.Q1, 24.Q2)
        quarter_pattern = r'^\d{2}\.Q[1-4]$'
        if re.match(quarter_pattern, date_str):
            return True
        
        # YY.MM 형식 검증 (예: 24.10, 24.01)
        month_pattern = r'^\d{2}\.(0[1-9]|1[0-2]|\d)$'
        if re.match(month_pattern, date_str):
            return True
        
        return False
    
    def _on_confirm(self):
        date = self.date_input.text().strip()
        content = self.content_input.text().strip()
        
        if not date or not content:
            msg = QMessageBox(self)
            msg.setIcon(QMessageBox.Icon.Warning)
            msg.setWindowTitle("입력 오류")
            msg.setText("날짜와 내용을 모두 입력해주세요.")
            msg.setStyleSheet("""
                QMessageBox {
                    background-color: white;
                }
                QLabel {
                    color: #1d1d1f;
                    font-size: 14px;
                }
                QPushButton {
                    background-color: #007AFF;
                    color: white;
                    border: none;
                    border-radius: 6px;
                    padding: 8px 16px;
                    min-width: 80px;
                }
            """)
            msg.exec()
            return
        
        # 날짜 양식 검증
        if not self._validate_date(date):
            msg = QMessageBox(self)
            msg.setIcon(QMessageBox.Icon.Warning)
            msg.setWindowTitle("날짜 형식 오류")
            msg.setText("날짜는 YY.MM 또는 YY.Qn 형식으로 입력해주세요.\n\n예시:\n- 24.10 (2024년 10월)\n- 24.Q3 (2024년 3분기)")
            msg.setStyleSheet("""
                QMessageBox {
                    background-color: white;
                }
                QLabel {
                    color: #1d1d1f;
                    font-size: 14px;
                }
                QPushButton {
                    background-color: #007AFF;
                    color: white;
                    border: none;
                    border-radius: 6px;
                    padding: 8px 16px;
                    min-width: 80px;
                }
            """)
            msg.exec()
            return
        
        self.result = {
            "shape": self.shape_combo.currentText(),
            "color": self.selected_color,
            "date": date,
            "content": content,
            "memo": self.memo_input.toPlainText().strip(),
            "attachment": self.attached_file
        }
        self.accept()


class DateFilterDialog(ModernDialog):
    """날짜 필터 다이얼로그"""
    
    def __init__(self, parent=None):
        super().__init__(parent, "날짜 필터")
        self.setFixedSize(400, 250)
        self.result = None
        
        from datetime import datetime
        current_year = datetime.now().year
        
        layout = QVBoxLayout()
        layout.setSpacing(15)
        layout.setContentsMargins(30, 30, 30, 30)
        
        layout.addWidget(QLabel("년도 선택"))
        self.year_combo = QComboBox()
        # 현재 ±10년
        years = [str(year) for year in range(current_year - 10, current_year + 11)]
        self.year_combo.addItems(years)
        # 현재 년도를 기본값으로
        self.year_combo.setCurrentText(str(current_year))
        layout.addWidget(self.year_combo)
        
        layout.addWidget(QLabel("분기 선택"))
        self.quarter_combo = QComboBox()
        self.quarter_combo.addItems(["Q1 (1~3월)", "Q2 (4~6월)", "Q3 (7~9월)", "Q4 (10~12월)"])
        layout.addWidget(self.quarter_combo)
        
        btn_layout = QHBoxLayout()
        btn_layout.addStretch()
        
        cancel_btn = QPushButton("취소")
        cancel_btn.setObjectName("secondary")
        cancel_btn.setFixedWidth(100)
        cancel_btn.clicked.connect(self.reject)
        btn_layout.addWidget(cancel_btn)
        
        apply_btn = QPushButton("검색")
        apply_btn.setFixedWidth(100)
        apply_btn.setDefault(True)
        apply_btn.clicked.connect(self._on_apply)
        btn_layout.addWidget(apply_btn)
        
        layout.addLayout(btn_layout)
        self.setLayout(layout)
    
    def _on_apply(self):
        quarter_text = self.quarter_combo.currentText()
        quarter = int(quarter_text.split()[0][1])  # "Q1 (1~3월)" -> 1
        
        self.result = {
            "year": int(self.year_combo.currentText()),
            "quarter": quarter
        }
        self.accept()


class SearchFilterDialog(ModernDialog):
    """검색 및 필터 다이얼로그"""
    
    def __init__(self, parent=None):
        super().__init__(parent, "검색 및 필터")
        self.setFixedSize(450, 360)
        self.result = None
        
        layout = QVBoxLayout()
        layout.setSpacing(15)
        layout.setContentsMargins(30, 30, 30, 30)
        
        layout.addWidget(QLabel("제목, 부제목 검색"))
        self.keyword_input = QLineEdit()
        self.keyword_input.setPlaceholderText("제목, 부제목에서 검색")
        layout.addWidget(self.keyword_input)
        
        layout.addWidget(QLabel("내용 검색"))
        self.content_input = QLineEdit()
        self.content_input.setPlaceholderText("노드 내용에서 검색")
        layout.addWidget(self.content_input)
        
        layout.addWidget(QLabel("모양 필터"))
        self.shape_combo = QComboBox()
        self.shape_combo.addItems(["전체"] + NodeDialog.SHAPES)
        layout.addWidget(self.shape_combo)
        
        btn_layout = QHBoxLayout()
        btn_layout.addStretch()
        
        cancel_btn = QPushButton("취소")
        cancel_btn.setObjectName("secondary")
        cancel_btn.setFixedWidth(100)
        cancel_btn.clicked.connect(self.reject)
        btn_layout.addWidget(cancel_btn)
        
        apply_btn = QPushButton("적용")
        apply_btn.setFixedWidth(100)
        apply_btn.setDefault(True)  # 엔터키로 클릭 가능
        apply_btn.clicked.connect(self._on_apply)
        btn_layout.addWidget(apply_btn)
        
        layout.addLayout(btn_layout)
        self.setLayout(layout)
    
    def _on_apply(self):
        self.result = {
            "keyword": self.keyword_input.text().strip(),
            "content_keyword": self.content_input.text().strip(),
            "shape": None if self.shape_combo.currentText() == "전체" else self.shape_combo.currentText()
        }
        self.accept()


class ZoomableTimelineDialog(ModernDialog):
    """확대 가능한 타임라인 다이얼로그"""
    
    def __init__(self, parent=None, milestone_data: dict = None):
        super().__init__(parent, f"타임라인 확대 보기 - {milestone_data.get('title', '')}")
        self.setMinimumSize(1200, 700)
        self.milestone_data = milestone_data or {"nodes": []}
        
        from timeline_canvas import TimelineCanvas, ZoomableTimelineView
        
        layout = QVBoxLayout()
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(15)
        
        # 컨트롤 버튼
        control_layout = QHBoxLayout()
        
        zoom_in_btn = QPushButton("➕ 확대")
        zoom_in_btn.setObjectName("secondary")
        zoom_in_btn.setFixedWidth(100)
        zoom_in_btn.clicked.connect(self._zoom_in)
        control_layout.addWidget(zoom_in_btn)
        
        zoom_out_btn = QPushButton("➖ 축소")
        zoom_out_btn.setObjectName("secondary")
        zoom_out_btn.setFixedWidth(100)
        zoom_out_btn.clicked.connect(self._zoom_out)
        control_layout.addWidget(zoom_out_btn)
        
        fit_btn = QPushButton("⊡ 전체보기")
        fit_btn.setObjectName("secondary")
        fit_btn.setFixedWidth(120)
        fit_btn.clicked.connect(self._fit_in_view)
        control_layout.addWidget(fit_btn)
        
        control_layout.addStretch()
        
        info_label = QLabel("💡 마우스 휠로 확대/축소, 드래그로 이동")
        info_label.setStyleSheet("color: #86868b; font-size: 12px;")
        control_layout.addWidget(info_label)
        
        layout.addLayout(control_layout)
        
        # 타임라인 캔버스 생성 (확대 보기용)
        canvas = TimelineCanvas(self, milestone_data, None, is_zoomable=True)
        canvas.setFixedWidth(2400)
        canvas.draw_timeline()
        
        # ZoomableTimelineView로 표시
        self.zoom_view = ZoomableTimelineView(canvas.scene, self)
        self.zoom_view.setMinimumSize(1160, 500)
        layout.addWidget(self.zoom_view)
        
        # 닫기 버튼
        close_btn = QPushButton("닫기")
        close_btn.setFixedWidth(100)
        close_btn.clicked.connect(self.accept)
        
        btn_layout = QHBoxLayout()
        btn_layout.addStretch()
        btn_layout.addWidget(close_btn)
        layout.addLayout(btn_layout)
        
        self.setLayout(layout)
        
        # 초기에 전체보기
        QTimer.singleShot(100, self._fit_in_view)
    
    def _zoom_in(self):
        self.zoom_view.zoom_in()
    
    def _zoom_out(self):
        self.zoom_view.zoom_out()
    
    def _fit_in_view(self):
        self.zoom_view.fit_in_view()
