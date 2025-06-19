import streamlit as st
from game_engine import GameEngine
from state_manager import GameStateManager

st.set_page_config(page_title="文字冒险游戏", layout="wide")

# 初始化全局状态
if "engine" not in st.session_state:
    st.session_state.engine = GameEngine()
if "state_manager" not in st.session_state:
    st.session_state.state_manager = GameStateManager()
if "game_started" not in st.session_state:
    st.session_state.game_started = False
if "menu_mode" not in st.session_state:
    st.session_state.menu_mode = "main"
if "message" not in st.session_state:
    st.session_state.message = ""

engine = st.session_state.engine
state_manager = st.session_state.state_manager

def show_main_menu():
    st.title("🧙‍♂️ 文字冒险游戏")
    st.markdown("---")
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        if st.button("新游戏"):
            st.session_state.menu_mode = "new_game"
    with col2:
        if st.button("继续游戏"):
            st.session_state.menu_mode = "continue_game"
    with col3:
        if st.button("查看存档"):
            st.session_state.menu_mode = "view_saves"
    with col4:
        if st.button("退出游戏"):
            st.session_state.menu_mode = "quit"

    st.markdown("---")
    st.markdown("> 请选择上方操作开始游戏。")

def show_new_game():
    st.header("新游戏")
    with st.form("new_game_form"):
        player_name = st.text_input("请输入角色名称（可留空，默认为冒险者）")
        submitted = st.form_submit_button("开始冒险")
        if submitted:
            state_manager.create_new_game(player_name or "冒险者")
            engine.start_new_game(state_manager)
            st.session_state.game_started = True
            st.session_state.menu_mode = "game"
            st.session_state.message = f"欢迎，{player_name or '冒险者'}！你的冒险即将开始..."
    if st.button("返回主菜单"):
        st.session_state.menu_mode = "main"

def show_continue_game():
    st.header("继续游戏")
    saves = state_manager.list_saves()
    if not saves:
        st.info("没有找到任何存档文件。")
    else:
        for save in saves:
            save_info = state_manager.get_save_info(save['name'])
            if save_info:
                st.markdown(f"**{save['name']}** - {save_info['player_name']} (等级{save_info['player_level']}) - {save_info['last_updated']}")
                if st.button(f"读取存档: {save['name']}"):
                    if state_manager.load_game(save['name']):
                        st.session_state.game_started = True
                        st.session_state.menu_mode = "game"
                        st.session_state.message = f"已读取存档：{save['name']}"
                        return
    if st.button("返回主菜单"):
        st.session_state.menu_mode = "main"

def show_view_saves():
    st.header("存档详情")
    saves = state_manager.list_saves()
    if not saves:
        st.info("没有找到任何存档文件。")
    else:
        for save in saves:
            save_info = state_manager.get_save_info(save['name'])
            if save_info:
                st.markdown(f"**存档名称:** {save['name']}  ")
                st.markdown(f"角色: {save_info['player_name']} (等级 {save_info['player_level']})  ")
                st.markdown(f"当前场景: {save_info['current_scene']}  ")
                st.markdown(f"游戏状态: {'已结束' if save_info['is_ended'] else '进行中'}  ")
                st.markdown(f"最后更新: {save_info['last_updated']}  ")
                if st.button(f"删除存档: {save['name']}"):
                    state_manager.delete_save(save['name'])
                    st.success(f"已删除存档: {save['name']}")
    if st.button("返回主菜单"):
        st.session_state.menu_mode = "main"

