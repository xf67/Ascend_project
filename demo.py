BATCH_SIZE=0
CHANNEL=0
HEIGHT=0
WIDTH=0
####################
import time
try:
    import numpy as np
except:
    print("import numpy failed, try pip/conda install numpy")
try:
    import acl
except:
    print("import acl failed, try run check_env.py in file \'sync\' ")


# error code
ACL_SUCCESS = 0
# rule for memory
ACL_MEM_MALLOC_HUGE_FIRST = 0
ACL_MEM_MALLOC_HUGE_ONLY = 1
ACL_MEM_MALLOC_NORMAL_ONLY = 2
# rule for memory copy
ACL_MEMCPY_HOST_TO_HOST = 0
ACL_MEMCPY_HOST_TO_DEVICE = 1
ACL_MEMCPY_DEVICE_TO_HOST = 2
ACL_MEMCPY_DEVICE_TO_DEVICE = 3

buffer_method = {
    "in": acl.mdl.get_input_size_by_index,#根据aclmdlDesc类型的数据，获取指定输入的大小，单位为Byte。
    "out": acl.mdl.get_output_size_by_index#根据aclmdlDesc类型的数据，获取指定输出的大小，单位为Byte。
    }

def check_ret(message, ret):
    if ret != ACL_SUCCESS:
        raise Exception("{} failed ret={}".format(message, ret))

