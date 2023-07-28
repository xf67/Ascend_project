# Better_ATC 工具

一键式部署pytorch的CNN网络到Atlas200DK。

## 使用之前

### 训练端

python库依赖：pytorch, numpy, onnx

Ascend toolkit：ATC工具。 （可以不是完全安装的toolkit。可直接拷贝[整个文件](https://jbox.sjtu.edu.cn/l/Z1dFfA)） 

一个可以正常输出的pytorch网络

### 推理端

Atlas200DK开发者套件，Ascend310型号NPU。

python库依赖：acl, numpy

acl库来自华为CANN程序包(toolkit或者nnrt均可)

## 注意事项

不支持动态batch_size

不支持多input/output的网络

## 使用方式

### 训练端

将整个文件夹复制到你的项目中，以便python在导入库的时候能找到它。

#### 调用库：

```python
#。。。。。。在前面训练了一个名为net的网络

from better_ATC import Better
a=Better(net,batch_size,channel,height,width,sync_dir="",ascend_dir="",device="cuda:0")
a.save()
```

如果VScode不能正常解析这个库，在VScode的设置`@id:python.analysis.extraPaths ` 中加入库的地址

#### 参数介绍：

net：你的pytorch网络

batch_siz：生成的om模型的batch_size

channel,height,width：CNN的输入张量形状

sync_dir=""：生成的sync文件夹的位置。默认为空，则选择当前文件夹。注意确保对这个文件夹有读写权限。

ascend_dir=""：Ascend文件夹的位置，用于找到ATC工具。默认为空，会查找Ascend的常见安装目录`/usr/local/Ascend`和`$HOME/Ascend`。

device="cuda:0"：你的pytorch网络所在的设备，默认为`cuda:0`，可以改为比如`cpu`、`cuda:1`。

#### 输出实例：

```sh
Start working...
cd /home/xxf/test/AlexNet
/home/xxf/test/AlexNet/sync exists, files in it may be modified later
No Ascend file path specified, using default path: /home/xxf/Ascend
Set environment OK

================ Diagnostic Run torch.onnx.export version 2.0.1 ================
verbose: False, log level: Level.ERROR
======================= 0 NONE 0 NOTE 0 WARNING 0 ERROR ========================

Generate ONNX OK. The input layer name is: ['input.1']
Generate input OK
Generate output OK
 
ATC start working now, please wait for a moment.
ATC run success, welcome to the next use.

Generate om OK. The om model is at /home/xxf/test/AlexNet/sync/net.om
All done. Now use 'scp -r' to move the file 'sync' to Ascend310 RC, 'cd' to it, then run 'python demo.py'. 
ACL initialization may need 'sudo' permission, be careful. 
```

用scp把整个sync文件夹传到推理端

### 推理端

cd进入sync文件夹，直接运行`python demo.py`即可。

#### 输出实例：

```sh
Input (Byte):3211264
Output (Byte):640
Initialization : 1.183734655380249 s
host to device: 0.011240720748901367 s
forward: 0.012872934341430664 s
device to host: 0.0002944469451904297 s
release resources: 0.01649618148803711 s
batch size: 16
Tensor norm by NPU:14.026219367980957
Tensor norm by GPU:14.025784492492676
Delta tensor norm:0.00528715318068862
```

#### 输出介绍：

顾名思义即可。另外，Tensor norm是计算了F2范数。调用了`numpy.linalg.norm(result,"fro")`，可以大致评估网络计算的精度。