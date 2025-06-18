# 状态与存档管理 

import json
import os
from datetime import datetime
from typing import Dict, Any, Optional
from models.player import Player
from models.story_state import StoryState

class GameStateManager:
    """游戏状态管理器"""
    
    def __init__(self, save_directory: str = "saves"):
        self.save_directory = save_directory
        self.player: Player = Player()
        self.story: StoryState = StoryState()
        self.game_metadata: Dict[str, Any] = {
            'created_at': datetime.now().isoformat(),
            'last_updated': datetime.now().isoformat(),
            'play_time': 0,  # 游戏时间（秒）
            'version': '1.0'
        }
        
        # 确保存档目录存在
        if not os.path.exists(self.save_directory):
            os.makedirs(self.save_directory)
    
    def update_metadata(self) -> None:
        """更新游戏元数据"""
        self.game_metadata['last_updated'] = datetime.now().isoformat()
    
    def create_new_game(self, player_name: str = "冒险者") -> None:
        """创建新游戏"""
        self.player = Player(name=player_name)
        self.story = StoryState()
        self.game_metadata = {
            'created_at': datetime.now().isoformat(),
            'last_updated': datetime.now().isoformat(),
            'play_time': 0,
            'version': '1.0'
        }
    
    def update_story(self, scene_id: str, description: str, options: list, player_choice: str = None) -> None:
        """更新剧情状态"""
        # 记录玩家选择
        if player_choice:
            self.story.record_choice(player_choice)
        
        # 添加新场景
        self.story.add_scene(scene_id, description, options)
        self.update_metadata()
    
    def set_story_flag(self, flag_name: str, value: Any) -> None:
        """设置故事标记"""
        self.story.set_flag(flag_name, value)
        self.update_metadata()
    
    def get_story_flag(self, flag_name: str, default: Any = None) -> Any:
        """获取故事标记"""
        return self.story.get_flag(flag_name, default)
    
    def add_player_item(self, item: str) -> None:
        """给玩家添加物品"""
        self.player.add_item(item)
        self.update_metadata()
    
    def player_use_item(self, item: str) -> bool:
        """玩家使用物品"""
        if self.player.remove_item(item):
            self.update_metadata()
            return True
        return False
    
    def player_gain_experience(self, exp: int) -> None:
        """玩家获得经验"""
        old_level = self.player.level
        self.player.add_experience(exp)
        if self.player.level > old_level:
            # 升级了，可以在这里添加升级提示逻辑
            pass
        self.update_metadata()
    
    def get_current_state(self) -> Dict[str, Any]:
        """获取当前游戏状态"""
        return {
            'description': self.story.current_description,
            'options': self.story.current_options,
            'is_end': self.story.is_ended,
            'player_status': {
                'name': self.player.name,
                'level': self.player.level,
                'health': self.player.health,
                'max_health': self.player.max_health,
                'inventory': self.player.inventory
            }
        }
    
    def get_story_context(self) -> str:
        """获取故事上下文"""
        return self.story.get_story_context()
    
    def can_go_back(self) -> bool:
        """检查是否可以回退"""
        return self.story.can_go_back()
    
    def go_back(self) -> bool:
        """回退到上一个场景"""
        if self.story.go_back():
            self.update_metadata()
            return True
        return False
    
    def end_game(self, ending_type: str = "normal") -> None:
        """结束游戏"""
        self.story.end_story(ending_type)
        self.update_metadata()
    
    def save_game(self, save_name: str) -> bool:
        """保存游戏"""
        try:
            save_data = {
                'player': self.player.to_dict(),
                'story': self.story.to_dict(),
                'metadata': self.game_metadata
            }
            
            save_path = os.path.join(self.save_directory, f"{save_name}.json")
            with open(save_path, 'w', encoding='utf-8') as f:
                json.dump(save_data, f, ensure_ascii=False, indent=2)
            
            print(f"游戏已保存到: {save_path}")
            return True
        
        except Exception as e:
            print(f"保存游戏失败: {e}")
            return False
    
    def load_game(self, save_name: str) -> bool:
        """读取游戏"""
        try:
            save_path = os.path.join(self.save_directory, f"{save_name}.json")
            
            if not os.path.exists(save_path):
                print(f"存档文件不存在: {save_path}")
                return False
            
            with open(save_path, 'r', encoding='utf-8') as f:
                save_data = json.load(f)
            
            # 恢复玩家状态
            self.player = Player.from_dict(save_data['player'])
            
            # 恢复剧情状态
            self.story = StoryState.from_dict(save_data['story'])
            
            # 恢复元数据
            self.game_metadata = save_data.get('metadata', {})
            
            print(f"游戏已从 {save_path} 读取")
            return True
        
        except Exception as e:
            print(f"读取游戏失败: {e}")
            return False
    
    def list_saves(self) -> list:
        """列出所有存档"""
        saves = []
        try:
            for filename in os.listdir(self.save_directory):
                if filename.endswith('.json'):
                    save_name = filename[:-5]  # 移除.json后缀
                    save_path = os.path.join(self.save_directory, filename)
                    
                    # 获取文件修改时间
                    mtime = os.path.getmtime(save_path)
                    modified_time = datetime.fromtimestamp(mtime).strftime('%Y-%m-%d %H:%M:%S')
                    
                    saves.append({
                        'name': save_name,
                        'path': save_path,
                        'modified_time': modified_time
                    })
            
            # 按修改时间排序
            saves.sort(key=lambda x: x['modified_time'], reverse=True)
            
        except Exception as e:
            print(f"列出存档失败: {e}")
        
        return saves
    
    def delete_save(self, save_name: str) -> bool:
        """删除存档"""
        try:
            save_path = os.path.join(self.save_directory, f"{save_name}.json")
            if os.path.exists(save_path):
                os.remove(save_path)
                print(f"存档 {save_name} 已删除")
                return True
            else:
                print(f"存档 {save_name} 不存在")
                return False
        
        except Exception as e:
            print(f"删除存档失败: {e}")
            return False
    
    def get_save_info(self, save_name: str) -> Optional[Dict[str, Any]]:
        """获取存档信息"""
        try:
            save_path = os.path.join(self.save_directory, f"{save_name}.json")
            
            if not os.path.exists(save_path):
                return None
            
            with open(save_path, 'r', encoding='utf-8') as f:
                save_data = json.load(f)
            
            player_data = save_data['player']
            story_data = save_data['story']
            metadata = save_data.get('metadata', {})
            
            return {
                'player_name': player_data.get('name', '未知'),
                'player_level': player_data.get('level', 1),
                'current_scene': story_data.get('current_scene_id', '未知'),
                'is_ended': story_data.get('is_ended', False),
                'created_at': metadata.get('created_at', '未知'),
                'last_updated': metadata.get('last_updated', '未知'),
                'play_time': metadata.get('play_time', 0)
            }
        
        except Exception as e:
            print(f"获取存档信息失败: {e}")
            return None


