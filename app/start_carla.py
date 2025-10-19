import subprocess
import os
import time

def launch_carla(carla_path=r"D:\CARLA0.9.15\WindowsNoEditor\CarlaUE4.exe",
                 quality="Low",# Low,Epic
                 benchmark=True,
                 port=2000):
    if not os.path.exists(carla_path):
        print(f"❌ 错误：找不到 Carla 可执行文件路径：{carla_path}")
        return

    # 构造启动参数
    args = [carla_path]
    args.append(f"-quality-level={quality}")
    if benchmark == True:
        args.append("-benchmark")
    args.append(f"-carla-world-port={port}")

    try:
        subprocess.Popen(args)
        print("✅ 成功启动 CarlaUE4.exe")
        time.sleep(5)  # 可选：等待几秒以确保 CARLA 启动完成
    except Exception as e:
        print(f"❌ 启动 Carla 时出错: {e}")

if __name__ == "__main__":
    launch_carla()
