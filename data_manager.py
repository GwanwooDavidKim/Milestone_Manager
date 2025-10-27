"""데이터 관리 모듈 - raw.json 파일 읽기/쓰기 및 데이터 구조 관리"""

import json
import os
from typing import Dict, List, Optional
from datetime import datetime


class DataManager:
    """raw.json 파일의 읽기/쓰기 등 데이터 처리 로직을 담당하는 클래스"""
    
    def __init__(self, filename: str = "raw.json"):
        """
        Args:
            filename (str): 저장할 JSON 파일명 (기본값: raw.json)
        """
        self.filename = filename
        self.data = {"milestones": []}
    
    def load_data(self) -> Dict:
        """raw.json 파일을 불러옵니다.
        
        Returns:
            Dict: 불러온 데이터 딕셔너리
        """
        try:
            if os.path.exists(self.filename):
                with open(self.filename, 'r', encoding='utf-8') as f:
                    self.data = json.load(f)
                return self.data
            else:
                return {"milestones": []}
        except Exception as e:
            raise Exception(f"raw.json 파일을 불러올 수 없습니다: {str(e)}")
    
    def save_data(self, data: Dict) -> None:
        """현재 데이터를 raw.json 파일에 저장합니다.
        
        Args:
            data (Dict): 저장할 데이터 딕셔너리
        """
        try:
            self.data = data
            with open(self.filename, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
        except Exception as e:
            raise Exception(f"데이터 저장 중 오류 발생: {str(e)}")
    
    def get_milestones(self) -> List[Dict]:
        """모든 마일스톤 목록을 반환합니다.
        
        Returns:
            List[Dict]: 마일스톤 리스트
        """
        return self.data.get("milestones", [])
    
    def add_milestone(self, title: str, subtitle: str) -> Dict:
        """새로운 마일스톤을 추가합니다.
        
        Args:
            title (str): 마일스톤 제목
            subtitle (str): 마일스톤 부제목
        
        Returns:
            Dict: 생성된 마일스톤 데이터
        """
        milestone = {
            "id": self._generate_id(),
            "title": title,
            "subtitle": subtitle,
            "nodes": []
        }
        self.data["milestones"].append(milestone)
        return milestone
    
    def update_milestone(self, milestone_id: str, title: str, subtitle: str) -> None:
        """마일스톤을 수정합니다.
        
        Args:
            milestone_id (str): 마일스톤 ID
            title (str): 수정할 제목
            subtitle (str): 수정할 부제목
        """
        for milestone in self.data["milestones"]:
            if milestone["id"] == milestone_id:
                milestone["title"] = title
                milestone["subtitle"] = subtitle
                return
        raise ValueError(f"마일스톤을 찾을 수 없습니다: {milestone_id}")
    
    def delete_milestone(self, milestone_id: str) -> None:
        """마일스톤을 삭제합니다.
        
        Args:
            milestone_id (str): 삭제할 마일스톤의 ID
        """
        self.data["milestones"] = [
            m for m in self.data["milestones"] if m["id"] != milestone_id
        ]
    
    def add_node(self, milestone_id: str, node_data: Dict) -> Dict:
        """특정 마일스톤에 노드를 추가합니다.
        
        Args:
            milestone_id (str): 마일스톤 ID
            node_data (Dict): 노드 데이터
        
        Returns:
            Dict: 생성된 노드 데이터
        """
        for milestone in self.data["milestones"]:
            if milestone["id"] == milestone_id:
                node = {
                    "id": self._generate_id(),
                    **node_data
                }
                milestone["nodes"].append(node)
                return node
        raise ValueError(f"마일스톤을 찾을 수 없습니다: {milestone_id}")
    
    def update_node(self, milestone_id: str, node_id: str, node_data: Dict) -> None:
        """노드를 수정합니다.
        
        Args:
            milestone_id (str): 마일스톤 ID
            node_id (str): 노드 ID
            node_data (Dict): 수정할 노드 데이터
        """
        for milestone in self.data["milestones"]:
            if milestone["id"] == milestone_id:
                for i, node in enumerate(milestone["nodes"]):
                    if node["id"] == node_id:
                        milestone["nodes"][i] = {"id": node_id, **node_data}
                        return
        raise ValueError(f"노드를 찾을 수 없습니다: {node_id}")
    
    def delete_node(self, milestone_id: str, node_id: str) -> None:
        """노드를 삭제합니다.
        
        Args:
            milestone_id (str): 마일스톤 ID
            node_id (str): 삭제할 노드 ID
        """
        for milestone in self.data["milestones"]:
            if milestone["id"] == milestone_id:
                milestone["nodes"] = [
                    n for n in milestone["nodes"] if n["id"] != node_id
                ]
                return
    
    def _generate_id(self) -> str:
        """유니크 ID를 생성합니다.
        
        Returns:
            str: 타임스탬프 기반 ID
        """
        return str(int(datetime.now().timestamp() * 1000000))
