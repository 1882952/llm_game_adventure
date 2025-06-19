# 场景Prompt模板 
import os
import json
from langchain_community.llms import Ollama
import re
from typing import Dict, List, Any, Optional
from langchain.chains import LLMChain
from langchain.prompts import PromptTemplate
from langchain_core.runnables import RunnableSequence

class ScenePrompt:
    def __init__(self, config_path="config.json"):
        if os.path.exists(config_path):
            with open(config_path, "r", encoding="utf-8") as f:
                config = json.load(f)
        else:
            config = {
                "model_name": "llama3",
                "base_url": "http://localhost:11434"
            }
        self.llm = Ollama(model=config["model_name"], base_url=config["base_url"])
        # 剧情摘要链
        self.summary_prompt = PromptTemplate(
            input_variables=["history"],
            template="""
你是一名文字冒险游戏的剧情总结助手。请将以下剧情历史内容进行高度精炼的总结，保留主线脉络、关键事件和重要角色，控制在150字以内：

剧情历史：
{history}

剧情摘要：
"""
        )
        self.summary_chain = self.summary_prompt | self.llm
        # 各类型Prompt
        self.prompt_dict = {
            "explore": PromptTemplate(
                input_variables=["context", "player_action"],
                template="""
你是一名文字冒险游戏的剧情生成AI。请根据剧情摘要和玩家操作，生成一个探索场景。

剧情摘要：{context}
玩家操作：{player_action}

请以如下JSON格式输出（不要输出任何解释性文字，只输出JSON）：
示例：
{{
  "description": "你站在一座古老的石门前，门上刻满了神秘符号，周围弥漫着淡淡的蓝色光芒。",
  "options": [
    {{"text": "推开神秘的石门", "event": "open_door"}},
    {{"text": "仔细观察墙上的符号", "event": "inspect_symbols"}},
    {{"text": "呼喊同伴寻求帮助", "event": "call_for_help"}}
  ]
}}
格式要求：
{{
  "description": "（生动描述当前场景）",
  "options": [
    {{"text": "（与当前场景相关的选项1）", "event": "（事件标签1）"}},
    {{"text": "（与当前场景相关的选项2）", "event": "（事件标签2）"}},
    {{"text": "（与当前场景相关的选项3）", "event": "（事件标签3）"}}
  ]
}}
要求：
- 选项内容必须结合当前剧情和玩家操作，每轮都要不同，不要照搬示例。
- 选项内容要简洁明了，直接描述玩家可执行的动作。
- 不要输出任何解释性文字或说明，只输出JSON。
- 请严格输出标准JSON，所有属性名和字符串都必须用双引号。
- **不要输出括号内容或占位符，必须生成具体、真实的选项。**
"""
            ),
            "battle": PromptTemplate(
                input_variables=["context", "player_action"],
                template="""
你是一名文字冒险游戏的战斗场景生成AI。请根据剧情摘要和玩家操作，生成一个战斗场景。

剧情摘要：{context}
玩家操作：{player_action}

请以如下JSON格式输出（不要输出任何解释性文字，只输出JSON）：
示例：
{{
  "description": "你与一只巨大的石像鬼展开激烈的战斗，石像鬼的利爪在空中划出寒光。",
  "options": [
    {{"text": "挥剑攻击石像鬼", "event": "damage:20"}},
    {{"text": "使用治疗药水", "event": "heal:15"}},
    {{"text": "尝试躲避攻击", "event": "none"}}
  ]
}}
格式要求：
{{
  "description": "（生动描述当前战斗场景）",
  "options": [
    {{"text": "（与当前战斗相关的选项1）", "event": "（事件标签1）"}},
    {{"text": "（与当前战斗相关的选项2）", "event": "（事件标签2）"}},
    {{"text": "（与当前战斗相关的选项3）", "event": "（事件标签3）"}}
  ]
}}
要求：
- 选项内容必须结合当前剧情和玩家操作，每轮都要不同，不要照搬示例。
- 选项内容要简洁明了，直接描述玩家可执行的动作。
- 不要输出任何解释性文字或说明，只输出JSON。
- 请严格输出标准JSON，所有属性名和字符串都必须用双引号。
- **不要输出括号内容或占位符，必须生成具体、真实的选项。**
"""
            ),
            "dialogue": PromptTemplate(
                input_variables=["context", "player_action"],
                template="""
你是一名文字冒险游戏的对话场景生成AI。请根据剧情摘要和玩家操作，生成一个对话场景。

剧情摘要：{context}
玩家操作：{player_action}

请以如下JSON格式输出（不要输出任何解释性文字，只输出JSON）：
示例：
{{
  "description": "神秘的老人微笑着看着你，眼中闪烁着智慧的光芒。",
  "options": [
    {{"text": "向老人请教符号的含义", "event": "add_experience:10"}},
    {{"text": "请求老人帮助解谜", "event": "add_item:线索碎片"}},
    {{"text": "谨慎地与老人保持距离", "event": "none"}}
  ]
}}
格式要求：
{{
  "description": "（生动描述当前对话场景）",
  "options": [
    {{"text": "（与当前对话相关的选项1）", "event": "（事件标签1）"}},
    {{"text": "（与当前对话相关的选项2）", "event": "（事件标签2）"}},
    {{"text": "（与当前对话相关的选项3）", "event": "（事件标签3）"}}
  ]
}}
要求：
- 选项内容必须结合当前剧情和玩家操作，每轮都要不同，不要照搬示例。
- 选项内容要简洁明了，直接描述玩家可执行的动作。
- 不要输出任何解释性文字或说明，只输出JSON。
- 请严格输出标准JSON，所有属性名和字符串都必须用双引号。
- **不要输出括号内容或占位符，必须生成具体、真实的选项。**
"""
            )
        }
        # 直接用prompt | llm组合
        self.scene_runnables = {
            key: self.prompt_dict[key] | self.llm for key in self.prompt_dict
        }
    
    def build_scene_prompt(self, story_context: str, player_action: str = None, scene_type: str = "adventure") -> str:
        """构建场景描述提示词"""
        base_prompt = f"""你是一位专业的文字冒险游戏剧情作家。请根据当前故事背景和玩家行为，创作引人入胜的下一个场景。

游戏设定：这是一个{scene_type}类型的文字冒险游戏，注重氛围营造和角色发展。

当前故事背景：
{story_context}
"""
        
        if player_action:
            base_prompt += f"\n玩家刚才的行动：{player_action}\n"
        
        base_prompt += """
请按以下格式生成内容：

场景描述：[用200-300字描述当前场景，要求：
1. 生动细致地描绘环境、氛围和感官体验
2. 融入故事背景，保持情节连贯性  
3. 适当制造悬念或冲突点
4. 语言富有感染力，营造沉浸感]

选项：
1. [第一个行动选项 - 偏向勇敢/直接的选择]
2. [第二个行动选项 - 偏向谨慎/智慧的选择]  
3. [第三个行动选项 - 偏向创新/意外的选择]

请确保每个选项都能推进不同方向的剧情发展。
"""
        return base_prompt
    
    def build_character_dialogue_prompt(self, character_info: Dict[str, str], dialogue_context: str, player_speech: str = None) -> str:
        """构建角色对话提示词"""
        prompt = f"""你现在要扮演游戏中的角色进行对话。

角色信息：
- 姓名：{character_info.get('name', '未知角色')}
- 身份：{character_info.get('identity', '神秘人物')}
- 性格：{character_info.get('personality', '复杂多面')}
- 语气特点：{character_info.get('tone', '平和中性')}
- 背景故事：{character_info.get('background', '身世成谜')}

对话场景：
{dialogue_context}
"""
        
        if player_speech:
            prompt += f"\n玩家刚才说：\"{player_speech}\"\n"
        
        prompt += f"""
请以{character_info.get('name', '该角色')}的身份回应，要求：
1. 严格按照角色设定的性格和语气说话
2. 对话要推进剧情发展或透露关键信息
3. 语言要符合角色身份和时代背景
4. 保持神秘感，不要一次性透露太多信息
5. 对话长度控制在50-100字

格式：直接输出角色的对话内容，不需要额外标注。
"""
        return prompt
    
    def build_options_prompt(self, current_situation: str, story_context: str, difficulty: str = "medium") -> str:
        """构建选项生成提示词"""
        prompt = f"""请为当前游戏情况生成3个行动选项。

故事背景：{story_context}

当前情况：{current_situation}

难度设定：{difficulty}（easy=简单直接, medium=需要思考, hard=复杂多变）

请生成3个不同风格的选项：

选项类型要求：
1. 【行动派】- 直接行动，可能有风险但效果明显
2. 【策略派】- 需要思考和准备，相对安全但耗时
3. 【创意派】- 意想不到的解决方案，结果难以预测

输出格式：
1. [选项内容 - 简洁有力，15字内]
2. [选项内容 - 简洁有力，15字内]  
3. [选项内容 - 简洁有力，15字内]

每个选项要能引出完全不同的剧情走向。
"""
        return prompt
    
    def build_event_progression_prompt(self, story_context: str, player_choice: str, previous_events: List[str] = None) -> str:
        """构建事件推进提示词"""
        prompt = f"""你需要根据玩家的选择推进游戏剧情。

故事背景：{story_context}

玩家选择：{player_choice}
"""
        
        if previous_events:
            prompt += f"\n之前发生的事件：\n"
            for i, event in enumerate(previous_events[-3:], 1):  # 只取最近3个事件
                prompt += f"{i}. {event}\n"
        
        prompt += """
请描述玩家选择导致的结果和后续发展：

事件结果：[100-150字描述：
1. 玩家行动的直接后果
2. 环境或其他角色的反应
3. 新出现的情况或线索
4. 为下一步设置悬念]

状态变化：[如果有的话，描述：
- 获得/失去的物品
- 角色状态变化（生命值、经验等）
- 解锁的新信息或区域
- 其他重要变化]

格式要求：内容要与玩家选择逻辑相符，保持故事连贯性。
"""
        return prompt
    
    def _route_scene_type(self, scene_type: str) -> str:
        # 简单路由逻辑，可扩展
        if scene_type in self.scene_runnables:
            return scene_type
        return "explore"
    
    def generate_scene(self, story_context: str, player_action: str = None, scene_type: str = "explore") -> dict:
        """根据剧情类型动态选择Prompt，生成结构化场景描述和选项"""
        route = self._route_scene_type(scene_type)
        chain_input = {"context": story_context, "player_action": player_action or ""}
        response = self.scene_runnables[route].invoke(chain_input)
        return self.parse_structured_scene_response(response)
    
    def generate_character_dialogue(self, character_info: Dict[str, str], dialogue_context: str, player_speech: str = None) -> str:
        """生成角色对话"""
        prompt = self.build_character_dialogue_prompt(character_info, dialogue_context, player_speech)
        response = self.llm.invoke(prompt)
        return response.strip()
    
    def generate_options(self, current_situation: str, story_context: str, difficulty: str = "medium") -> List[str]:
        """生成行动选项"""
        prompt = self.build_options_prompt(current_situation, story_context, difficulty)
        response = self.llm.invoke(prompt)
        return self.parse_options_response(response)
    
    def generate_event_progression(self, story_context: str, player_choice: str, previous_events: List[str] = None) -> Dict[str, Any]:
        """生成事件推进"""
        prompt = self.build_event_progression_prompt(story_context, player_choice, previous_events)
        response = self.llm.invoke(prompt)
        return self.parse_event_response(response)
    
    def parse_structured_scene_response(self, response: str) -> dict:
        """解析结构化JSON响应，增强健壮性"""
        import re
        import json
        try:
            # 去除markdown代码块包裹
            response = response.strip()
            if response.startswith("```"):
                response = re.sub(r"^```[a-zA-Z]*", "", response)
                response = response.strip("`").strip()
            # 用正则提取第一个大括号包裹的内容
            match = re.search(r'\{[\s\S]*\}', response)
            if match:
                json_str = match.group(0)
                data = json.loads(json_str)
                options = data.get("options", [])
                return {
                    'description': data.get("description", ""),
                    'options': [opt.get("text", "") for opt in options],
                    'option_events': [opt.get("event", "none") for opt in options],
                    'raw_response': response
                }
            else:
                raise ValueError("未找到合法JSON结构")
        except Exception as e:
            print(f"结构化解析失败，降级为普通解析: {e}")
            # fallback到原有解析
            return self.parse_scene_response(response)
    
    def parse_scene_response(self, response: str) -> Dict[str, Any]:
        """解析场景生成的响应"""
        try:
            # 提取场景描述
            scene_match = re.search(r'场景描述：(.*?)(?=选项：|$)', response, re.DOTALL)
            description = scene_match.group(1).strip() if scene_match else response
            
            # 提取选项
            options = []
            option_matches = re.findall(r'\d+\.\s*(.+)', response)
            if option_matches:
                options = [opt.strip() for opt in option_matches[:3]]
            else:
                # 如果没有匹配到标准格式，生成默认选项
                options = ["继续探索", "仔细观察", "寻找线索"]
            
            return {
                'description': description,
                'options': options,
                'raw_response': response
            }
        except Exception as e:
            return {
                'description': response,
                'options': ["继续", "观察", "思考"],
                'raw_response': response,
                'error': str(e)
            }
    
    def parse_options_response(self, response: str) -> List[str]:
        """解析选项生成的响应"""
        try:
            options = re.findall(r'\d+\.\s*(.+)', response)
            return [opt.strip() for opt in options[:3]] if options else ["继续探索", "仔细观察", "寻找线索"]
        except:
            return ["继续探索", "仔细观察", "寻找线索"]
    
    def parse_event_response(self, response: str) -> Dict[str, Any]:
        """解析事件推进的响应"""
        try:
            # 提取事件结果
            event_match = re.search(r'事件结果：(.*?)(?=状态变化：|$)', response, re.DOTALL)
            event_result = event_match.group(1).strip() if event_match else response
            
            # 提取状态变化
            status_match = re.search(r'状态变化：(.*?)$', response, re.DOTALL)
            status_changes = status_match.group(1).strip() if status_match else ""
            
            return {
                'event_result': event_result,
                'status_changes': status_changes,
                'raw_response': response
            }
        except Exception as e:
            return {
                'event_result': response,
                'status_changes': "",
                'raw_response': response,
                'error': str(e)
            }

    def summarize_history(self, history: str) -> str:
        """对历史剧情进行摘要，返回精炼主线"""
        try:
            result = self.summary_chain.invoke({"history": history})
            return result.strip()
        except Exception as e:
            print(f"剧情摘要失败: {e}")
            return history[:150] + ("..." if len(history) > 150 else "")

