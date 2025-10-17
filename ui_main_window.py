"""메인 UI 윈도우 모듈 - 라이트 모드 디자인"""

from PyQt6.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
                              QPushButton, QScrollArea, QLabel, QCheckBox,
                              QFrame, QMessageBox, QFileDialog)
from PyQt6.QtCore import Qt, QSize
from PyQt6.QtGui import QShortcut, QKeySequence, QPixmap, QPainter
from typing import List, Dict, Set, Optional

from data_manager import DataManager
from custom_widgets import MilestoneDialog, NodeDialog, SearchFilterDialog
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
        self.selected_nodes_by_milestone: Dict[str, Optional[Dict]] = {}  # 마일스톤별 선택된 노드
        self.filter_settings = None
        
        self.setStyleSheet("""
            QMainWindow {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #f5f5f7, stop:1 #ffffff);
            }
            QPushButton {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #007AFF, stop:1 #0051D5);
                border: none;
                border-radius: 6px;
                color: white;
                padding: 8px 16px;
                font-size: 13px;
                font-weight: bold;
                min-height: 10px;
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
        """UI 구성"""
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        main_layout = QVBoxLayout(central_widget)
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(15)
        
        title_label = QLabel("Milestone Manager")
        title_label.setStyleSheet("""
            font-size: 22px;
            font-weight: bold;
            color: #1d1d1f;
            margin-bottom: 5px;
            padding: 5px;
        """)
        main_layout.addWidget(title_label)
        
        # 데이터 상태 표시 레이블
        self.data_status_label = QLabel("⚠️ 데이터 없음")
        self.data_status_label.setStyleSheet("""
            color: #FF9500;
            font-size: 12px;
            padding: 4px 8px;
            background: #FFF3E0;
            border-radius: 4px;
            margin-bottom: 8px;
        """)
        main_layout.addWidget(self.data_status_label)
        
        toolbar = QHBoxLayout()
        toolbar.setSpacing(10)
        
        load_btn = QPushButton("📂 Data Load (Ctrl+L)")
        load_btn.clicked.connect(self.load_data)
        toolbar.addWidget(load_btn)
        
        save_btn = QPushButton("💾 Data 저장 (Ctrl+S)")
        save_btn.clicked.connect(self.save_data)
        toolbar.addWidget(save_btn)
        
        create_btn = QPushButton("➕ Milestone 생성")
        create_btn.clicked.connect(self.create_milestone)
        toolbar.addWidget(create_btn)
        
        delete_btn = QPushButton("🗑️ 선택 삭제")
        delete_btn.setObjectName("danger")
        delete_btn.clicked.connect(self.delete_selected_milestones)
        toolbar.addWidget(delete_btn)
        
        search_btn = QPushButton("🔍 검색/필터")
        search_btn.setObjectName("secondary")
        search_btn.clicked.connect(self.open_search_filter)
        toolbar.addWidget(search_btn)
        
        this_month_btn = QPushButton("📌 이번달 일정")
        this_month_btn.setObjectName("secondary")
        this_month_btn.clicked.connect(self.filter_this_month)
        toolbar.addWidget(this_month_btn)
        
        export_btn = QPushButton("📤 이미지 내보내기")
        export_btn.setObjectName("secondary")
        export_btn.clicked.connect(self.export_image)
        toolbar.addWidget(export_btn)
        
        toolbar.addStretch()
        
        # 필터 상태 표시 레이블
        self.filter_status_label = QLabel("")
        self.filter_status_label.setStyleSheet("""
            color: #007AFF;
            font-size: 13px;
            font-weight: bold;
            padding: 8px 12px;
            background: #E3F2FD;
            border-radius: 6px;
        """)
        self.filter_status_label.hide()
        toolbar.addWidget(self.filter_status_label)
        
        # 필터 해제 버튼
        self.clear_filter_btn = QPushButton("✖ 필터 해제")
        self.clear_filter_btn.setObjectName("secondary")
        self.clear_filter_btn.clicked.connect(self.clear_filter)
        self.clear_filter_btn.hide()
        toolbar.addWidget(self.clear_filter_btn)
        
        main_layout.addLayout(toolbar)
        
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        
        scroll_content = QWidget()
        self.scroll_layout = QVBoxLayout(scroll_content)
        self.scroll_layout.setSpacing(20)
        self.scroll_layout.setContentsMargins(10, 10, 10, 10)
        
        scroll.setWidget(scroll_content)
        main_layout.addWidget(scroll)
    
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
                self._show_message(QMessageBox.Icon.Information, "성공", "데이터를 성공적으로 불러왔습니다.")
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
            msg.setStandardButtons(QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
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
            
            data = {"milestones": milestones}
            self.data_manager.save_data(data)
            self._update_data_status()
            
            backup_msg = "\n(백업: raw.json.backup)" if os.path.exists("raw.json.backup") else ""
            self._show_message(QMessageBox.Icon.Information, "성공", f"데이터가 저장되었습니다.{backup_msg}")
        except Exception as e:
            self._show_message(QMessageBox.Icon.Critical, "오류", str(e))
    
    def create_milestone(self):
        """마일스톤 생성"""
        dialog = MilestoneDialog(self)
        if dialog.exec() and dialog.result:
            self.data_manager.add_milestone(
                dialog.result["title"],
                dialog.result["subtitle"]
            )
            self._refresh_ui()
    
    def delete_selected_milestones(self):
        """선택된 마일스톤 삭제"""
        if not self.selected_milestone_ids:
            self._show_message(QMessageBox.Icon.Warning, "경고", "삭제할 마일스톤을 선택해주세요.")
            return
        
        count = len(self.selected_milestone_ids)
        msg = QMessageBox(self)
        msg.setIcon(QMessageBox.Icon.Question)
        msg.setWindowTitle("확인")
        msg.setText(f"{count}개의 마일스톤을 삭제하시겠습니까?")
        msg.setStandardButtons(QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
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
    
    def clear_filter(self):
        """필터 해제"""
        self.filter_settings = None
        self._update_filter_status()
        self._refresh_ui()
    
    def _update_filter_status(self):
        """필터 상태 표시 업데이트"""
        if self.filter_settings:
            status_parts = []
            keyword = self.filter_settings.get("keyword", "")
            shape = self.filter_settings.get("shape", "")
            this_month = self.filter_settings.get("this_month", False)
            
            if this_month:
                current_month = self.filter_settings.get("current_month", 0)
                status_parts.append(f"📌 이번달 일정 ({current_month}월)")
            if keyword:
                status_parts.append(f"키워드: '{keyword}'")
            if shape:
                status_parts.append(f"모양: {shape}")
            
            if status_parts:
                self.filter_status_label.setText("🔍 필터 적용 중: " + " | ".join(status_parts))
                self.filter_status_label.show()
                self.clear_filter_btn.show()
        else:
            self.filter_status_label.hide()
            self.clear_filter_btn.hide()
    
    def export_image(self):
        """이미지 내보내기 - Milestone_IMG 폴더에 블록별로 분리 저장"""
        if not self.milestone_widgets:
            self._show_message(QMessageBox.Icon.Warning, "경고", "내보낼 마일스톤이 없습니다.")
            return
        
        filename, _ = QFileDialog.getSaveFileName(
            self, "이미지 저장 (Milestone_IMG 폴더에 블록별로 저장됩니다)",
            "",
            "PNG Files (*.png);;JPG Files (*.jpg)"
        )
        
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
                for i, widget in enumerate(self.milestone_widgets, 1):
                    pixmap = widget.grab()
                    output_filename = os.path.join(img_folder, f"{base_name}_{i}{extension}")
                    pixmap.save(output_filename)
                    saved_files.append(output_filename)
                
                files_list = "\n".join([f"  • {os.path.basename(f)}" for f in saved_files])
                self._show_message(
                    QMessageBox.Icon.Information, 
                    "성공", 
                    f"{len(saved_files)}개의 이미지가 Milestone_IMG 폴더에 저장되었습니다:\n{files_list}"
                )
            except Exception as e:
                self._show_message(QMessageBox.Icon.Critical, "오류", f"이미지 저장 실패: {str(e)}")
    
    def _refresh_ui(self):
        """UI 새로고침"""
        while self.scroll_layout.count():
            item = self.scroll_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
        
        self.milestone_widgets.clear()
        
        milestones = self.data_manager.get_milestones()
        
        if not milestones:
            empty_label = QLabel("마일스톤이 없습니다. '➕ Milestone 생성' 버튼을 눌러 시작하세요.")
            empty_label.setStyleSheet("""
                color: #86868b;
                font-size: 16px;
                padding: 40px;
            """)
            empty_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            self.scroll_layout.addWidget(empty_label)
            return
        
        for milestone in milestones:
            if self._should_show_milestone(milestone):
                self._create_milestone_block(milestone)
        
        self.scroll_layout.addStretch()
    
    def _update_data_status(self):
        """데이터 상태 레이블 업데이트"""
        milestones = self.data_manager.get_milestones()
        count = len(milestones)
        
        if count == 0:
            self.data_status_label.setText("⚠️ 데이터 없음")
            self.data_status_label.setStyleSheet("""
                color: #FF9500;
                font-size: 12px;
                padding: 4px 8px;
                background: #FFF3E0;
                border-radius: 4px;
                margin-bottom: 8px;
            """)
        else:
            self.data_status_label.setText(f"✅ 데이터 로드됨 ({count}개 마일스톤)")
            self.data_status_label.setStyleSheet("""
                color: #34C759;
                font-size: 12px;
                padding: 4px 8px;
                background: #E8F5E9;
                border-radius: 4px;
                margin-bottom: 8px;
            """)
    
    def _should_show_milestone(self, milestone: Dict) -> bool:
        """필터링 - 제목과 부제목에서만 검색"""
        if not self.filter_settings:
            return True
        
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
        
        # 키워드 검색: 제목과 부제목에서만
        if keyword:
            title = milestone.get("title", "").lower()
            subtitle = milestone.get("subtitle", "").lower()
            if keyword.lower() not in title and keyword.lower() not in subtitle:
                return False
        
        # 모양 필터
        if shape_filter:
            has_matching_shape = any(
                node.get("shape") == shape_filter
                for node in milestone.get("nodes", [])
            )
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
        block_layout.setContentsMargins(15, 15, 15, 15)
        block_layout.setSpacing(10)
        
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
            lambda state: self._toggle_milestone_selection(milestone["id"], state == Qt.CheckState.Checked.value)
        )
        header.addWidget(checkbox)
        
        title_layout = QVBoxLayout()
        title_layout.setSpacing(5)
        
        title = QLabel(milestone.get("title", ""))
        title.setStyleSheet("""
            font-size: 18px;
            font-weight: bold;
            color: #1d1d1f;
        """)
        title_layout.addWidget(title)
        
        subtitle = QLabel(milestone.get("subtitle", ""))
        subtitle.setStyleSheet("""
            font-size: 12px;
            color: #86868b;
        """)
        title_layout.addWidget(subtitle)
        
        header.addLayout(title_layout, 1)
        
        btn_layout = QHBoxLayout()
        btn_layout.setSpacing(10)
        
        add_btn = QPushButton("➕ Node 추가")
        add_btn.clicked.connect(lambda: self._add_node_to_milestone(milestone["id"]))
        btn_layout.addWidget(add_btn)
        
        edit_btn = QPushButton("✏️ Node 수정")
        edit_btn.setObjectName("secondary")
        edit_btn.clicked.connect(lambda: self._edit_node(milestone["id"]))
        btn_layout.addWidget(edit_btn)
        
        delete_btn = QPushButton("🗑️ Node 삭제 (Ctrl+D)")
        delete_btn.setObjectName("danger")
        delete_btn.clicked.connect(lambda: self._delete_node(milestone["id"]))
        btn_layout.addWidget(delete_btn)
        
        header.addLayout(btn_layout)
        
        block_layout.addLayout(header)
        
        timeline = TimelineCanvas(
            parent=block,
            milestone_data=milestone,
            on_node_click=lambda nd: self._on_node_selected(milestone["id"], nd)
        )
        timeline.setMinimumHeight(400)
        block_layout.addWidget(timeline)
        
        self.scroll_layout.addWidget(block)
        self.milestone_widgets.append(block)
    
    def _toggle_milestone_selection(self, milestone_id: str, is_selected: bool):
        """마일스톤 선택 토글"""
        if is_selected:
            self.selected_milestone_ids.add(milestone_id)
        else:
            self.selected_milestone_ids.discard(milestone_id)
    
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
            self._show_message(QMessageBox.Icon.Warning, "경고", "수정할 노드를 먼저 선택해주세요.")
            return
        
        dialog = NodeDialog(self, node_data=selected_node)
        if dialog.exec() and dialog.result:
            self.data_manager.update_node(
                milestone_id,
                selected_node["id"],
                dialog.result
            )
            self.selected_nodes_by_milestone[milestone_id] = None
            self._refresh_ui()
    
    def _delete_node(self, milestone_id: str):
        """노드 삭제 - 해당 마일스톤의 선택된 노드만 삭제"""
        selected_node = self.selected_nodes_by_milestone.get(milestone_id)
        if not selected_node:
            self._show_message(QMessageBox.Icon.Warning, "경고", "삭제할 노드를 먼저 선택해주세요.")
            return
        
        msg = QMessageBox(self)
        msg.setIcon(QMessageBox.Icon.Question)
        msg.setWindowTitle("확인")
        msg.setText("선택한 노드를 삭제하시겠습니까?")
        msg.setStandardButtons(QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
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
        for milestone_id, selected_node in self.selected_nodes_by_milestone.items():
            if selected_node:
                self._delete_node(milestone_id)
                return
        
        self._show_message(QMessageBox.Icon.Warning, "경고", "먼저 노드를 선택해주세요.")
