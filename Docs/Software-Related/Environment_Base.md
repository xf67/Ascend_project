# 环境搭建

这里总结一份环境搭建的文档。

## 环境检查

如果不清楚已经安装了哪些部分，可以去NN-demo仓中的better_ATC文件夹中找到[check_env.py](https://gitee.com/sail-edge-center/nn-demo/blob/master/better_ATC/check_env.py)，检查依赖的安装情况。

下面假设你手上是一台新制卡之后的机器，里面除了NPU的驱动，Hw账户，暂时什么都没有。我们从这一步开始。

## Python

Ubuntu18.04随系统附带的python版本为3.6.x，这不符合华为3.7~3.9的python版本要求，故我们需要更新python。

### conda

安装conda，然后在conda环境中安装任何你想要的python版本，并使用conda管理你的python库，是一个明智且便利的做法。

使用conda安装python的**操作如下**：

下载适合arm64版本的miniconda安装包并安装之。

```sh
conda config --append channels conda-forge
conda create --name py375 python=3.7.5 -y 
#这里示例安装3.7.5版本，因为这个python版本已经不被支持，所以需要先添加channel才能下载到。
#对于安装3.8及以上的版本，不需要conda config的步骤
conda config --remove channels conda-forge
conda activate py375
python -V #检查python版本是否正确
```

### 不用conda

当然我们也可以直接对root的python进行更新。

此法的**优点**在于，在某些需要sudo运行python的时候，你的sudo可以调用到这个新版本的python而不是原来自带的3.6.x。

此法的**问题**在于，用pip安装python库时，也安装在root，但是我们的SSD是挂在/home的，root是SD卡较容易满。

可以选择更新root的python并安装一些必要的包，说不定能在特定关头带来方便。

更新python的**操作如下**：

前往[python官网](https://www.python.org/downloads/)下载python到随便一个目录，解压之。

```sh
mkdir /usr/local/python3 
cd 下载的python所在的文件夹
./configure --prefix=/usr/local/python3 #设置安装目录为我们刚才新建的文件夹
make -j8 #板卡的CPU很慢，用-j8调用多核以加快速度
make install
ln -s /usr/local/python3/bin/python3 /usr/local/bin/python3
ln -s /usr/local/python3/bin/pip3 /usr/local/bin/pip3
#你高兴的话，也可以把pip和python也设置软连接过去。我感觉python2也没什么大用。
ln -s /usr/local/python3/bin/python3 /usr/local/bin/python
ln -s /usr/local/python3/bin/pip3 /usr/local/bin/pip
python -V #检查python版本是否正确
```

## python库和其他软件依赖

具体需要什么库直接运行[check_env.py](https://gitee.com/sail-edge-center/nn-demo/blob/master/better_ATC/check_env.py)检查。

`conda install`和`pip install`解决python库，`sudo apt install`或`sudo apt-get install`解决软件即可。

### apt换源

默认的apt源有时候比较慢，可以考虑换交大的镜像。

`sudo vim /etc/apt/sources.list` 添加

```
#SJTU
deb https://mirror.sjtu.edu.cn/ubuntu-ports/ bionic main restricted universe multiverse
deb https://mirror.sjtu.edu.cn/ubuntu-ports/ bionic-security main restricted universe multiverse
deb https://mirror.sjtu.edu.cn/ubuntu-ports/ bionic-updates main restricted universe multiverse
deb https://mirror.sjtu.edu.cn/ubuntu-ports/ bionic-backports main restricted universe multiverse

deb-src https://mirror.sjtu.edu.cn/ubuntu-ports/ bionic main restricted universe multiverse
deb-src https://mirror.sjtu.edu.cn/ubuntu-ports/ bionic-security main restricted universe multiverse
deb-src https://mirror.sjtu.edu.cn/ubuntu-ports/ bionic-updates main restricted universe multiverse
deb-src https://mirror.sjtu.edu.cn/ubuntu-ports/ bionic-backports main restricted universe multiverse
```

然后把原来的注释掉。

使用交大源在校内的下载速度能到10MB/s，还是非常香的。

## CANN

如果需要开发和推理，则安装**CANN toolkit**；如果只需要推理，可安装**CANN nnrt**，它的安装包比toolkit小不少。

下载对应的`.run`格式的安装包，`sudo chmod +x 软件包名.run`，然后运行`./软件包地址 --install`即可。

接下来把环境变量的设置脚本添加到bashrc：

```sh
vim ~/.bashrc
#加入以下几行
	#nnrt
	source /home/{user}/Ascend/nnrt/set_env.sh
	#toolkit
	source /home/{user}/Ascend/ascend-toolkit/set_env.sh
```

{user}处填自己的用户名，nnrt还是toolkit按需选择。

接下来把自己加入Hw的用户组`sudo usermod -a -G HwHiAiUser {user}`

然后应该就可以正常使用`sudo npu-smi`和在python中import acl库了。如果是toolkit包，那么也能正常使用atc工具了。

## MindX toolbox （并非必要）

下载MindX DL toolbox 3.0.RC3的`.run`格式的安装包，同样的给它`chmod +x`之后`./软件包地址 --install`即可。

**注意**：安装前**设置umask为027**，否则你会被软件包脚本的读写权限安全检查烦死！

在运行软件包脚本最后给出的set.env.sh时，需先把/var文件设置为744，否则又会出现读写权限检查不过的问题。

弄完之后重新把/var设置为777，否则在正常使用`ascend-dmi`时的某些功能会报错没有/var的权限。

安装完毕。

## Go lang（并非必要）

NPU-exporter工具需要Go作为依赖，因为prometheus是一个用Go写的程序。下面是安装流程。

去go的官方网站下载最**新版本**`1.20.6`。`wget https://go.dev/dl/go1.20.6.linux-arm64.tar.gz`。

**注意**：直接用apt安装会下载一个**较老的版本**，导致NPU-exporter的安装脚本并不能正确运行。

按官网的描述简单安装一下，并加入环境变量即可。坑点只有不能直接apt install。

安装完之后，运行`go env -w GOPROXY=https://goproxy.cn,direct`更换到国内源，否则go会在后面的使用中尝试去`google.golang.org`下载文件，但是这个域名已经被墙了。