"""Milestone Manager - 애플리케이션 진입점
로그인 및 라이선스 체크 후 메인 윈도우 실행
"""

import customtkinter as ctk
from tkinter import messagebox
from datetime import datetime

from ui_main_window import MainWindow


class LoginWindow(ctk.CTk):
    """로그인 및 라이선스 체크 윈도우"""
    
    VALID_USERNAME = "MCI"
    VALID_PASSWORD = "mci2025!"
    EXPIRY_DATE = "2025-12-31"
    
    def __init__(self):
        super().__init__()
        
        self.title("Milestone Manager - Login")
        self.geometry("400x350")
        self.resizable(False, False)
        
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("blue")
        
        self.authenticated = False
        
        self._check_license()
        self._create_ui()
        
        self.protocol("WM_DELETE_WINDOW", self._on_closing)
    
    def _check_license(self):
        """라이선스 만료일 체크"""
        try:
            expiry = datetime.strptime(self.EXPIRY_DATE, "%Y-%m-%d")
            today = datetime.now()
            
            if today > expiry:
                messagebox.showerror(
                    "라이선스 만료",
                    f"프로그램 사용 기간이 만료되었습니다.\n만료일: {self.EXPIRY_DATE}"
                )
                self.quit()
                return
            
            remaining_days = (expiry - today).days
            if remaining_days <= 30:
                messagebox.showwarning(
                    "라이선스 경고",
                    f"프로그램 사용 기간이 {remaining_days}일 남았습니다.\n만료일: {self.EXPIRY_DATE}"
                )
        except Exception as e:
            messagebox.showerror("오류", f"라이선스 체크 실패: {str(e)}")
            self.quit()
    
    def _create_ui(self):
        """로그인 UI 구성"""
        ctk.CTkLabel(
            self,
            text="🎯 Milestone Manager",
            font=("Arial", 24, "bold")
        ).pack(pady=30)
        
        ctk.CTkLabel(
            self,
            text=f"라이선스 만료일: {self.EXPIRY_DATE}",
            font=("Arial", 10),
            text_color="#AAAAAA"
        ).pack(pady=5)
        
        ctk.CTkLabel(self, text="Username:", font=("Arial", 12)).pack(pady=(20, 5))
        self.username_entry = ctk.CTkEntry(self, width=300, placeholder_text="사용자 이름 입력")
        self.username_entry.pack(pady=5)
        
        ctk.CTkLabel(self, text="Password:", font=("Arial", 12)).pack(pady=(10, 5))
        self.password_entry = ctk.CTkEntry(self, width=300, show="*", 
                                           placeholder_text="비밀번호 입력")
        self.password_entry.pack(pady=5)
        
        self.password_entry.bind("<Return>", lambda e: self._login())
        
        ctk.CTkButton(
            self,
            text="로그인",
            command=self._login,
            width=300,
            height=40,
            font=("Arial", 14, "bold")
        ).pack(pady=30)
    
    def _login(self):
        """로그인 처리"""
        username = self.username_entry.get().strip()
        password = self.password_entry.get().strip()
        
        if username == self.VALID_USERNAME and password == self.VALID_PASSWORD:
            self.authenticated = True
            self.destroy()
        else:
            messagebox.showerror("로그인 실패", "아이디 또는 비밀번호가 올바르지 않습니다.")
            self.password_entry.delete(0, 'end')
    
    def _on_closing(self):
        """창 닫기 이벤트"""
        self.authenticated = False
        self.destroy()


def main():
    """애플리케이션 메인 함수"""
    login_window = LoginWindow()
    login_window.mainloop()
    
    if login_window.authenticated:
        main_window = MainWindow()
        main_window.mainloop()
    else:
        print("로그인이 취소되었습니다.")


if __name__ == "__main__":
    main()
