# 游戏主逻辑模块 
from prompts.scene_prompt import ScenePrompt
import random

class GameEngine:
    def __init__(self):
        self.scene_prompt = ScenePrompt()
        self.story_step = 0
        self.use_ai_generation = True  # 是否使用AI生成内容
        self.game_theme = "fantasy_adventure"  # 游戏主题
        
        # 初始故事设定
        self.initial_story_settings = {
            "fantasy_adventure": {
                'scene_id': 'start_0',
                'description': '你是一名年轻的冒险家，醒来时发现自己身处一个陌生而神秘的房间。房间里弥漫着古老的魔法气息，墙上的符文隐隐发光。',
                'context': '这是一个充满魔法与奇迹的世界。你刚刚开始一段寻找古老遗迹的冒险旅程，但似乎遇到了意外情况。',
                'options': ['仔细观察房间', '尝试回忆之前发生的事', '寻找出口'],
                'is_end': False
            },
            "sci_fi": {
                'scene_id': 'start_0', 
                'description': '你在一艘废弃的太空站中苏醒，周围的设备发出微弱的红光。空气中有淡淡的金属味道。',
                'context': '这是2157年，人类已经征服了银河系的大部分区域。你是一名太空探险者，但现在的处境似乎不太妙。',
                'options': ['检查周围设备', '查看个人装备', '尝试联系总部'],
                'is_end': False
            }
        }
    
    def start_new_game(self, state_manager, theme="fantasy_adventure"):
        """开始新游戏"""
        self.game_theme = theme
        self.story_step = 0
        
        # 获取初始故事设定
        initial_story = self.initial_story_settings.get(theme, self.initial_story_settings["fantasy_adventure"])
        
        # 如果启用AI生成，使用AI优化初始场景
        if self.use_ai_generation:
            try:
                ai_result = self.scene_prompt.generate_scene(
                    initial_story['context'], 
                    scene_type=theme
                )
                
                # 使用AI生成的内容
                state_manager.update_story(
                    initial_story['scene_id'],
                    ai_result['description'],
                    ai_result['options']
                )
                
                # 设置故事背景上下文
                state_manager.set_story_flag("story_theme", theme)
                state_manager.set_story_flag("story_context", initial_story['context'])
                
            except Exception as e:
                print(f"AI生成失败，使用默认场景: {e}")
                # 回退到预设场景
                state_manager.update_story(
                    initial_story['scene_id'],
                    initial_story['description'], 
                    initial_story['options']
                )
        else:
            # 使用预设场景
            state_manager.update_story(
                initial_story['scene_id'],
                initial_story['description'], 
                initial_story['options']
            )
    
    def next_step(self, player_input, state_manager):
        """处理玩家输入，生成下一步剧情"""
        self.story_step += 1
        
        # 如果启用AI生成
        if self.use_ai_generation:
            return self.generate_ai_story(player_input, state_manager)
        else:
            return self.generate_preset_story(player_input, state_manager)
    
    def generate_ai_story(self, player_input, state_manager):
        """使用AI生成故事内容"""
        try:
            # 获取当前故事上下文
            story_context = state_manager.get_story_context()
            theme = state_manager.get_story_flag("story_theme", "fantasy_adventure")
            
            # 生成事件推进
            previous_events = [node.description for node in state_manager.story.history[-3:]]
            event_result = self.scene_prompt.generate_event_progression(
                story_context, 
                player_input, 
                previous_events
            )
            
            # 处理状态变化
            self.process_status_changes(event_result.get('status_changes', ''), state_manager)
            
            # 生成新场景
            updated_context = story_context + f"\n最新发生：{event_result['event_result']}"
            scene_result = self.scene_prompt.generate_scene(
                updated_context,
                player_input,
                theme
            )
            
            # 随机添加一些游戏性元素
            self.add_random_game_elements(state_manager)
            
            # 检查是否应该结束游戏
            should_end = self.check_ending_conditions(state_manager)
            
            return {
                'scene_id': f'ai_scene_{self.story_step}',
                'description': scene_result['description'],
                'options': scene_result['options'] if not should_end else [],
                'is_end': should_end,
                'ending_type': 'ai_generated' if should_end else None
            }
            
        except Exception as e:
            print(f"AI生成故事失败: {e}")
            # 回退到预设逻辑
            return self.generate_preset_story(player_input, state_manager)
    
    def generate_preset_story(self, player_input, state_manager):
        """生成预设的故事内容（备用方案）"""
        # 预设的故事节点（原有逻辑）
        if self.story_step == 1:
            if "观察" in player_input or "环顾" in player_input:
                return {
                    'scene_id': f'scene_{self.story_step}',
                    'description': '你仔细观察房间，发现这里有一张古老的书桌、一扇紧闭的门和一扇窗。书桌上放着一本厚厚的日记。',
                    'options': ['查看日记', '尝试开门', '走向窗户'],
                    'is_end': False
                }
            elif "回忆" in player_input:
                return {
                    'scene_id': f'scene_{self.story_step}',
                    'description': '你努力回想，模糊记得自己在寻找一个传说中的魔法宝物，但之后的记忆一片空白。头部隐隐作痛。',
                    'options': ['继续回忆', '放弃回忆，探索房间', '检查身体状况'],
                    'is_end': False
                }
            else:  # 寻找出口
                return {
                    'scene_id': f'scene_{self.story_step}',
                    'description': '你寻找出口，但发现房门被一道魔法屏障封锁。屏障散发着蓝色的光芒，似乎需要特殊的方法才能破解。',
                    'options': ['尝试触摸屏障', '寻找破解方法', '探索其他出路'],
                    'is_end': False
                }
        
        elif self.story_step == 2:
            # 第二步的故事分支
            if "日记" in player_input:
                state_manager.add_player_item("神秘日记")
                state_manager.player_gain_experience(15)
                state_manager.set_story_flag("read_diary", True)
                
                return {
                    'scene_id': f'scene_{self.story_step}',
                    'description': '日记记录着一位法师的研究笔记。最后几页提到了"星光之石"的传说，以及打开封印的咒语。你获得了重要线索！',
                    'options': ['尝试念出咒语', '继续探索房间', '保存日记，寻找其他线索'],
                    'is_end': False
                }
            else:
                return {
                    'scene_id': f'scene_{self.story_step}',
                    'description': '你的行动产生了意想不到的效果。房间中的魔法能量开始波动，一些隐藏的机关被激活了。',
                    'options': ['观察魔法变化', '迅速寻找掩护', '尝试控制魔法能量'],
                    'is_end': False
                }
        
        elif self.story_step >= 3:
            # 根据玩家收集的物品和标记决定结局
            if state_manager.get_story_flag("read_diary", False):
                state_manager.player_gain_experience(50)
                return {
                    'scene_id': 'ending_good',
                    'description': '凭借日记中的知识，你成功破解了房间的封印。一道光芒闪过，你发现自己站在了一座宏伟的魔法图书馆中。真正的冒险现在才开始...',
                    'options': [],
                    'is_end': True,
                    'ending_type': 'good'
                }
            else:
                state_manager.player_gain_experience(20)
                return {
                    'scene_id': 'ending_neutral',
                    'description': '经过一番努力，你找到了离开房间的方法，但你感觉错过了什么重要的东西。也许还有其他的秘密等待着被发现...',
                    'options': [],
                    'is_end': True,
                    'ending_type': 'neutral'
                }
        
        # 默认情况
        return {
            'scene_id': 'default',
            'description': '你的冒险还在继续，未知的挑战在前方等待着你...',
            'options': ['继续探索', '仔细思考', '寻找线索'],
            'is_end': False
        }
    
    def process_status_changes(self, status_changes, state_manager):
        """处理AI生成的状态变化"""
        if not status_changes:
            return
        
        try:
            # 解析状态变化文本，寻找关键词
            text = status_changes.lower()
            
            # 检查物品获得
            if "获得" in text or "发现" in text:
                items = ["古老钥匙", "魔法水晶", "神秘卷轴", "治疗药水", "银币"]
                item = random.choice(items)
                state_manager.add_player_item(item)
                print(f"[系统] 你获得了：{item}")
            
            # 检查经验获得
            if "经验" in text or "学习" in text or "理解" in text:
                exp = random.randint(10, 30)
                state_manager.player_gain_experience(exp)
                print(f"[系统] 你获得了 {exp} 点经验")
            
            # 检查生命值变化
            if "受伤" in text or "伤害" in text:
                damage = random.randint(5, 15)
                state_manager.player.take_damage(damage)
                print(f"[系统] 你受到了 {damage} 点伤害")
            elif "治疗" in text or "恢复" in text:
                healing = random.randint(10, 25)
                state_manager.player.heal(healing)
                print(f"[系统] 你恢复了 {healing} 点生命值")
            
            # 设置故事标记
            if "重要" in text or "关键" in text:
                state_manager.set_story_flag(f"important_event_{self.story_step}", True)
                
        except Exception as e:
            print(f"处理状态变化时出错: {e}")
    
    def add_random_game_elements(self, state_manager):
        """随机添加游戏性元素"""
        if random.random() < 0.3:  # 30%概率
            # 随机事件
            events = [
                ("经验", random.randint(5, 15)),
                ("物品", random.choice(["幸运符", "能量果实", "神秘石头"])),
                ("治疗", random.randint(5, 10))
            ]
            
            event_type, value = random.choice(events)
            
            if event_type == "经验":
                state_manager.player_gain_experience(value)
                print(f"[幸运事件] 你在探索中有所收获，获得了 {value} 点经验！")
            elif event_type == "物品":
                state_manager.add_player_item(value)
                print(f"[幸运事件] 你发现了一个 {value}！")
            elif event_type == "治疗":
                state_manager.player.heal(value)
                print(f"[幸运事件] 你感到精神焕发，恢复了 {value} 点生命值！")
    
    def check_ending_conditions(self, state_manager):
        """检查是否应该结束游戏"""
        # 基于步数的结束条件
        if self.story_step >= 8:
            return True
        
        # 基于玩家状态的结束条件
        if not state_manager.player.is_alive():
            return True
        
        # 基于故事标记的结束条件
        if state_manager.get_story_flag("story_completed", False):
            return True
        
        return False
    
    def toggle_ai_generation(self, enabled=None):
        """切换AI生成模式"""
        if enabled is None:
            self.use_ai_generation = not self.use_ai_generation
        else:
            self.use_ai_generation = enabled
        
        return self.use_ai_generation
    
    def get_generation_status(self):
        """获取当前生成模式状态"""
        return {
            'ai_enabled': self.use_ai_generation,
            'theme': self.game_theme,
            'step': self.story_step
        }

# 测试GameEngine的AI集成功能
if __name__ == "__main__":
    from state_manager import GameStateManager
    
    print("测试GameEngine的AI集成功能...")
    
    # 创建测试实例
    engine = GameEngine()
    state_manager = GameStateManager()
    
    # 测试新游戏启动
    print("\n=== 测试新游戏启动 ===")
    state_manager.create_new_game("测试玩家")
    engine.start_new_game(state_manager, "fantasy_adventure")
    
    current_state = state_manager.get_current_state()
    print(f"初始场景: {current_state['description']}")
    print(f"选项: {current_state['options']}")
    
    # 测试故事推进
    print("\n=== 测试故事推进 ===")
    test_action = "仔细观察房间"
    next_state = engine.next_step(test_action, state_manager)
    
    if next_state:
        print(f"场景ID: {next_state['scene_id']}")
        print(f"描述: {next_state['description']}")
        print(f"选项: {next_state['options']}")
        print(f"是否结束: {next_state['is_end']}")
    
    # 显示玩家状态
    print(f"\n玩家状态: {state_manager.player.name} (等级 {state_manager.player.level})")
    print(f"背包: {state_manager.player.inventory}")
    
    print("\n测试完成！") 