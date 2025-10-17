# Milestone Manager 코딩 모범 사례 (Coding Best Practices)

이 문서는 Milestone Manager 프로젝트의 코드 품질, 가독성, 유지보수성을 높이기 위한 코딩 스타일 가이드와 모범 사례를 정의한다. 모든 프로젝트 기여자는 이 문서를 따르는 것을 원칙으로 한다.

---

### 1. 명명 규칙 (Naming Conventions)

> **"이름만 보고도 변수와 함수의 의도를 파악할 수 있어야 한다."**

코드의 가독성을 높이기 위해 파이썬 표준 스타일 가이드인 **PEP 8**의 명명 규칙을 따른다.

* **변수(Variables) 및 함수(Functions):**
  * 소문자와 밑줄(`_`)을 조합하는 `snake_case`를 사용한다.
  * `예시: milestone_block, calculate_node_position(), save_data_to_json()`

* **클래스(Classes):**
  * 각 단어의 첫 글자를 대문자로 하는 `PascalCase` (또는 `CapWords`)를 사용한다.
  * `예시: MilestoneBlock, NodeDialog, TimelineCanvas`

* **상수(Constants):**
  * 전체를 대문자로 하고 밑줄로 단어를 구분하는 `UPPERCASE_SNAKE_CASE`를 사용한다.
  * `예시: MAX_TIMELINE_ZOOM, DEFAULT_NODE_COLOR`

* **파일(Files):**
  * `snake_case`를 사용하여 모듈의 역할을 명확히 한다.
  * `예시: data_manager.py, ui_components.py`

---

### 2. 코드 구조화 (Code Structure)

> **"코드는 논리적인 단위로 분리되어야 한다."**

**단일 책임 원칙 (Single Responsibility Principle, SRP)**을 적용하여 코드의 복잡도를 낮춘다.

* **모듈 분리:** 기능별로 파일을 분리하여 관리한다.
  * `main.py`: 애플리케이션의 시작점.
  * `ui_main_window.py`: 메인 GUI 창의 레이아웃과 위젯 관리.
  * `data_manager.py`: `raw.json` 파일의 읽기/쓰기 등 데이터 처리 로직 담당.
  * `timeline_canvas.py`: 타임라인과 노드를 직접 그리는 시각화 로직 담당.
  * `custom_widgets.py`: 커스텀 다이얼로그나 버튼 등 재사용 가능한 위젯 모음.

* **로직과 UI의 분리:** GUI 코드(버튼 클릭, 화면 표시 등)와 핵심 로직(데이터 계산, 파일 처리 등)을 최대한 분리한다. 이를 통해 UI가 변경되어도 핵심 로직은 영향을 받지 않도록 한다.

---

### 3. 주석과 문서화 (Comments and Docstrings)

> **"코드는 '무엇을' 하는지 보여주고, 주석은 '왜' 그렇게 하는지 설명한다."**

* **인라인 주석 (`#`):**
  * 복잡하거나, 직관적이지 않거나, 최적화를 위해 특별한 방법을 사용한 코드 라인에 대해 **'왜'** 그렇게 작성했는지를 설명하기 위해 사용한다.
  * 코드가 무엇을 하는지 설명하는 주석은 지양한다. (좋은 코드와 변수명은 그 자체로 설명이 되어야 한다.)

* **독스트링 (Docstrings, `"""..."""`):**
  * 모든 **클래스, 함수, 모듈**의 시작 부분에 독스트링을 작성하여 해당 코드 조각의 **목적, 인자(Arguments), 반환 값(Returns)**을 명확히 설명한다.
  * **예시 (Google Python Style):**
    ```python
    def create_node(parent, node_data):
        """타임라인 위에 새로운 노드를 생성하고 표시합니다.
    
        Args:
            parent (QWidget): 노드가 그려질 부모 위젯 (캔버스).
            node_data (dict): 노드 생성을 위한 데이터 (모양, 색상, 날짜 등).
    
        Returns:
            NodeWidget: 생성된 노드 객체.
        """
        # ... 함수 내용 ...
        pass
    ```

---

### 4. 에러 처리 (Error Handling)

> **"예상 가능한 오류는 프로그램의 비정상적인 종료로 이어져서는 안 된다."**

* 파일 입/출력(`raw.json` 읽기/쓰기), 데이터 파싱 등 실패할 가능성이 있는 코드 블록은 `try...except` 구문을 사용하여 예외 상황을 적절히 처리한다.
* 사용자에게 오류가 발생했음을 알리는 명확한 메시지(예: "raw.json 파일을 찾을 수 없습니다.")를 다이얼로그 창으로 보여준다.

---

### 5. 버전 관리 (Version Control)

* **Git**을 사용하여 모든 코드 변경 사항을 추적한다.
* **커밋 메시지:** 변경된 내용을 명확하게 알 수 있도록 작성한다. (예: `Feat: 노드 겹침 방지 알고리즘 추가`, `Fix: 데이터 저장 시 날짜 형식 오류 수정`)
* **작은 단위 커밋:** 하나의 기능 추가나 버그 수정 등 논리적인 최소 단위로 커밋하여 변경 사항을 추적하기 쉽게 만든다.

---

### 6. 의존성 관리 (Dependency Management)

* 프로젝트에 필요한 외부 라이브러리(PyQt6, CustomTkinter 등)는 `requirements.txt` 파일에 명시하여 관리한다.
* 이를 통해 다른 환경에서도 `pip install -r requirements.txt` 명령 한 번으로 동일한 개발 환경을 쉽게 구축할 수 있다.

