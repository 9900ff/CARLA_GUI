import sys
import os
project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, project_root)
import subprocess
import math
import time
import random
import configparser
from PyQt5.QtWidgets import QApplication, QMainWindow, QFileDialog
from PyQt5.QtCore import QTimer
from PyQt5.QtCore import QThread
import carla
from QT_CARLA.CARLA_tools import Ui_MainWindow

def load_config():
    """
    读取配置文件并返回配置对象。
    会先在当前目录搜索 config.ini，如果找不到，则去上级目录搜索。
    """
    # 1. 定义要搜索的目录
    current_dir = os.path.dirname(os.path.abspath(__file__))
    parent_dir = os.path.dirname(current_dir)

    # 2. 创建一个按优先级排序的搜索路径列表
    search_paths = [
        os.path.join(current_dir, 'config.ini'),
        os.path.join(parent_dir, 'config.ini')
    ]

    config = configparser.ConfigParser()

    # 3. 遍历列表，查找并读取第一个找到的配置文件
    for config_path in search_paths:
        # 使用 os.path.exists() 来检查文件是否存在
        if os.path.exists(config_path):
            print(f"成功找到并加载配置文件: {config_path}")
            config.read(config_path, encoding='utf-8')
            # 找到后立即返回，停止继续搜索
            return config

    # 4. 如果循环结束后仍然没有找到文件，则抛出异常
    raise FileNotFoundError(f"在指定的目录中都找不到 'config.ini' 文件。搜索路径: {search_paths}")


