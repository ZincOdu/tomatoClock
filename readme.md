一个小巧的win桌面端番茄工作法计时器

![interface](interface.jpg)

使用python的tk开发

gen_icon_str用于生成icon字串，这样打包时就可以将图标打到程序里

打包用pyinstaller

```cmd
pyinstaller -w main.py -i tomato.ico --name=tomatoClock --onefile
```

