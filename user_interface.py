class UserInterface:
    def display_scene(self, description):
        print("\n场景描述：")
        print(description)

    def display_options(self, options):
        print("\n可选项：")
        for idx, opt in enumerate(options, 1):
            print(f"  {idx}. {opt}")

    def get_player_input(self, options=None):
        while True:
            if options:
                inp = input("请输入选项编号或自定义指令：").strip()
                if inp.isdigit():
                    idx = int(inp)
                    if 1 <= idx <= len(options):
                        return options[idx-1]
                    else:
                        print(f"编号无效，请输入1-{len(options)}之间的数字，或自定义文本。")
                elif inp:
                    return inp
                else:
                    print("输入不能为空，请重新输入。")
            else:
                inp = input("请输入指令：").strip()
                if inp:
                    return inp
                else:
                    print("输入不能为空，请重新输入。")

    def show_message(self, msg):
        print(msg) 