# 测试代码
if __name__ == "__main__":
    # 创建状态管理器
    state_manager = GameStateManager()
    
    # 创建新游戏
    state_manager.create_new_game("测试玩家")
    
    # 模拟游戏流程
    state_manager.update_story(
        "scene_1",
        "你站在一座古老的城堡前，大门紧闭。",
        ["敲门", "寻找其他入口", "离开"]
    )
    
    # 记录玩家选择
    state_manager.update_story(
        "scene_2",
        "你敲了敲门，一个老管家打开了门。",
        ["进入城堡", "询问情况", "道歉离开"],
        "敲门"
    )
    
    # 给玩家添加物品和经验
    state_manager.add_player_item("古老的钥匙")
    state_manager.player_gain_experience(50)
    state_manager.set_story_flag("met_butler", True)
    
    # 保存游戏
    state_manager.save_game("test_save")
    
    # 显示当前状态
    print("\n当前游戏状态:")
    current_state = state_manager.get_current_state()
    print(f"场景: {current_state['description']}")
    print(f"选项: {current_state['options']}")
    print(f"玩家: {current_state['player_status']['name']} (等级 {current_state['player_status']['level']})")
    print(f"背包: {current_state['player_status']['inventory']}")
    
    # 列出存档
    print("\n存档列表:")
    saves = state_manager.list_saves()
    for save in saves:
        print(f"- {save['name']} (修改时间: {save['modified_time']})")
    
    # 获取存档信息
    save_info = state_manager.get_save_info("test_save")
    if save_info:
        print(f"\n存档信息: {save_info}") 