class Net(object):
    def __init__(self, deviceID, modelPath,batch_size=1):
        self.device_id = deviceID
        self.model_path = modelPath
        self.model_id = None
        self.context = None
        self.input_data = []
        self.output_data = []
        self.model_desc = None
        self.load_input_dataset = None
        self.load_output_dataset = None
        self.result = []
        self.batch_size=batch_size
        try:
            self.init_resource()
        except:
            print("Initialize failed, something wrong with acl or your model")

    def init_resource(self):
        tic=time.time()
        ret = acl.init()#初始化
        check_ret("acl.init", ret)
        ret = acl.rt.set_device(self.device_id)#指定device
        check_ret("acl.rt.set_device", ret)
        self.context, ret = acl.rt.create_context(self.device_id)#显式创建context
        check_ret("acl.rt.create_context", ret)
        self.model_id, ret = acl.mdl.load_from_file(self.model_path)#加载模型,返回模型的指针
        check_ret("acl.mdl.load_from_file", ret)
        self.model_desc = acl.mdl.create_desc()#创建desc数据的指针
        ret = acl.mdl.get_desc(self.model_desc, self.model_id)#获取desc数据,存到model_desc所指的地址
        check_ret("acl.mdl.get_desc", ret)
        input_size = acl.mdl.get_num_inputs(self.model_desc)#输入个数
        #print(f"input_size:{input_size}")
        output_size = acl.mdl.get_num_outputs(self.model_desc)#输出个数
        self._gen_data_buffer(input_size, des="in")
        self._gen_data_buffer(output_size, des="out")
        toc=time.time()
        delta=toc-tic
        print(f"Initialization : {delta} s")

    def _gen_data_buffer(self, size, des):
        func = buffer_method[des]#buffer_method在最前面定义
        for i in range(size):
            # check temp_buffer dtype
            temp_buffer_size = func(self.model_desc, i)  
            temp_buffer, ret = acl.rt.malloc(temp_buffer_size,ACL_MEM_MALLOC_HUGE_FIRST)
            # HUGE_FIRST不是数据大端存储的意思,是优先分配大页内存的意思
            check_ret("acl.rt.malloc", ret)
            if des == "in":
                self.input_data.append({"buffer": temp_buffer,"size": temp_buffer_size})
                print(f"Input (Byte):{temp_buffer_size}")
            elif des == "out":
                self.output_data.append({"buffer": temp_buffer,"size": temp_buffer_size})
                print(f"Output (Byte):{temp_buffer_size}")

    def run(self, images):
        self._data_from_host_to_device(images)
        self.forward()
        self._destroy_databuffer()
        self._data_from_device_to_host()

    def _data_from_host_to_device(self, images):
        tic=time.time()
        # copy images to device
        self._data_interaction(images, ACL_MEMCPY_HOST_TO_DEVICE)
        #print("data_interaction h_to_d OK")
        # load input data into model
        self._gen_dataset("in")
        # load output data into model
        self._gen_dataset("out")
        toc=time.time()
        delta=toc-tic
        print(f"host to device: {delta} s")

    def _gen_dataset(self, type_str):
        dataset = acl.mdl.create_dataset()
        temp_dataset = None
        if type_str == "in":
            self.load_input_dataset = dataset
            temp_dataset = self.input_data
        elif type_str == "out":
            self.load_output_dataset = dataset
            temp_dataset = self.output_data
        for item in temp_dataset:
            data = acl.create_data_buffer(item["buffer"], item["size"])
            _, ret = acl.mdl.add_dataset_buffer(dataset, data)
            if ret != ACL_SUCCESS:
                ret = acl.destroy_data_buffer(data)
                check_ret("acl.destroy_data_buffer", ret)

    def forward(self):
        tic=time.time()
        ret = acl.mdl.execute(self.model_id,
                              self.load_input_dataset,
                              self.load_output_dataset)
        check_ret("acl.mdl.execute", ret)
        toc=time.time()
        delta=toc-tic
        print(f"forward: {delta} s")

    def _data_from_device_to_host(self):
        tic=time.time()
        res = []
        # copy device to host
        self._data_interaction(res, ACL_MEMCPY_DEVICE_TO_HOST)
        #print(f"res:{res}")
        dims, ret = acl.mdl.get_cur_output_dims(self.model_desc, 0)
        #print(f"dims:{dims}")
        check_ret("acl.mdl.get_cur_output_dims", ret)
        out_dim = dims['dims']
        for temp in res:
            ptr = temp["buffer"]
            #float32类型的数据
            bytes_data = acl.util.ptr_to_bytes(ptr, temp["size"])
            data = np.frombuffer(bytes_data, dtype=np.float32).reshape(out_dim)
            self.result.append(data)
        #free host memory
        for item in res:
            ptr = item['buffer']
            ret = acl.rt.free_host(ptr)
            check_ret('acl.rt.free_host', ret)
        toc=time.time()
        delta=toc-tic
        print(f"device to host: {delta} s")

    def _destroy_databuffer(self):
        for dataset in [self.load_input_dataset, self.load_output_dataset]:
            if not dataset:
                continue
            number = acl.mdl.get_dataset_num_buffers(dataset)
            for i in range(number):
                data_buf = acl.mdl.get_dataset_buffer(dataset, i)
                if data_buf:
                    ret = acl.destroy_data_buffer(data_buf)
                    check_ret("acl.destroy_data_buffer", ret)
            ret = acl.mdl.destroy_dataset(dataset)
            check_ret("acl.mdl.destroy_dataset", ret)

    def _data_interaction(self, dataset, policy):
        temp_data_buffer = self.input_data \
            if policy == ACL_MEMCPY_HOST_TO_DEVICE \
            else self.output_data
        if len(dataset) == 0 and policy == ACL_MEMCPY_DEVICE_TO_HOST:
            for item in self.output_data:
                temp, ret = acl.rt.malloc_host(item["size"])
                if ret != 0:
                    raise Exception("can't malloc_host ret={}".format(ret))
                dataset.append({"size": item["size"], "buffer": temp})
        #print(temp_data_buffer)
        #print(sys.getsizeof(dataset))
        for i, item in enumerate(temp_data_buffer):
            if policy == ACL_MEMCPY_HOST_TO_DEVICE:
                bytes_data = dataset[i].tobytes()
                #bytes_data = dataset[i].tobytes()
                ptr = acl.util.bytes_to_ptr(bytes_data)
                ret = acl.rt.memcpy(item["buffer"],
                                    item["size"],
                                    ptr,
                                    item["size"],
                                    policy)
                #item['buffer']是目标地址,ptr是源地址,host_to_device
                check_ret("acl.rt.memcpy", ret)
            else:
                ptr = dataset[i]["buffer"]
                ret = acl.rt.memcpy(ptr,
                                    item["size"],
                                    item["buffer"],
                                    item["size"],
                                    policy)
                check_ret("acl.rt.memcpy", ret)
                #device_to_host

    def release_resource(self):
        tic=time.time()
        ret = acl.mdl.unload(self.model_id)
        check_ret("acl.mdl.unload", ret)
        if self.model_desc:
            acl.mdl.destroy_desc(self.model_desc)
            self.model_desc = None
        while self.input_data:
            item = self.input_data.pop()
            ret = acl.rt.free(item["buffer"])
            check_ret("acl.rt.free", ret)
        while self.output_data:
            item = self.output_data.pop()
            ret = acl.rt.free(item["buffer"])
            check_ret("acl.rt.free", ret)
        if self.context:
            ret = acl.rt.destroy_context(self.context)
            check_ret("acl.rt.destroy_context", ret)
            self.context = None
        ret = acl.rt.reset_device(self.device_id)
        check_ret("acl.rt.reset_device", ret)
        ret = acl.finalize()
        check_ret("acl.finalize", ret)
        toc=time.time()
        delta=toc-tic
        print(f"release resources: {delta} s")      

    def print_result(self):
        print(self.result) 

    def get_result(self):
        return self.result         

if __name__ == '__main__':
    inputX=np.fromfile("./inputX.bin", dtype=np.float32, count=-1).reshape(BATCH_SIZE,CHANNEL,HEIGHT,WIDTH) 
    inputX=inputX.astype(np.float32)
    #inputX=inputX.flatten()
    #print(inputX)
    inputS=[]
    inputS.append(inputX)
    modelPath="./net.om"
    deviceID=0
    net=Net(deviceID,modelPath)
    net.run(inputS)
    #print("Results:")
    #net.print_result()
    result=net.get_result()
    result=np.array(result).reshape(BATCH_SIZE,-1)
    net.release_resource()
    #print("Results by GPU:")
    outputX=np.fromfile("./outputX.bin", dtype=np.float32, count=-1).reshape(BATCH_SIZE,-1).astype(np.float32)
    #print(outputX)
    delta=np.subtract(result,outputX)
    F2A=np.linalg.norm(result,"fro")
    F2B=np.linalg.norm(outputX,"fro")
    F2D=np.linalg.norm(delta,"fro")
    print(f"batch size: {BATCH_SIZE}")
    print(f"Tensor norm by NPU:{F2A}\nTensor norm by GPU:{F2B}\nDelta tensor norm:{F2D}")
    