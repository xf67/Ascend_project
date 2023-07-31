# 网络配置备注

这里备注了两台设备的**网络配置**。



## IP信息

ARES500AI，OTG连接ip地址192.168.2.22，网关192.168.2.0，子网掩码255.255.255.0；以太网ip地址192.168.1.193。

ARES501AI，OTG连接ip地址192.168.1.2，网关192.168.1.2，子网掩码255.255.255.0；以太网ip地址192.168.1.175。



## 备用（OTG共享网络）

在不得已使用OTG时，以下命令用于临时在笔记本电脑和板卡之间共享网络。

### 笔记本为Ubuntu

测试环境为Ubuntu22.04（虚拟机）

笔记本端运行命令：

```sh
sudo bash
echo "1" > /proc/sys/net/ipv4/ip_forward
iptables -P FORWARD ACCEPT
iptables -A POSTROUTING -t nat -j MASQUERADE -s 192.168.1.0/24
```

其中192.168.1.0/24处改成板卡所在的网段。

板卡端运行命令：

```sh
sudo route add default gw 192.168.1.20 dev usb0
```

其中192.168.1.20是笔记本的IP地址。

### 笔记本为MacOS

测试环境为MacOS10.15.7

笔记本端运行命令：

```sh
sudo sysctl -w net.inet.ip.forwarding=1
sudo echo "nat on en0 from en8:network to any -> (en0)" | sudo pfctl -ef - 
```

其中en8是局域网网卡，en0是连接外网网卡。

不用关心No ALTQ support in kernel报错，不影响使用。

板卡端运行命令：

```sh
sudo route add default gw 192.168.1.20 dev usb0
```

其中192.168.1.20是笔记本的IP地址。

