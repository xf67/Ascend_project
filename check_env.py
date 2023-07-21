import sys
import subprocess
import importlib
import os

def get_python_version():
    python_version = sys.version_info
    print(f"Python Version: {python_version.major}.{python_version.minor}.{python_version.micro}")
    if python_version.major != 3:
        print("You are running python2. Check your symbolic links.")
    else:
        if python_version.minor == 7 :
            if python_version.micro > 11:
                print("We suggest python 3.7.x(3.7.0~3.7.11)")
            else:
                print("Python verison OK")
        elif python_version.minor == 9 :
            if python_version.micro > 11:
                print("We suggest python 3.8.x(3.8.0~3.8.11)")
            else:
                print("Python verison OK")
        elif python_version.minor == 9 :
            if python_version.micro > 7:
                print("We suggest python 3.9.x(3.9.0~3.9.7)")
            else:
                print("Python verison OK")
        else:
            print("We suggest python 3.7~3.9")

def compare_version(v_split,v_ok_split):
    for v1, v2 in zip(v_split, v_ok_split):
        if int(v1) < int(v2):
            return -1
        elif int(v1) > int(v2):
            return 1
    return 0

def check_package_v(package_name,version):
    try:
        output = subprocess.check_output([f"{package_name}", "--version"]).decode()
        pkg_version = output.split("\n")[0]
        p_v = pkg_version.strip().split()[-1]
        v_split = p_v.split('.')
        v_ok_split = version.split('.')
        v_split += [0] * (3 - len(v_split))
        v_ok_split += [0] * (3 - len(v_ok_split))
        res = compare_version(v_split,v_ok_split)
        if res == -1:
            print(f"{package_name} version: {p_v}. But we need {version}")
        else:
            print(f"{package_name} OK")     
    except:
        print(f"{package_name} is not installed.")
        return False
    return True

def check_package(package_name):
    try:
        subprocess.check_call(['dpkg', '-s', package_name],stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        print(f"{package_name} OK")
    except:
        print(f"{package_name} is not installed.")
        return False
    return True

def check_pip_package(package_name):
    try:
        module = importlib.import_module(package_name)
        print(f"{package_name} OK")
    except:
        print(f"{package_name} is not installed.")
        return False
    return True

def check_pip_package_v(package_name,version):
    try:
        module = importlib.import_module(package_name)
        module_version = module.__version__
        v_split=module_version.split('.')
        v_ok_split=version.split('.')
        v_split += [0] * (3 - len(v_split))
        v_ok_split += [0] * (3 - len(v_ok_split))
        res=compare_version(v_split,v_ok_split)
        if res == -1:
            print(f"{package_name} version: {module_version}. But we need {version}")
        else:
            print(f"{package_name} OK")     
    except:
        print(f"{package_name} is not installed.")
        return False
    return True

def check_path():
    if 'ASCEND_TOOLKIT_HOME' not in os.environ:
        print("Ascend toolkit path is not set. You can find set_env.sh and run for yourself.")
    elif 'LD_LIBRARY_PATH' not in os.environ:
        print("LD_LIBRARY_PATH is not set. You can find set_env.sh and run for yourself.")
    else:
        sp1_path=os.path.join(os.environ['ASCEND_TOOLKIT_HOME'],'x86_64-linux/devlib/')
        sp2_path=os.path.join(os.environ['ASCEND_TOOLKIT_HOME'],'aarch64-linux/devlib/')
        if sp1_path not in os.environ['LD_LIBRARY_PATH'] and sp2_path not in os.environ['LD_LIBRARY_PATH']:
            print("Try run \' export LD_LIBRARY_PATH=${ASCEND_TOOLKIT_HOME}/x86_64-linux/devlib/:$LD_LIBRARY_PATH \'\n\
            or \' export LD_LIBRARY_PATH=${ASCEND_TOOLKIT_HOME}/aarch64-linux/devlib/:$LD_LIBRARY_PATH \'")
            print("This path is not always needed, but may solve some problem.")
        else:
            print("System Path OK")

if __name__ == "__main__":

    print("*** Check Environment for CANN ***")

    get_python_version()

    required_packages_v = {
        'cmake':'3.5.1', 'gcc':'7.5.0', 'g++':'7.5.0'
    }
    missing_packages_v = {}
    for package, verison in required_packages_v.items():
        if not check_package_v(package, verison):
            missing_packages_v.update({package: verison})

    required_packages = [
        'make', 'zlib1g', 'zlib1g-dev', 'libsqlite3-dev',
        'openssl', 'libssl-dev', 'libffi-dev', 'unzip', 'pciutils', 'net-tools',
        'libblas-dev', 'gfortran', 'libblas3', 'liblapack-dev', 'liblapack3',
    ]
    missing_packages = []
    for package in required_packages:
        if not check_package(package):
            missing_packages.append(package)

    required_pip_v = {
        'numpy':"1.14.3", "decorator":"4.4.0", "sympy":"1.4", "cffi":"1.12.3", "protobuf":"3.11.3"
    }
    missing_pip_v = {}
    for package, verison in required_pip_v.items():
        if not check_pip_package_v(package, verison):
            missing_pip_v.update({package: verison})

    required_pip = [
        'attrs', 'yaml', 'pathlib', 'scipy', 'requests', 'psutil', 'absl'
    ]
    missing_pip = []
    for package in required_pip:
        if not check_pip_package(package):
            missing_pip.append(package)

    print("*** Check Environment Requirments Done ***")

    print("*** Check System Path ***")
    check_path()
    print("use \'id\' to check for yourself whether you are in group(HwHiAiUser)")
    print("*** Check System Path Done ***")

    