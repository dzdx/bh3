bh3
====




![wow screenshot](screenshot.png)


**bh3** 素材来自游戏《崩坏3》http://www.bh3.com/ ， 随机显示的文本为游戏中角色的台词


## Features

* 随机选取角色的台词用随机的颜色打印出来
* 会在终端显示一个女武神的Q版头像
* 支持指定女武神名字和编号显示对应的头像和台词，例如 `bh3 --avator mei --no 2` 将会出现影舞冲击 。不指定即为随机选择
* 支持自定义输入 `ls /usr/bin | bh3` 将会出现自定义输入的文本围绕着女武神
* 其他相关设置参考 `bh3 --help`

## Installation

1. 使用 pip

`pip install bh3`


2. 下载安装
```
git clone https://github.com/dzdx/bh3.git
cd bh3
python setup.py install
```

## Notes

你需要一个能在支持unicode的系统上运行的支持256色的终端


终端中的女武神Q版头像是由 [img2xterm][i2x] 创建

目前只录入了部分角色Q版头像和台词，希望米娜桑可以帮忙继续添加新头像和台词，或者贡献新feature.



[i2x]: https://github.com/rossy2401/img2xterm