class MyMainWindow(QMainWindow):
    def __init__(self,carla_path='D:\CARLA0.9.15\WindowsNoEditor\CarlaUE4.exe'):
        # 初始化
        super().__init__()
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)
        # 设置CARLA对象
        self.carla_path = carla_path # 默认路径，可以修改
        print("初始化carla_path:", self.carla_path)
        self.ip = None
        self.port = None
        self.client = None
        self.world = None
        self.map = None
        self.car = None
        self.follower_thread = None
        self.speed_thread = None
        # 初始化qt界面部分内容
        self.ui.textBrowser_chooseCARLA.setText(self.carla_path)

        # 设置一个 QTimer，每2秒检查一次连接状态
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.refresh_world_data)
        self.timer.timeout.connect(self.refresh_ifcarconnect_data)
        self.timer.start(2000)  # 每2000毫秒（2秒）触发一次
        # 按钮点击事件连接
        self.ui.pushButton_chooseCARLA.clicked.connect(self.choose_carla_path) # 选择carla路径
        self.ui.pushButton_startCARLA.clicked.connect(self.start_carla_clicked) # 启动carla
        self.ui.pushButton_closeCARLA.clicked.connect(self.close_carla_clicked)  # 关闭carla
        self.ui.pushButton_connectCARLA.clicked.connect(self.connect_carla_clicked)  # 连接carla
        self.ui.pushButton_chooseMap.clicked.connect(self.change_map) # 切换地图
        self.ui.pushButton_setAsyn.clicked.connect(self.set_Asyn_mode)  # 设置同步模式
        self.ui.pushButton_clearAllActor.clicked.connect(self.delete_all_actor)  # 清除所有actor
        self.ui.pushButton_spawnCar.clicked.connect(self.spawn_car)  # 生成车辆
        self.ui.pushButton_spawnCarPygame.clicked.connect(self.spawn_car_pygame)  # 在pygame画面生成车辆
        self.ui.pushButton_refreshCars.clicked.connect(lambda: self.refresh_car_data(refresh_Rolename=True)) # 更新车辆列表
        self.ui.pushButton_connectCar.clicked.connect(self.connect_car)  # 连接车辆
        self.ui.pushButton_setCarPose.clicked.connect(self.set_car_pose)  # 设置车辆位置
        self.ui.pushButton_clearActor_roleneme.clicked.connect(self.delete_actor_by_id)  # 删除车辆
        self.ui.pushButton_setSpectatorPose_tocar.clicked.connect(self.set_spectator_to_car)  # 设置观测者到车辆
        self.ui.pushButton_setSpectatorPose.clicked.connect(self.set_spectator)  # 设置观测者到指定坐标

        self.ui.pushButton_SpectatorFollower_pro.clicked.connect(self.spectator_follow_pro)  # 设置观测者跟随车辆 pro
        self.ui.pushButton_SpectatorFollower_easy.clicked.connect(self.spectator_follow_easy)  # 设置观测者跟随车辆 easy
        self.ui.pushButton_StopSpectatorFollower.clicked.connect(self.stop_spectator_follow)  # 停止观测者跟随车辆
        self.ui.pushButton_chooseWeather.clicked.connect(self.choose_weather)  # 设置天气

        self.ui.pushButton_render.clicked.connect(self.open_render) # 启用画面渲染
        self.ui.pushButton_norender.clicked.connect(self.close_render) # 禁用画面渲染
        self.ui.pushButton_HUD2d.clicked.connect(self.open_HUD2d) # 启用2D画面渲染

        self.ui.pushButton_showSpeed.clicked.connect(self.show_vehicle_speed) # 启用速度显示
        self.ui.pushButton_hideSpeed.clicked.connect(self.close_vehicle_speed)   # 禁用速度显示

    def choose_carla_path(self):
        file_path, _ = QFileDialog.getOpenFileName(self, "选择 CARLA 启动程序", "", "可执行文件 (*.exe);;所有文件 (*)")
        if file_path:
            print(f"选择的CARLA路径是: {file_path}")
            # 显示在界面上
            self.ui.textBrowser_chooseCARLA.setText(file_path)
            # 保存为成员变量
            self.carla_path = file_path

    def start_carla_clicked(self):
        carla_path = self.carla_path
        quality = self.ui.comboBox_quality.currentText()
        benchmark=True
        port=self.ui.lineEdit_port.text()
        renderingmode=self.ui.rendering_mode.currentText()

        print('启动carla中，当前参数如下:')
        print('carla_path:', carla_path)
        print('quality:', quality)
        print('port:', port)
        print('渲染模式:', renderingmode)

        # 构造启动参数
        args = [carla_path]
        args.append(f"-quality-level={quality}")
        if benchmark == True:
            args.append("-benchmark")
        args.append(f"-carla-world-port={port}")

        # 渲染模式
        if renderingmode == "离屏渲染":
            args.append("-RenderOffScreen")

        try:
            subprocess.Popen(args)
            print("✅ 成功启动 CarlaUE4.exe")
        except Exception as e:
            print(f"❌ 启动 Carla 时出错: {e}")

    def close_carla_clicked(self):
        try:
            self.set_Asyn_mode() # 异步模式
            self.delete_all_actor() # 先清楚全部actor
            # 关闭 Carla 进程（Windows 使用 taskkill）
            os.system("taskkill /F /IM CarlaUE4.exe >nul 2>nul")
            os.system("taskkill /F /IM CarlaUE4-Win64-Shipping.exe >nul 2>nul")
            print("✅ 已尝试关闭 Carla")
        except Exception as e:
            print(f"❌ 关闭失败: {e}")
        finally:
            print("正在重置应用程序状态...")
            # 1. 停止任何活动的线程
            if self.follower_thread and self.follower_thread.isRunning():
                self.stop_spectator_follow()
            if self.speed_thread and self.speed_thread.isRunning():
                self.hide_vehicle_speed()
            # 2. 清空核心CARLA对象引用
            self.client = None
            self.world = None
            self.map = None
            self.car = None
            self.follower_thread = None
            # 3. 重置UI界面显示
            self.ui.textBrowser_connectState.setText("未连接")
            self.ui.textBrowser_carState.setText("无")
            self.ui.comboBox_carRolename.clear()
            print("✅ 状态重置完成。")

    def connect_carla_clicked(self):
        try:
            print("尝试连接到CARLA世界")
            time.sleep(1)
            ip=self.ui.lineEdit_IP.text()
            port=int(self.ui.lineEdit_port.text())
            print('当前IP:', ip, ':', port)
            self.client = carla.Client(ip, port)  # 默认本地连接
            self.client.set_timeout(10.0)
            self.world = self.client.get_world()
            print("成功连接到CARLA世界")

            self.client.set_timeout(5.0)
        except Exception as e:
            raise ConnectionError(f"CARLA连接失败: {str(e)}")

    def refresh_world_data(self):
        try:
            # 判断连接状态下
            server_version = self.client.get_server_version()
            # ip，port，当前地图
            ip_info = self.ui.lineEdit_IP.text()
            port_info = int(self.ui.lineEdit_port.text())

            # 同步异步信息
            mode_info = "异步模式"
            if self.world.get_settings().synchronous_mode == True:
                mode_info= '同步模式'

            # 获取观测者信息
            spectator_info = "无数据"
            spectator = self.world.get_spectator()
            transform = spectator.get_transform()  # 获取 Transform 对象
            location = transform.location  # 位置
            rotation = transform.rotation  # 朝向
            spectator_info = f"{location.x:.2f}  {location.y:.2f}\n{location.z:.2f}  {rotation.yaw:.2f}"

            info_lines = [
                f"已连接上CARLA v{server_version}",'\n'
                f"ip = {ip_info}:{port_info}",
                f"当前模式 = {mode_info}",'\n'
                f"观测者坐标：\n{spectator_info}", '\n'
            ]
            all_info = "\n".join(info_lines)

            self.ui.textBrowser_connectState.setText(all_info)

            # 同时刷新车辆状态表
            self.refresh_car_data()
        except RuntimeError:
            self.ui.textBrowser_connectState.setText("未连接")
            self.ip = None
            self.port = None
            self.client = None
            self.world = None
            self.map = None
            self.car = None
        except Exception as e:
            self.ui.textBrowser_connectState.setText("未连接")
            self.ip = None
            self.port = None
            self.client = None
            self.world = None
            self.map = None
            self.car = None

    def change_map(self):
        if self.client is None:
            self.ui.textBrowser_connectState.setText("未连接，无法切换地图")
            return

        selected_map = self.ui.comboBox_map.currentText()
        try:
            self.world = self.client.load_world(selected_map)
            self.map = self.world.get_map()
            self.ui.textBrowser_connectState.setText(f"✅ 地图切换至 {selected_map}")
            print(f"[INFO] 地图成功切换为 {selected_map}")
        except Exception as e:
            self.ui.textBrowser_connectState.setText("❌ 地图切换失败")
            print(f"[ERROR] 地图切换失败: {e}")

    def set_Asyn_mode(self):
        settings = self.world.get_settings()
        settings.synchronous_mode = False
        settings.fixed_delta_seconds = False
        self.world.apply_settings(settings)
        print('开启异步模式')

    def delete_all_actor(self):
        actors = self.world.get_actors()
        for actor in actors:
            try:
                # 不清除 spectator 或 ego vehicle（可选）
                if actor.type_id != 'spectator':
                    actor.destroy()
                    print(f'已清除 actor: {actor.id} - {actor.type_id}')
            except Exception as e:
                print(f'无法清除 actor: {actor.id}, 原因: {e}')

    def spawn_car(self):
        blueprint_library = self.world.get_blueprint_library()
        car_bp = blueprint_library.find('vehicle.tesla.model3')
        # 设置车辆的 role_name
        role_name = self.ui.lineEdit_spawnname.text()
        car_bp.set_attribute('role_name', role_name)
        # 定义生成位置和旋转
        x = float(self.ui.lineEdit_spawnX.text())
        y = float(self.ui.lineEdit_spawnY.text())
        z = float(self.ui.lineEdit_spawnZ.text())
        yaw = float(self.ui.lineEdit_spawnYaw.text())
        spawn_point = carla.Transform(
            carla.Location(x=x, y=y, z=z),  # z=0.3 避免车辆陷入地面
            carla.Rotation(yaw=yaw)
        )
        # 生成车辆
        try:
            vehicle = self.world.spawn_actor(car_bp, spawn_point)
            print(f"生成成功！车辆 ID: {vehicle.id}, role_name: {vehicle.attributes['role_name']}")
            return vehicle
        except Exception as e:
            print(f"生成失败: {e}")
            return None

    def spawn_car_pygame(self):
        # 获取坐标信息
        try:
            x = float(self.ui.lineEdit_spawnX.text())
            y = float(self.ui.lineEdit_spawnY.text())
            z = float(self.ui.lineEdit_spawnZ.text())
            yaw = float(self.ui.lineEdit_spawnYaw.text())
        except ValueError:
            print("⚠️ 输入的坐标或角度不是有效数字")
            return
        # 获取角色名
        role_name = self.ui.lineEdit_spawnname.text()
        if not role_name:
            role_name = "ego"
        # 获取地图名字
        current_map = self.world.get_map().name

        # 构造命令
        spawn_point = f"{x}, {y}, {z}, {yaw}"
        command = [
            "python", "spawn_car_with_GUI.py",
            "--spawn_point", spawn_point,
            "--rolename", role_name,
            "--map", current_map,
            "--host",self.ui.lineEdit_IP.text(),
            "--port",self.ui.lineEdit_port.text()
        ]

        try:
            subprocess.Popen(command)
            print(f"🚗 已运行: {' '.join(command)}")
        except Exception as e:
            print(f"❌ 启动失败: {e}")

    def refresh_ifcarconnect_data(self):
        # 连接成功时的样式：蓝色背景，加粗字体
        connected_style = """
            font-weight: bold; 
            color: #0078d7; 
            padding: 5px; 
            border: 1px solid #a0c8e8; 
            border-radius: 4px; 
            background-color: #e7f3fe;
        """
        # 未连接时的样式：灰色背景，普通字体
        disconnected_style = """
            font-weight: normal; 
            color: #555; 
            padding: 5px; 
            border: 1px solid #ddd; 
            border-radius: 4px; 
            background-color: #f0f0f0;
        """

        self.ui.label_current_car_info.setText("当前未连接车辆")
        self.ui.label_current_car_info.setStyleSheet(disconnected_style)
        if self.car is not None:
            try:
                # 获取当前世界中所有actor的id
                current_actor_ids = [actor.id for actor in self.world.get_actors()]
                if self.car.id not in current_actor_ids:
                    self.car = None
                else:
                    rolename = self.car.attributes.get('role_name', 'N/A')
                    actor_id = self.car.id
                    car_info=(f"{rolename}  id={actor_id}")
                    self.ui.label_current_car_info.setText(f"当前控制车辆: {car_info}")
                    self.ui.label_current_car_info.setStyleSheet(connected_style)
            except Exception as e:
                self.car = None

    def refresh_car_data(self,refresh_Rolename = False):
        world = self.world
        if world is None:
            print("[错误] CARLA World 尚未初始化，无法刷新车辆列表。")
            return
        actors = world.get_actors().filter('vehicle.*')
        # 设置车辆选择界面
        if refresh_Rolename:
            self.ui.comboBox_carRolename.clear()
            for actor in actors:
                rolename = actor.attributes.get('role_name', 'N/A')
                actor_id = actor.id
                display_text = f"{rolename} id={actor_id}"
                self.ui.comboBox_carRolename.addItem(display_text,actor_id)
        # 更新actor信息

        # 已连接到的车辆信息
        car_info = "无"
        if self.car is not None:
            try:
                # 获取当前世界中所有actor的id
                current_actor_ids = [actor.id for actor in self.world.get_actors()]
                if self.car.id not in current_actor_ids:
                    self.car = None
                else:
                    rolename = self.car.attributes.get('role_name', 'N/A')
                    actor_id = self.car.id
                    car_info=(f"{rolename}  id={actor_id}")
            except Exception as e:
                self.car = None

        # 所有actor信息
        actor_data = []
        actors = self.world.get_actors().filter('vehicle.*')
        for actor in actors:
            rolename = actor.attributes.get('role_name', 'N/A')
            actor_id = actor.id
            actor_data.append(f"{rolename}  id={actor_id}")
        all_actor_info = "\n".join(actor_data)

        # 最终显示内容
        info_lines = [
            all_actor_info
        ]
        all_info = "\n".join(info_lines)

        self.ui.textBrowser_carState.setText(all_info)

    def connect_car(self):
        try:
            # 从 ComboBox 获取用户选中的车辆 ID
            selected_index = self.ui.comboBox_carRolename.currentIndex()
            selected_id = self.ui.comboBox_carRolename.itemData(selected_index)  # 这是你之前 addItem 的第二个参数

            if selected_id is None:
                print("❌ 未选择车辆或车辆 ID 无效")
                self.car = None
                return

            # 获取当前车辆列表
            actor_list = list(self.world.get_actors())
            selected_car = None
            for actor in actor_list:
                if actor.id == selected_id and 'vehicle.' in actor.type_id:
                    selected_car = actor
                    print(f"✅ 成功连接车辆: role_name={actor.attributes.get('role_name', '')}, id={actor.id}")
                    break
            if selected_car:
                self.car = selected_car  # 存储为成员变量
            else:
                print(f"❌ 没有找到 ID 为 {selected_id} 的车辆")
                self.car = None

        except Exception as e:
            print(f"❌ 连接车辆失败: {e}")
            self.car = None

    def set_car_pose(self):
        try:
            # 获取车辆对象
            vehicle = self.car
            # 获取位置和朝向输入
            x = float(self.ui.lineEdit_moveX.text())
            y = float(self.ui.lineEdit_moveY.text())
            z = float(self.ui.lineEdit_moveZ.text())
            yaw = float(self.ui.lineEdit_moveYaw.text())
            # 设置新的 Transform
            from carla import Transform, Location, Rotation
            new_transform = Transform(Location(x=x, y=y, z=z), Rotation(yaw=yaw))
            vehicle.set_transform(new_transform)
            print(f"✅ 已将车辆移动到 ({x}, {y}, {z})，Yaw={yaw}")

        except Exception as e:
            print(f"❌ 设置车辆位置失败: {e}")

    def delete_actor_by_id(self):
        try:
            if self.car is not None:
                self.car.destroy()
                print(f"✅ 成功销毁车辆 id={self.car.id}")
                self.car = None  # 防止再次访问已销毁对象
            else:
                print("⚠️ 当前没有车辆对象可销毁")
        except Exception as e:
            print(f"❌ 销毁车辆失败: {e}")

    def set_spectator_to_car(self):
        try:
            if self.car is None:
                print("⚠️ 当前没有车辆")
                return

            # 获取车辆的变换（位置 + 朝向）
            transform = self.car.get_transform()
            location = transform.location
            rotation = transform.rotation

            # 设置观察者稍微在车辆后方和上方的位置
            spectator = self.world.get_spectator()
            spectator_location = location + carla.Location(x=-6 * math.cos(math.radians(rotation.yaw)),
                                                           y=-6 * math.sin(math.radians(rotation.yaw)),
                                                           z=3)
            spectator_rotation = carla.Rotation(pitch=-15, yaw=rotation.yaw, roll=0)
            spectator_transform = carla.Transform(spectator_location, spectator_rotation)

            spectator.set_transform(spectator_transform)
            print("✅ 观察者位置已更新")
        except Exception as e:
            print(f"❌ 设置观察者失败: {e}")

    def set_spectator(self):
        try:
            # 获取变换（位置 + 朝向）
            x = float(self.ui.lineEdit_spectatorX.text())
            y = float(self.ui.lineEdit_spectatorY.text())
            z = float(self.ui.lineEdit_spectatorZ.text())
            yaw = float(self.ui.lineEdit_spectatorYaw.text())
            move_pose = carla.Transform(
                carla.Location(x=x, y=y, z=z),  # z=0.3 避免车辆陷入地面
                carla.Rotation(yaw=yaw)
            )
            spectator = self.world.get_spectator()
            spectator.set_transform(move_pose)
            print("✅ 观察者位置已更新")
        except Exception as e:
            print(f"❌ 设置观察者失败: {e}")

    def spectator_follow_easy(self):
        # 如果之前有线程在运行，先停止它
        if self.follower_thread is not None:
            self.follower_thread.stop()
            self.follower_thread.wait()  # 等待线程安全退出
            self.follower_thread = None
        self.follower_thread = SpectatorFollowerThread_easy(self.world, self.car)
        self.follower_thread.start()

    def spectator_follow_pro(self):
        # 如果之前有线程在运行，先停止它
        if self.follower_thread is not None:
            self.follower_thread.stop()
            self.follower_thread.wait()  # 等待线程安全退出
            self.follower_thread = None
        self.follower_thread = SpectatorFollowerThread_pro(self.world, self.car)
        self.follower_thread.start()

    def stop_spectator_follow(self):
        if hasattr(self, 'follower_thread'):
            self.follower_thread.stop()
            self.follower_thread.wait()  # 等待线程安全退出

    def choose_weather(self):
        world = self.world
        weather_type = self.ui.comboBox_weather.currentText()
        # 字符串 → WeatherParameters 对象映射
        weather_dict = {
            "晴朗 正午": carla.WeatherParameters.ClearNoon,
            "多云 正午": carla.WeatherParameters.CloudyNoon,
            "湿润 正午": carla.WeatherParameters.WetNoon,
            "湿润多云 正午": carla.WeatherParameters.WetCloudyNoon,
            "小雨 正午": carla.WeatherParameters.SoftRainNoon,
            "中雨 正午": carla.WeatherParameters.MidRainyNoon,
            "大雨 正午": carla.WeatherParameters.HardRainNoon,
            "晴朗 日出": carla.WeatherParameters.ClearSunset,
            "多云 日出": carla.WeatherParameters.CloudySunset,
            "湿润 日出": carla.WeatherParameters.WetSunset,
            "小雨 日出": carla.WeatherParameters.SoftRainSunset,
            "中雨 日出": carla.WeatherParameters.MidRainSunset,
            "大雨 日出": carla.WeatherParameters.HardRainSunset
        }
        # 设置天气
        if weather_type in weather_dict:
            world.set_weather(weather_dict[weather_type])
            print(f"[Info] 已设置天气为: {weather_type}")
        else:
            print(f"[Error] 无效天气类型: {weather_type}")

    def open_render(self):
        """
        开启CARLA的渲染显示窗口。
        """
        print("尝试开启渲染...")
        try:
            if self.world is None:
                print("❌ 操作失败: 未连接到CARLA世界。")
                return
            settings = self.world.get_settings()
            settings.no_rendering_mode = False
            self.world.apply_settings(settings)
            print("✅ 成功开启渲染模式。")
        except Exception as e:
            print(f"❌ 开启渲染时出错: {e}")

    def close_render(self):
        print("尝试开启渲染...")
        try:
            if self.world is None:
                print("❌ 操作失败: 未连接到CARLA世界。")
                return
            settings = self.world.get_settings()
            settings.no_rendering_mode = True
            self.world.apply_settings(settings)
            print("✅ 成功关闭渲染模式。")
        except Exception as e:
            print(f"❌ 关闭渲染时出错: {e}")

    def open_HUD2d(self):
        # 构造命令
        role_name = self.ui.lineEdit_spawnname.text()
        command = [
            "python", "no_rendering_mode.py",
            "--role-name", role_name
        ]
        try:
            subprocess.Popen(command)
            print(f"🚗 已运行: {' '.join(command)}")
        except Exception as e:
            print(f"❌ 启动失败: {e}")

    def show_vehicle_speed(self):
        """
        启动一个线程，在【所有】车辆上方显示实时速度。
        """
        print("请求显示所有车辆速度...")
        # 【修改点】不再需要检查 self.car 是否存在
        if self.world is None:
            print("❌ 操作失败: 请先连接到CARLA世界。")
            return

        # 如果已有速度显示线程在运行，先停止旧的
        if self.speed_thread and self.speed_thread.isRunning():
            self.speed_thread.stop()
            self.speed_thread.wait()

        # 【修改点】创建线程时不再传入 self.car
        self.speed_thread = SpeedDisplayThread(self.world)
        self.speed_thread.start()
        print("✅ 所有车辆速度显示线程已启动。")

    def close_vehicle_speed(self):
        """
        停止显示车辆速度的线程。
        """
        print("请求隐藏车辆速度...")
        if self.speed_thread and self.speed_thread.isRunning():
            self.speed_thread.stop()
            self.speed_thread.wait()  # 等待线程安全退出
            self.speed_thread = None  # 清理引用
            print("✅ 速度显示线程已停止。")
        else:
            print("ℹ️ 当前没有正在运行的速度显示线程。")


