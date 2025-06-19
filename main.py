# 项目启动入口 
from game_engine import GameEngine
from user_interface import UserInterface
from state_manager import GameStateManager

def show_main_menu(ui, state_manager):
    """显示主菜单"""
    print("\n=== 文字冒险游戏 ===")
    print("1. 新游戏")
    print("2. 继续游戏")
    print("3. 查看存档")
    print("4. 退出游戏")
    
    choice = ui.get_player_input()
    
    if choice == "1" or choice == "新游戏":
        # 新游戏
        player_name = input("请输入角色名称（直接回车使用默认名称）：").strip()
        if not player_name:
            player_name = "冒险者"
        state_manager.create_new_game(player_name)
        print(f"欢迎，{player_name}！你的冒险即将开始...")
        return "new_game"
    
    elif choice == "2" or choice == "继续游戏":
        # 继续游戏
        saves = state_manager.list_saves()
        if not saves:
            print("没有找到任何存档文件。")
            return "menu"
        
        print("\n可用存档：")
        for i, save in enumerate(saves, 1):
            save_info = state_manager.get_save_info(save['name'])
            if save_info:
                print(f"{i}. {save['name']} - {save_info['player_name']} (等级{save_info['player_level']}) - {save_info['last_updated']}")
            else:
                print(f"{i}. {save['name']} - {save['modified_time']}")
        
        print(f"{len(saves) + 1}. 返回主菜单")
        
        load_choice = ui.get_player_input()
        
        if load_choice.isdigit():
            index = int(load_choice) - 1
            if 0 <= index < len(saves):
                if state_manager.load_game(saves[index]['name']):
                    return "continue_game"
                else:
                    print("读取存档失败！")
                    return "menu"
            elif index == len(saves):
                return "menu"
        
        print("无效选择。")
        return "menu"
    
    elif choice == "3" or choice == "查看存档":
        # 查看存档
        saves = state_manager.list_saves()
        if not saves:
            print("没有找到任何存档文件。")
        else:
            print("\n存档详情：")
            for save in saves:
                save_info = state_manager.get_save_info(save['name'])
                if save_info:
                    print(f"\n存档名称: {save['name']}")
                    print(f"角色: {save_info['player_name']} (等级 {save_info['player_level']})")
                    print(f"当前场景: {save_info['current_scene']}")
                    print(f"游戏状态: {'已结束' if save_info['is_ended'] else '进行中'}")
                    print(f"最后更新: {save_info['last_updated']}")
        
        input("\n按回车键返回主菜单...")
        return "menu"
    
    elif choice == "4" or choice == "退出游戏":
        return "quit"
    
    else:
        print("无效选择，请重新输入。")
        return "menu"

