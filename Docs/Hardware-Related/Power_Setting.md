# 功率档位设定

Atlas200DK可以设置多挡功率模式，具体操作如下。

## 具体操作

```sh
 sudo npu-smi set -t nve-level -i 0 -c 0 -d 2 #功率模式设定为2
 #返回   Status : OK
 #返回   Message : The nve-level of the chip is set successfully. Please reboot system.
 sudo reboot
 #需重启生效
 sudo npu-smi info -t nve-level -i 0 -c 0 #查看
 #返回 nve level : High
 #注 (0: Low: 2W, 1: Middle: 4W, 2: High: 8W, 3: Full: 12.8W)
```

## 备注

用Restnet152(fp16)做了测试，功率和算力之间大致为线性关系。

（**需要补充**：用ascend-dmi工具测不同功率模式下理论算力数值）