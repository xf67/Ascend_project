# 挂载SSD备注

注意，Atlas200DK只能挂载**M.2接口**的**SATA协议**的硬盘。

ARES500AI的硬盘是全长的，ARES501AI的硬盘是半长的。（**需要补充**：具体规格为2242，2260，2280中之何）

## 格式化和挂载

需要sudo权限

```sh
fdisk -l	#查看到磁盘是/dev/sda。
fdisk /dev/sda	#进入磁盘，p是查看，n是新建，w是保存，q是退出。格式化挂载盘
mkfs -t ext4 /dev/sda1	#格式化分区
cd /mnt
mkdir tmp
mount /dev/sda1 /mnt/tmp	#临时挂载在/mnt/tmp目录下
df -lh	#能查看到磁盘
cp -a /home/ /mnt/tmp	#复制原home内容
```

## 设置自动挂载

使用修改fstab的方式会导致系统无法正常启动，这很奇怪，但是可能是由于板卡在启动初始化时执行了一些操作对硬盘的挂载存在影响。

解决方案：

在/mnt文件夹新建一个ssd.sh，里面只需要一句话`sudo mount /dev/sda1 /home`

在`/etc/rc.local`的厂商预置的指令**之后**，加一句`sh /mnt/ssd.sh` 

即可实现在开机之后自动挂载SSD。

## 增加内存交换空间

以防止爆内存。板卡只有8G内存在执行一些编译之类的任务时会出问题。

```sh
sudo mkdir swap	#在home(SSD)目录下新建一个swap文件夹里面用来存swap.img
cd swap
sudo fallocate -l 16G ./swap.img
sudo chmod 600 swap.img
sudo mkswap swap.img
sudo swapon swap.img
free -h
#              total        used        free      shared  buff/cache   available
#Mem:           7.6G        2.2G        5.3G        476K         92M        5.3G
#Swap:           15G          0B         15G
#内存交换已经加上了
```

下面设置自动挂载内存交换，同样的，修改fstab的方式并不可行。

提前在/home/swap创建内存交换文件。

在/mnt文件夹里新建一个memory.sh，写入：

```sh
if [ -d "/home/swap/" ]; then
        cd /home/swap
        sudo chmod 600 swap.img > /dev/null 2>&1
        sudo mkswap swap.img > /dev/null 2>&1
        sudo swapon swap.img > /dev/null 2>&1
else
        echo "/home未正确挂载,请重新运行sh /mnt/memory.sh"
fi
```

然后在`/etc/rc.local`的厂商预置的指令**之后**，加一句`sh /mnt/memory.sh` 

即可实现开机自动打开内存交换。 