*.exe生成指令（打包成功后项目中新增dist文件）

pip install pyinstaller

命令语法：pyinstaller -F 文件名（带后缀py）
常用参数说明：
–icon=图标路径
-F 打包成一个exe文件
-w 使用窗口，无控制台
-c 使用控制台，无窗口
-D 创建一个目录，里面包含exe以及其他一些依赖性文件
pyinstaller -h 来查看参数
 
有命令窗口弹出
pyinstaller -F shjys_rjjqk.py  
无命令窗口弹出
pyinstaller -F -w shjys_rjjqk.py 
带有图标
pyinstaller -F --icon=my.ico shjys_rjjqk.py