import tkinter as tk
import ttkbootstrap as ttk
import winsound
from base64 import b64decode
from PIL import ImageTk
from utils import TomatoMeter

min2sec = 60

class tomatoClock:
    def __init__(self, master):
        self.master = master
        self.master.title("tomato")
        self.master.resizable(False, False)
        self.master.geometry("315x320")
        icon_str = b'iVBORw0KGgoAAAANSUhEUgAAACAAAAAgCAYAAABzenr0AAAAAXNSR0IArs4c6QAAA+1JREFUWEfFlm1sU2UUx//n6ToIatxoSTTGhJioESSBSNS4QXvx5RMRibZrCC+9wyyZMdJOne38QPmgGzjX8sH3rJ0zwa6QCIuRZGS0gwGJL4mYQPAlQePEBFrxbQa39h65t7t1W8tuu17xSZqb23vO//ye8zzPeQ7hfx5UTfzuY65lWUWcqRHK8hfW7j87H62qALpSTUkAzqu/VMA5IP3nAJ1JdwgKnQw+PDCkBisFsOd40/pcllcHpUSoHKCyM9CZ9DiJOAnmLwJSYvW1ALqS7s9BdB8zSUEpnjKCqARgKRGfVwWZSQ5K8b7ZGehMerxEHFNtBFnuanfs+9Y0gKkZq+JegEcDzsQaPeC/QO7jADUCfCTgTDxmFFz9XnYGNIAR1wqw+Co/Q/K0O+IDepA9I54mhTmuvivMGzukxEHTAWZlYcYsu1LuIYAeBeN0QBpYWU7wOTOQeV5epuTYLYieAvA7BJ62vR47++pRl0MIoW0uItrwkiM+uHvE8zgzH9L2B6gt6IyHVX/k0M8EYWGKCaLDN4d7v5sNVrQEP7Ruqr9xYe17AD0505hes4Wj7VNZ+AjAEwDOMPMBItqZt+WxKzyxIiQd/DXjl/cCeG66BgGHFrC19YbIuz/r/88AuNy2fZXCyiiARSVS+P2kJXvvLd0fjO8edt3PFnEYwGLdjhk/seCWDkfik0ybfDuYTwNUX0JnglisWxzpPVG0BBm/zHOtncK8a0mkTyswnSnXRoJlPcB3MGhQydLwy498qG3QtL+5n8Bb5tKyhWPa5AsZyPjldwC0GG2e6RClbDN+OQJgh5EOCN22ntiLGkDat+UeQTVfMlBr6Jg/ZrsA/uxi3V9Hlof2T3BLi/W3RZNrJsFrRWE/GCr9oVjpNg3gF3/zKwzuMHQpNsgSMMpAAwBrpf4ksEkDyPjlUwAerFSgWnsGv60DqDV+abWC8/A/qQP8jTLXfx5B5nChP3WAywDqzBUvS+1c/hT45W8IuLMsFxONiNGvZ0CtSg+ZqF2WFBE9O3UMvc8w6I2yvEw0YuQe0AAu+TbfSmQ9T8ACE/UNpOiELRxtLJTitE9+kwit1wtAEG2o74kOFgAu7Wi+22LBKWYudYOZy0WI2npi22dcRvml8IYqqOXzgiJQOqegccne6NdFANcBYpyZN9sjfYV+sWRTmvF5fcjfauYVJ8IFhrLV3vP+8PTUXbMrvujzrqwRYiczq61XteMcQ2yzh3s/nS1k2JanffI6ANuIsLUiCsIVAPuuFrghS+3Cobqut9RyXzQMAXQPtc8jFg2A0sCgVQDbCWRjsB2MMRB+nHqOCcGjF24a/1htVoyg/wEhlYO6cVARSAAAAABJRU5ErkJggg=='
        icon_img = b64decode(icon_str)
        icon_img = ImageTk.PhotoImage(data=icon_img)
        self.master.iconphoto(False, icon_img)
        self.config_path = "config.txt"

        # 参数
        self.is_running = False
        self.state = "focus" # focus or break
        self.beep_flag = tk.BooleanVar()
        self.beep_flag.set(True)
        self.shake_flag = tk.BooleanVar()
        self.shake_flag.set(True)
        self.focus_time = 25 # min
        self.break_time = 5 # min
        self.tomato_count = 0
        self.total_focus_time = 0 # min
        self.total_break_time = 0 #min
        self.passing_time = 0 # min
        self.passing_time_sec = 0 # sec

        self.load_config()

        # 选项卡容器
        self.notebook = ttk.Notebook(self.master)
        self.notebook.pack(pady=5, fill=tk.BOTH, expand=True)

        # 计时tab页
        self.tab1 = ttk.Frame(self.notebook)
        self.notebook.add(self.tab1, text="计时")

        # tab1
        self.meter = TomatoMeter(
            self.tab1,
            metersize=150,
            amountused=self.focus_time * min2sec,
            amounttotal=self.focus_time * min2sec,
            amountused_show=self.focus_time,
            meterthickness=15,
            metertype="semi",
            bootstyle="heat",
            textright='min',
            stripethickness=2,
            subtext="准备专注",
            interactive=False,
        )
        self.meter.pack(pady=(5,0))

        # 创建按钮框架，用于水平排列部分按钮
        button_frame = ttk.Frame(self.tab1)
        button_frame.pack()

        self.start_pause_button = ttk.Button(button_frame, text="开始", command=self.start_pause)
        self.start_pause_button.pack(side=tk.LEFT)
        self.reset_button = ttk.Button(button_frame, text="重置", command=self.reset)
        self.reset_button.pack(side=tk.LEFT, padx=5)

        # tab2
        self.tab2 = ttk.Frame(self.notebook)
        self.notebook.add(self.tab2, text="统计")

        # 在第二个Tab页面添加内容
        # 总番茄统计
        tomato_count_frame = ttk.Frame(self.tab2)
        tomato_count_frame.pack(pady=(50, 0))

        ttk.Label(tomato_count_frame, text=f"共完成 ").pack(side=tk.LEFT)
        self.total_tomato_label = ttk.Label(tomato_count_frame, text=f"{self.tomato_count}")
        self.total_tomato_label.pack(side=tk.LEFT, padx=5)
        ttk.Label(tomato_count_frame, text=f" 个番茄").pack(side=tk.LEFT, padx=5)

        # 总专注时长统计
        focus_time_frame = ttk.Frame(self.tab2)
        focus_time_frame.pack(pady=(10,0))
        ttk.Label(focus_time_frame, text=f"专注总计 ").pack(side=tk.LEFT)
        self.total_focus_time_label = ttk.Label(focus_time_frame, text=f"{self.total_focus_time}")
        self.total_focus_time_label.pack(side=tk.LEFT, padx=5)
        ttk.Label(focus_time_frame, text=f"分钟").pack(side=tk.LEFT, padx=5)

        # 总休息时长统计
        break_time_frame = ttk.Frame(self.tab2)
        break_time_frame.pack(pady=(10,0))
        ttk.Label(break_time_frame, text=f"休息总计 ").pack(side=tk.LEFT)
        self.total_break_time_label = ttk.Label(break_time_frame, text=f"{self.total_break_time}")
        self.total_break_time_label.pack(side=tk.LEFT, padx=5)
        ttk.Label(break_time_frame, text=f"分钟").pack(side=tk.LEFT, padx=5)

        # tab3
        self.tab3 = ttk.Frame(self.notebook)
        self.notebook.add(self.tab3, text="设置")

        focus_time_frame = ttk.Frame(self.tab3)
        focus_time_frame.pack(pady=(50,0))

        # 专注时间显示标签
        ttk.Label(focus_time_frame, text="专注时间:").pack(side=tk.LEFT)
        self.focus_time_label = ttk.Label(focus_time_frame, text=f"{self.focus_time:02d}")
        self.focus_time_label.pack(side=tk.LEFT, padx=5)
        ttk.Label(focus_time_frame, text="分钟").pack(side=tk.LEFT)

        # 增加专注时间按钮
        increase_focus_button = ttk.Button(focus_time_frame, text="+", command=self.increase_focus_time, width=1)
        increase_focus_button.pack(side=tk.LEFT, padx=5)

        # 减少专注时间按钮
        decrease_focus_button = ttk.Button(focus_time_frame, text="-", command=self.decrease_focus_time, width=1)
        decrease_focus_button.pack(side=tk.LEFT, padx=5)

        # 休息时间调节按钮框架
        break_time_frame = ttk.Frame(self.tab3)
        break_time_frame.pack(pady=10)

        # 休息时间显示标签
        ttk.Label(break_time_frame, text="休息时间:").pack(side=tk.LEFT)
        self.break_time_label = ttk.Label(break_time_frame, text=f"{self.break_time:02d}")
        self.break_time_label.pack(side=tk.LEFT, padx=5)
        ttk.Label(break_time_frame, text="分钟").pack(side=tk.LEFT)

        # 增加休息时间按钮
        increase_break_button = ttk.Button(break_time_frame, text="+", command=self.increase_break_time, width=1)
        increase_break_button.pack(side=tk.LEFT, padx=5)

        # 减少休息时间按钮
        decrease_break_button = ttk.Button(break_time_frame, text="-", command=self.decrease_break_time, width=1)
        decrease_break_button.pack(side=tk.LEFT, padx=5)

        # 提示选项
        remind_frame = ttk.Frame(self.tab3)
        remind_frame.pack(pady=20)

        ttk.Checkbutton(remind_frame, text = "声音提示", variable=self.beep_flag, command=self.save_config).pack(side=tk.LEFT, padx=(0,15))
        ttk.Checkbutton(remind_frame, text = "抖窗提示", variable=self.shake_flag, command=self.save_config).pack(side=tk.LEFT, padx=(15,0))

    def load_config(self):
        try:
            with open(self.config_path, "r") as f:
                lines = f.readlines()
                self.focus_time = int(lines[0].strip())
                self.break_time = int(lines[1].strip())
                self.beep_flag.set(lines[2].strip() == "True")
                self.shake_flag.set(lines[3].strip() == "True")
        except:
            pass

    def save_config(self):
        with open(self.config_path, "w") as f:
            f.write(f"{self.focus_time}\n")
            f.write(f"{self.break_time}\n")
            f.write(f"{self.beep_flag.get()}\n")
            f.write(f"{self.shake_flag.get()}\n")

    def start_pause(self):
        if self.is_running:
            self.is_running = False
            self.start_pause_button.config(text="开始")
            if self.state == "focus":
                self.meter.configure(subtext="准备专注")
            else:
                self.meter.configure(subtext="准备休息")
        else:
            self.is_running = True
            self.start_pause_button.config(text="暂停")
            if self.state == "focus":
                self.meter.configure(subtext="专注中")
            else:
                self.meter.configure(subtext="休息中")
            self.update_timer()

    def reset(self):
        self.is_running = False
        self.state = "focus"
        self.start_pause_button.config(text="开始", bootstyle="heat")
        self.reset_button.config(bootstyle="heat")
        self.meter.configure(amountused=self.focus_time * min2sec,
                             amounttotal=self.focus_time * min2sec,
                             amountused_show=self.focus_time,
                             subtext="准备专注",
                             bootstyle="heat")
        self.passing_time_sec = 0
        self.passing_time = 0

    def update_timer(self):
        if self.is_running and self.state == "focus":
            self.passing_time_sec += 1
            self.master.after(1000, self.update_timer)
            self.meter.step(1)
            if self.passing_time_sec % min2sec == 0:
                self.passing_time += 1
                self.meter.configure(amountused_show=self.focus_time - self.passing_time)
            if self.passing_time_sec >= self.focus_time * min2sec:
                self.is_running = False
                self.state = "break"
                self.play_break_sound()
                self.shake_window()
                self.start_pause_button.config(text="开始", bootstyle="success")
                self.reset_button.config(bootstyle="success")
                self.meter.configure(amountused=self.break_time * min2sec,
                                     amounttotal=self.break_time * min2sec,
                                     amountused_show=self.break_time,
                                     subtext="准备休息", bootstyle="success")
                self.passing_time_sec = 0
                self.passing_time = 0
                self.total_focus_time += self.focus_time
                self.total_focus_time_label.config(text=f"{self.total_focus_time}")

        elif self.is_running and self.state == "break":
            self.passing_time_sec += 1
            self.master.after(1000, self.update_timer)
            self.meter.step(1)
            if self.passing_time_sec % min2sec == 0:
                self.passing_time += 1
                self.meter.configure(amountused_show=self.break_time - self.passing_time)
            if self.passing_time_sec >= self.break_time * min2sec:
                self.is_running = False
                self.state = "focus"
                self.play_focus_sound()
                self.shake_window()
                self.start_pause_button.config(text="开始", bootstyle="heat")
                self.reset_button.config(bootstyle="heat")
                self.meter.configure(amountused=self.focus_time * min2sec,
                                     amounttotal=self.focus_time * min2sec,
                                     amountused_show=self.focus_time,
                                     subtext="准备专注", bootstyle="heat")
                self.passing_time_sec = 0
                self.passing_time = 0
                self.tomato_count += 1
                self.total_tomato_label.config(text=f"{self.tomato_count}")
                self.total_break_time += self.break_time
                self.total_break_time_label.config(text=f"{self.total_break_time}")

    def increase_focus_time(self):
        if not self.is_running and self.focus_time < 60:
            self.focus_time += 5
            self.focus_time_label.config(text=f"{self.focus_time:02d}")
            if self.state == "focus":
                self.meter.configure(amountused=max(0, (self.focus_time - self.passing_time) * min2sec),
                                     amounttotal=self.focus_time * min2sec,
                                     amountused_show=self.focus_time)
            self.save_config()

    def decrease_focus_time(self):
        if not self.is_running and self.focus_time > 5:
            self.focus_time -= 5
            self.focus_time_label.config(text=f"{self.focus_time:02d}")
            if self.state == "focus":
                self.meter.configure(amountused=max(0, (self.focus_time - self.passing_time) * min2sec),
                                     amounttotal=self.focus_time * min2sec,
                                     amountused_show=self.focus_time)
            self.save_config()

    def increase_break_time(self):
        if not self.is_running and self.break_time < 60:
            self.break_time += 5
            self.break_time_label.config(text=f"{self.break_time:02d}")
            if self.state == "break":
                self.meter.configure(max(0, (self.break_time - self.passing_time) * min2sec),
                                     amounttotal=self.break_time * min2sec,
                                     amountused_show=self.break_time)
            self.save_config()

    def decrease_break_time(self):
        if not self.is_running and self.break_time > 5:
            self.break_time -= 5
            self.break_time_label.config(text=f"{self.break_time:02d}")
            if self.state == "break":
                self.meter.configure(max(0, (self.break_time - self.passing_time) * min2sec),
                                     amounttotal=self.break_time * min2sec,
                                     amountused_show=self.break_time)
            self.save_config()

    def play_break_sound(self):
        if self.beep_flag.get():
            winsound.Beep(200, 400)
            winsound.Beep(400, 400)

    def play_focus_sound(self):
        if self.beep_flag.get():
            winsound.Beep(400, 400)
            winsound.Beep(200, 400)

    def shake_window(self):
        if self.shake_flag.get():
            if self.master.state() == "iconic":
                self.master.deiconify()
            sign = 1
            for _ in range(10):
                x_offset = sign * 50
                sign *= -1
                self.master.geometry(f"+{self.master.winfo_x() + x_offset}+{self.master.winfo_y()}")
                self.master.update()
                self.master.after(50)

if __name__ == '__main__':
    root = ttk.Window(themename='journal')
    app = tomatoClock(root)
    root.mainloop()