def game_loop(ui, engine, state_manager):
    """主游戏循环"""
    while True:
        # 获取当前游戏状态
        current_state = state_manager.get_current_state()
        
        # 检查游戏是否结束
        if current_state.get('is_end', False):
            ui.display_scene(current_state.get('description', ''))
            print("游戏结束！")
            
            # 询问是否保存游戏
            save_choice = input("是否保存游戏？(y/n): ").strip().lower()
            if save_choice in ['y', 'yes', '是']:
                save_name = input("请输入存档名称: ").strip()
                if save_name:
                    state_manager.save_game(save_name)
            break
        
        # 显示当前场景
        ui.display_scene(current_state.get('description', ''))
        
        # 显示玩家状态
        player_status = current_state.get('player_status', {})
        if player_status.get('inventory'):
            print(f"\n[背包: {', '.join(player_status['inventory'])}]")
        print(f"[{player_status.get('name', '冒险者')} - 等级{player_status.get('level', 1)} - 生命值{player_status.get('health', 100)}/{player_status.get('max_health', 100)}]")
        
        # 显示选项
        options = current_state.get('options', [])
        option_events = current_state.get('option_events', [])
        special_options = ["保存游戏", "查看角色属性", "返回主菜单"]
        
        # 展示选项并获取输入
        if options:
            ui.display_options(options + special_options)
            player_input = ui.get_player_input(options + special_options)
        else:
            print("\n特殊选项:")
            for i, option in enumerate(special_options, 1):
                print(f"  {i}. {option}")
            player_input = ui.get_player_input(special_options)
        
        # 处理特殊选项
        if player_input == "保存游戏":
            save_name = input("请输入存档名称: ").strip()
            if save_name:
                state_manager.save_game(save_name)
            continue
        elif player_input == "查看角色属性":
            player = state_manager.player
            print("\n=== 当前角色属性 ===")
            print(f"姓名: {player.name}")
            print(f"等级: {player.level}")
            print(f"经验: {player.experience}")
            print(f"生命值: {player.health}/{player.max_health}")
            print(f"背包: {', '.join(player.inventory) if player.inventory else '无'}")
            if player.skills:
                print("技能:")
                for skill, lv in player.skills.items():
                    print(f"  {skill}: {lv}")
            else:
                print("技能: 无")
            if player.attributes:
                print("其他属性:")
                for k, v in player.attributes.items():
                    print(f"  {k}: {v}")
            input("\n按回车键继续...")
            continue
        elif player_input == "返回主菜单":
            save_choice = input("是否保存当前进度？(y/n): ").strip().lower()
            if save_choice in ['y', 'yes', '是']:
                save_name = input("请输入存档名称: ").strip()
                if save_name:
                    state_manager.save_game(save_name)
            break
        
        # 处理正常游戏输入
        # 判断是否为结构化选项
        chosen_index = None
        if options and player_input in options:
            chosen_index = options.index(player_input)
        elif options and player_input.isdigit():
            idx = int(player_input) - 1
            if 0 <= idx < len(options):
                chosen_index = idx
        
        # 触发AI结构化事件
        if chosen_index is not None and option_events and chosen_index < len(option_events):
            event_str = option_events[chosen_index]
            player = state_manager.player
            if event_str and event_str != "none":
                try:
                    if event_str.startswith("heal:"):
                        amount = int(event_str.split(":")[1])
                        player.heal(amount)
                        print(f"[事件] 你恢复了 {amount} 点生命值！")
                    elif event_str.startswith("damage:"):
                        amount = int(event_str.split(":")[1])
                        player.take_damage(amount)
                        print(f"[事件] 你受到了 {amount} 点伤害！")
                    elif event_str.startswith("add_item:"):
                        item = event_str.split(":", 1)[1]
                        player.add_item(item)
                        print(f"[事件] 你获得了物品：{item}")
                    elif event_str.startswith("remove_item:"):
                        item = event_str.split(":", 1)[1]
                        if player.remove_item(item):
                            print(f"[事件] 你失去了物品：{item}")
                    elif event_str.startswith("add_experience:"):
                        exp = int(event_str.split(":")[1])
                        player.add_experience(exp)
                        print(f"[事件] 你获得了 {exp} 点经验！")
                    # 可扩展更多事件类型
                except Exception as e:
                    print(f"[事件处理异常] {e}")
        
        next_state = engine.next_step(player_input, state_manager)
        # 更新游戏状态
        if next_state:
            state_manager.update_story(
                next_state.get('scene_id', f"scene_{state_manager.story.current_scene_id}"),
                next_state.get('description', ''),
                next_state.get('options', []),
                player_input
            )
            # 如果游戏结束，标记结束
            if next_state.get('is_end', False):
                state_manager.end_game(next_state.get('ending_type', 'normal'))
            if not state_manager.player.is_alive():
                print("\n你的生命值已降为0，游戏结束！")
                state_manager.end_game("dead")
                break

def main():
    print("欢迎来到文字冒险游戏！\n")
    
    # 初始化组件
    ui = UserInterface()
    engine = GameEngine()
    state_manager = GameStateManager()
    
    # 主程序循环
    while True:
        menu_result = show_main_menu(ui, state_manager)
        
        if menu_result == "quit":
            print("感谢游玩，再见！")
            break
        
        elif menu_result in ["new_game", "continue_game"]:
            # 启动游戏引擎
            if menu_result == "new_game":
                engine.start_new_game(state_manager)
            
            # 进入游戏循环
            game_loop(ui, engine, state_manager)
        
        # menu_result == "menu" 时继续显示主菜单

if __name__ == "__main__":
    main() 