class SpectatorFollowerThread_pro(QThread): # 带运镜的跟随
    def __init__(self, world, vehicle, x_offset=110, y_offset=60, z_offset=40, tolerance=2):
        super().__init__()
        self.world = world
        self.spectator = world.get_spectator()
        self.vehicle = vehicle

        self.x_offset = x_offset
        self.y_offset = y_offset
        self.z_offset = z_offset
        self.tolerance = tolerance

        self._running = True  # 控制程序运行状态

    def run(self):
        while self._running:
            try:
                self.world.wait_for_tick()
                self.follow_once()
            except Exception as e:
                print(f"线程运行异常：{e}")
                self.stop()
                break

    def stop(self):
        print("停止程序调用，准备退出。")
        self._running = False
        self.quit()  # 通知线程退出事件循环
        self.wait()  # 等待线程完全退出

    def follow_once(self):
        if not self._running:
            return False

        if self.vehicle is None:
            print("车辆不存在，停止更新观测者。")
            self.stop()
            return False
        vehicle_transform = self.vehicle.get_transform()
        vehicle_location = self.vehicle.get_transform().location
        spectator_transform = self.spectator.get_transform()
        spectator_location = spectator_transform.location

        min_distance = math.sqrt(self.z_offset**2) - self.tolerance
        max_distance = math.sqrt(self.x_offset**2 + self.y_offset**2 + self.z_offset**2) + self.tolerance

        distance = vehicle_location.distance(spectator_location)

        if distance < min_distance or distance > max_distance:
            new_transform = self.get_spectator_transform()
            self.spectator.set_transform(new_transform)
        else:
            new_rotation = self.get_rotation_towards(vehicle_transform, spectator_location)
            new_transform = carla.Transform(spectator_location, new_rotation)
            self.spectator.set_transform(new_transform)

        return True

    def get_spectator_transform(self):
        transform = self.vehicle.get_transform()
        location = transform.location
        forward = transform.get_forward_vector()
        right = transform.get_right_vector()

        angular_velocity = self.vehicle.get_angular_velocity()
        yaw_rate = angular_velocity.z  # 获取横摆角速度
        threshold = 0.05  # 你可以根据需要调整阈值，单位是弧度/秒
        if abs(yaw_rate) < threshold:
            # 小于阈值，左右随机
            y_offset = self.y_offset if random.random() > 0.5 else -self.y_offset
        else:
            # 按角速度符号确定左右
            if yaw_rate < 0:
                # 车辆左转，y_offset为正
                y_offset = self.y_offset
            else:
                # 车辆右转，y_offset负
                y_offset = -self.y_offset

        cam_location = location + forward * self.x_offset + right * y_offset
        cam_location.z += self.z_offset

        rotation = self.get_rotation_towards(transform, cam_location)
        return carla.Transform(cam_location, rotation)

    def get_rotation_towards(self, vehicle_transform, from_location):
        """
        计算摄像头应朝向车辆前方10米处的旋转角度。

        参数：
            vehicle_transform: carla.Transform，车辆当前的变换信息（位置+朝向）
            from_location: carla.Location，摄像头当前位置

        返回：
            carla.Rotation，摄像头应当的旋转角度，使其朝向车辆前方10米处
        """
        vehicle_location = vehicle_transform.location
        forward = vehicle_transform.get_forward_vector()
        # 计算车辆前方10米的位置
        look_at_location = vehicle_location + forward * 30

        # 计算摄像头位置到目标位置的方向向量
        direction = look_at_location - from_location

        # 计算yaw角（水平旋转），atan2(y, x)
        yaw = math.degrees(math.atan2(direction.y, direction.x))

        # 计算pitch角（俯仰角），atan2(z, 水平距离）
        horizontal_dist = math.hypot(direction.x, direction.y)
        pitch = math.degrees(math.atan2(direction.z, horizontal_dist))

        # roll保持0
        return carla.Rotation(pitch=pitch, yaw=yaw, roll=0)

