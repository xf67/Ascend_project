import torch
import numpy as np
import os
import sys
import onnx
import shutil

def test():
    print("module import OK ")


class Better():
    def __init__(self,net,batch_size,channel,height,width,sync_dir="",ascend_dir="",device="cuda:0"):
        self.net=net
        self.batch_size=batch_size
        self.channel=channel
        self.height=height
        self.width=width
        self.ascend_dir=ascend_dir
        self.sync_dir=sync_dir
        self.atc_dir=""
        self.device=device

    def _get_input_layer_names(self,onnx_model_path):
        input_layer_names = []
        try:
            model = onnx.load(onnx_model_path)
            for input in model.graph.input:
                input_layer_names.append(input.name)
        except Exception as e:
            print(f"Error while loading ONNX model: {e}")
        return input_layer_names

    def _set_env(self):
        if self.ascend_dir == "":
            if 'ASCEND_TOOLKIT_HOME' not in os.environ:
                home_dir=os.environ['HOME']
                self.ascend_dir=os.path.join(home_dir,"Ascend")
            else:
                self.ascend_dir=os.path.dirname(os.path.dirname(os.environ['ASCEND_TOOLKIT_HOME']))
            print(f"No Ascend file path specified, using default path: {self.ascend_dir}")
        self.ascend_dir=os.path.join(self.ascend_dir,"ascend-toolkit/latest")
        if not os.path.exists(self.ascend_dir):
            print("Wrong Ascend Path")
        else:
            os.environ['ASCEND_TOOLKIT_HOME'] = f'{self.ascend_dir}'
            try:
                os.environ['LD_LIBRARY_PATH'] += f'{self.ascend_dir}/x86_64-linux/devlib/:{self.ascend_dir}/lib64:{self.ascend_dir}/lib64/plugin/opskernel:{self.ascend_dir}/lib64/plugin/nnengine'
            except:
                os.environ['LD_LIBRARY_PATH'] = f'{self.ascend_dir}/x86_64-linux/devlib/:{self.ascend_dir}/lib64:{self.ascend_dir}/lib64/plugin/opskernel:{self.ascend_dir}/lib64/plugin/nnengine'
            try:
                os.environ['PYTHONPATH'] += f'{self.ascend_dir}/python/site-packages:{self.ascend_dir}/opp/op_impl/built-in/ai_core/tbe'
            except:
                os.environ['PYTHONPATH'] = f'{self.ascend_dir}/python/site-packages:{self.ascend_dir}/opp/op_impl/built-in/ai_core/tbe'
            os.environ['PATH'] += f'{self.ascend_dir}/bin:{self.ascend_dir}/compiler/ccec_compiler/bin'
            os.environ['ASCEND_AICPU_PATH'] = f'{self.ascend_dir}'
            os.environ['ASCEND_OPP_PATH'] = f'{self.ascend_dir}/opp'
            os.environ['TOOLCHAIN_HOME'] = f'{self.ascend_dir}/toolkit'
            os.environ['ASCEND_HOME_PATH'] = f'{self.ascend_dir}'

    def _gen_demo(self):
        module_dir=os.path.dirname(__file__)
        shutil.copy(f"{module_dir}/check_env.py",f"{self.sync_dir}/sync/check_env.py")
        shutil.copy(f"{module_dir}/demo.py",f"{self.sync_dir}/sync/demo.py")
        with open(f"{self.sync_dir}/sync/demo.py","r+") as file:
            file.write(f"BATCH_SIZE={self.batch_size}\n")
            file.write(f"CHANNEL={self.channel}\n")
            file.write(f"HEIGHT={self.height}\n")
            file.write(f"WIDTH={self.width}\n")
            file.close()
        

    def save(self):
        """
        自动化模型转换与测试
        """
        print("Start working...")
        if self.sync_dir == "":
            current_dir = os.path.abspath(os.curdir)   
            self.sync_dir=current_dir
            print(f"No sync directory specified, using current directory: {self.sync_dir}")
        else:
            os.chdir(self.sync_dir)
            print(f"cd {self.sync_dir}")
        if not os.path.exists("sync"):
            os.makedirs("sync")
            print(f"{self.sync_dir}/sync is created")
        else:
            print(f"{self.sync_dir}/sync exists, files in it may be modified later")
  
        self._set_env()
        self.atc_dir=os.path.join(self.ascend_dir,"bin/atc")
        print("Set environment OK\n")

        self.net.to(torch.device(self.device))
        self.net.eval()
        if self.device =="cpu" :
            input=torch.randn(1,self.channel,self.height,self.width)
        else:
            input=torch.randn(1,self.channel,self.height,self.width).cuda()
        try:
            torch.onnx.export(self.net,input,"./sync/net.onnx",export_params=True,opset_version=12)
        except:
            torch.onnx.export(self.net.module,input,"./sync/net.onnx",export_params=True,opset_version=12)
        input_layer=self._get_input_layer_names("./sync/net.onnx")
        print(f"Generate ONNX OK. The input layer name is: {input_layer}")

        with torch.no_grad():
            inputX=torch.randn(size=(self.batch_size,self.channel,self.height,self.width))
            inputX_n=np.array(inputX).astype(np.float32)
            inputX_n.tofile("./sync/inputX.bin")
            print("Generate input OK")
            if self.device != "cpu" :
                inputX=inputX.cuda()
            outputX=self.net(inputX)
            if self.device != "cpu":
                outputX=outputX.cpu()
            outputX=np.array(outputX).astype(np.float32)
            outputX.tofile("./sync/outputX.bin")
        print("Generate output OK")
        print(" ")

        size_string=""
        for i,names in enumerate(input_layer):
            if i != 0:
                size_string+=";" #多个输入tensor的情况,ATC工具可以支持.但是在目前只考虑了一个tensor输入,一个tensor输出.
                print("Multiple input tensors, work on your own risk")
            size_string+=f"{names}:{self.batch_size},{self.channel},{self.height},{self.width}"
        
        result=os.system(f"{self.atc_dir} --framework=5 --soc_version=Ascend310 --model=./sync/net.onnx --output=sync/net --input_shape={size_string}")
        if result != 0:
            print(f"It seems like somthing WRONG")
            print(f"Check yourself whether you have permissions to fully access {self.sync_dir}")
            print(f"Check your Ascend files at {self.ascend_dir}")
            print(f"Check your onnx modle at {self.sync_dir}/sync/net.onnx")
            exit(1)

        print(f"Generate om OK. The om model is at {self.sync_dir}/sync/net.om")

        self._gen_demo()
        print("All done. Now use \'scp -r\' to move the file \'sync\' to Ascend310 RC, \'cd\' to it, then run \'python demo.py\'. ")
        print("ACL initialization may need \'sudo\' permission, be careful. ")

    if __name__ == '__main__':
        save(0,0)