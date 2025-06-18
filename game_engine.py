# 游戏主逻辑模块 
from prompts.scene_prompt import ScenePrompt

class GameEngine:
    def __init__(self):
        self.scene_prompt = ScenePrompt()
        # 初始故事模板
        self.initial_stories = [
            {
                'scene_id': 'start_0',
                'description': '你醒来发现自己身处一个陌生的房间，四周昏暗，只有微弱的光线从窗缝透入。',
                'options': ['环顾四周', '呼喊有人吗', '继续睡觉'],
                'is_end': False
            }
        ]
        self.story_step = 0
    
    def start_new_game(self, state_manager):
        """开始新游戏"""
        # 设置初始场景
        initial_story = self.initial_stories[0]
        state_manager.update_story(
            initial_story['scene_id'],
            initial_story['description'], 
            initial_story['options']
        )
        self.story_step = 0
    
    def next_step(self, player_input, state_manager):
        """处理玩家输入，生成下一步剧情"""
        try:
            # 获取当前故事上下文
            story_context = state_manager.get_story_context()
            
            # 简单的故事推进逻辑（后续可以用AI生成）
            self.story_step += 1
            
            # 预设的故事节点
            if self.story_step == 1:
                if "环顾四周" in player_input:
                    return {
                        'scene_id': f'scene_{self.story_step}',
                        'description': '你仔细观察房间，发现这里有一张古老的书桌、一扇紧闭的门和一扇窗。书桌上放着一本厚厚的日记。',
                        'options': ['查看日记', '尝试开门', '走向窗户'],
                        'is_end': False
                    }
                elif "呼喊" in player_input:
                    return {
                        'scene_id': f'scene_{self.story_step}',
                        'description': '你大声呼喊，但只有回声回应。然而，你听到了楼下传来的脚步声，似乎有人正在上楼。',
                        'options': ['躲起来', '准备迎接来访者', '寻找武器'],
                        'is_end': False
                    }
                else:  # 继续睡觉
                    return {
                        'scene_id': f'scene_{self.story_step}',
                        'description': '你试图再次入睡，但奇怪的声音让你无法安眠。突然，房门被人轻轻推开了...',
                        'options': ['假装睡着', '立即起身', '观察来者'],
                        'is_end': False
                    }
            
            elif self.story_step == 2:
                # 第二步的故事分支
                if "日记" in player_input:
                    # 给玩家添加物品和经验
                    state_manager.add_player_item("神秘日记")
                    state_manager.player_gain_experience(10)
                    state_manager.set_story_flag("read_diary", True)
                    
                    return {
                        'scene_id': f'scene_{self.story_step}',
                        'description': '日记记录了一个神秘法师的实验。最后几页提到了一个隐藏的密室和一把魔法钥匙。你获得了重要线索！',
                        'options': ['寻找密室', '继续探索房间', '离开这里'],
                        'is_end': False
                    }
                elif "开门" in player_input:
                    return {
                        'scene_id': f'scene_{self.story_step}',
                        'description': '门被锁住了，但你发现门框上有奇怪的符文。当你触摸符文时，它们发出微弱的光芒。',
                        'options': ['研究符文', '用力撞门', '寻找钥匙'],
                        'is_end': False
                    }
                elif "躲起来" in player_input:
                    return {
                        'scene_id': f'scene_{self.story_step}',
                        'description': '你藏在床下，一个穿着长袍的神秘人走进房间。他似乎在寻找什么东西。',
                        'options': ['继续躲藏', '突然出现', '偷偷跟踪'],
                        'is_end': False
                    }
                else:
                    return {
                        'scene_id': f'scene_{self.story_step}',
                        'description': '你的行动引起了意想不到的结果，房间开始发生奇怪的变化...',
                        'options': ['观察变化', '寻找出路', '保持冷静'],
                        'is_end': False
                    }
            
            elif self.story_step >= 3:
                # 故事结束分支
                endings = [
                    {
                        'description': '你成功解开了房间的谜题，发现了通往外界的秘密通道。当你走出这个神秘的地方时，阳光洒在你的脸上，新的冒险正在等待着你...',
                        'ending_type': 'good'
                    },
                    {
                        'description': '尽管经历了种种困难，你最终还是被困在了这个神秘的房间里。但你相信，总有一天你会找到离开的方法...',
                        'ending_type': 'neutral'
                    }
                ]
                
                # 根据玩家的选择和收集的物品决定结局
                if state_manager.get_story_flag("read_diary", False) and state_manager.player.has_item("神秘日记"):
                    ending = endings[0]  # 好结局
                    state_manager.player_gain_experience(50)
                else:
                    ending = endings[1]  # 普通结局
                    state_manager.player_gain_experience(20)
                
                return {
                    'scene_id': f'ending_{ending["ending_type"]}',
                    'description': ending['description'],
                    'options': [],
                    'is_end': True,
                    'ending_type': ending['ending_type']
                }
            
        except Exception as e:
            print(f"生成故事时出错: {e}")
            # 返回错误处理场景
            return {
                'scene_id': 'error',
                'description': '一阵迷雾包围了你，当雾气散去时，你发现自己回到了起点...',
                'options': ['重新开始'],
                'is_end': False
            }
        
        # 默认返回（不应该到达这里）
        return {
            'scene_id': 'default',
            'description': '你的冒险还在继续...',
            'options': ['继续探索'],
            'is_end': False
        }
    
    def generate_scene_with_ai(self, story_context, player_action):
        """使用AI生成场景（预留接口）"""
        try:
            # 调用scene_prompt生成新场景
            response = self.scene_prompt.generate_scene(story_context, player_action)
            
            # 这里需要解析AI返回的文本，提取场景描述和选项
            # 暂时返回简单格式，后续可以添加更复杂的解析逻辑
            return {
                'scene_id': f'ai_scene_{self.story_step}',
                'description': response,
                'options': ['继续', '查看周围', '思考'],
                'is_end': False
            }
        except Exception as e:
            print(f"AI生成场景失败: {e}")
            return None 