class SpectatorFollowerThread_easy(QThread): # 带运镜的跟随
    def __init__(self, world, vehicle, x_offset=-20, z_offset=15, look_at_offset=5):
        """
        参数:
            client (carla.Client): CARLA 客户端对象。
            world (carla.World): CARLA 世界对象。
            vehicle (carla.Actor): 要跟随的车辆对象。
            x_offset (float): 旁观者相对于车辆后方的距离 (负值表示在车辆后方)。
            z_offset (float): 旁观者相对于车辆高度的偏移量 (正值表示在车辆上方)。
            look_at_offset (float): 旁观者看向车辆前方多少米的位置。
        """
        super().__init__()
        self.world = world
        self.spectator = world.get_spectator()
        self.vehicle = vehicle

        self.x_offset = x_offset
        self.z_offset = z_offset
        self.look_at_offset = look_at_offset

        self._running = True  # 控制程序运行状态

    def run(self):
        while self._running:
            try:
                self.world.wait_for_tick()
                self.follow_once()
            except Exception as e:
                print(f"线程运行异常：{e}")
                self.stop()
                break

    def stop(self):
        print("停止程序调用，准备退出。")
        self._running = False
        self.quit()  # 通知线程退出事件循环
        self.wait()  # 等待线程完全退出

    def follow_once(self):
        if not self._running:
            return False

        if self.vehicle is None:
            print("车辆不存在，停止更新观测者。")
            self.stop()
            return False
        # 车辆位置
        vehicle_transform = self.vehicle.get_transform()
        vehicle_location = self.vehicle.get_transform().location
        vehicle_forward_vector = vehicle_transform.get_forward_vector()

        # 计算旁观者的新位置
        spectator_location = carla.Location(
            x=vehicle_location.x + vehicle_forward_vector.x * self.x_offset,
            y=vehicle_location.y + vehicle_forward_vector.y * self.x_offset,
            z=vehicle_location.z + self.z_offset
        )

        # 计算旁观者看向的位置（车辆前方 look_at_offset 处）
        look_at_point = carla.Location(
            x=vehicle_location.x + vehicle_forward_vector.x * self.look_at_offset,
            y=vehicle_location.y + vehicle_forward_vector.y * self.look_at_offset,
            z=vehicle_location.z # 可以稍微抬高，如果需要
        )

        # 计算从旁观者位置到目标点的旋转
        direction_vector = look_at_point - spectator_location
        # 确保分母不为零，避免atan2错误
        horizontal_dist = math.sqrt(direction_vector.x**2 + direction_vector.y**2)
        pitch = math.degrees(math.atan2(direction_vector.z, horizontal_dist)) if horizontal_dist != 0 else 0
        yaw = math.degrees(math.atan2(direction_vector.y, direction_vector.x))
        roll = 0.0

        spectator_rotation = carla.Rotation(pitch=pitch, yaw=yaw, roll=roll)

        # 更新旁观者的变换
        new_spectator_transform = carla.Transform(spectator_location, spectator_rotation)
        self.spectator.set_transform(new_spectator_transform)
        return True

