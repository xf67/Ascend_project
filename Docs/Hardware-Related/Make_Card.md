# 制卡流程备注

当板卡出现严重问题时，我们可能不得不重新制卡，下面记录了制卡流程，并提供制卡所需的文件在交大云盘的[备份](https://jbox.sjtu.edu.cn/l/L1NOLk)。

注：云盘备份的版本为Ubuntu18.04.4, NPU-driver21.0.4

## 制卡流程

安装依赖

```sh
pip3 install pyyaml
sudo apt-get install qemu-user-static binfmt-support python3-yaml squashfs-tools gcc-aarch64-linux-gnu g++-aarch64-linux-gnu
```

下载云盘中的文件（一共四个，分别为Ubuntu、NPU-driver、make_sd_card.py、make_ubuntu_sd.sh），放于同一个文件夹中。

cd到这个文件夹，运行`sudo python3 make_sd_card.py local /dev/sda`，其中sda是SD的设备名。

注意这里**需要sudo权限**！否则会报错找不到这个设备名之类的。

另注，可以通过修改“make_sd_card.py”中的如下参数配置Atlas 200 DK的USB网卡IP与NIC网卡IP。

- “NETWORK_CARD_DEFAULT_IP”：NIC网卡的IP地址，默认值“192.168.0.2”。
- “USB_CARD_DEFAULT_IP”：USB网卡的IP地址，默认值“192.168.1.2”。

[参考华为文档](https://www.hiascend.com/document/detail/zh/Atlas200DKDeveloperKit/1013/environment/atlased_04_0010.html) 

