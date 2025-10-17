"""Milestone Manager - 애플리케이션 진입점
로그인 및 라이선스 체크 후 메인 윈도우 실행
"""

import sys
from PyQt6.QtWidgets import QApplication, QDialog, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QPushButton, QMessageBox
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont
from datetime import datetime

from ui_main_window import MainWindow


class LoginWindow(QDialog):
    """애플 스타일의 로그인 윈도우 - 라이트 모드"""
    
    VALID_USERNAME = "MCI"
    VALID_PASSWORD = "mci2025!"
    EXPIRY_DATE = "2025-12-31"
    
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Milestone Manager - Login")
        self.setFixedSize(450, 450)
        self.setModal(True)
        
        self.authenticated = False
        
        self.setStyleSheet("""
            QDialog {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #f5f5f7, stop:1 #e8e8ed);
            }
            QLabel {
                color: #1d1d1f;
            }
            QLineEdit {
                background-color: white;
                border: 1px solid #d2d2d7;
                border-radius: 10px;
                padding: 14px 16px;
                color: #1d1d1f;
                font-size: 15px;
                min-height: 20px;
            }
            QLineEdit:focus {
                border: 2px solid #007AFF;
                background-color: white;
            }
            QPushButton {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #007AFF, stop:1 #0051D5);
                border: none;
                border-radius: 10px;
                color: white;
                padding: 16px 24px;
                font-size: 16px;
                font-weight: bold;
                min-height: 20px;
            }
            QPushButton:hover {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #1A8CFF, stop:1 #0062E6);
            }
            QPushButton:pressed {
                background: #0051D5;
            }
        """)
        
        self._check_license()
        self._create_ui()
    
    def _check_license(self):
        """라이선스 만료일 체크"""
        try:
            expiry = datetime.strptime(self.EXPIRY_DATE, "%Y-%m-%d")
            today = datetime.now()
            
            if today > expiry:
                msg = QMessageBox(self)
                msg.setIcon(QMessageBox.Icon.Critical)
                msg.setWindowTitle("라이선스 만료")
                msg.setText(f"프로그램 사용 기간이 만료되었습니다.\n만료일: {self.EXPIRY_DATE}")
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
                sys.exit(0)
            
            remaining_days = (expiry - today).days
            if remaining_days <= 30:
                msg = QMessageBox(self)
                msg.setIcon(QMessageBox.Icon.Warning)
                msg.setWindowTitle("라이선스 경고")
                msg.setText(f"프로그램 사용 기간이 {remaining_days}일 남았습니다.\n만료일: {self.EXPIRY_DATE}")
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
        except Exception as e:
            msg = QMessageBox(self)
            msg.setIcon(QMessageBox.Icon.Critical)
            msg.setWindowTitle("오류")
            msg.setText(f"라이선스 체크 실패: {str(e)}")
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
            sys.exit(1)
    
    def _create_ui(self):
        """로그인 UI 구성"""
        layout = QVBoxLayout()
        layout.setContentsMargins(40, 40, 40, 40)
        layout.setSpacing(20)
        
        title = QLabel("Milestone Manager")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title.setFont(QFont("Apple SD Gothic Neo", 28, QFont.Weight.Bold))
        title.setStyleSheet("color: #1d1d1f; margin: 20px 0px;")
        title.setMinimumHeight(60)
        layout.addWidget(title)
        
        license_info = QLabel(f"라이선스 만료일: {self.EXPIRY_DATE}")
        license_info.setAlignment(Qt.AlignmentFlag.AlignCenter)
        license_info.setStyleSheet("color: #86868b; font-size: 12px; margin-bottom: 20px;")
        layout.addWidget(license_info)
        
        username_label = QLabel("Username")
        username_label.setStyleSheet("font-size: 14px; margin-top: 10px; color: #1d1d1f;")
        layout.addWidget(username_label)
        
        self.username_input = QLineEdit()
        self.username_input.setPlaceholderText("사용자 이름을 입력하세요")
        layout.addWidget(self.username_input)
        
        password_label = QLabel("Password")
        password_label.setStyleSheet("font-size: 14px; margin-top: 10px; color: #1d1d1f;")
        layout.addWidget(password_label)
        
        self.password_input = QLineEdit()
        self.password_input.setPlaceholderText("비밀번호를 입력하세요")
        self.password_input.setEchoMode(QLineEdit.EchoMode.Password)
        self.password_input.returnPressed.connect(self._login)
        layout.addWidget(self.password_input)
        
        login_btn = QPushButton("로그인")
        login_btn.clicked.connect(self._login)
        layout.addWidget(login_btn, 0, Qt.AlignmentFlag.AlignCenter)
        
        layout.addStretch()
        
        self.setLayout(layout)
    
    def _login(self):
        """로그인 처리"""
        username = self.username_input.text().strip()
        password = self.password_input.text().strip()
        
        if username == self.VALID_USERNAME and password == self.VALID_PASSWORD:
            self.authenticated = True
            self.accept()
        else:
            msg = QMessageBox(self)
            msg.setIcon(QMessageBox.Icon.Critical)
            msg.setWindowTitle("로그인 실패")
            msg.setText("아이디 또는 비밀번호가 올바르지 않습니다.")
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
            self.password_input.clear()


def main():
    """애플리케이션 메인 함수"""
    app = QApplication(sys.argv)
    app.setStyle("Fusion")
    
    login_window = LoginWindow()
    
    if login_window.exec() == QDialog.DialogCode.Accepted and login_window.authenticated:
        main_window = MainWindow()
        main_window.show()
        sys.exit(app.exec())
    else:
        print("로그인이 취소되었습니다.")
        sys.exit(0)


if __name__ == "__main__":
    main()
