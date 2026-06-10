from typing import Dict, List, Optional
class InterviewRepository:
    def __init__(self):
        self.interviews: Dict[str, dict] = {}
    def save(self, interview: dict) -> dict:
        self.interviews[interview["interview_id"]] = interview
        return interview
    def find_by_id(self, interview_id: str) -> Optional[dict]:
        return self.interviews.get(interview_id)
    def find_by_user_id(self, user_id: str) -> List[dict]:
        result = []
        
        for interview in self.interviews.values():
            if interview["user_id"] == user_id:
                result.append(interview)
        return result