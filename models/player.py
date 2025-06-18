# 玩家数据模型 
from dataclasses import dataclass, field
from typing import Dict, List, Any
import json

@dataclass
class Player:
    """玩家数据模型"""
    name: str = "冒险者"
    level: int = 1
    health: int = 100
    max_health: int = 100
    experience: int = 0
    inventory: List[str] = field(default_factory=list)
    skills: Dict[str, int] = field(default_factory=dict)
    attributes: Dict[str, Any] = field(default_factory=dict)
    
    def add_item(self, item: str) -> None:
        """添加物品到背包"""
        self.inventory.append(item)
    
    def remove_item(self, item: str) -> bool:
        """从背包移除物品"""
        if item in self.inventory:
            self.inventory.remove(item)
            return True
        return False
    
    def has_item(self, item: str) -> bool:
        """检查是否拥有指定物品"""
        return item in self.inventory
    
    def add_experience(self, exp: int) -> None:
        """增加经验值"""
        self.experience += exp
        # 简单的升级逻辑
        while self.experience >= self.level * 100:
            self.experience -= self.level * 100
            self.level_up()
    
    def level_up(self) -> None:
        """升级"""
        self.level += 1
        self.max_health += 10
        self.health = self.max_health
    
    def heal(self, amount: int) -> None:
        """治疗"""
        self.health = min(self.health + amount, self.max_health)
    
    def take_damage(self, amount: int) -> None:
        """受到伤害"""
        self.health = max(0, self.health - amount)
    
    def is_alive(self) -> bool:
        """检查是否存活"""
        return self.health > 0
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典格式"""
        return {
            'name': self.name,
            'level': self.level,
            'health': self.health,
            'max_health': self.max_health,
            'experience': self.experience,
            'inventory': self.inventory,
            'skills': self.skills,
            'attributes': self.attributes
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Player':
        """从字典创建玩家对象"""
        return cls(
            name=data.get('name', '冒险者'),
            level=data.get('level', 1),
            health=data.get('health', 100),
            max_health=data.get('max_health', 100),
            experience=data.get('experience', 0),
            inventory=data.get('inventory', []),
            skills=data.get('skills', {}),
            attributes=data.get('attributes', {})
        ) 