def show_game():
    current_state = state_manager.get_current_state()
    player_status = current_state.get('player_status', {})
    options = current_state.get('options', [])
    option_events = current_state.get('option_events', [])
    special_options = ["保存游戏", "查看角色属性", "返回主菜单"]
    st.markdown("# 🗺️ 当前场景")
    st.markdown(f"<div style='background:#222831;color:#f2f2f2;padding:1.5em;border-radius:10px;font-size:1.2em;'>{current_state.get('description','')}</div>", unsafe_allow_html=True)
    st.markdown("---")
    col1, col2 = st.columns([2,1])
    with col2:
        st.markdown("## 🧑‍🎤 角色状态")
        st.markdown(f"**姓名:** {player_status.get('name','冒险者')}")
        st.markdown(f"**等级:** {player_status.get('level',1)}")
        st.markdown(f"**经验:** {getattr(state_manager.player, 'experience', 0)}")
        st.markdown(f"**生命值:** {player_status.get('health',100)}/{player_status.get('max_health',100)}")
        st.markdown(f"**背包:** {', '.join(player_status.get('inventory', [])) or '无'}")
        skills = getattr(state_manager.player, 'skills', {})
        if skills:
            st.markdown("**技能:**")
            for skill, lv in skills.items():
                st.markdown(f"- {skill}: {lv}")
        attributes = getattr(state_manager.player, 'attributes', {})
        if attributes:
            st.markdown("**其他属性:**")
            for k, v in attributes.items():
                st.markdown(f"- {k}: {v}")
    with col1:
        st.markdown("## 🎲 可选项")
        option_buttons = []
        for i, opt in enumerate(options):
            if st.button(opt, key=f"opt_{i}"):
                st.session_state.selected_option = opt
        for i, opt in enumerate(special_options):
            if st.button(opt, key=f"special_{i}"):
                st.session_state.selected_option = opt
        # 保存游戏输入框状态
        if "save_pending" not in st.session_state:
            st.session_state.save_pending = False
        # 处理选项
        if st.session_state.get("save_pending", False):
            save_name = st.text_input("请输入存档名称", key="save_name")
            if st.button("确认保存"):
                if save_name:
                    state_manager.save_game(save_name)
                    st.session_state.message = f"已保存游戏：{save_name}"
                st.session_state.save_pending = False
                if hasattr(st, 'rerun'):
                    st.rerun()
                else:
                    st.experimental_rerun()
        elif "selected_option" in st.session_state:
            player_input = st.session_state.selected_option
            # 用spinner包裹所有耗时处理
            with st.spinner("AI正在生成剧情，请稍候..."):
                # 特殊选项
                if player_input == "保存游戏":
                    st.session_state.save_pending = True
                    del st.session_state.selected_option
                    if hasattr(st, 'rerun'):
                        st.rerun()
                    else:
                        st.experimental_rerun()
                elif player_input == "查看角色属性":
                    st.info(f"姓名: {state_manager.player.name}\n等级: {state_manager.player.level}\n经验: {state_manager.player.experience}\n生命值: {state_manager.player.health}/{state_manager.player.max_health}\n背包: {', '.join(state_manager.player.inventory) or '无'}")
                    del st.session_state.selected_option
                    if hasattr(st, 'rerun'):
                        st.rerun()
                    else:
                        st.experimental_rerun()
                elif player_input == "返回主菜单":
                    st.session_state.menu_mode = "main"
                    st.session_state.game_started = False
                    del st.session_state.selected_option
                    if hasattr(st, 'rerun'):
                        st.rerun()
                    else:
                        st.experimental_rerun()
                else:
                    # 触发AI结构化事件
                    chosen_index = None
                    if options and player_input in options:
                        chosen_index = options.index(player_input)
                    elif options and player_input.isdigit():
                        idx = int(player_input) - 1
                        if 0 <= idx < len(options):
                            chosen_index = idx
                    if chosen_index is not None and option_events and chosen_index < len(option_events):
                        event_str = option_events[chosen_index]
                        player = state_manager.player
                        if event_str and event_str != "none":
                            try:
                                if event_str.startswith("heal:"):
                                    amount = int(event_str.split(":")[1])
                                    player.heal(amount)
                                    st.session_state.message = f"[事件] 你恢复了 {amount} 点生命值！"
                                elif event_str.startswith("damage:"):
                                    amount = int(event_str.split(":")[1])
                                    player.take_damage(amount)
                                    st.session_state.message = f"[事件] 你受到了 {amount} 点伤害！"
                                elif event_str.startswith("add_item:"):
                                    item = event_str.split(":", 1)[1]
                                    player.add_item(item)
                                    st.session_state.message = f"[事件] 你获得了物品：{item}"
                                elif event_str.startswith("remove_item:"):
                                    item = event_str.split(":", 1)[1]
                                    if player.remove_item(item):
                                        st.session_state.message = f"[事件] 你失去了物品：{item}"
                                elif event_str.startswith("add_experience:"):
                                    exp = int(event_str.split(":")[1])
                                    player.add_experience(exp)
                                    st.session_state.message = f"[事件] 你获得了 {exp} 点经验！"
                            except Exception as e:
                                st.session_state.message = f"[事件处理异常] {e}"
                    next_state = engine.next_step(player_input, state_manager)
                    if next_state:
                        state_manager.update_story(
                            next_state.get('scene_id', f"scene_{state_manager.story.current_scene_id}"),
                            next_state.get('description', ''),
                            next_state.get('options', []),
                            player_input,
                            next_state.get('option_events', [])
                        )
                        if next_state.get('is_end', False):
                            state_manager.end_game(next_state.get('ending_type', 'normal'))
                            st.session_state.message = "游戏结束！"
                            st.session_state.game_started = False
                        if not state_manager.player.is_alive():
                            st.session_state.message = "你的生命值已降为0，游戏结束！"
                            state_manager.end_game("dead")
                            st.session_state.game_started = False
                    del st.session_state.selected_option
                    if hasattr(st, 'rerun'):
                        st.rerun()
                    else:
                        st.experimental_rerun()
    st.markdown("---")
    if st.session_state.message:
        st.info(st.session_state.message)
        st.session_state.message = ""
    if not st.session_state.game_started:
        if st.button("返回主菜单", key="end_back_main"):
            st.session_state.menu_mode = "main"

def main():
    if st.session_state.menu_mode == "main":
        show_main_menu()
    elif st.session_state.menu_mode == "new_game":
        show_new_game()
    elif st.session_state.menu_mode == "continue_game":
        show_continue_game()
    elif st.session_state.menu_mode == "view_saves":
        show_view_saves()
    elif st.session_state.menu_mode == "game":
        show_game()
    elif st.session_state.menu_mode == "quit":
        st.warning("感谢游玩，再见！")

if __name__ == "__main__":
    main() 