# 测试和验证功能
def test_scene_prompt():
    """测试场景生成功能"""
    print("=== 场景生成测试 ===")
    scene_prompt = ScenePrompt()
    
    story_context = "你是一名年轻的冒险家，刚刚踏入传说中的迷雾森林。据说这里隐藏着古老的魔法遗迹，但也充满了未知的危险。"
    player_action = "你小心翼翼地沿着苔藓覆盖的石径前进。"
    
    try:
        result = scene_prompt.generate_scene(story_context, player_action)
        print(f"场景描述：{result['description']}")
        print(f"选项：")
        for i, option in enumerate(result['options'], 1):
            print(f"  {i}. {option}")
    except Exception as e:
        print(f"测试失败：{e}")

def test_character_dialogue():
    """测试角色对话功能"""
    print("\n=== 角色对话测试 ===")
    scene_prompt = ScenePrompt()
    
    character_info = {
        'name': '艾莉娅',
        'identity': '森林守护者',
        'personality': '智慧而神秘，对外来者既警惕又好奇',
        'tone': '优雅而古老的语调',
        'background': '守护这片森林数百年的精灵'
    }
    
    dialogue_context = "玩家在森林中迷路时遇到了这位神秘的森林守护者。"
    player_speech = "请问，你能告诉我离开这片森林的路吗？"
    
    try:
        dialogue = scene_prompt.generate_character_dialogue(character_info, dialogue_context, player_speech)
        print(f"艾莉娅说：{dialogue}")
    except Exception as e:
        print(f"测试失败：{e}")

