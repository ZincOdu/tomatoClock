import tkinter as tk
import tkinter.filedialog
import ttkbootstrap as ttk
from PIL import ImageTk, Image
import os
import time
import threading
import pygame
from utils import (TomatoMeter, break_beep, focus_beep, warning_sound,
                   get_icon_img, get_like_img)

min2sec = 2

class tomatoClock:
    def __init__(self, master):
        self.master = master
        self.master.title("tomato")
        self.master.resizable(False, False)
        self.master.geometry("315x320")
        self.master.iconphoto(False, ImageTk.PhotoImage(data=get_icon_img()))
        self.config_path = "config.txt"

        pygame.mixer.init()

        # 参数
        self.is_running = False
        self.state = "focus"  # focus or break
        self.focus_time = 25  # min
        self.break_time = 5  # min
        self.tomato_count = 0
        self.total_focus_time = 0  # min
        self.total_break_time = 0  # min
        self.passing_time = 0  # min
        self.passing_time_sec = 0  # sec
        self.beep_flag = tk.BooleanVar()
        self.beep_flag.set(True)
        self.shake_flag = tk.BooleanVar()
        self.shake_flag.set(True)
        self.lock_screen_flag = tk.BooleanVar()
        self.lock_screen_flag.set(False)
        self.play_music_flag = tk.BooleanVar()
        self.play_music_flag.set(False)
        self.remind_sound_path = tk.StringVar()
        self.remind_sound_path.set("默认")
        self.custom_remind_sound = None
        self.music_path = tk.StringVar()
        self.music_path.set("")
        self.custom_music = None
        self.music_channel = None

        # 按钮防抖
        self.last_click_time = 0

        # 加载配置
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
        self.meter.pack(pady=(5, 0))

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

        # 日期
        date_frame = ttk.Frame(self.tab2)
        date_frame.pack(pady=(5, 0))
        tk.Label(date_frame, text="今天是").pack(side=tk.LEFT)
        tk.Label(date_frame, text=time.strftime("%Y-%m-%d %A", time.localtime())).pack(side=tk.LEFT, padx=5)

        # 总番茄统计
        tomato_count_frame = ttk.Frame(self.tab2)
        tomato_count_frame.pack(pady=(5, 0))

        tk.Label(tomato_count_frame, text=f"共完成").pack(side=tk.LEFT,padx=2)
        self.total_tomato_label = tk.Label(tomato_count_frame, text=f"{self.tomato_count}")
        self.total_tomato_label.pack(side=tk.LEFT, padx=2)
        tk.Label(tomato_count_frame, text=f"个番茄").pack(side=tk.LEFT, padx=2)

        # 总时长统计
        total_time_frame = ttk.Frame(self.tab2)
        total_time_frame.pack(pady=(2, 0))
        tk.Label(total_time_frame, text=f"专注").pack(side=tk.LEFT,padx=2)
        self.total_focus_time_label = ttk.Label(total_time_frame, text=f"{self.total_focus_time}")
        self.total_focus_time_label.pack(side=tk.LEFT, padx=2)
        tk.Label(total_time_frame, text=f"分钟，").pack(side=tk.LEFT, padx=2)
        tk.Label(total_time_frame, text=f"休息").pack(side=tk.LEFT,padx=(0,2))
        self.total_break_time_label = tk.Label(total_time_frame, text=f"{self.total_break_time}")
        self.total_break_time_label.pack(side=tk.LEFT, padx=2)
        tk.Label(total_time_frame, text=f"分钟").pack(side=tk.LEFT, padx=2)

        # tab3
        self.tab3 = ttk.Frame(self.notebook)
        self.notebook.add(self.tab3, text="设置")

        focus_time_frame = ttk.Frame(self.tab3)
        focus_time_frame.pack(pady=(12, 0))

        # 专注时间显示标签
        tk.Label(focus_time_frame, text="专注时间:").pack(side=tk.LEFT)
        self.focus_time_label = tk.Label(focus_time_frame, text=f"{self.focus_time:02d}")
        self.focus_time_label.pack(side=tk.LEFT, padx=5)
        tk.Label(focus_time_frame, text="分钟").pack(side=tk.LEFT)

        # 增加专注时间按钮
        ttk.Button(focus_time_frame, text="+", command=self.increase_focus_time,
                   width=1, style='tomato.TButton').pack(side=tk.LEFT, padx=2)

        # 减少专注时间按钮
        ttk.Button(focus_time_frame, text="-", command=self.decrease_focus_time,
                   width=1, style='tomato.TButton').pack(side=tk.LEFT, padx=2)

        # 休息时间调节按钮框架
        break_time_frame = ttk.Frame(self.tab3)
        break_time_frame.pack(pady=(10, 0))

        # 休息时间显示标签
        tk.Label(break_time_frame, text="休息时间:").pack(side=tk.LEFT)
        self.break_time_label = tk.Label(break_time_frame, text=f"{self.break_time:02d}")
        self.break_time_label.pack(side=tk.LEFT, padx=5)
        tk.Label(break_time_frame, text="分钟").pack(side=tk.LEFT)

        # 增加休息时间按钮
        ttk.Button(break_time_frame, text="+", command=self.increase_break_time,
                   width=1, style='tomato.TButton').pack(side=tk.LEFT, padx=2)

        # 减少休息时间按钮
        ttk.Button(break_time_frame, text="-", command=self.decrease_break_time,
                   width=1, style='tomato.TButton').pack(side=tk.LEFT, padx=2)

        # 提示选项
        remind_frame = ttk.Frame(self.tab3)
        remind_frame.pack(pady=(25, 0))

        ttk.Checkbutton(remind_frame, text="声音提示", variable=self.beep_flag,
                        command=self.set_remind_sound).pack(side=tk.LEFT, padx=(0, 15))
        ttk.Checkbutton(remind_frame, text="抖窗提示", variable=self.shake_flag,
                        command=self.set_shake_window).pack(side=tk.LEFT, padx=(15, 0))

        # 自定义提示声
        custom_sound_frame = ttk.Frame(self.tab3)
        custom_sound_frame.pack(pady=(10, 0))
        remind_sound_state = tk.NORMAL if self.beep_flag.get() else tk.DISABLED
        self.remind_sound_label = tk.Label(custom_sound_frame, text="提示声:", state=remind_sound_state)
        self.remind_sound_label.pack(side=tk.LEFT, padx=(0, 0))
        self.remind_sound_entry = tk.Entry(custom_sound_frame, textvariable=self.remind_sound_path,
                                           width=10, state=remind_sound_state)
        self.remind_sound_entry.pack(side=tk.LEFT, padx=(5, 0))
        self.remind_sound_select_button = ttk.Button(custom_sound_frame, text="...",
                                                     command=self.select_remind_sound_path,
                                                     style='tomato.TButton', state=remind_sound_state)
        self.remind_sound_select_button.pack(side=tk.LEFT, padx=(5, 0))

        # 休息选项
        break_option_frame = ttk.Frame(self.tab3)
        break_option_frame.pack(pady=(25, 0))

        tk.Label(break_option_frame, text="休息时:").pack(side=tk.LEFT, padx=(0, 0))
        ttk.Checkbutton(break_option_frame, text="锁屏", variable=self.lock_screen_flag,
                        command=self.set_lock_screen).pack(
            side=tk.LEFT, padx=(15, 0))
        ttk.Checkbutton(break_option_frame, text="播放音乐", variable=self.play_music_flag,
                        command=self.set_play_music).pack(
            side=tk.LEFT, padx=(15, 0))

        # 自定义音乐
        music_frame = ttk.Frame(self.tab3)
        music_frame.pack(pady=(10, 0))
        music_state = tk.NORMAL if self.play_music_flag.get() else tk.DISABLED
        self.music_label = tk.Label(music_frame, text="音乐:", state=music_state)
        self.music_label.pack(side=tk.LEFT, padx=(0, 0))
        self.music_path_entry = tk.Entry(music_frame, textvariable=self.music_path, width=11, state=music_state)
        self.music_path_entry.pack(side=tk.LEFT, padx=(5, 0))
        self.music_select_button = ttk.Button(music_frame, text="...", command=self.select_music_path,
                                              style='tomato.TButton', state=music_state)
        self.music_select_button.pack(side=tk.LEFT, padx=(5, 0))

        # 赞赏tab
        self.tab4 = ttk.Frame(self.notebook)
        self.notebook.add(self.tab4, text="赞赏")
        self.like_img = ImageTk.PhotoImage(data=get_like_img())
        ttk.Label(self.tab4, image=self.like_img).pack(pady=(10, 0))

    def load_config(self):
        try:
            with open(self.config_path, "r") as f:
                lines = f.readlines()
                self.focus_time = int(lines[0].strip())
                self.break_time = int(lines[1].strip())
                self.beep_flag.set(lines[2].strip() == "True")
                self.shake_flag.set(lines[3].strip() == "True")
                self.remind_sound_path.set(lines[4].strip())
                self.lock_screen_flag.set(lines[5].strip() == "True")
                self.play_music_flag.set(lines[6].strip() == "True")
                self.music_path.set(lines[7].strip())
            if os.path.exists(self.remind_sound_path.get()):
                self.custom_remind_sound = pygame.mixer.Sound(self.remind_sound_path.get())
            else:
                self.custom_remind_sound = None
                self.remind_sound_path.set("默认")
            if os.path.exists(self.music_path.get()):
                self.custom_music = pygame.mixer.Sound(self.music_path.get())
            else:
                self.custom_music = None
                self.music_path.set("")
        except:
            pass

    def save_config(self):
        if not os.path.exists(self.remind_sound_path.get()):
            self.remind_sound_path.set("默认")
            self.custom_remind_sound = None
        if not os.path.exists(self.music_path.get()):
            self.music_path.set("")
            self.custom_music = None
        with open(self.config_path, "w") as f:
            f.write(f"{self.focus_time}\n")
            f.write(f"{self.break_time}\n")
            f.write(f"{self.beep_flag.get()}\n")
            f.write(f"{self.shake_flag.get()}\n")
            f.write(f"{self.remind_sound_path.get()}\n")
            f.write(f"{self.lock_screen_flag.get()}\n")
            f.write(f"{self.play_music_flag.get()}\n")
            f.write(f"{self.music_path.get()}\n")

    def set_tab3_disabled(self):
        for frame_child in self.tab3.winfo_children():
            for child in frame_child.winfo_children():
                child.config(state=tk.DISABLED)

    def set_tab3_enabled(self):
        for frame_child in self.tab3.winfo_children():
            for child in frame_child.winfo_children():
                child.config(state=tk.NORMAL)
                if not self.beep_flag.get():
                    self.remind_sound_label.config(state=tk.DISABLED)
                    self.remind_sound_entry.config(state=tk.DISABLED)
                    self.remind_sound_select_button.config(state=tk.DISABLED)
                if not self.play_music_flag.get():
                    self.music_label.config(state=tk.DISABLED)
                    self.music_path_entry.config(state=tk.DISABLED)
                    self.music_select_button.config(state=tk.DISABLED)

    def switch_to_pause(self):
        self.is_running = False
        self.start_pause_button.config(text="开始")
        if self.state == "focus":
            self.meter.configure(subtext="准备专注")
        else:
            self.pause_music()
            self.meter.configure(subtext="准备休息")
        self.set_tab3_enabled()

    def switch_to_start(self):
        self.is_running = True
        self.start_pause_button.config(text="暂停")
        if self.state == "focus":
            self.meter.configure(subtext="专注中")
        else:
            self.play_music()
            self.meter.configure(subtext="休息中")
        self.set_tab3_disabled()


    def start_pause(self):
        if self.is_running:
            self.switch_to_pause()
        else:
            self.switch_to_start()
            self.update_timer()

    def reset_to_ready_for_focus(self):
        self.is_running = False
        self.state = "focus"
        self.start_pause_button.config(text="开始", bootstyle="heat")
        self.reset_button.config(bootstyle="heat")
        self.meter.configure(amountused=self.focus_time * min2sec,
                             amounttotal=self.focus_time * min2sec,
                             amountused_show=self.focus_time,
                             subtext="准备专注",
                             bootstyle="heat")
        self.set_tab3_enabled()
        self.passing_time_sec = 0
        self.passing_time = 0
        self.stop_music()


    def reset_to_ready_for_break(self):
        self.is_running = False
        self.state = "break"
        self.start_pause_button.config(text="开始", bootstyle="success")
        self.reset_button.config(bootstyle="success")
        self.meter.configure(amountused=self.break_time * min2sec,
                             amounttotal=self.break_time * min2sec,
                             amountused_show=self.break_time,
                             subtext="准备休息",
                             bootstyle="success")
        self.set_tab3_enabled()
        self.passing_time_sec = 0
        self.passing_time = 0
        self.stop_music()


    def reset(self):
        self.reset_to_ready_for_focus()

    def update_timer(self):
        if self.is_running and self.state == "focus":
            self.passing_time_sec += 1
            self.master.after(1000, self.update_timer)
            self.meter.step(1)
            if self.passing_time_sec % min2sec == 0:
                self.passing_time += 1
                self.meter.configure(amountused_show=self.focus_time - self.passing_time)
            if self.passing_time_sec >= self.focus_time * min2sec:
                self.reset_to_ready_for_break()
                threading.Thread(target=self.play_break_remind_sound).start()
                self.shake_window()
                self.total_focus_time += self.focus_time
                self.total_focus_time_label.config(text=f"{self.total_focus_time}")
                self.lock_screen()
        elif self.is_running and self.state == "break":
            self.passing_time_sec += 1
            self.master.after(1000, self.update_timer)
            self.meter.step(1)
            if self.passing_time_sec % min2sec == 0:
                self.passing_time += 1
                self.meter.configure(amountused_show=self.break_time - self.passing_time)
            if self.passing_time_sec >= self.break_time * min2sec:
                self.reset_to_ready_for_focus()
                threading.Thread(target=self.play_focus_remind_sound).start()
                self.shake_window()
                self.tomato_count += 1
                self.total_tomato_label.config(text=f"{self.tomato_count}")
                self.total_break_time += self.break_time
                self.total_break_time_label.config(text=f"{self.total_break_time}")

    # 按钮防抖
    def can_click(self):
        current_time = time.time()
        if current_time - self.last_click_time > 0.5:
            self.last_click_time = current_time
            return True
        else:
            return False


    def increase_focus_time(self):
        if self.can_click():
            if self.focus_time < 60:
                self.focus_time += 5
                self.focus_time_label.config(text=f"{self.focus_time:02d}")
                if self.state == "focus":
                    self.meter.configure(amountused=max(0,self.focus_time * min2sec - self.passing_time_sec),
                                         amounttotal=self.focus_time * min2sec,
                                         amountused_show=max(0,self.focus_time - self.passing_time))
                self.save_config()
            else:
                threading.Thread(target=warning_sound).start()

    def decrease_focus_time(self):
        if self.can_click():
            if self.focus_time > 5:
                self.focus_time -= 5
                self.focus_time_label.config(text=f"{self.focus_time:02d}")
                if self.state == "focus":
                    self.meter.configure(amountused=max(0, self.focus_time * min2sec - self.passing_time_sec),
                                         amounttotal=self.focus_time * min2sec,
                                         amountused_show=max(0,self.focus_time - self.passing_time))
                self.save_config()
            else:
                threading.Thread(target=warning_sound).start()

    def increase_break_time(self):
        if self.can_click():
            if self.break_time < 60:
                self.break_time += 5
                self.break_time_label.config(text=f"{self.break_time:02d}")
                if self.state == "break":
                    self.meter.configure(amountused=max(0, self.break_time * min2sec - self.passing_time_sec),
                                         amounttotal=self.break_time * min2sec,
                                         amountused_show=max(0,self.break_time - self.passing_time))
                self.save_config()
            else:
                threading.Thread(target=warning_sound).start()

    def decrease_break_time(self):
        if self.can_click():
            if self.break_time > 5:
                self.break_time -= 5
                self.break_time_label.config(text=f"{self.break_time:02d}")
                if self.state == "break":
                    self.meter.configure(amountused=max(0, self.break_time * min2sec - self.passing_time_sec),
                                         amounttotal=self.break_time * min2sec,
                                         amountused_show=max(0, self.break_time - self.passing_time))
                self.save_config()
            else:
                threading.Thread(target=warning_sound).start()

    def set_remind_sound(self):
        if self.beep_flag.get():
            self.remind_sound_label.config(state=tk.NORMAL)
            self.remind_sound_entry.config(state=tk.NORMAL)
            self.remind_sound_select_button.config(state=tk.NORMAL)
            threading.Thread(target=self.play_remind_sound).start()
        else:
            self.remind_sound_label.config(state=tk.DISABLED)
            self.remind_sound_entry.config(state=tk.DISABLED)
            self.remind_sound_select_button.config(state=tk.DISABLED)
        self.save_config()

    def set_shake_window(self):
        if self.shake_flag.get():
            self.shake_window()
        self.save_config()

    def set_lock_screen(self):
        self.save_config()

    def set_play_music(self):
        if self.play_music_flag.get():
            self.music_label.config(state=tk.NORMAL)
            self.music_path_entry.config(state=tk.NORMAL)
            self.music_select_button.config(state=tk.NORMAL)
        else:
            self.music_label.config(state=tk.DISABLED)
            self.music_path_entry.config(state=tk.DISABLED)
            self.music_select_button.config(state=tk.DISABLED)
        self.save_config()

    def select_remind_sound_path(self):
        if self.can_click():
            path_ = tkinter.filedialog.askopenfilename(filetypes=[("音频文件", "*.mp3;*.wav")])
            path_ = path_.replace("/", "\\")
            if os.path.exists(path_):
                self.remind_sound_path.set(path_)
                self.custom_remind_sound = pygame.mixer.Sound(path_)
            self.save_config()

    def select_music_path(self):
        if self.can_click():
            path_ = tkinter.filedialog.askopenfilename(filetypes=[("音频文件", "*.mp3;*.wav")])
            path_ = path_.replace("/", "\\")
            if os.path.exists(path_):
                if self.music_channel is not None:
                    self.music_channel.stop()
                    self.music_channel = None
                self.music_path.set(path_)
                self.custom_music = pygame.mixer.Sound(path_)
            self.save_config()

    # 用户自定义提示声控制在10秒内
    def play_custom_remind_sound(self):
        remind_channel = self.custom_remind_sound.play()
        pygame.time.delay(10000)
        remind_channel.fadeout(500)

    def play_remind_sound(self):
        if self.custom_remind_sound is not None:
            self.play_custom_remind_sound()
        else:
            focus_beep()

    def play_break_remind_sound(self):
        if self.beep_flag.get():
            if self.custom_remind_sound is not None:
                self.play_custom_remind_sound()
            else:
                break_beep()

    def play_focus_remind_sound(self):
        if self.beep_flag.get():
            if self.custom_remind_sound is not None:
                self.play_custom_remind_sound()
            else:
                focus_beep()

    def play_music(self):
        if self.play_music_flag.get():
            if self.custom_music is not None:
                if self.music_channel is None:
                    pygame.time.delay(500)
                    self.music_channel = self.custom_music.play(-1)
                else:
                    if self.music_channel.get_busy():
                        pygame.time.delay(500)
                        self.music_channel.unpause()
                    else:
                        self.music_channel = self.custom_music.play(-1)

    def pause_music(self):
        if self.play_music_flag.get():
            if self.custom_music is not None and self.music_channel is not None:
                if self.music_channel.get_busy():
                    pygame.time.delay(500)
                    self.music_channel.pause()

    def stop_music(self):
        if self.play_music_flag.get():
            if self.custom_music is not None and self.music_channel is not None:
                if self.music_channel.get_busy():
                    self.music_channel.fadeout(1000)

    def shake_window(self):
        if self.shake_flag.get():
            if self.master.state() == "iconic":
                self.master.deiconify()
            self.master.attributes("-topmost", True)
            sign = 1
            for _ in range(10):
                x_offset = sign * 50
                sign *= -1
                self.master.geometry(f"+{self.master.winfo_x() + x_offset}+{self.master.winfo_y()}")
                self.master.update()
                self.master.after(50)

    def lock_screen(self):
        if self.lock_screen_flag.get():
            self.switch_to_start()
            os.system("rundll32.exe user32.dll, LockWorkStation")


if __name__ == '__main__':
    root = ttk.Window()
    style = ttk.Style()
    style.theme_use('journal')
    style.configure('tomato.TButton', font=('Bold', 8), padding=(6, 3, 6, 3))
    app = tomatoClock(root)
    root.mainloop()
