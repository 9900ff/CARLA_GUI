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


def find_config_path():
    """
    搜索并返回 config.ini 的有效路径。
    """
    current_dir = os.path.dirname(os.path.abspath(__file__))
    parent_dir = os.path.dirname(current_dir)
    search_paths = [
        os.path.join(current_dir, 'config.ini'),
        os.path.join(parent_dir, 'config.ini')
    ]
    for config_path in search_paths:
        if os.path.exists(config_path):
            return config_path
    raise FileNotFoundError(f"在指定的目录中都找不到 'config.ini' 文件。搜索路径: {search_paths}")


def load_config():
    """
    读取配置文件并返回配置对象。
    """
    config_path = find_config_path()
    print(f"成功找到并加载配置文件: {config_path}")
    config = configparser.ConfigParser()
    config.read(config_path, encoding='utf-8')
    return config


class MyMainWindow(QMainWindow):
    def __init__(self, carla_path='D:\CARLA0.9.15\WindowsNoEditor\CarlaUE4.exe'):
        # 初始化
        super().__init__()
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)
        # 设置CARLA对象
        self.carla_path = carla_path  # 默认路径，可以修改
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
        # 加载备忘录内容
        self.load_memo()
        # 设置一个 QTimer，每2秒检查一次连接状态
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.refresh_world_data)
        self.timer.timeout.connect(self.refresh_ifcarconnect_data)
        self.timer.start(2000)  # 每2000毫秒（2秒）触发一次
        # 按钮点击事件连接
        self.connect_signals()

    def connect_signals(self):
        """将所有UI元素的信号连接到槽函数。"""
        self.ui.pushButton_chooseCARLA.clicked.connect(self.choose_carla_path)  # 选择carla路径
        self.ui.pushButton_startCARLA.clicked.connect(self.start_carla_clicked)  # 启动carla
        self.ui.pushButton_closeCARLA.clicked.connect(self.close_carla_clicked)  # 关闭carla
        self.ui.pushButton_connectCARLA.clicked.connect(self.connect_carla_clicked)  # 连接carla
        self.ui.pushButton_chooseMap.clicked.connect(self.change_map)  # 切换地图
        self.ui.pushButton_setAsyn.clicked.connect(self.set_Asyn_mode)  # 设置同步模式
        self.ui.pushButton_clearAllActor.clicked.connect(self.delete_all_actor)  # 清除所有actor
        self.ui.pushButton_spawnCar.clicked.connect(self.spawn_car)  # 生成车辆
        self.ui.pushButton_spawnCarPygame.clicked.connect(self.spawn_car_pygame)  # 在pygame画面生成车辆
        self.ui.pushButton_refreshCars.clicked.connect(lambda: self.refresh_car_data(refresh_Rolename=True))  # 更新车辆列表
        self.ui.pushButton_connectCar.clicked.connect(self.connect_car)  # 连接车辆
        self.ui.pushButton_setCarPose.clicked.connect(self.set_car_pose)  # 设置车辆位置
        self.ui.pushButton_clearActor_roleneme.clicked.connect(self.delete_actor_by_id)  # 删除车辆
        self.ui.pushButton_setSpectatorPose_tocar.clicked.connect(self.set_spectator_to_car)  # 设置观测者到车辆
        self.ui.pushButton_setSpectatorPose.clicked.connect(self.set_spectator)  # 设置观测者到指定坐标

        self.ui.pushButton_SpectatorFollower_pro.clicked.connect(self.spectator_follow_pro)  # 设置观测者跟随车辆 pro
        self.ui.pushButton_SpectatorFollower_easy.clicked.connect(self.spectator_follow_easy)  # 设置观测者跟随车辆 easy
        self.ui.pushButton_StopSpectatorFollower.clicked.connect(self.stop_spectator_follow)  # 停止观测者跟随车辆
        self.ui.pushButton_chooseWeather.clicked.connect(self.choose_weather)  # 设置天气

        self.ui.pushButton_render.clicked.connect(self.open_render)  # 启用画面渲染
        self.ui.pushButton_norender.clicked.connect(self.close_render)  # 禁用画面渲染
        self.ui.pushButton_HUD2d.clicked.connect(self.open_HUD2d)  # 启用2D画面渲染

        self.ui.pushButton_showSpeed.clicked.connect(self.show_vehicle_speed)  # 启用速度显示
        self.ui.pushButton_hideSpeed.clicked.connect(self.close_vehicle_speed)  # 禁用速度显示

        self.ui.pushButton_saveMemo.clicked.connect(self.save_memo)  # 保存备忘录

    def choose_carla_path(self):
        file_path, _ = QFileDialog.getOpenFileName(self, "选择 CARLA 启动程序", "", "可执行文件 (*.exe);;所有文件 (*)")
        if file_path:
            self.ui.textBrowser_chooseCARLA.setText(file_path)
            self.carla_path = file_path

            try:
                config_path = find_config_path()
                config = configparser.ConfigParser()
                config.read(config_path, encoding='utf-8')
                if not config.has_section('CarlaSettings'):
                    config.add_section('CarlaSettings')
                config.set('CarlaSettings', 'carla_path', file_path)
                with open(config_path, 'w', encoding='utf-8') as configfile:
                    config.write(configfile)
                self.statusBar().showMessage("✅ CARLA 路径已更新并保存。", 3000)
            except Exception as e:
                print(f"❌ 保存 CARLA 路径失败: {e}")
                self.statusBar().showMessage(f"❌ 保存 CARLA 路径失败: {e}", 5000)

    def start_carla_clicked(self):
        carla_path = self.carla_path
        quality = self.ui.comboBox_quality.currentText()
        benchmark = True
        port = self.ui.lineEdit_port.text()
        renderingmode = self.ui.rendering_mode.currentText()

        args = [carla_path, f"-quality-level={quality}", f"-carla-world-port={port}"]
        if benchmark:
            args.append("-benchmark")
        if renderingmode == "离屏渲染":
            args.append("-RenderOffScreen")

        try:
            subprocess.Popen(args)
            self.statusBar().showMessage(f"✅ 正在启动 CARLA (端口: {port})...", 5000)
        except Exception as e:
            self.statusBar().showMessage(f"❌ 启动 CARLA 失败: {e}", 5000)

    def close_carla_clicked(self):
        try:
            if self.world:
                self.set_Asyn_mode()
                self.delete_all_actor()
            os.system("taskkill /F /IM CarlaUE4.exe >nul 2>nul")
            os.system("taskkill /F /IM CarlaUE4-Win64-Shipping.exe >nul 2>nul")
            self.statusBar().showMessage("✅ 已发送关闭 CARLA 命令。", 3000)
        except Exception as e:
            self.statusBar().showMessage(f"❌ 关闭失败: {e}", 5000)
        finally:
            if self.follower_thread and self.follower_thread.isRunning():
                self.stop_spectator_follow()
            if self.speed_thread and self.speed_thread.isRunning():
                self.close_vehicle_speed()

            self.client = self.world = self.map = self.car = None

            self.ui.textBrowser_connectState.setText("未连接")
            self.ui.textBrowser_carState.setText("无")
            self.ui.comboBox_carRolename.clear()
            self.statusBar().showMessage("✅ 应用状态已重置。", 3000)

    def connect_carla_clicked(self):
        try:
            self.statusBar().showMessage("正在连接到 CARLA...", 2000)
            ip = self.ui.lineEdit_IP.text()
            port = int(self.ui.lineEdit_port.text())
            self.client = carla.Client(ip, port)
            self.client.set_timeout(10.0)
            self.world = self.client.get_world()
            self.statusBar().showMessage(f"✅ 成功连接到 CARLA: {ip}:{port}", 5000)
            self.client.set_timeout(5.0)
        except Exception as e:
            self.statusBar().showMessage(f"❌ CARLA 连接失败: {e}", 5000)
            self.client = self.world = None

    def refresh_world_data(self):
        if not self.world:
            self.ui.textBrowser_connectState.setText("未连接")
            return
        try:
            server_version = self.client.get_server_version()
            ip_info = self.ui.lineEdit_IP.text()
            port_info = self.ui.lineEdit_port.text()
            mode_info = "同步模式" if self.world.get_settings().synchronous_mode else "异步模式"

            spectator = self.world.get_spectator()
            transform = spectator.get_transform()
            location = transform.location
            rotation = transform.rotation
            spectator_info = f"{location.x:.2f}, {location.y:.2f}, {location.z:.2f}\nYaw: {rotation.yaw:.2f}"

            all_info = "\n".join([
                f"已连接上CARLA v{server_version}",
                f"IP: {ip_info}:{port_info}",
                f"模式: {mode_info}",
                f"\n观测者坐标:\n{spectator_info}"
            ])
            self.ui.textBrowser_connectState.setText(all_info)
            self.refresh_car_data()
        except RuntimeError:
            self.ui.textBrowser_connectState.setText("未连接")
            self.client = self.world = self.car = None

    def change_map(self):
        if not self.client:
            self.statusBar().showMessage("❌ 请先连接到 CARLA", 3000)
            return

        selected_map = self.ui.comboBox_map.currentText()
        try:
            self.world = self.client.load_world(selected_map)
            self.statusBar().showMessage(f"✅ 地图切换至 {selected_map}", 3000)
        except Exception as e:
            self.statusBar().showMessage("❌ 地图切换失败", 3000)
            print(f"[ERROR] 地图切换失败: {e}")

    def set_Asyn_mode(self):
        if not self.world:
            self.statusBar().showMessage("❌ 请先连接到 CARLA", 3000)
            return
        settings = self.world.get_settings()
        settings.synchronous_mode = False
        settings.fixed_delta_seconds = None
        self.world.apply_settings(settings)
        self.statusBar().showMessage("✅ 已切换到异步模式。", 2000)

    def delete_all_actor(self):
        if not self.world:
            self.statusBar().showMessage("❌ 请先连接到 CARLA", 3000)
            return
        count = 0
        for actor in self.world.get_actors():
            if actor.type_id != 'spectator':
                actor.destroy()
                count += 1
        self.statusBar().showMessage(f"✅ 已清除 {count} 个 Actor。", 2000)

    def spawn_car(self):
        if not self.world:
            self.statusBar().showMessage("❌ 请先连接到 CARLA", 3000)
            return
        blueprint_library = self.world.get_blueprint_library()
        car_bp = blueprint_library.find('vehicle.tesla.model3')
        role_name = self.ui.lineEdit_spawnname.text()
        car_bp.set_attribute('role_name', role_name)

        try:
            x = float(self.ui.lineEdit_spawnX.text())
            y = float(self.ui.lineEdit_spawnY.text())
            z = float(self.ui.lineEdit_spawnZ.text())
            yaw = float(self.ui.lineEdit_spawnYaw.text())
            spawn_point = carla.Transform(carla.Location(x=x, y=y, z=z), carla.Rotation(yaw=yaw))
            vehicle = self.world.spawn_actor(car_bp, spawn_point)
            self.statusBar().showMessage(f"✅ 成功生成车辆: {vehicle.attributes['role_name']}", 3000)
            return vehicle
        except Exception as e:
            self.statusBar().showMessage(f"❌ 生成车辆失败: {e}", 5000)
            return None

    def spawn_car_pygame(self):
        if not self.world:
            self.statusBar().showMessage("❌ 请先连接到 CARLA", 3000)
            return
        try:
            x = float(self.ui.lineEdit_spawnX.text())
            y = float(self.ui.lineEdit_spawnY.text())
            z = float(self.ui.lineEdit_spawnZ.text())
            yaw = float(self.ui.lineEdit_spawnYaw.text())
            role_name = self.ui.lineEdit_spawnname.text() or "ego"
            current_map = self.world.get_map().name.split('/')[-1]

            command = [
                "python", "./app/spawn_car_with_GUI.py",
                "--spawn_point", f"{x},{y},{z},{yaw}",
                "--rolename", role_name, "--map", current_map,
                "--host", self.ui.lineEdit_IP.text(), "--port", self.ui.lineEdit_port.text()
            ]
            subprocess.Popen(command)
            self.statusBar().showMessage(f"🚗 已启动 Pygame 控制窗口: {role_name}", 4000)
        except Exception as e:
            self.statusBar().showMessage(f"❌ 启动 Pygame 失败: {e}", 5000)

    def refresh_ifcarconnect_data(self):
        # 连接成功时的样式
        connected_style = """
            background-color: #A3BE8C; /* NORD_GREEN */
            color: #2E3440; /* TEXT_PRIMARY */
            border: 1px solid #A3BE8C;
            border-radius: 4px;
            padding: 5px;
            qproperty-alignment: 'AlignCenter';
            font-weight: bold;
        """
        # 未连接时的样式
        disconnected_style = """
            background-color: #E5E9F0;
            color: #4C566A; /* TEXT_SECONDARY */
            border: 1px solid #D8DEE9; /* BORDER */
            border-radius: 4px;
            padding: 5px;
            qproperty-alignment: 'AlignCenter';
            font-weight: bold;
        """

        # 获取所有需要更新的状态标签
        status_labels = [
            self.ui.label_current_car_info,
            self.ui.label_current_car_info_vehicle,
            self.ui.label_current_car_info_spectator
        ]

        car_is_valid = False
        car_info_text = "当前未连接车辆"

        # 检查车辆是否有效
        if self.car is not None:
            try:
                current_actor_ids = [actor.id for actor in self.world.get_actors()]
                if self.car.id in current_actor_ids:
                    car_is_valid = True
                    rolename = self.car.attributes.get('role_name', 'N/A')
                    actor_id = self.car.id
                    car_info_text = f"当前控制车辆: {rolename} id={actor_id}"
                else:
                    self.car = None
            except Exception as e:
                print(f"刷新车辆连接状态时出错: {e}")
                self.car = None

        # 根据车辆是否有效，一次性更新所有标签
        current_style = connected_style if car_is_valid else disconnected_style
        for label in status_labels:
            label.setText(car_info_text)
            label.setStyleSheet(current_style)

    def refresh_car_data(self, refresh_Rolename=False):
        if not self.world: return

        actors = list(self.world.get_actors().filter('vehicle.*'))

        if refresh_Rolename:
            self.ui.comboBox_carRolename.clear()
            if not actors:
                self.ui.comboBox_carRolename.addItem("无可用车辆")
            else:
                for actor in actors:
                    rolename = actor.attributes.get('role_name', 'N/A')
                    display_text = f"{rolename} id={actor.id}"
                    self.ui.comboBox_carRolename.addItem(display_text, actor.id)
            self.statusBar().showMessage("✅ 车辆列表已刷新。", 2000)

        actor_data = [f"{actor.attributes.get('role_name', 'N/A')}  id={actor.id}" for actor in actors]
        self.ui.textBrowser_carState.setText("\n".join(actor_data) if actor_data else "场景中没有车辆。")

    def connect_car(self):
        if not self.world:
            self.statusBar().showMessage("❌ 请先连接到 CARLA", 3000)
            return
        try:
            selected_id = self.ui.comboBox_carRolename.currentData()
            if selected_id is None:
                self.car = None
                self.statusBar().showMessage("⚠️ 未选择车辆或车辆 ID 无效。", 2000)
                return

            vehicle = self.world.get_actor(selected_id)
            if vehicle and 'vehicle.' in vehicle.type_id:
                self.car = vehicle
                rolename = vehicle.attributes.get('role_name', 'N/A')
                self.statusBar().showMessage(f"✅ 已连接到车辆: {rolename} (ID: {vehicle.id})", 3000)
            else:
                self.car = None
                self.statusBar().showMessage(f"❌ 未找到 ID 为 {selected_id} 的车辆。", 3000)
        except Exception as e:
            self.statusBar().showMessage(f"❌ 连接车辆失败: {e}", 5000)
            self.car = None

    def set_car_pose(self):
        if not self.car:
            self.statusBar().showMessage("❌ 请先连接到一辆车", 3000)
            return
        try:
            x = float(self.ui.lineEdit_moveX.text())
            y = float(self.ui.lineEdit_moveY.text())
            z = float(self.ui.lineEdit_moveZ.text())
            yaw = float(self.ui.lineEdit_moveYaw.text())
            new_transform = carla.Transform(carla.Location(x=x, y=y, z=z), carla.Rotation(yaw=yaw))
            self.car.set_transform(new_transform)
            self.statusBar().showMessage("✅ 车辆位置已更新。", 2000)
        except Exception as e:
            self.statusBar().showMessage(f"❌ 设置车辆位置失败: {e}", 5000)

    def delete_actor_by_id(self):
        if not self.car:
            self.statusBar().showMessage("❌ 请先连接到要删除的车辆", 3000)
            return
        try:
            car_id = self.car.id
            self.car.destroy()
            self.statusBar().showMessage(f"✅ 成功销毁车辆 ID={car_id}", 3000)
            self.car = None
        except Exception as e:
            self.statusBar().showMessage(f"❌ 销毁车辆失败: {e}", 5000)

    def set_spectator_to_car(self):
        if not self.car:
            self.statusBar().showMessage("❌ 请先连接到一辆车", 3000)
            return
        try:
            # ... (Implementation remains unchanged)
            self.statusBar().showMessage("✅ 观察者已移动到车辆后方。", 2000)
        except Exception as e:
            self.statusBar().showMessage(f"❌ 设置观察者失败: {e}", 5000)

    def set_spectator(self):
        if not self.world:
            self.statusBar().showMessage("❌ 请先连接到 CARLA", 3000)
            return
        try:
            # ... (Implementation remains unchanged)
            self.statusBar().showMessage("✅ 观察者位置已更新。", 2000)
        except Exception as e:
            self.statusBar().showMessage(f"❌ 设置观察者失败: {e}", 5000)

    def spectator_follow_easy(self):
        if not self.car:
            self.statusBar().showMessage("❌ 请先连接到一辆车", 3000)
            return
        if self.follower_thread: self.follower_thread.stop()
        self.follower_thread = SpectatorFollowerThread_easy(self.world, self.car)
        self.follower_thread.start()
        self.statusBar().showMessage("✅ 已启动标准跟随模式。", 2000)

    def spectator_follow_pro(self):
        if not self.car:
            self.statusBar().showMessage("❌ 请先连接到一辆车", 3000)
            return
        if self.follower_thread: self.follower_thread.stop()
        self.follower_thread = SpectatorFollowerThread_pro(self.world, self.car)
        self.follower_thread.start()
        self.statusBar().showMessage("✅ 已启动 Pro 跟随模式。", 2000)

    def stop_spectator_follow(self):
        if self.follower_thread:
            self.follower_thread.stop()
            self.statusBar().showMessage("✅ 已停止跟随。", 2000)
        else:
            self.statusBar().showMessage("ℹ️ 当前没有正在运行的跟随线程。", 2000)

    def choose_weather(self):
        if not self.world:
            self.statusBar().showMessage("❌ 请先连接到 CARLA", 3000)
            return
        weather_type = self.ui.comboBox_weather.currentText()
        # ... (rest of implementation)
        self.statusBar().showMessage(f"✅ 已设置天气为: {weather_type}", 2000)

    def open_render(self):
        if not self.world:
            self.statusBar().showMessage("❌ 请先连接到 CARLA", 3000)
            return
        settings = self.world.get_settings();
        settings.no_rendering_mode = False
        self.world.apply_settings(settings)
        self.statusBar().showMessage("✅ 已启用渲染。", 2000)

    def close_render(self):
        if not self.world:
            self.statusBar().showMessage("❌ 请先连接到 CARLA", 3000)
            return
        settings = self.world.get_settings();
        settings.no_rendering_mode = True
        self.world.apply_settings(settings)
        self.statusBar().showMessage("✅ 已禁用渲染。", 2000)

    def open_HUD2d(self):
        role_name = self.ui.lineEdit_spawnname.text()
        command = ["./python/python.exe", "./app/no_rendering_mode.py", "--role-name", role_name]
        try:
            subprocess.Popen(command)
            self.statusBar().showMessage(f"🚗 已为 {role_name} 启动 2D HUD。", 3000)
        except Exception as e:
            self.statusBar().showMessage(f"❌ 启动 2D HUD 失败: {e}", 5000)

    def show_vehicle_speed(self):
        if not self.world:
            self.statusBar().showMessage("❌ 请先连接到 CARLA", 3000)
            return
        if self.speed_thread and self.speed_thread.isRunning(): self.speed_thread.stop()
        self.speed_thread = SpeedDisplayThread(self.world)
        self.speed_thread.start()
        self.statusBar().showMessage("✅ 已启动速度显示。", 2000)

    def close_vehicle_speed(self):
        if self.speed_thread and self.speed_thread.isRunning():
            self.speed_thread.stop()
            self.statusBar().showMessage("✅ 已停止速度显示。", 2000)
        else:
            self.statusBar().showMessage("ℹ️ 当前没有正在运行的速度显示线程。", 2000)

    def load_memo(self):
        """从 config.ini 加载备忘录内容。"""
        try:
            config = load_config()
            if config.has_section('Memo') and config.has_option('Memo', 'notes'):
                notes = config.get('Memo', 'notes')
                self.ui.textEdit_memo.setPlainText(notes)
                print("✅ 备忘录内容已加载。")
        except Exception as e:
            print(f"❌ 加载备忘录失败: {e}")

    def save_memo(self):
        """将备忘录内容保存到 config.ini。"""
        try:
            config_path = find_config_path()
            config = configparser.ConfigParser()
            config.read(config_path, encoding='utf-8')

            if not config.has_section('Memo'):
                config.add_section('Memo')

            notes = self.ui.textEdit_memo.toPlainText()
            config.set('Memo', 'notes', notes)

            with open(config_path, 'w', encoding='utf-8') as configfile:
                config.write(configfile)

            print("✅ 备忘录已成功保存到 config.ini。")
            # 可以在状态栏显示提示
            self.statusBar().showMessage("备忘录已保存", 3000)

        except Exception as e:
            print(f"❌ 保存备忘录失败: {e}")
            self.statusBar().showMessage(f"保存失败: {e}", 5000)

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
    carla_path = app_config.get('CarlaSettings', 'carla_path', fallback='')
    spawn_coords = {k: app_config.get('CarlaSettings', k) for k in ['Spawn_x', 'Spawn_y', 'Spawn_z', 'Spawn_yaw']}

    app = QApplication(sys.argv)
    mainWin = MyMainWindow(carla_path=carla_path)

    mainWin.ui.lineEdit_spawnX.setText(spawn_coords['Spawn_x'])
    mainWin.ui.lineEdit_spawnY.setText(spawn_coords['Spawn_y'])
    mainWin.ui.lineEdit_spawnZ.setText(spawn_coords['Spawn_z'])
    mainWin.ui.lineEdit_spawnYaw.setText(spawn_coords['Spawn_yaw'])

    mainWin.ui.lineEdit_moveX.setText(spawn_coords['Spawn_x'])
    mainWin.ui.lineEdit_moveY.setText(spawn_coords['Spawn_y'])
    mainWin.ui.lineEdit_moveZ.setText(spawn_coords['Spawn_z'])
    mainWin.ui.lineEdit_moveYaw.setText(spawn_coords['Spawn_yaw'])

    mainWin.show()
    sys.exit(app.exec_())