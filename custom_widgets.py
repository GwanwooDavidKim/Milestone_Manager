"""커스텀 위젯 모듈 - 라이트 모드 다이얼로그"""

from PyQt6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QGridLayout, QLabel, 
                              QLineEdit, QPushButton, QComboBox, QTextEdit,
                              QFileDialog, QColorDialog, QMessageBox, QWidget,
                              QCheckBox, QScrollArea, QInputDialog, QFrame)
from PyQt6.QtCore import Qt, QTimer, pyqtSignal
from PyQt6.QtGui import QColor, QFont
from typing import Optional, Dict, List
import re
from datetime import datetime


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
        self.setFixedSize(500, 380)
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
        
        category_label = QLabel("카테고리")
        category_label.setStyleSheet("margin-top: 15px;")
        layout.addWidget(category_label)
        self.category_input = QLineEdit()
        self.category_input.setPlaceholderText("카테고리를 입력하세요 (선택사항)")
        self.category_input.setMinimumHeight(45)
        if milestone_data:
            self.category_input.setText(milestone_data.get("category", ""))
        layout.addWidget(self.category_input)
        
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
            "subtitle": self.subtitle_input.text().strip(),
            "category": self.category_input.text().strip()
        }
        self.accept()


class NodeDialog(ModernDialog):
    """노드 생성/수정 다이얼로그 - 날짜 양식 검증 추가"""
    
    SHAPES = ["●(동그라미)", "▲(세모)", "■(네모)", "★(별)", "◆(마름모)"]
    
    def __init__(self, parent=None, node_data: Optional[Dict] = None):
        super().__init__(parent, "노드 추가" if not node_data else "노드 수정")
        self.setFixedSize(550, 800)
        self.result = None
        self.selected_color = node_data.get("color", "#FF6B6B") if node_data else "#FF6B6B"
        self.selected_color2 = node_data.get("color2", "") if node_data else ""
        self.attached_file = node_data.get("attachment", "") if node_data else ""
        
        layout = QVBoxLayout()
        layout.setSpacing(12)
        layout.setContentsMargins(30, 30, 30, 30)
        
        layout.addWidget(QLabel("모양 1 (필수)"))
        self.shape_combo = QComboBox()
        self.shape_combo.addItems(self.SHAPES)
        if node_data:
            idx = self.SHAPES.index(node_data.get("shape", self.SHAPES[0]))
            self.shape_combo.setCurrentIndex(idx)
        layout.addWidget(self.shape_combo)
        
        layout.addWidget(QLabel("색상 1 (필수)"))
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
        
        # 두 번째 모양/색상 (선택사항)
        layout.addWidget(QLabel("모양 2 (선택사항 - 같은 날짜에 여러 항목 구분용)"))
        self.shape_combo2 = QComboBox()
        self.shape_combo2.addItem("없음")
        self.shape_combo2.addItems(self.SHAPES)
        if node_data and node_data.get("shape2"):
            idx = self.SHAPES.index(node_data.get("shape2", self.SHAPES[0]))
            self.shape_combo2.setCurrentIndex(idx + 1)  # +1은 "없음" 때문
        layout.addWidget(self.shape_combo2)
        
        layout.addWidget(QLabel("색상 2 (선택사항)"))
        color_layout2 = QHBoxLayout()
        self.color_btn2 = QPushButton(f"선택된 색상: {self.selected_color2 if self.selected_color2 else '없음'}")
        if self.selected_color2:
            self.color_btn2.setStyleSheet(f"""
                QPushButton {{
                    background-color: {self.selected_color2};
                    border: 2px solid #d2d2d7;
                    border-radius: 8px;
                    color: white;
                    font-weight: bold;
                }}
            """)
        else:
            self.color_btn2.setStyleSheet("""
                QPushButton {
                    background-color: #e8e8ed;
                    border: 2px solid #d2d2d7;
                    border-radius: 8px;
                    color: #1d1d1f;
                    font-weight: bold;
                }
            """)
        self.color_btn2.clicked.connect(self._choose_color2)
        color_layout2.addWidget(self.color_btn2)
        layout.addLayout(color_layout2)
        
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
    
    def _choose_color2(self):
        initial_color = QColor(self.selected_color2) if self.selected_color2 else QColor("#4A90E2")
        color = QColorDialog.getColor(initial_color, self)
        if color.isValid():
            self.selected_color2 = color.name()
            self.color_btn2.setText(f"선택된 색상: {self.selected_color2}")
            self.color_btn2.setStyleSheet(f"""
                QPushButton {{
                    background-color: {self.selected_color2};
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
        
        # 두 번째 모양/색상 처리
        shape2 = self.shape_combo2.currentText()
        if shape2 == "없음":
            shape2 = ""
            color2 = ""
        else:
            color2 = self.selected_color2
        
        self.result = {
            "shape": self.shape_combo.currentText(),
            "color": self.selected_color,
            "shape2": shape2,
            "color2": color2,
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


class ClickableKeywordFrame(QFrame):
    """클릭 가능한 키워드 프레임 - Custom State Pattern"""
    
    clicked = pyqtSignal(str)  # 클릭 시그널
    
    def __init__(self, keyword: str, parent=None):
        super().__init__(parent)
        self.keyword = keyword
        self.is_selected = False
        
        # 프레임 ID 설정 (스타일시트 selector용)
        self.setObjectName("keyword_frame")
        self.setFrameShape(QFrame.Shape.StyledPanel)
        
        # 레이아웃 설정
        layout = QHBoxLayout()
        layout.setContentsMargins(8, 6, 8, 6)
        
        # 체크박스 (시각적 표시만, 클릭 불가)
        self.checkbox = QCheckBox()
        self.checkbox.setEnabled(False)  # 클릭 불가능하게 설정
        layout.addWidget(self.checkbox)
        
        # 키워드 레이블
        self.label = QLabel(keyword)
        layout.addWidget(self.label)
        layout.addStretch()
        
        self.setLayout(layout)
        
        # 초기 스타일 적용 (_update_style에서 모든 스타일 설정)
        self._update_style()
        
        # 마우스 커서 변경
        self.setCursor(Qt.CursorShape.PointingHandCursor)
    
    def set_selected(self, selected: bool):
        """선택 상태 설정"""
        self.is_selected = selected
        self.checkbox.setChecked(selected)
        self._update_style()
    
    def toggle_selected(self):
        """선택 상태 토글"""
        self.set_selected(not self.is_selected)
    
    def _update_style(self):
        """스타일 업데이트 - 직접 스타일 지정 (selector 없이)"""
        if self.is_selected:
            # 선택됨: 연두색 배경 + 굵은 테두리
            self.setStyleSheet("""
                background-color: #D4EDDA;
                border: 2px solid #34C759;
                border-radius: 4px;
            """)
            # 체크박스 별도 설정
            self.checkbox.setStyleSheet("""
                QCheckBox {
                    spacing: 0px;
                }
                QCheckBox::indicator {
                    width: 16px;
                    height: 16px;
                    border-radius: 4px;
                    border: 2px solid #d2d2d7;
                    background: white;
                }
                QCheckBox::indicator:checked {
                    background: #34C759;
                    border: 2px solid #34C759;
                }
                QCheckBox::indicator:disabled {
                    opacity: 1.0;
                }
            """)
            # 레이블 별도 설정
            self.label.setStyleSheet("""
                color: #1d1d1f;
                font-size: 12px;
                border: none;
                background: transparent;
            """)
        else:
            # 선택 안됨: 회색 배경 + 얇은 테두리
            self.setStyleSheet("""
                background-color: #f9f9f9;
                border: 1px solid #e8e8ed;
                border-radius: 4px;
            """)
            # 체크박스 별도 설정
            self.checkbox.setStyleSheet("""
                QCheckBox {
                    spacing: 0px;
                }
                QCheckBox::indicator {
                    width: 16px;
                    height: 16px;
                    border-radius: 4px;
                    border: 2px solid #d2d2d7;
                    background: white;
                }
                QCheckBox::indicator:checked {
                    background: #34C759;
                    border: 2px solid #34C759;
                }
                QCheckBox::indicator:disabled {
                    opacity: 1.0;
                }
            """)
            # 레이블 별도 설정
            self.label.setStyleSheet("""
                color: #1d1d1f;
                font-size: 12px;
                border: none;
                background: transparent;
            """)
    
    def mousePressEvent(self, event):
        """마우스 클릭 이벤트 - 프레임 전체 클릭"""
        if event.button() == Qt.MouseButton.LeftButton:
            self.toggle_selected()
            self.clicked.emit(self.keyword)
        super().mousePressEvent(event)


class KeywordBlock(QWidget):
    """키워드 필터링 Block 위젯"""
    
    keywords_changed = pyqtSignal(list)  # 선택된 키워드 변경 시그널
    
    def __init__(self, parent=None, data_manager=None):
        super().__init__(parent)
        self.data_manager = data_manager
        self.keyword_checkboxes = {}
        
        self.setStyleSheet("""
            QWidget {
                background: white;
                border: 1px solid #d2d2d7;
                border-radius: 8px;
            }
            QPushButton {
                background: #007AFF;
                border: none;
                border-radius: 6px;
                color: white;
                padding: 8px 16px;
                font-size: 11px;
                font-weight: bold;
            }
            QPushButton:hover {
                background: #1A8CFF;
            }
            QPushButton#delete {
                background: #FF3B30;
            }
            QPushButton#delete:hover {
                background: #FF4D42;
            }
            QCheckBox {
                color: #1d1d1f;
                font-size: 12px;
                spacing: 8px;
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
        """)
        
        layout = QVBoxLayout()
        layout.setContentsMargins(15, 15, 15, 15)
        layout.setSpacing(10)
        
        # 제목
        title_label = QLabel("📌 키워드 필터")
        title_label.setStyleSheet("font-size: 15px; font-weight: bold; color: #1d1d1f; border: none;")
        layout.addWidget(title_label)
        
        # 버튼 영역
        btn_layout = QHBoxLayout()
        add_btn = QPushButton("+ 추가")
        add_btn.clicked.connect(self._add_keyword)
        btn_layout.addWidget(add_btn)
        
        delete_btn = QPushButton("- 삭제")
        delete_btn.setObjectName("delete")
        delete_btn.clicked.connect(self._delete_selected_keywords)
        btn_layout.addWidget(delete_btn)
        
        layout.addLayout(btn_layout)
        
        # 스크롤 영역
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setStyleSheet("QScrollArea { border: none; background: transparent; }")
        
        self.keyword_container = QWidget()
        self.keyword_layout = QVBoxLayout()
        self.keyword_layout.setSpacing(8)
        self.keyword_layout.setContentsMargins(5, 5, 5, 5)
        self.keyword_container.setLayout(self.keyword_layout)
        self.keyword_container.setStyleSheet("background: transparent; border: none;")
        
        scroll_area.setWidget(self.keyword_container)
        layout.addWidget(scroll_area)
        
        self.setLayout(layout)
        self.load_keywords()
    
    def load_keywords(self):
        """키워드 목록 불러오기 - 선택 상태 보존"""
        if not self.data_manager:
            return
        
        # ✅ 기존 선택 상태 저장
        selected_keywords = set()
        for kw, frame in self.keyword_checkboxes.items():
            if frame.is_selected:
                selected_keywords.add(kw)        
        # 기존 위젯 제거
        for i in reversed(range(self.keyword_layout.count())):
            item = self.keyword_layout.itemAt(i)
            if item.widget():
                item.widget().deleteLater()
        
        self.keyword_checkboxes.clear()
        
        keywords = self.data_manager.get_keywords()
        for keyword in keywords:
            # 키워드 아이템을 담을 클릭 가능한 컨테이너
            item_frame = ClickableKeywordFrame(keyword)
            
            # ✅ 선택 상태 복원
            if keyword in selected_keywords:
                item_frame.set_selected(True)            
            # 클릭 시 선택된 키워드 목록 업데이트 및 필터 적용
            item_frame.clicked.connect(lambda kw=keyword: self._emit_selected_keywords())
            
            self.keyword_layout.addWidget(item_frame)
            self.keyword_checkboxes[keyword] = item_frame
    
    def _add_keyword(self):
        """키워드 추가"""
        text, ok = QInputDialog.getText(self, "키워드 추가", "")
        if ok and text.strip():
            keyword = text.strip()
            if keyword not in self.keyword_checkboxes:
                self.data_manager.add_keyword(keyword)
                self.load_keywords()
                self._emit_selected_keywords()
    
    def _delete_selected_keywords(self):
        """선택된 키워드 삭제"""
        selected = [kw for kw, frame in self.keyword_checkboxes.items() if frame.is_selected]
        if selected:
            reply = QMessageBox.question(
                self, "키워드 삭제",
                f"{len(selected)}개의 키워드를 삭제하시겠습니까?",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
            )
            if reply == QMessageBox.StandardButton.Yes:
                self.data_manager.delete_keywords(selected)
                self.load_keywords()
                self._emit_selected_keywords()
    
    def _emit_selected_keywords(self):
        """선택된 키워드 시그널 발송"""
        selected = [kw for kw, frame in self.keyword_checkboxes.items() if frame.is_selected]
        self.keywords_changed.emit(selected)
    
    def get_selected_keywords(self) -> List[str]:
        """선택된 키워드 목록 반환"""
        return [kw for kw, frame in self.keyword_checkboxes.items() if frame.is_selected]
    
    def clear_all_selections(self):
        """모든 키워드 선택 해제"""
        for frame in self.keyword_checkboxes.values():
            frame.set_selected(False)
        self._emit_selected_keywords()


class MilestoneListBlock(QWidget):
    """Milestone List Block - 단일 선택 방식"""
    
    milestone_selected = pyqtSignal(str)  # 선택된 마일스톤 ID 전달
    
    def __init__(self, parent=None):
        super().__init__(parent)
        
        self.selected_milestone_id = None  # 현재 선택된 마일스톤 ID
        self.milestone_cards = {}  # milestone_id -> card 위젯 매핑
        
        self.setStyleSheet("""
            QWidget {
                background: white;
                border: 1px solid #d2d2d7;
                border-radius: 8px;
            }
            QLabel {
                color: #1d1d1f;
                border: none;
            }
        """)
        
        layout = QVBoxLayout()
        layout.setContentsMargins(15, 15, 15, 15)
        layout.setSpacing(10)
        
        # 제목
        title_label = QLabel("📋 Milestone List")
        title_label.setStyleSheet("font-size: 15px; font-weight: bold; color: #1d1d1f; border: none;")
        layout.addWidget(title_label)
        
        # 스크롤 영역
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setStyleSheet("QScrollArea { border: none; background: transparent; }")
        
        self.list_container = QWidget()
        self.list_layout = QVBoxLayout()
        self.list_layout.setSpacing(8)
        self.list_layout.setContentsMargins(5, 5, 5, 5)
        self.list_container.setLayout(self.list_layout)
        self.list_container.setStyleSheet("background: transparent; border: none;")
        
        scroll_area.setWidget(self.list_container)
        layout.addWidget(scroll_area)
        
        self.setLayout(layout)
    
    def update_milestones(self, milestones: List[Dict]):
        """마일스톤 목록 업데이트"""
        # 기존 카드 제거
        while self.list_layout.count():
            item = self.list_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
        
        self.milestone_cards.clear()
        
        # 마일스톤 카드 생성
        if not milestones:
            no_data_label = QLabel("마일스톤이 없습니다.")
            no_data_label.setStyleSheet("color: #86868b; font-size: 13px; padding: 20px;")
            no_data_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            self.list_layout.addWidget(no_data_label)
        else:
            for milestone in milestones:
                card = self._create_milestone_card(milestone)
                self.list_layout.addWidget(card)
                self.milestone_cards[milestone["id"]] = card
            
            # 빈 공간 채우기
            self.list_layout.addStretch()
    
    def _create_milestone_card(self, milestone: Dict) -> QFrame:
        """마일스톤 카드 생성 - 클릭 시 단일 선택"""
        card = QFrame()
        card.setObjectName("milestone_card")
        card.setStyleSheet("""
            QFrame#milestone_card {
                background: white;
                border: 2px solid #e8e8ed;
                border-radius: 8px;
                padding: 12px;
            }
            QFrame#milestone_card:hover {
                border: 2px solid #86868b;
            }
        """)
        card.setCursor(Qt.CursorShape.PointingHandCursor)
        
        # 마일스톤 ID를 카드에 저장
        card.milestone_id = milestone["id"]
        
        layout = QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(4)
        
        # 제목
        title = QLabel(milestone.get("title", ""))
        title.setStyleSheet("font-size: 14px; font-weight: bold; color: #1d1d1f; border: none;")
        title.setWordWrap(True)
        layout.addWidget(title)
        
        # 부제목
        subtitle = QLabel(milestone.get("subtitle", ""))
        subtitle.setStyleSheet("font-size: 12px; color: #86868b; border: none;")
        subtitle.setWordWrap(True)
        layout.addWidget(subtitle)
        
        card.setLayout(layout)
        
        # 클릭 이벤트
        card.mousePressEvent = lambda event: self._on_card_clicked(milestone["id"])
        
        return card
    
    def _on_card_clicked(self, milestone_id: str):
        """카드 클릭 시 단일 선택 처리"""
        # 이전에 선택된 카드의 스타일 해제
        if self.selected_milestone_id and self.selected_milestone_id in self.milestone_cards:
            prev_card = self.milestone_cards[self.selected_milestone_id]
            prev_card.setStyleSheet("""
                QFrame#milestone_card {
                    background: white;
                    border: 2px solid #e8e8ed;
                    border-radius: 8px;
                    padding: 12px;
                }
                QFrame#milestone_card:hover {
                    border: 2px solid #86868b;
                }
            """)
        
        # 새로운 카드 선택
        self.selected_milestone_id = milestone_id
        if milestone_id in self.milestone_cards:
            card = self.milestone_cards[milestone_id]
            card.setStyleSheet("""
                QFrame#milestone_card {
                    background: white;
                    border: 2px solid #007AFF;
                    border-radius: 8px;
                    padding: 12px;
                }
                QFrame#milestone_card:hover {
                    border: 2px solid #007AFF;
                }
            """)
        
        # 시그널 발송
        self.milestone_selected.emit(milestone_id)
    
    def clear_selection(self):
        """선택 해제"""
        if self.selected_milestone_id and self.selected_milestone_id in self.milestone_cards:
            card = self.milestone_cards[self.selected_milestone_id]
            card.setStyleSheet("""
                QFrame#milestone_card {
                    background: white;
                    border: 2px solid #e8e8ed;
                    border-radius: 8px;
                    padding: 12px;
                }
                QFrame#milestone_card:hover {
                    border: 2px solid #86868b;
                }
            """)
        
        self.selected_milestone_id = None
    
    def select_milestone(self, milestone_id: str):
        """외부에서 마일스톤 선택 (Milestone Tree 연동용)"""
        if milestone_id in self.milestone_cards:
            self._on_card_clicked(milestone_id)


class ThisMonthBlock(QWidget):
    """이번달 일정 관리 Block 위젯 - 2열 그리드"""
    
    milestone_clicked = pyqtSignal(str)  # KPI 카드에서 마일스톤 ID를 전달
    
    def __init__(self, parent=None):
        super().__init__(parent)
        
        self.setStyleSheet("""
            QWidget {
                background: white;
                border: 1px solid #d2d2d7;
                border-radius: 8px;
            }
            QLabel {
                color: #1d1d1f;
                border: none;
            }
        """)
        
        layout = QVBoxLayout()
        layout.setContentsMargins(15, 15, 15, 15)
        layout.setSpacing(10)
        
        # 제목
        title_label = QLabel("📅 이번달 일정")
        title_label.setStyleSheet("font-size: 15px; font-weight: bold; color: #1d1d1f; border: none;")
        layout.addWidget(title_label)
        
        # 스크롤 영역
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setStyleSheet("QScrollArea { border: none; background: transparent; }")
        
        self.kpi_container = QWidget()
        # ✅ 2열 그리드 레이아웃으로 변경
        self.kpi_layout = QGridLayout()
        self.kpi_layout.setSpacing(8)
        self.kpi_layout.setContentsMargins(5, 5, 5, 5)
        self.kpi_container.setLayout(self.kpi_layout)
        self.kpi_container.setStyleSheet("background: transparent; border: none;")
        
        scroll_area.setWidget(self.kpi_container)
        layout.addWidget(scroll_area)
        
        self.setLayout(layout)
    
    def update_nodes(self, milestones: List[Dict]):
        """이번달 노드들로 KPI 차트 업데이트 - 2열 그리드"""
        # 기존 KPI 카드 제거
        while self.kpi_layout.count():
            item = self.kpi_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
        
        # 이번달 추출
        today = datetime.now()
        current_year = today.year % 100  # 24, 25 등
        current_month = today.month
        
        this_month_nodes = []
        for milestone in milestones:
            milestone_id = milestone.get("id", "")
            milestone_title = milestone.get("title", "")
            for node in milestone.get("nodes", []):
                date_str = node.get("date", "")
                if self._is_this_month(date_str, current_year, current_month):
                    this_month_nodes.append({
                        "milestone_id": milestone_id,
                        "milestone_title": milestone_title,
                        "node": node
                    })
        
        # KPI 카드 생성 - 2열 그리드로 배치
        if not this_month_nodes:
            no_data_label = QLabel("이번달 일정이 없습니다.")
            no_data_label.setStyleSheet("color: #86868b; font-size: 13px; padding: 20px;")
            no_data_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            self.kpi_layout.addWidget(no_data_label, 0, 0, 1, 2)  # 2열 전체
        else:
            row = 0
            col = 0
            for item in this_month_nodes:
                kpi_card = self._create_kpi_card(item["milestone_id"], item["milestone_title"], item["node"])
                self.kpi_layout.addWidget(kpi_card, row, col)
                
                # 다음 위치 계산 (2열)
                col += 1
                if col >= 2:
                    col = 0
                    row += 1
    
    def _is_this_month(self, date_str: str, current_year: int, current_month: int) -> bool:
        """날짜가 이번달인지 확인 (월 또는 분기)"""
        try:
            parts = date_str.strip().upper().split(".")
            if len(parts) != 2:
                return False
            
            year = int(parts[0])
            if year != current_year:
                return False
            
            # 월 형식 (YY.MM)
            if "Q" not in date_str:
                month = int(parts[1])
                return month == current_month
            
            # 분기 형식 (YY.Qn)
            if parts[1].startswith("Q"):
                quarter = int(parts[1][1])  # "Q4" -> 4
                # 분기별 월 계산
                quarter_months = {
                    1: [1, 2, 3],
                    2: [4, 5, 6],
                    3: [7, 8, 9],
                    4: [10, 11, 12]
                }
                return current_month in quarter_months.get(quarter, [])
        except:
            pass
        return False
    
    def _create_kpi_card(self, milestone_id: str, milestone_title: str, node: Dict) -> QWidget:
        """KPI 카드 생성 - 클릭 가능, 고정 크기, 메모 2줄"""
        card = ClickableKPICard(milestone_id, milestone_title, node, parent=self)
        # 카드의 클릭 시그널을 ThisMonthBlock의 시그널로 포워딩
        card.milestone_clicked.connect(self.milestone_clicked.emit)
        return card


class ClickableMemoArea(QScrollArea):
    """클릭 시 메모 내용을 클립보드에 복사하는 위젯"""
    
    def __init__(self, memo_text: str, parent=None):
        super().__init__(parent)
        self.memo_text = memo_text
        
        self.setWidgetResizable(True)
        self.setStyleSheet("""
            QScrollArea { 
                border: 1px solid #e8e8ed; 
                border-radius: 4px; 
                background: white; 
            }
            QScrollArea:hover {
                border: 2px solid #007AFF;
            }
            QToolTip {
                background-color: white;
                color: #1d1d1f;
                border: 1px solid #007AFF;
                border-radius: 4px;
                padding: 5px;
                font-size: 12px;
            }
        """)
        
        self.memo_label = QLabel(memo_text)
        self.memo_label.setStyleSheet("font-size: 13px; color: #86868b; padding: 10px;")
        self.memo_label.setWordWrap(True)
        self.setWidget(self.memo_label)
        
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.setToolTip("📋 복사")
    
    def mousePressEvent(self, event):
        """클릭 시 메모 내용을 클립보드에 복사"""
        if event.button() == Qt.MouseButton.LeftButton:
            from PyQt6.QtWidgets import QApplication
            clipboard = QApplication.clipboard()
            clipboard.setText(self.memo_text)
            
            # 시각적 피드백 - 텍스트 색상 변경
            self.memo_label.setStyleSheet(
                "font-size: 13px; color: #007AFF; padding: 10px; font-weight: bold;"
            )
            QTimer.singleShot(500, lambda: self.memo_label.setStyleSheet(
                "font-size: 13px; color: #86868b; padding: 10px;"
            ))
            
            # 툴팁 피드백 - "복사됨!" 표시 후 원래대로
            self.setToolTip("✅ 복사됨!")
            QTimer.singleShot(1500, lambda: self.setToolTip("📋 복사"))
        super().mousePressEvent(event)


class ClickableKPICard(QFrame):
    """클릭 가능한 KPI 카드 - 고정 크기, 메모 2줄 제한"""
    
    milestone_clicked = pyqtSignal(str)  # milestone_id를 전달하는 시그널
    
    def __init__(self, milestone_id: str, milestone_title: str, node: Dict, parent=None):
        super().__init__(parent)
        self.milestone_id = milestone_id
        self.milestone_title = milestone_title
        self.node = node
        
        # ✅ 고정 크기 확대 (가독성 향상)
        self.setFixedSize(450, 160)
        
        self.setStyleSheet("""
            QFrame {
                background: #f5f5f7;
                border: 1px solid #e8e8ed;
                border-radius: 6px;
            }
            QFrame:hover {
                background: #eeeeee;
                border: 1px solid #007AFF;
            }
        """)
        
        card_layout = QVBoxLayout()
        card_layout.setSpacing(5)
        card_layout.setContentsMargins(12, 12, 12, 12)
        
        # 제목 (마일스톤 제목) - 1줄
        title_label = QLabel(milestone_title)
        title_label.setStyleSheet("font-size: 14px; font-weight: bold; color: #007AFF;")
        title_label.setWordWrap(False)
        title_label.setMaximumHeight(18)
        fm = title_label.fontMetrics()
        elided_title = fm.elidedText(milestone_title, Qt.TextElideMode.ElideRight, 426)
        title_label.setText(elided_title)
        card_layout.addWidget(title_label)
        
        # 노드 내용 - 1줄
        content = node.get("content", "")
        if content:
            content_label = QLabel(content)
            content_label.setStyleSheet("font-size: 13px; color: #1d1d1f;")
            content_label.setWordWrap(False)
            content_label.setMaximumHeight(17)
            fm_content = content_label.fontMetrics()
            elided_content = fm_content.elidedText(content, Qt.TextElideMode.ElideRight, 426)
            content_label.setText(elided_content)
            card_layout.addWidget(content_label)
        
        # ✅ 메모 - 2줄로 제한
        memo = node.get("memo", "")
        if memo:
            memo_label = QLabel(memo)
            memo_label.setStyleSheet("font-size: 12px; color: #86868b;")
            memo_label.setWordWrap(True)
            memo_label.setMaximumHeight(80)  # 약 2줄 높이
            card_layout.addWidget(memo_label)
        
        card_layout.addStretch()
        self.setLayout(card_layout)
        
        # ✅ 클릭 가능하게 설정
        self.setCursor(Qt.CursorShape.PointingHandCursor)
    
    def mousePressEvent(self, event):
        """클릭 시 상세 정보 팝업 + 마일스톤 필터링"""
        if event.button() == Qt.MouseButton.LeftButton:
            self._show_detail_dialog()
            self.milestone_clicked.emit(self.milestone_id)  # 시그널 발행
        super().mousePressEvent(event)
    
    def _show_detail_dialog(self):
        """노드 상세 정보 팝업 다이얼로그"""
        dialog = QDialog(self)
        dialog.setWindowTitle("노드 상세 정보")
        dialog.setModal(True)
        dialog.setFixedSize(550, 500)
        
        # KPI Card와 동일한 배경색 설정
        dialog.setStyleSheet("QDialog { background: #f5f5f7; }")
        
        layout = QVBoxLayout()
        layout.setSpacing(15)
        layout.setContentsMargins(25, 25, 25, 25)
        
        # 마일스톤 제목
        milestone_label = QLabel(self.milestone_title)
        milestone_label.setStyleSheet("font-size: 18px; font-weight: bold; color: #007AFF;")
        layout.addWidget(milestone_label)
        
        # 구분선
        line1 = QFrame()
        line1.setFrameShape(QFrame.Shape.HLine)
        line1.setStyleSheet("background: #d2d2d7;")
        layout.addWidget(line1)
        
        # 노드 정보 그리드
        info_layout = QVBoxLayout()
        info_layout.setSpacing(10)
        
        # 모양 + 색상
        shape_color_layout = QHBoxLayout()
        shape = self.node.get("shape", "circle")
        color = self.node.get("color", "#007AFF")
        shape2 = self.node.get("shape2", "")
        color2 = self.node.get("color2", "")
        
        shape_label = QLabel(f"모양: {shape}")
        shape_label.setStyleSheet("font-size: 14px; color: #1d1d1f;")
        shape_color_layout.addWidget(shape_label)
        
        color_box = QLabel("   ")
        color_box.setStyleSheet(f"background: {color}; border: 1px solid #d2d2d7; border-radius: 4px;")
        color_box.setFixedSize(30, 20)
        shape_color_layout.addWidget(color_box)
        
        if shape2:
            shape2_label = QLabel(f"+ {shape2}")
            shape2_label.setStyleSheet("font-size: 14px; color: #1d1d1f;")
            shape_color_layout.addWidget(shape2_label)
            
            color2_box = QLabel("   ")
            color2_box.setStyleSheet(f"background: {color2}; border: 1px solid #d2d2d7; border-radius: 4px;")
            color2_box.setFixedSize(30, 20)
            shape_color_layout.addWidget(color2_box)
        
        shape_color_layout.addStretch()
        info_layout.addLayout(shape_color_layout)
        
        # 날짜
        date = self.node.get("date", "")
        date_label = QLabel(f"📅 날짜: {date}")
        date_label.setStyleSheet("font-size: 14px; color: #1d1d1f;")
        info_layout.addWidget(date_label)
        
        # 내용
        content = self.node.get("content", "")
        content_label = QLabel(f"📝 내용:\n{content}")
        content_label.setStyleSheet("font-size: 14px; color: #1d1d1f;")
        content_label.setWordWrap(True)
        info_layout.addWidget(content_label)
        
        # 메모 - 클릭 시 복사 가능
        memo = self.node.get("memo", "")
        if memo:
            memo_title = QLabel("💬 메모: (클릭하여 복사)")
            memo_title.setStyleSheet("font-size: 14px; font-weight: bold; color: #1d1d1f;")
            info_layout.addWidget(memo_title)
            
            # 클릭 가능한 메모 영역
            memo_scroll = ClickableMemoArea(memo, parent=dialog)
            memo_scroll.setFixedHeight(180)
            info_layout.addWidget(memo_scroll)
        
        layout.addLayout(info_layout)
        layout.addStretch()
        
        # 닫기 버튼
        close_btn = QPushButton("닫기")
        close_btn.setStyleSheet("""
            QPushButton {
                background: #007AFF;
                color: white;
                border: none;
                border-radius: 6px;
                padding: 10px 20px;
                font-size: 13px;
                font-weight: bold;
            }
            QPushButton:hover {
                background: #1A8CFF;
            }
        """)
        close_btn.clicked.connect(dialog.accept)
        layout.addWidget(close_btn, alignment=Qt.AlignmentFlag.AlignCenter)
        
        dialog.setLayout(layout)
        dialog.exec()


class MilestoneTreeDialog(ModernDialog):
    """Milestone Tree 다이얼로그 - Category별로 마일스톤을 그룹화하여 표시"""
    
    milestone_selected = pyqtSignal(str)  # 선택된 마일스톤 ID
    
    def __init__(self, parent=None, milestones: List[Dict] = None):
        super().__init__(parent, "🌳 Milestone Tree")
        self.setFixedSize(1400, 900)
        self.milestones = milestones or []
        self.selected_milestone_id = None
        
        layout = QVBoxLayout()
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(15)
        
        # 설명 레이블
        desc_label = QLabel("카테고리별로 그룹화된 마일스톤을 확인하고 선택하세요")
        desc_label.setStyleSheet("font-size: 13px; color: #86868b;")
        layout.addWidget(desc_label)
        
        # 스크롤 영역
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setStyleSheet("QScrollArea { border: none; background: transparent; }")
        
        scroll_content = QWidget()
        scroll_layout = QHBoxLayout(scroll_content)
        scroll_layout.setSpacing(15)
        scroll_layout.setContentsMargins(10, 10, 10, 10)
        
        # 카테고리별로 그룹화
        categories = {}
        uncategorized = []
        
        for milestone in self.milestones:
            category = milestone.get("category", "").strip()
            if category:
                if category not in categories:
                    categories[category] = []
                categories[category].append(milestone)
            else:
                uncategorized.append(milestone)
        
        # 카테고리가 있는 것들 먼저 표시
        for category_name in sorted(categories.keys()):
            category_widget = self._create_category_column(category_name, categories[category_name])
            scroll_layout.addWidget(category_widget)
        
        # 카테고리 없는 것들 마지막에 표시
        if uncategorized:
            category_widget = self._create_category_column("미분류", uncategorized)
            scroll_layout.addWidget(category_widget)
        
        scroll_layout.addStretch()
        
        scroll_area.setWidget(scroll_content)
        layout.addWidget(scroll_area)
        
        # 닫기 버튼
        btn_layout = QHBoxLayout()
        btn_layout.addStretch()
        
        close_btn = QPushButton("닫기")
        close_btn.setObjectName("secondary")
        close_btn.setFixedWidth(120)
        close_btn.clicked.connect(self.reject)
        btn_layout.addWidget(close_btn)
        
        layout.addLayout(btn_layout)
        self.setLayout(layout)
    
    def _create_category_column(self, category_name: str, milestones: List[Dict]) -> QWidget:
        """카테고리 컬럼 생성"""
        column = QWidget()
        column.setFixedWidth(350)
        column.setStyleSheet("""
            QWidget {
                background: white;
                border: 2px solid #e8e8ed;
                border-radius: 12px;
            }
        """)
        
        column_layout = QVBoxLayout(column)
        column_layout.setContentsMargins(15, 15, 15, 15)
        column_layout.setSpacing(5)
        
        # 카테고리 제목
        title_label = QLabel(category_name)
        title_label.setStyleSheet("""
            font-size: 16px;
            font-weight: bold;
            color: #1d1d1f;
            padding: 8px;
            background: #f5f5f7;
            border-radius: 8px;
        """)
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        column_layout.addWidget(title_label)
        
        # 마일스톤 개수
        count_label = QLabel(f"{len(milestones)}개 마일스톤")
        count_label.setStyleSheet("font-size: 11px; color: #86868b; padding: 4px;")
        count_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        column_layout.addWidget(count_label)
        
        # 마일스톤 카드들
        for milestone in milestones:
            card = self._create_milestone_card(milestone)
            column_layout.addWidget(card)
        
        column_layout.addStretch()
        return column
    
    def _create_milestone_card(self, milestone: Dict) -> QWidget:
        """마일스톤 카드 생성 (클릭 가능)"""
        card = QFrame()
        card.setFixedHeight(85)
        card.setCursor(Qt.CursorShape.PointingHandCursor)
        card.setStyleSheet("""
            QFrame {
                background: white;
                border: 2px solid #d2d2d7;
                border-radius: 10px;
            }
            QFrame:hover {
                border: 2px solid #007AFF;
                background: #F0F8FF;
            }
        """)
        
        # 마일스톤 ID 저장
        card.milestone_id = milestone["id"]
        
        # 카드 내용 레이아웃
        card_layout = QVBoxLayout(card)
        card_layout.setSpacing(4)
        card_layout.setContentsMargins(10, 8, 10, 8)
        
        # 제목
        title_label = QLabel(milestone.get("title", ""))
        title_label.setStyleSheet("""
            font-size: 13px;
            font-weight: bold;
            color: #1d1d1f;
            border: none;
            background: transparent;
        """)
        title_label.setWordWrap(True)
        card_layout.addWidget(title_label)
        
        # 부제목
        subtitle = milestone.get("subtitle", "")
        if subtitle:
            subtitle_label = QLabel(subtitle)
            subtitle_label.setStyleSheet("""
                font-size: 10px;
                color: #86868b;
                border: none;
                background: transparent;
            """)
            subtitle_label.setWordWrap(True)
            card_layout.addWidget(subtitle_label)
        
        # 노드 개수
        node_count = len(milestone.get("nodes", []))
        node_label = QLabel(f"📊 {node_count}개 노드")
        node_label.setStyleSheet("""
            font-size: 9px;
            color: #007AFF;
            border: none;
            background: transparent;
        """)
        card_layout.addWidget(node_label)
        
        card_layout.addStretch()
        
        # 클릭 이벤트
        card.mousePressEvent = lambda event: self._on_milestone_clicked(milestone["id"])
        
        return card
    
    def _on_milestone_clicked(self, milestone_id: str):
        """마일스톤 카드 클릭 시"""
        self.selected_milestone_id = milestone_id
        self.milestone_selected.emit(milestone_id)
        self.accept()  # 다이얼로그 닫기