def test_options_generation():
    """测试选项生成功能"""
    print("\n=== 选项生成测试 ===")
    scene_prompt = ScenePrompt()
    
    story_context = "迷雾森林中的冒险"
    current_situation = "你面前出现了一座废弃的古塔，塔门紧闭，但周围有奇怪的魔法符文闪烁。"
    
    try:
        options = scene_prompt.generate_options(current_situation, story_context)
        print("生成的选项：")
        for i, option in enumerate(options, 1):
            print(f"  {i}. {option}")
    except Exception as e:
        print(f"测试失败：{e}")

def test_event_progression():
    """测试事件推进功能"""
    print("\n=== 事件推进测试 ===")
    scene_prompt = ScenePrompt()
    
    story_context = "迷雾森林冒险"
    player_choice = "触摸古塔门上的魔法符文"
    previous_events = ["进入森林", "遇到森林守护者", "获得古老地图"]
    
    try:
        result = scene_prompt.generate_event_progression(story_context, player_choice, previous_events)
        print(f"事件结果：{result['event_result']}")
        if result['status_changes']:
            print(f"状态变化：{result['status_changes']}")
    except Exception as e:
        print(f"测试失败：{e}")

# 主测试函数
if __name__ == "__main__":
    print("开始测试文字冒险游戏提示词系统...")
    print("注意：需要本地运行Ollama服务")
    
    # 运行所有测试
    test_scene_prompt()
    test_character_dialogue() 
    test_options_generation()
    test_event_progression()
    
    print("\n测试完成！")