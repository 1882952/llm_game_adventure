# 剧情状态数据模型 
from dataclasses import dataclass, field
from typing import Dict, List, Any, Optional
from datetime import datetime

@dataclass
class StoryNode:
    """单个剧情节点"""
    scene_id: str
    description: str
    options: List[str]
    player_choice: Optional[str] = None
    timestamp: datetime = field(default_factory=datetime.now)
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典格式"""
        return {
            'scene_id': self.scene_id,
            'description': self.description,
            'options': self.options,
            'player_choice': self.player_choice,
            'timestamp': self.timestamp.isoformat()
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'StoryNode':
        """从字典创建剧情节点对象"""
        return cls(
            scene_id=data['scene_id'],
            description=data['description'],
            options=data['options'],
            player_choice=data.get('player_choice'),
            timestamp=datetime.fromisoformat(data['timestamp'])
        )

@dataclass
class StoryState:
    """剧情状态数据模型"""
    current_scene_id: str = "scene_0"
    current_description: str = ""
    current_options: List[str] = field(default_factory=list)
    history: List[StoryNode] = field(default_factory=list)
    story_flags: Dict[str, Any] = field(default_factory=dict)
    branch_count: Dict[str, int] = field(default_factory=dict)
    is_ended: bool = False
    ending_type: Optional[str] = None
    
    def add_scene(self, scene_id: str, description: str, options: List[str]) -> None:
        """添加新场景到历史记录"""
        # 保存当前场景到历史
        if self.current_scene_id:
            node = StoryNode(
                scene_id=self.current_scene_id,
                description=self.current_description,
                options=self.current_options
            )
            self.history.append(node)
        
        # 更新当前场景
        self.current_scene_id = scene_id
        self.current_description = description
        self.current_options = options
    
    def record_choice(self, choice: str) -> None:
        """记录玩家选择"""
        if self.history:
            self.history[-1].player_choice = choice
        
        # 统计分支选择次数
        if choice in self.branch_count:
            self.branch_count[choice] += 1
        else:
            self.branch_count[choice] = 1
    
    def set_flag(self, flag_name: str, value: Any) -> None:
        """设置故事标记"""
        self.story_flags[flag_name] = value
    
    def get_flag(self, flag_name: str, default: Any = None) -> Any:
        """获取故事标记"""
        return self.story_flags.get(flag_name, default)
    
    def has_flag(self, flag_name: str) -> bool:
        """检查是否存在指定标记"""
        return flag_name in self.story_flags
    
    def end_story(self, ending_type: str = "normal") -> None:
        """结束故事"""
        self.is_ended = True
        self.ending_type = ending_type
    
    def get_history_summary(self, max_entries: int = 5) -> List[str]:
        """获取历史记录摘要"""
        recent_history = self.history[-max_entries:] if self.history else []
        summary = []
        for node in recent_history:
            choice_text = f" (选择: {node.player_choice})" if node.player_choice else ""
            summary.append(f"{node.description}{choice_text}")
        return summary
    
    def get_story_context(self, include_history: bool = True) -> str:
        """获取完整的故事上下文"""
        context = ""
        if include_history and self.history:
            context += "之前的经历:\n"
            for summary in self.get_history_summary():
                context += f"- {summary}\n"
            context += "\n"
        
        context += f"当前情况: {self.current_description}"
        return context
    
    def can_go_back(self) -> bool:
        """检查是否可以回退"""
        return len(self.history) > 0
    
    def go_back(self) -> bool:
        """回退到上一个场景"""
        if not self.can_go_back():
            return False
        
        # 恢复上一个场景
        last_node = self.history.pop()
        self.current_scene_id = last_node.scene_id
        self.current_description = last_node.description
        self.current_options = last_node.options
        
        return True
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典格式"""
        return {
            'current_scene_id': self.current_scene_id,
            'current_description': self.current_description,
            'current_options': self.current_options,
            'history': [node.to_dict() for node in self.history],
            'story_flags': self.story_flags,
            'branch_count': self.branch_count,
            'is_ended': self.is_ended,
            'ending_type': self.ending_type
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'StoryState':
        """从字典创建剧情状态对象"""
        history = [StoryNode.from_dict(node_data) for node_data in data.get('history', [])]
        
        return cls(
            current_scene_id=data.get('current_scene_id', 'scene_0'),
            current_description=data.get('current_description', ''),
            current_options=data.get('current_options', []),
            history=history,
            story_flags=data.get('story_flags', {}),
            branch_count=data.get('branch_count', {}),
            is_ended=data.get('is_ended', False),
            ending_type=data.get('ending_type')
        ) 