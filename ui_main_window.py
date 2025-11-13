"""메인 UI 윈도우 모듈 - 라이트 모드 디자인"""

from PyQt6.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
                             QPushButton, QScrollArea, QLabel, QCheckBox,
                             QFrame, QMessageBox, QFileDialog)
from PyQt6.QtCore import Qt, QSize
from PyQt6.QtGui import QShortcut, QKeySequence, QPixmap, QPainter
from typing import List, Dict, Set, Optional

from data_manager import DataManager
from custom_widgets import (MilestoneDialog, NodeDialog, SearchFilterDialog,
                            DateFilterDialog, ZoomableTimelineDialog,
                            KeywordBlock, MilestoneListBlock, ThisMonthBlock,
                            MilestoneTreeDialog)
from timeline_canvas import TimelineCanvas


class MainWindow(QMainWindow):
    """라이트 모드 메인 윈도우"""

    def __init__(self):
        super().__init__()
        self.setWindowTitle("Milestone Manager")
        self.setGeometry(100, 100, 1600, 900)

        self.data_manager = DataManager()
        self.milestone_widgets = []
        self.selected_milestone_ids: Set[str] = set()
        self.selected_nodes_by_milestone: Dict[str, Optional[Dict]] = {
        }  # 마일스톤별 선택된 노드
        self.filter_settings = None
        self.current_milestone_index = 0  # 현재 표시 중인 마일스톤 인덱스
        self.filtered_milestones = []  # 필터링된 마일스톤 목록
        self.selected_milestone_id_from_list: Optional[str] = None  # Milestone List에서 선택된 마일스톤 ID

        self.setStyleSheet("""
            QMainWindow {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #f5f5f7, stop:1 #ffffff);
            }
            QPushButton {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #007AFF, stop:1 #0051D5);
                border: none;
                border-radius: 4px;
                color: white;
                padding: 4px 10px;
                font-size: 11px;
                font-weight: bold;
                min-height: 5px;
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
            QPushButton#danger {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #FF3B30, stop:1 #D32F2F);
                color: white;
            }
            QPushButton#danger:hover {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #FF4C41, stop:1 #E43A3A);
            }
            QScrollArea {
                border: none;
                background: transparent;
            }
            QLabel {
                color: #1d1d1f;
            }
        """)

        self._create_ui()

        # 단축키 설정
        load_shortcut = QShortcut(QKeySequence("Ctrl+L"), self)
        load_shortcut.activated.connect(self.load_data)

        save_shortcut = QShortcut(QKeySequence("Ctrl+S"), self)
        save_shortcut.activated.connect(self.save_data)

        delete_node_shortcut = QShortcut(QKeySequence("Ctrl+D"), self)
        delete_node_shortcut.activated.connect(self._delete_node_shortcut)

        # 프로그램 시작 시 자동 로드
        self.load_data(auto_load=True)

    def _create_ui(self):
        """UI 구성 - 3행 레이아웃"""
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        main_layout = QVBoxLayout(central_widget)
        main_layout.setContentsMargins(15, 5, 15, 15)
        main_layout.setSpacing(1)

        # ===== 행1: 2열 레이아웃 (왼쪽: 제목+툴바, 오른쪽: Tree 버튼) =====
        row1_container = QWidget()
        row1_main_layout = QHBoxLayout(row1_container)
        row1_main_layout.setContentsMargins(0, 0, 0, 0)
        row1_main_layout.setSpacing(15)
        
        # 왼쪽 열: 제목 + 툴바
        left_column = QWidget()
        left_column_layout = QVBoxLayout(left_column)
        left_column_layout.setContentsMargins(0, 0, 0, 0)
        left_column_layout.setSpacing(1)

        # 제목 + 데이터 상태
        header_layout = QHBoxLayout()
        header_layout.setSpacing(5)

        title_label = QLabel("Milestone Manager")
        title_label.setStyleSheet("""
            font-size: 18px;
            font-weight: bold;
            color: #1d1d1f;
            padding: 0px;
            margin: 0px;
        """)
        header_layout.addWidget(title_label)

        # 데이터 상태 표시 레이블
        self.data_status_label = QLabel("⚠️ 데이터 없음")
        self.data_status_label.setStyleSheet("""
            color: #FF9500;
            font-size: 9px;
            padding: 0px;
        """)
        self.data_status_label.setAlignment(Qt.AlignmentFlag.AlignVCenter)
        header_layout.addWidget(self.data_status_label)
        header_layout.addStretch()

        left_column_layout.addLayout(header_layout)

        # 툴바 (기존 버튼들)
        toolbar = QHBoxLayout()
        toolbar.setSpacing(4)

        load_btn = QPushButton("📂 Data Load")
        load_btn.clicked.connect(self.load_data)
        toolbar.addWidget(load_btn)

        save_btn = QPushButton("💾 저장")
        save_btn.clicked.connect(self.save_data)
        toolbar.addWidget(save_btn)

        create_btn = QPushButton("➕ 생성")
        create_btn.clicked.connect(self.create_milestone)
        toolbar.addWidget(create_btn)

        delete_btn = QPushButton("🗑️ 삭제")
        delete_btn.setObjectName("danger")
        delete_btn.clicked.connect(self.delete_selected_milestones)
        toolbar.addWidget(delete_btn)

        search_btn = QPushButton("🔍 검색")
        search_btn.setObjectName("secondary")
        search_btn.clicked.connect(self.open_search_filter)
        toolbar.addWidget(search_btn)

        date_filter_btn = QPushButton("🗓️ 날짜")
        date_filter_btn.setObjectName("secondary")
        date_filter_btn.clicked.connect(self.filter_by_date)
        toolbar.addWidget(date_filter_btn)

        this_month_btn = QPushButton("📅 이번달 Milestone")
        this_month_btn.setObjectName("secondary")
        this_month_btn.clicked.connect(self.filter_this_month)
        toolbar.addWidget(this_month_btn)

        export_btn = QPushButton("📤 이미지")
        export_btn.setObjectName("secondary")
        export_btn.clicked.connect(self.export_image)
        toolbar.addWidget(export_btn)

        toolbar.addStretch()

        # 필터 상태 표시 레이블
        self.filter_status_label = QLabel("")
        self.filter_status_label.setStyleSheet("""
            color: #007AFF;
            font-size: 11px;
            font-weight: bold;
            padding: 6px 10px;
            background: #E3F2FD;
            border-radius: 6px;
        """)
        self.filter_status_label.hide()
        toolbar.addWidget(self.filter_status_label)

        # 필터 해제 버튼
        self.clear_filter_btn = QPushButton("✖")
        self.clear_filter_btn.setObjectName("secondary")
        self.clear_filter_btn.setFixedWidth(35)
        self.clear_filter_btn.clicked.connect(self.clear_filter)
        self.clear_filter_btn.hide()
        toolbar.addWidget(self.clear_filter_btn)

        left_column_layout.addLayout(toolbar)
        
        row1_main_layout.addWidget(left_column, stretch=3)
        
        # 오른쪽 열: Milestone Tree 버튼만
        right_column = QWidget()
        right_column_layout = QVBoxLayout(right_column)
        right_column_layout.setContentsMargins(0, 0, 0, 0)
        right_column_layout.setSpacing(0)
        right_column_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        tree_btn = QPushButton("🌳 Milestone Tree")
        tree_btn.setStyleSheet("""
            QPushButton {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #007AFF, stop:1 #0051D5);
                color: white;
                border: none;
                border-radius: 12px;
                padding: 15px 30px;
                font-size: 15px;
                font-weight: bold;
                min-width: 200px;
                min-height: 50px;
            }
            QPushButton:hover {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #1A8CFF, stop:1 #0062FF);
            }
            QPushButton:pressed {
                background: #0051D5;
            }
        """)
        tree_btn.clicked.connect(self._show_milestone_tree)
        right_column_layout.addWidget(tree_btn)
        
        row1_main_layout.addWidget(right_column, stretch=1)

        main_layout.addWidget(row1_container, stretch=0)

        # ===== 행2: Milestone List Block (25%) + 키워드 Block (25%) + 이번달 일정 Block (50%) =====
        row2_layout = QHBoxLayout()
        row2_layout.setSpacing(10)

        # Milestone List Block - 고정 높이
        self.milestone_list_block = MilestoneListBlock(self)
        self.milestone_list_block.setFixedWidth(int(1600 * 0.25))  # 25% 너비
        self.milestone_list_block.setFixedHeight(450)  # 고정 높이
        self.milestone_list_block.milestone_selected.connect(
            self._on_milestone_list_selected)
        row2_layout.addWidget(self.milestone_list_block)

        # 키워드 Block - 고정 높이
        self.keyword_block = KeywordBlock(self, self.data_manager)
        self.keyword_block.setFixedWidth(int(1600 * 0.25))  # 25% 너비
        self.keyword_block.setFixedHeight(450)  # 고정 높이
        self.keyword_block.keywords_changed.connect(
            self._on_keyword_filter_changed)
        row2_layout.addWidget(self.keyword_block)

        # 이번달 일정 Block - 고정 높이
        self.this_month_block = ThisMonthBlock(self)
        self.this_month_block.setFixedHeight(450)  # 고정 높이
        self.this_month_block.milestone_clicked.connect(
            self._filter_by_milestone_id)
        row2_layout.addWidget(self.this_month_block, stretch=1)

        main_layout.addLayout(row2_layout, stretch=0)

        # ===== 행3: 단일 Milestone Block + 페이지네이션 =====
        # 페이지네이션 컨트롤
        pagination_layout = QHBoxLayout()
        pagination_layout.setSpacing(10)

        self.prev_btn = QPushButton("◀ 이전")
        self.prev_btn.setObjectName("secondary")
        self.prev_btn.setFixedWidth(100)
        self.prev_btn.clicked.connect(self._show_previous_milestone)
        pagination_layout.addWidget(self.prev_btn)

        self.milestone_nav_label = QLabel("0 / 0")
        self.milestone_nav_label.setStyleSheet("""
            font-size: 18px;
            font-weight: bold;
            color: #1d1d1f;
            padding: 8px 16px;
            background: #f5f5f7;
            border-radius: 6px;
        """)
        self.milestone_nav_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        pagination_layout.addWidget(self.milestone_nav_label)

        self.next_btn = QPushButton("다음 ▶")
        self.next_btn.setObjectName("secondary")
        self.next_btn.setFixedWidth(100)
        self.next_btn.clicked.connect(self._show_next_milestone)
        pagination_layout.addWidget(self.next_btn)

        pagination_layout.addStretch()

        main_layout.addLayout(pagination_layout)

        # 단일 Milestone 표시 영역 (스크롤 없이 고정 높이)
        self.milestone_container = QWidget()
        self.milestone_container.setStyleSheet("""
            background: white;
            border: 1px solid #d2d2d7;
            border-radius: 8px;
        """)
        self.milestone_layout = QVBoxLayout(self.milestone_container)
        self.milestone_layout.setContentsMargins(0, 0, 0, 0)
        self.milestone_layout.setSpacing(0)

        self.milestone_container.setFixedHeight(450)

        main_layout.addWidget(self.milestone_container)

    def _show_message(self, icon, title, text):
        """메시지 박스 표시 (라이트 모드 스타일)"""
        msg = QMessageBox(self)
        msg.setIcon(icon)
        msg.setWindowTitle(title)
        msg.setText(text)
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
        return msg.exec()

    def load_data(self, auto_load=False):
        """데이터 로드"""
        try:
            self.data_manager.load_data()
            self._refresh_ui()
            self._update_data_status()
            if not auto_load:
                self._show_message(QMessageBox.Icon.Information, "성공",
                                   "데이터를 성공적으로 불러왔습니다.")
        except Exception as e:
            self._update_data_status()
            if not auto_load:
                self._show_message(QMessageBox.Icon.Critical, "오류", str(e))

    def save_data(self):
        """데이터 저장 - 백업 자동 생성"""
        milestones = self.data_manager.get_milestones()

        # 빈 데이터 저장 경고
        if not milestones:
            msg = QMessageBox(self)
            msg.setIcon(QMessageBox.Icon.Warning)
            msg.setWindowTitle("경고")
            msg.setText("현재 데이터가 비어있습니다.\n저장하면 기존 데이터가 삭제됩니다.\n\n계속하시겠습니까?")
            msg.setStandardButtons(QMessageBox.StandardButton.Yes
                                   | QMessageBox.StandardButton.No)
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
            if msg.exec() != QMessageBox.StandardButton.Yes:
                return

        try:
            import os
            import shutil

            # 기존 파일이 있으면 백업 생성
            if os.path.exists("raw.json"):
                shutil.copy2("raw.json", "raw.json.backup")

            data = {
                "milestones": milestones,
                "keywords": self.data_manager.get_keywords()
            }
            self.data_manager.save_data(data)
            self._update_data_status()

            backup_msg = "\n(백업: raw.json.backup)" if os.path.exists(
                "raw.json.backup") else ""
            self._show_message(QMessageBox.Icon.Information, "성공",
                               f"데이터가 저장되었습니다.{backup_msg}")
        except Exception as e:
            self._show_message(QMessageBox.Icon.Critical, "오류", str(e))

    def create_milestone(self):
        """마일스톤 생성"""
        dialog = MilestoneDialog(self)
        if dialog.exec() and dialog.result:
            self.data_manager.add_milestone(
                dialog.result["title"],
                dialog.result["subtitle"],
                dialog.result.get("category", "")
            )
            self._refresh_ui()

    def delete_selected_milestones(self):
        """선택된 마일스톤 삭제"""
        if not self.selected_milestone_ids:
            self._show_message(QMessageBox.Icon.Warning, "경고",
                               "삭제할 마일스톤을 선택해주세요.")
            return

        count = len(self.selected_milestone_ids)
        msg = QMessageBox(self)
        msg.setIcon(QMessageBox.Icon.Question)
        msg.setWindowTitle("확인")
        msg.setText(f"{count}개의 마일스톤을 삭제하시겠습니까?")
        msg.setStandardButtons(QMessageBox.StandardButton.Yes
                               | QMessageBox.StandardButton.No)
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
        reply = msg.exec()

        if reply == QMessageBox.StandardButton.Yes:
            for milestone_id in self.selected_milestone_ids:
                self.data_manager.delete_milestone(milestone_id)
            self.selected_milestone_ids.clear()
            self._refresh_ui()

    def open_search_filter(self):
        """검색/필터 다이얼로그"""
        dialog = SearchFilterDialog(self)
        if dialog.exec() and dialog.result:
            self.filter_settings = dialog.result
            self._update_filter_status()
            self._refresh_ui()

    def filter_by_date(self):
        """날짜 필터 다이얼로그"""
        dialog = DateFilterDialog(self)
        if dialog.exec() and dialog.result:
            year = dialog.result["year"]
            quarter = dialog.result["quarter"]

            # 분기별 월 매칭
            # Q1 = 1,2,3월 / Q2 = 4,5,6월 / Q3 = 7,8,9월 / Q4 = 10,11,12월
            quarter_months = {
                1: [1, 2, 3],
                2: [4, 5, 6],
                3: [7, 8, 9],
                4: [10, 11, 12]
            }

            self.filter_settings = {
                "date_filter": True,
                "filter_year": year % 100,  # 2025 -> 25
                "filter_quarter": quarter,
                "filter_months": quarter_months[quarter]
            }
            self._update_filter_status()
            self._refresh_ui()

    def filter_this_month(self):
        """이번달 일정 필터"""
        from datetime import datetime
        today = datetime.now()
        current_year = today.year % 100
        current_month = today.month

        self.filter_settings = {
            "this_month": True,
            "current_year": current_year,
            "current_month": current_month
        }
        self._update_filter_status()
        self._refresh_ui()

    def _filter_by_milestone_id(self, milestone_id: str):
        """마일스톤 ID로 필터링 (KPI Chart 클릭 시)"""
        # 마일스톤 제목 찾기
        milestone_title = ""
        for m in self.data_manager.get_milestones():
            if m.get("id") == milestone_id:
                milestone_title = m.get("title", "")
                break
        
        self.filter_settings = {
            "milestone_id": milestone_id,
            "milestone_title": milestone_title
        }
        self._update_filter_status()
        self._refresh_ui()

    def clear_filter(self):
        """필터 해제"""
        self.filter_settings = None
        # 키워드 블록의 선택도 해제
        self.keyword_block.clear_all_selections()
        # Milestone List 블록의 선택도 해제
        self.milestone_list_block.clear_selection()
        self.selected_milestone_id_from_list = None
        self._update_filter_status()
        self._refresh_ui()

    def _update_filter_status(self):
        """필터 상태 표시 업데이트"""
        if self.filter_settings:
            status_parts = []

            # 키워드 필터
            if self.filter_settings.get("type") == "keyword":
                keywords = self.filter_settings.get("keywords", [])
                if keywords:
                    kw_text = ", ".join(keywords)
                    status_parts.append(f"📌 키워드: {kw_text}")

            # Milestone List 필터
            milestone_list_id = self.filter_settings.get("milestone_list_id", "")
            milestone_list_title = self.filter_settings.get("milestone_list_title", "")
            if milestone_list_id and milestone_list_title:
                status_parts.append(f"📋 선택: {milestone_list_title}")

            keyword = self.filter_settings.get("keyword", "")
            content_keyword = self.filter_settings.get("content_keyword", "")
            shape = self.filter_settings.get("shape", "")
            this_month = self.filter_settings.get("this_month", False)
            date_filter = self.filter_settings.get("date_filter", False)
            milestone_id = self.filter_settings.get("milestone_id", "")
            milestone_title = self.filter_settings.get("milestone_title", "")

            if milestone_id and milestone_title:
                status_parts.append(f"📍 마일스톤: {milestone_title}")
            if this_month:
                current_month = self.filter_settings.get("current_month", 0)
                status_parts.append(f"📅 이번달 일정 ({current_month}월)")
            if date_filter:
                year = self.filter_settings.get("filter_year", 0)
                quarter = self.filter_settings.get("filter_quarter", 0)
                status_parts.append(f"🗓️ {year}년 Q{quarter}")
            if keyword:
                status_parts.append(f"제목/부제목: '{keyword}'")
            if content_keyword:
                status_parts.append(f"내용: '{content_keyword}'")
            if shape:
                status_parts.append(f"모양: {shape}")

            if status_parts:
                self.filter_status_label.setText("🔍 " +
                                                 " | ".join(status_parts))
                self.filter_status_label.show()
                self.clear_filter_btn.show()
        else:
            self.filter_status_label.hide()
            self.clear_filter_btn.hide()

    def export_image(self):
        """이미지 내보내기 - 필터링된 마일스톤만 저장"""
        # 필터링 확인
        if not self.filter_settings:
            self._show_message(QMessageBox.Icon.Warning, "필터 필요",
                               "이미지 추출을 위해서는 필터를 적용해주세요.\n\n"
                               "🔍 Search: 키워드로 검색\n"
                               "🗓️ Date: 날짜로 필터링\n"
                               "📌 키워드: 키워드 선택\n"
                               "📅 이번달 Milestone: 이번달 일정")
            return
        
        if not self.filtered_milestones:
            self._show_message(QMessageBox.Icon.Warning, "경고",
                               "필터링된 마일스톤이 없습니다.")
            return

        filename, _ = QFileDialog.getSaveFileName(
            self, "이미지 저장 (Milestone_IMG 폴더에 블록별로 저장됩니다)", "",
            "PNG Files (*.png);;JPG Files (*.jpg)")

        if filename:
            try:
                import os

                # Milestone_IMG 폴더 생성
                img_folder = "Milestone_IMG"
                os.makedirs(img_folder, exist_ok=True)

                # 파일명과 확장자 분리
                base_name = os.path.splitext(os.path.basename(filename))[0]
                extension = os.path.splitext(filename)[1]

                saved_files = []
                # 필터링된 각 마일스톤을 이미지로 저장
                for i, milestone in enumerate(self.filtered_milestones, 1):
                    # 임시로 마일스톤 블록 생성
                    temp_widget = self._create_milestone_block(milestone)
                    # 이미지 저장을 위한 크기 설정 (Main UI와 동일한 가로, 세로는 600px)
                    temp_widget.setFixedSize(1500, 600)  # 가로 1500px, 세로 600px
                    
                    # 타임라인 캔버스 높이도 조정 (이미지에 모든 노드가 보이도록)
                    timeline_canvas = temp_widget.findChild(TimelineCanvas)
                    if timeline_canvas:
                        timeline_canvas.setFixedHeight(500)  # 타임라인 높이 증가
                    
                    temp_widget.show()  # 렌더링을 위해 보이도록 설정
                    temp_widget.repaint()  # 강제 렌더링
                    pixmap = temp_widget.grab()
                    output_filename = os.path.join(
                        img_folder, f"{base_name}_{i}{extension}")
                    pixmap.save(output_filename)
                    saved_files.append(output_filename)
                    temp_widget.deleteLater()  # 임시 위젯 삭제

                files_list = "\n".join(
                    [f"  • {os.path.basename(f)}" for f in saved_files])
                self._show_message(
                    QMessageBox.Icon.Information, "성공",
                    f"{len(saved_files)}개의 이미지가 Milestone_IMG 폴더에 저장되었습니다:\n{files_list}"
                )
            except Exception as e:
                self._show_message(QMessageBox.Icon.Critical, "오류",
                                   f"이미지 저장 실패: {str(e)}")

    def _refresh_ui(self):
        """UI 새로고침 - 페이지네이션 방식"""
        milestones = self.data_manager.get_milestones()

        # 필터링된 마일스톤 목록 생성 (키워드 필터 적용)
        self.filtered_milestones = [
            m for m in milestones if self._should_show_milestone(m)
        ]

        # 키워드 Block reload
        self.keyword_block.load_keywords()

        # Milestone List Block 업데이트 (키워드 필터링된 결과만 표시)
        self.milestone_list_block.update_milestones(self.filtered_milestones)

        # 이번달 일정 Block 업데이트
        self.this_month_block.update_nodes(milestones)

        # 현재 인덱스 범위 확인 및 조정
        if not self.filtered_milestones:
            self.current_milestone_index = 0
        elif self.current_milestone_index >= len(self.filtered_milestones):
            self.current_milestone_index = max(
                0,
                len(self.filtered_milestones) - 1)

        # 현재 마일스톤 표시 (행3)
        self._show_current_milestone_for_row3()

    def _update_data_status(self):
        """데이터 상태 레이블 업데이트"""
        milestones = self.data_manager.get_milestones()
        count = len(milestones)

        if count == 0:
            self.data_status_label.setText("⚠️ 데이터 없음")
            self.data_status_label.setStyleSheet("""
                color: #FF9500;
                font-size: 9px;
                padding: 0px;
            """)
        else:
            self.data_status_label.setText(f"✅ 데이터 로드됨 ({count}개)")
            self.data_status_label.setStyleSheet("""
                color: #34C759;
                font-size: 9px;
                padding: 0px;
            """)

    def _should_show_milestone(self, milestone: Dict) -> bool:
        """필터링 - 제목과 부제목에서만 검색"""
        if not self.filter_settings:
            return True

        # 마일스톤 ID 필터 (KPI Chart 클릭)
        milestone_id_filter = self.filter_settings.get("milestone_id", "")
        if milestone_id_filter:
            return milestone.get("id") == milestone_id_filter

        # 키워드 필터 (여러 키워드 AND 조건)
        if self.filter_settings.get("type") == "keyword":
            keywords = self.filter_settings.get("keywords", [])
            if keywords:
                title = milestone.get("title", "").lower()
                subtitle = milestone.get("subtitle", "").lower()
                combined_text = title + " " + subtitle

                # 모든 키워드가 제목+부제목에 포함되어야 함 (AND 조건)
                for kw in keywords:
                    if kw.lower() not in combined_text:
                        return False

        keyword = self.filter_settings.get("keyword", "")
        shape_filter = self.filter_settings.get("shape")
        this_month = self.filter_settings.get("this_month", False)

        # 이번달 일정 필터
        if this_month:
            current_year = self.filter_settings.get("current_year", 0)
            current_month = self.filter_settings.get("current_month", 0)

            # 노드 중에 이번달에 해당하는 노드가 있는지 확인
            has_this_month_node = False
            for node in milestone.get("nodes", []):
                date_str = node.get("date", "").strip().upper()

                # 날짜 파싱
                if "Q" in date_str:
                    # 24.Q3 형식
                    parts = date_str.split("Q")
                    if len(parts) == 2:
                        try:
                            year = int(parts[0].replace(".", "").strip())
                            quarter = int(parts[1].strip())
                            # 분기를 월로 변환 (Q1=3월, Q2=6월, Q3=9월, Q4=12월)
                            month = quarter * 3
                            if year == current_year and month == current_month:
                                has_this_month_node = True
                                break
                        except:
                            pass
                else:
                    # 24.10 형식
                    parts = date_str.split(".")
                    if len(parts) == 2:
                        try:
                            year = int(parts[0].strip())
                            month = int(parts[1].strip())
                            if year == current_year and month == current_month:
                                has_this_month_node = True
                                break
                        except:
                            pass

            if not has_this_month_node:
                return False

        # 날짜 필터 (년도 + 분기)
        date_filter = self.filter_settings.get("date_filter", False)
        if date_filter:
            filter_year = self.filter_settings.get("filter_year", 0)
            filter_months = self.filter_settings.get("filter_months", [])

            # 노드 중에 해당 년도의 해당 분기 월에 해당하는 노드가 있는지 확인
            has_matching_date_node = False
            for node in milestone.get("nodes", []):
                date_str = node.get("date", "").strip().upper()

                # 날짜 파싱
                if "Q" in date_str:
                    # 24.Q3 형식
                    parts = date_str.split("Q")
                    if len(parts) == 2:
                        try:
                            year = int(parts[0].replace(".", "").strip())
                            quarter = int(parts[1].strip())
                            # 분기를 월로 변환
                            quarter_months = {
                                1: [1, 2, 3],
                                2: [4, 5, 6],
                                3: [7, 8, 9],
                                4: [10, 11, 12]
                            }
                            node_months = quarter_months.get(quarter, [])
                            # 년도가 일치하고, 분기의 월이 겹치는지 확인
                            if year == filter_year and any(
                                    m in filter_months for m in node_months):
                                has_matching_date_node = True
                                break
                        except:
                            pass
                else:
                    # 24.10 형식
                    parts = date_str.split(".")
                    if len(parts) == 2:
                        try:
                            year = int(parts[0].strip())
                            month = int(parts[1].strip())
                            # 년도가 일치하고, 월이 필터 월에 포함되는지 확인
                            if year == filter_year and month in filter_months:
                                has_matching_date_node = True
                                break
                        except:
                            pass

            if not has_matching_date_node:
                return False

        # 키워드 검색: 제목과 부제목에서만
        if keyword:
            title = milestone.get("title", "").lower()
            subtitle = milestone.get("subtitle", "").lower()
            if keyword.lower() not in title and keyword.lower(
            ) not in subtitle:
                return False

        # 내용 검색: 노드의 content 필드에서
        content_keyword = self.filter_settings.get("content_keyword", "")
        if content_keyword:
            has_matching_content = False
            for node in milestone.get("nodes", []):
                node_content = node.get("content", "").lower()
                if content_keyword.lower() in node_content:
                    has_matching_content = True
                    break
            if not has_matching_content:
                return False

        # 모양 필터
        if shape_filter:
            has_matching_shape = any(
                node.get("shape") == shape_filter
                for node in milestone.get("nodes", []))
            if not has_matching_shape:
                return False

        return True

    def _create_milestone_block(self, milestone: Dict):
        """라이트 모드 마일스톤 블록 생성"""
        block = QFrame()
        block.setStyleSheet("""
            QFrame {
                background: white;
                border: 2px solid #e8e8ed;
                border-radius: 16px;
            }
        """)

        block_layout = QVBoxLayout(block)
        block_layout.setContentsMargins(12, 12, 12, 12)
        block_layout.setSpacing(8)

        header = QHBoxLayout()

        checkbox = QCheckBox()
        checkbox.setChecked(milestone["id"] in self.selected_milestone_ids)
        checkbox.setStyleSheet("""
            QCheckBox::indicator {
                width: 20px;
                height: 20px;
                border-radius: 6px;
                border: 2px solid #d2d2d7;
                background: white;
            }
            QCheckBox::indicator:checked {
                background: #007AFF;
                border: 2px solid #007AFF;
            }
        """)
        checkbox.stateChanged.connect(
            lambda state: self._toggle_milestone_selection(
                milestone["id"], state == Qt.CheckState.Checked.value))
        header.addWidget(checkbox)

        title_layout = QVBoxLayout()
        title_layout.setSpacing(3)

        title = QLabel(milestone.get("title", ""))
        title.setStyleSheet("""
            font-size: 15px;
            font-weight: bold;
            color: #1d1d1f;
        """)
        title_layout.addWidget(title)

        subtitle = QLabel(milestone.get("subtitle", ""))
        subtitle.setStyleSheet("""
            font-size: 10px;
            color: #86868b;
        """)
        title_layout.addWidget(subtitle)

        header.addLayout(title_layout, 1)

        btn_layout = QHBoxLayout()
        btn_layout.setSpacing(6)

        # 마일스톤 수정 버튼
        edit_milestone_btn = QPushButton("✏️ 제목 수정")
        edit_milestone_btn.setObjectName("secondary")
        edit_milestone_btn.clicked.connect(
            lambda: self._edit_milestone(milestone["id"]))
        btn_layout.addWidget(edit_milestone_btn)

        # 타임라인 확대 보기 버튼
        zoom_btn = QPushButton("🔍 확대 보기")
        zoom_btn.setObjectName("secondary")
        zoom_btn.clicked.connect(
            lambda: self._show_zoomable_timeline(milestone))
        btn_layout.addWidget(zoom_btn)

        add_btn = QPushButton("➕ Node 추가")
        add_btn.setStyleSheet("""
            QPushButton {
                background: #007AFF;
                color: white;
                border: none;
                border-radius: 6px;
                padding: 8px 12px;
                font-size: 11px;
                font-weight: bold;
            }
            QPushButton:hover {
                background: #1A8CFF;
            }
        """)
        add_btn.clicked.connect(
            lambda: self._add_node_to_milestone(milestone["id"]))
        btn_layout.addWidget(add_btn)

        edit_btn = QPushButton("✏️ Node 수정")
        edit_btn.setObjectName("secondary")
        edit_btn.clicked.connect(lambda: self._edit_node(milestone["id"]))
        btn_layout.addWidget(edit_btn)

        delete_btn = QPushButton("🗑️ Node 삭제")
        delete_btn.setStyleSheet("""
            QPushButton {
                background: #FF3B30;
                color: white;
                border: none;
                border-radius: 6px;
                padding: 8px 12px;
                font-size: 11px;
                font-weight: bold;
            }
            QPushButton:hover {
                background: #FF4D42;
            }
        """)
        delete_btn.clicked.connect(lambda: self._delete_node(milestone["id"]))
        btn_layout.addWidget(delete_btn)

        header.addLayout(btn_layout)

        block_layout.addLayout(header)

        # 카테고리 표시 (제목/부제목과 버튼들 사이)
        category_text = milestone.get("category", "")
        if category_text:
            category_layout = QHBoxLayout()
            category_layout.setContentsMargins(30, 5, 0, 5)
            
            category_label = QLabel(f"📁 {category_text}")
            category_label.setStyleSheet("""
                background: #E3F2FD;
                color: #007AFF;
                font-size: 11px;
                font-weight: bold;
                padding: 5px 12px;
                border-radius: 12px;
                border: 1px solid #007AFF;
            """)
            category_layout.addWidget(category_label)
            category_layout.addStretch()
            
            block_layout.addLayout(category_layout)

        timeline = TimelineCanvas(parent=block,
                                  milestone_data=milestone,
                                  on_node_click=lambda nd: self.
                                  _on_node_selected(milestone["id"], nd))
        # 메인 UI에서는 350px 고정 높이로 스크롤 없이 전체 표시
        timeline.setFixedHeight(350)
        block_layout.addWidget(timeline)

        # 위젯 반환 (추가는 호출하는 쪽에서)
        return block

    def _toggle_milestone_selection(self, milestone_id: str,
                                    is_selected: bool):
        """마일스톤 선택 토글"""
        if is_selected:
            self.selected_milestone_ids.add(milestone_id)
        else:
            self.selected_milestone_ids.discard(milestone_id)

    def _edit_milestone(self, milestone_id: str):
        """마일스톤 수정"""
        # 마일스톤 찾기
        milestone = None
        for m in self.data_manager.get_milestones():
            if m["id"] == milestone_id:
                milestone = m
                break

        if not milestone:
            self._show_message(QMessageBox.Icon.Warning, "경고",
                               "마일스톤을 찾을 수 없습니다.")
            return

        # 다이얼로그 열기
        dialog = MilestoneDialog(self, milestone_data=milestone)
        if dialog.exec() and dialog.result:
            self.data_manager.update_milestone(
                milestone_id,
                dialog.result["title"],
                dialog.result["subtitle"],
                dialog.result.get("category", "")
            )
            self._refresh_ui()

    def _add_node_to_milestone(self, milestone_id: str):
        """노드 추가"""
        dialog = NodeDialog(self)
        if dialog.exec() and dialog.result:
            self.data_manager.add_node(milestone_id, dialog.result)
            self._refresh_ui()

    def _on_node_selected(self, milestone_id: str, node_data: Optional[Dict]):
        """노드 선택 - 마일스톤별로 독립적으로 관리"""
        self.selected_nodes_by_milestone[milestone_id] = node_data

    def _edit_node(self, milestone_id: str):
        """노드 수정 - 해당 마일스톤의 선택된 노드만 수정"""
        selected_node = self.selected_nodes_by_milestone.get(milestone_id)
        if not selected_node:
            self._show_message(QMessageBox.Icon.Warning, "경고",
                               "수정할 노드를 먼저 선택해주세요.")
            return

        dialog = NodeDialog(self, node_data=selected_node)
        if dialog.exec() and dialog.result:
            self.data_manager.update_node(milestone_id, selected_node["id"],
                                          dialog.result)
            self.selected_nodes_by_milestone[milestone_id] = None
            self._refresh_ui()

    def _delete_node(self, milestone_id: str):
        """노드 삭제 - 해당 마일스톤의 선택된 노드만 삭제"""
        selected_node = self.selected_nodes_by_milestone.get(milestone_id)
        if not selected_node:
            self._show_message(QMessageBox.Icon.Warning, "경고",
                               "삭제할 노드를 먼저 선택해주세요.")
            return

        msg = QMessageBox(self)
        msg.setIcon(QMessageBox.Icon.Question)
        msg.setWindowTitle("확인")
        msg.setText("선택한 노드를 삭제하시겠습니까?")
        msg.setStandardButtons(QMessageBox.StandardButton.Yes
                               | QMessageBox.StandardButton.No)
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
        reply = msg.exec()

        if reply == QMessageBox.StandardButton.Yes:
            self.data_manager.delete_node(milestone_id, selected_node["id"])
            self.selected_nodes_by_milestone[milestone_id] = None
            self._refresh_ui()

    def _delete_node_shortcut(self):
        """단축키로 노드 삭제 - 선택된 노드 삭제"""
        # 노드가 선택된 마일스톤 찾기
        for milestone_id, selected_node in self.selected_nodes_by_milestone.items(
        ):
            if selected_node:
                self._delete_node(milestone_id)
                return

        self._show_message(QMessageBox.Icon.Warning, "경고", "먼저 노드를 선택해주세요.")

    def _show_zoomable_timeline(self, milestone: Dict):
        """타임라인 확대 보기 다이얼로그 표시"""
        dialog = ZoomableTimelineDialog(self, milestone)
        dialog.exec()

    def _on_keyword_filter_changed(self, selected_keywords: List[str]):
        """키워드 필터 변경 핸들러"""
        # 키워드가 선택되면 필터 적용
        if selected_keywords:
            self.filter_settings = {
                "type": "keyword",
                "keywords": selected_keywords
            }
            self._update_filter_status()
        else:
            # 키워드가 없으면 필터 해제
            if self.filter_settings and self.filter_settings.get(
                    "type") == "keyword":
                self.clear_filter()
                return  # clear_filter()가 _refresh_ui()를 호출하므로 여기서 종료

        # Milestone List 선택 초기화 (키워드 변경 시)
        self.milestone_list_block.clear_selection()
        self.selected_milestone_id_from_list = None

        # UI 갱신
        self._refresh_ui()
    
    def _on_milestone_list_selected(self, milestone_id: str):
        """Milestone List에서 선택 시 핸들러"""
        self.selected_milestone_id_from_list = milestone_id
        
        # 선택된 마일스톤의 제목 찾기
        milestone_title = ""
        for m in self.filtered_milestones:
            if m.get("id") == milestone_id:
                milestone_title = m.get("title", "")
                break
        
        # 필터 설정 업데이트 (기존 키워드 필터는 유지하고 마일스톤 선택 추가)
        if self.filter_settings and self.filter_settings.get("type") == "keyword":
            # 키워드 필터가 있으면 마일스톤 선택 정보 추가
            self.filter_settings["milestone_list_id"] = milestone_id
            self.filter_settings["milestone_list_title"] = milestone_title
        else:
            # 키워드 필터가 없으면 마일스톤 선택만 설정
            self.filter_settings = {
                "type": "milestone_list",
                "milestone_list_id": milestone_id,
                "milestone_list_title": milestone_title
            }
        
        # 필터 상태 표시 업데이트
        self._update_filter_status()
        
        # 행3에 해당 마일스톤만 표시하도록 UI 갱신
        self._show_current_milestone_for_row3()

    def _show_previous_milestone(self):
        """이전 마일스톤 표시"""
        if self.current_milestone_index > 0:
            self.current_milestone_index -= 1
            self._show_current_milestone_for_row3()

    def _show_next_milestone(self):
        """다음 마일스톤 표시"""
        if self.current_milestone_index < len(self.filtered_milestones) - 1:
            self.current_milestone_index += 1
            self._show_current_milestone_for_row3()

    def _show_current_milestone_for_row3(self):
        """행3에 마일스톤 표시 - Milestone List 선택 고려"""
        # 기존 위젯 제거
        for i in reversed(range(self.milestone_layout.count())):
            widget = self.milestone_layout.itemAt(i).widget()
            if widget:
                widget.deleteLater()

        # Milestone List에서 선택된 마일스톤이 있으면 해당 마일스톤만 표시
        if self.selected_milestone_id_from_list:
            # filtered_milestones에서 해당 마일스톤 찾기
            selected_milestone = None
            for m in self.filtered_milestones:
                if m.get("id") == self.selected_milestone_id_from_list:
                    selected_milestone = m
                    break
            
            if selected_milestone:
                milestone_widget = self._create_milestone_block(selected_milestone)
                self.milestone_layout.addWidget(milestone_widget)
                
                # 페이지네이션 비활성화 (단일 마일스톤만 표시)
                self.prev_btn.setEnabled(False)
                self.next_btn.setEnabled(False)
                self.milestone_nav_label.setText("1 / 1")
            else:
                # 선택된 마일스톤이 필터링된 목록에 없음
                no_data_label = QLabel("선택된 마일스톤이 필터링되어 표시되지 않습니다.")
                no_data_label.setStyleSheet("""
                    font-size: 14px;
                    color: #86868b;
                    padding: 50px;
                """)
                no_data_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
                self.milestone_layout.addWidget(no_data_label)
                
                self.prev_btn.setEnabled(False)
                self.next_btn.setEnabled(False)
                self.milestone_nav_label.setText("0 / 0")
            return

        # Milestone List 선택이 없으면 기존 페이지네이션 방식
        # 마일스톤이 없으면 빈 메시지 표시
        if not self.filtered_milestones:
            no_data_label = QLabel("마일스톤이 없습니다.")
            no_data_label.setStyleSheet("""
                font-size: 14px;
                color: #86868b;
                padding: 50px;
            """)
            no_data_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            self.milestone_layout.addWidget(no_data_label)

            self.prev_btn.setEnabled(False)
            self.next_btn.setEnabled(False)
            self.milestone_nav_label.setText("0 / 0")
            return

        # 현재 마일스톤 표시
        current_milestone = self.filtered_milestones[
            self.current_milestone_index]
        milestone_widget = self._create_milestone_block(current_milestone)
        self.milestone_layout.addWidget(milestone_widget)

        # 네비게이션 업데이트
        total = len(self.filtered_milestones)
        current = self.current_milestone_index + 1
        self.milestone_nav_label.setText(f"{current} / {total}")

        # 버튼 활성화/비활성화
        self.prev_btn.setEnabled(self.current_milestone_index > 0)
        self.next_btn.setEnabled(self.current_milestone_index < total - 1)

    def _show_milestone_tree(self):
        """Milestone Tree 다이얼로그 표시"""
        # 모든 마일스톤 가져오기 (필터링 없이)
        all_milestones = self.data_manager.get_milestones()
        
        if not all_milestones:
            self._show_message(QMessageBox.Icon.Information, "안내",
                               "마일스톤이 없습니다.\n먼저 마일스톤을 생성해주세요.")
            return
        
        # Milestone Tree 다이얼로그 열기
        dialog = MilestoneTreeDialog(self, all_milestones)
        dialog.milestone_selected.connect(self._on_milestone_selected_from_tree)
        dialog.exec()
    
    def _on_milestone_selected_from_tree(self, milestone_id: str):
        """Milestone Tree에서 마일스톤 선택 시 - Milestone List Block과 동일한 방식으로 처리"""
        # Milestone List Block의 선택도 동기화
        self.milestone_list_block.select_milestone(milestone_id)
        
        # Milestone List 선택 핸들러 호출 (필터링 및 표시 처리)
        self._on_milestone_list_selected(milestone_id)