class SpeedDisplayThread(QThread):
    """
    一个在【所有】车辆上方实时显示速度的线程。
    """

    def __init__(self, world):  # <-- 修改点：不再需要 vehicle 参数
        """
        初始化速度显示线程。

        参数:
            world (carla.World): CARLA 世界对象。
        """
        super().__init__()
        self.world = world
        self._running = True  # 控制线程运行状态的标志

    def run(self):
        """
        线程主循环。只要 _running 为 True，就持续更新所有车辆的速度显示。
        """
        while self._running:
            try:
                # 【核心修改】在每一帧开始时，获取当前世界中所有车辆的列表
                vehicle_list = self.world.get_actors().filter('vehicle.*')

                # 如果世界中没有车辆，就直接等待下一帧
                if not vehicle_list:
                    self.world.wait_for_tick()
                    continue

                # 遍历列表中的每一辆车
                for vehicle in vehicle_list:
                    # 检查车辆是否有效（可能在遍历过程中被销毁）
                    if not vehicle.is_alive:
                        continue

                    # --- 后续逻辑与之前版本完全相同，只是作用于当前循环的 vehicle ---
                    velocity = vehicle.get_velocity()
                    speed_kmh = 3.6 * math.sqrt(velocity.x ** 2 + velocity.y ** 2 + velocity.z ** 2)

                    vehicle_location = vehicle.get_location()
                    text_location = vehicle_location + carla.Location(y=1.0,z=2.5)

                    display_text = f"{speed_kmh:.1f} km/h"

                    self.world.debug.draw_string(
                        location=text_location,
                        text=display_text,
                        draw_shadow=True,
                        color=carla.Color(r=255, g=0, b=0),
                        # life_time=0.1,
                        persistent_lines=True
                    )

                # 在处理完当前帧的所有车辆后，等待下一个tick
                self.world.wait_for_tick()

            except RuntimeError as e:
                print(f"线程运行时发生错误 (可能CARLA已关闭): {e}")
                break
            except Exception as e:
                print(f"多车速度显示线程发生未知异常: {e}")
                break

        print("多车速度显示线程已安全退出。")

    def stop(self):
        print("正在请求停止多车速度显示线程...")
        self._running = False


