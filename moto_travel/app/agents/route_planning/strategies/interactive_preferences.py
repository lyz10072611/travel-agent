"""
交互式偏好配置
支持在路线规划过程中动态询问用户偏好
"""
from typing import Dict, List, Any, Optional
from loguru import logger

from .route_preferences import RoutePreferences, PreferenceQuestionnaire, HighwayPreference


class InteractivePreferenceCollector:
    """交互式偏好收集器"""
    
    def __init__(self):
        self.questionnaire = PreferenceQuestionnaire()
        self.current_answers: Dict[str, Any] = {}
        self.asked_questions: List[str] = []
    
    def get_next_question(
        self,
        context: Optional[Dict[str, Any]] = None
    ) -> Optional[Dict[str, Any]]:
        """获取下一个需要询问的问题"""
        # 获取所有问题
        all_questions = (
            self.questionnaire.get_required_questions() +
            self.questionnaire.get_optional_questions()
        )
        
        # 找出未回答的问题
        unanswered = [
            q for q in all_questions
            if q["key"] not in self.current_answers and q["key"] not in self.asked_questions
        ]
        
        if not unanswered:
            return None
        
        # 优先询问核心问题
        required = [q for q in unanswered if q.get("required", False)]
        if required:
            return required[0]
        
        # 根据上下文智能选择问题
        if context:
            # 如果用户提到"高速"，优先询问高速偏好
            if "高速" in str(context.get("query", "")) or "highway" in str(context.get("query", "")).lower():
                highway_q = next((q for q in unanswered if q["key"] == "highway_preference"), None)
                if highway_q:
                    return highway_q
            
            # 如果用户提到"晚上"或"夜间"，优先询问晚上国道偏好
            if "晚上" in str(context.get("query", "")) or "夜间" in str(context.get("query", "")):
                night_q = next((q for q in unanswered if q["key"] == "avoid_national_road_at_night"), None)
                if night_q:
                    return night_q
        
        # 返回第一个未回答的问题
        return unanswered[0]
    
    def answer_question(self, key: str, value: Any) -> Dict[str, Any]:
        """回答一个问题"""
        self.current_answers[key] = value
        self.asked_questions.append(key)
        
        return {
            "answered": key,
            "value": value,
            "remaining": self.get_remaining_count()
        }
    
    def get_remaining_count(self) -> int:
        """获取剩余问题数量"""
        all_questions = (
            self.questionnaire.get_required_questions() +
            self.questionnaire.get_optional_questions()
        )
        return len([q for q in all_questions if q["key"] not in self.current_answers])
    
    def is_complete(self) -> bool:
        """检查是否已回答所有必需问题"""
        required_questions = self.questionnaire.get_required_questions()
        required_keys = [q["key"] for q in required_questions if q.get("required", False)]
        
        return all(key in self.current_answers for key in required_keys)
    
    def build_preferences(self) -> RoutePreferences:
        """构建偏好配置"""
        return self.questionnaire.parse_answers(self.current_answers)
    
    def get_summary(self) -> Dict[str, Any]:
        """获取偏好摘要"""
        prefs = self.build_preferences()
        return {
            "answers": self.current_answers,
            "preferences": prefs.to_dict(),
            "is_complete": self.is_complete(),
            "remaining_questions": self.get_remaining_count()
        }


class PreferenceInference:
    """偏好推断器 - 从用户查询中自动推断偏好"""
    
    @staticmethod
    def infer_from_query(query: str) -> Dict[str, Any]:
        """从查询中推断偏好"""
        inferred = {}
        query_lower = query.lower()
        
        # 推断高速偏好
        if any(keyword in query_lower for keyword in ["不走高速", "避开高速", "禁止高速", "avoid highway"]):
            inferred["highway_preference"] = "forbid"
        elif any(keyword in query_lower for keyword in ["尽量避开高速", "avoid highway"]):
            inferred["highway_preference"] = "avoid"
        elif any(keyword in query_lower for keyword in ["优先高速", "走高速", "prefer highway"]):
            inferred["highway_preference"] = "prefer"
        else:
            inferred["highway_preference"] = "allow"  # 默认允许
        
        # 推断晚上国道偏好
        if any(keyword in query_lower for keyword in ["晚上", "夜间", "night"]):
            # 如果提到晚上，默认开启避开国道
            inferred["avoid_national_road_at_night"] = True
        
        # 推断风景路线
        if any(keyword in query_lower for keyword in ["风景", "观景", "scenic"]):
            inferred["prefer_scenic_route"] = True
        
        # 推断续航里程
        import re
        fuel_match = re.search(r'(\d+)\s*(?:公里|km|续航)', query)
        if fuel_match:
            inferred["fuel_range_km"] = int(fuel_match.group(1))
        
        return inferred
    
    @staticmethod
    def merge_inferred_and_answers(
        inferred: Dict[str, Any],
        answers: Dict[str, Any]
    ) -> Dict[str, Any]:
        """合并推断的偏好和用户答案"""
        merged = inferred.copy()
        merged.update(answers)  # 用户答案优先
        return merged

