# 场景Prompt模板 
from langchain_community.llms import Ollama

class ScenePrompt:
    def __init__(self, model_name="unsafe-llama3-14b:latest"):
        self.llm = Ollama(model=model_name)

    def build_prompt(self, story_context, player_action=None):
        prompt = """
你是一款文字冒险游戏的故事生成AI。请根据当前剧情上下文和玩家操作，生成下一步的场景描述。
要求：
- 语言生动、细节丰富，营造沉浸感。
- 结尾给出3个可选项，格式如下：
场景描述内容
选项：
1. xxx
2. xxx
3. xxx

当前剧情：{story_context}
"""
        if player_action:
            prompt += f"\n玩家操作：{player_action}\n"
        prompt += "\n请生成下一步场景。"
        return prompt

    def generate_scene(self, story_context, player_action=None):
        prompt = self.build_prompt(story_context, player_action)
        response = self.llm(prompt)
        return response 


# 测试代码
if __name__ == "__main__":
    # 实例化 ScenePrompt 类
    scene_prompt = ScenePrompt()

    # 初始剧情上下文
    initial_story = "你发现自己身处一个古老的森林中，周围树木高大茂密，阳光透过树叶缝隙洒下斑驳的光影。一条蜿蜒的小路通向森林深处，另一条岔路则指向一个看似废弃的小屋。"
    
    # 测试无玩家操作的情况
    print("测试初始场景生成：")
    initial_scene = scene_prompt.generate_scene(initial_story)
    print(initial_scene)
    
    # 选择一个玩家操作
    player_action = "你决定沿着小路走向废弃的小屋。"
    
    # 测试有玩家操作的情况
    print("\n\n测试玩家操作后的场景生成：")
    next_scene = scene_prompt.generate_scene(initial_story, player_action)
    print(next_scene)