if __name__ == '__main__':
    app_config  = load_config()
    carla_path = app_config.get('CarlaSettings', 'carla_path') # get() 方法获取字符串
    Spawn_x = app_config.get('CarlaSettings', 'Spawn_x') # get() 方法获取字符串
    Spawn_y = app_config.get('CarlaSettings', 'Spawn_y') # get() 方法获取字符串
    Spawn_z = app_config.get('CarlaSettings', 'Spawn_z') # get() 方法获取字符串
    Spawn_yaw = app_config.get('CarlaSettings', 'Spawn_yaw') # get() 方法获取字符串

    app = QApplication(sys.argv)
    mainWin = MyMainWindow(carla_path=carla_path)

    mainWin.carlaPath = carla_path
    mainWin.ui.lineEdit_spawnX.setText(Spawn_x)
    mainWin.ui.lineEdit_spawnY.setText(Spawn_y)
    mainWin.ui.lineEdit_spawnZ.setText(Spawn_z)
    mainWin.ui.lineEdit_spawnYaw.setText(Spawn_yaw)

    mainWin.ui.lineEdit_moveX.setText(Spawn_x)
    mainWin.ui.lineEdit_moveY.setText(Spawn_y)
    mainWin.ui.lineEdit_moveZ.setText(Spawn_z)
    mainWin.ui.lineEdit_moveYaw.setText(Spawn_yaw)

    print(f"carla_path: {carla_path}")
    mainWin.show()
    sys.exit(app.exec_())