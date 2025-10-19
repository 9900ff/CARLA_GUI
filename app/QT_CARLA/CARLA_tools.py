# -*- coding: utf-8 -*-

"""
CARLA 工具箱 - 重构美化版
作者: Gemini
描述: 一个使用 PyQt5 构建的现代化、响应式布局的 CARLA 模拟器控制工具。
"""

from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QGridLayout,
    QPushButton, QLineEdit, QLabel, QComboBox, QTextBrowser, QGroupBox,
    QFrame, QSizePolicy
)


class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(1000, 900)  # 再次增加高度以容纳新控件
        MainWindow.setWindowTitle("CARLA 工具箱 by 王则祺 (Gemini 美化版)")

        # 设置全局字体和样式
        font = QtGui.QFont("Microsoft YaHei UI", 9)
        MainWindow.setFont(font)
        self.apply_stylesheet(MainWindow)

        self.centralwidget = QWidget(MainWindow)
        self.centralwidget.setObjectName("centralwidget")

        # 主布局
        main_layout = QHBoxLayout(self.centralwidget)

        # --- 左侧面板 ---
        left_panel = QWidget()
        left_layout = QVBoxLayout(left_panel)
        left_layout.setSpacing(15)

        # CARLA 服务器控制
        self.create_server_control_group(left_layout)
        # CARLA 连接控制
        self.create_connection_group(left_layout)
        # 世界控制
        self.create_world_control_group(left_layout)

        left_layout.addStretch(1)  # 添加伸缩，让控件更紧凑

        # --- 右侧面板 ---
        right_panel = QWidget()
        right_layout = QVBoxLayout(right_panel)
        right_layout.setSpacing(15)

        # Actor 生成与控制
        self.create_actor_control_group(right_layout)
        # 车辆/观察者控制
        self.create_vehicle_spectator_group(right_layout)

        right_layout.addStretch(1)

        main_layout.addWidget(left_panel, 1)
        main_layout.addWidget(right_panel, 2)

        MainWindow.setCentralWidget(self.centralwidget)
        self.setup_menubar_statusbar(MainWindow)

        self.retranslateUi(MainWindow)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

    def create_server_control_group(self, parent_layout):
        group = QGroupBox("CARLA 服务器")
        layout = QGridLayout(group)

        self.pushButton_chooseCARLA = QPushButton("...")
        self.textBrowser_chooseCARLA = QLineEdit()  # 使用 QLineEdit 更合适
        self.textBrowser_chooseCARLA.setPlaceholderText("点击右侧按钮选择 CARLA.exe 路径")

        self.pushButton_startCARLA = QPushButton()
        self.pushButton_startCARLA.setStyleSheet("background-color: #4CAF50;")
        self.pushButton_closeCARLA = QPushButton()
        self.pushButton_closeCARLA.setStyleSheet("background-color: #f44336;")

        self.comboBox_quality = QComboBox()
        self.rendering_mode = QComboBox()

        layout.addWidget(self.textBrowser_chooseCARLA, 0, 0, 1, 2)
        layout.addWidget(self.pushButton_chooseCARLA, 0, 2)
        layout.addWidget(self.pushButton_startCARLA, 1, 0, 1, 3)
        layout.addWidget(self.pushButton_closeCARLA, 2, 0, 1, 3)
        layout.addWidget(QLabel("图形质量:"), 3, 0)
        layout.addWidget(self.comboBox_quality, 3, 1, 1, 2)
        layout.addWidget(QLabel("渲染模式:"), 4, 0)
        layout.addWidget(self.rendering_mode, 4, 1, 1, 2)

        parent_layout.addWidget(group)

    def create_connection_group(self, parent_layout):
        group = QGroupBox("连接")
        layout = QGridLayout(group)

        self.lineEdit_IP = QLineEdit()
        self.lineEdit_port = QLineEdit()
        self.pushButton_connectCARLA = QPushButton()
        self.pushButton_connectCARLA.setStyleSheet("background-color: #008CBA;")
        self.textBrowser_connectState = QTextBrowser()

        layout.addWidget(QLabel("IP:"), 0, 0)
        layout.addWidget(self.lineEdit_IP, 0, 1)
        layout.addWidget(QLabel("端口:"), 1, 0)
        layout.addWidget(self.lineEdit_port, 1, 1)
        layout.addWidget(self.pushButton_connectCARLA, 2, 0, 1, 2)
        layout.addWidget(QLabel("连接状态:"), 3, 0, 1, 2)
        layout.addWidget(self.textBrowser_connectState, 4, 0, 1, 2)

        parent_layout.addWidget(group)

    def create_world_control_group(self, parent_layout):
        group = QGroupBox("世界控制")
        layout = QGridLayout(group)

        self.comboBox_map = QComboBox()
        self.pushButton_chooseMap = QPushButton()

        self.comboBox_weather = QComboBox()
        self.pushButton_chooseWeather = QPushButton()

        self.pushButton_setAsyn = QPushButton()
        self.pushButton_clearAllActor = QPushButton()

        self.pushButton_render = QPushButton()
        self.pushButton_norender = QPushButton()

        self.pushButton_HUD2d = QPushButton()
        self.pushButton_showSpeed = QPushButton()
        self.pushButton_hideSpeed = QPushButton()

        layout.addWidget(self.comboBox_map, 0, 0)
        layout.addWidget(self.pushButton_chooseMap, 0, 1)
        layout.addWidget(self.comboBox_weather, 1, 0)
        layout.addWidget(self.pushButton_chooseWeather, 1, 1)
        layout.addWidget(self.pushButton_setAsyn, 2, 0)
        layout.addWidget(self.pushButton_clearAllActor, 2, 1)
        layout.addWidget(self.pushButton_render, 3, 0)
        layout.addWidget(self.pushButton_norender, 3, 1)

        line = QFrame();
        line.setFrameShape(QFrame.HLine);
        line.setFrameShadow(QFrame.Sunken)
        layout.addWidget(line, 4, 0, 1, 2)

        layout.addWidget(self.pushButton_HUD2d, 5, 0, 1, 2)
        layout.addWidget(self.pushButton_showSpeed, 6, 0)
        layout.addWidget(self.pushButton_hideSpeed, 6, 1)

        parent_layout.addWidget(group)

    def create_actor_control_group(self, parent_layout):
        main_group = QGroupBox("Actor 管理")
        main_layout = QVBoxLayout(main_group)

        spawn_group = QGroupBox("生成车辆")
        spawn_layout = QGridLayout(spawn_group)
        self.lineEdit_spawnname = QLineEdit()
        self.lineEdit_spawnX = QLineEdit()
        self.lineEdit_spawnY = QLineEdit()
        self.lineEdit_spawnZ = QLineEdit()
        self.lineEdit_spawnYaw = QLineEdit()
        self.pushButton_spawnCar = QPushButton()
        self.pushButton_spawnCarPygame = QPushButton()

        spawn_layout.addWidget(QLabel("Role Name:"), 0, 0)
        spawn_layout.addWidget(self.lineEdit_spawnname, 0, 1, 1, 3)
        spawn_layout.addWidget(QLabel("X:"), 1, 0)
        spawn_layout.addWidget(self.lineEdit_spawnX, 1, 1)
        spawn_layout.addWidget(QLabel("Y:"), 1, 2)
        spawn_layout.addWidget(self.lineEdit_spawnY, 1, 3)
        spawn_layout.addWidget(QLabel("Z:"), 2, 0)
        spawn_layout.addWidget(self.lineEdit_spawnZ, 2, 1)
        spawn_layout.addWidget(QLabel("Yaw:"), 2, 2)
        spawn_layout.addWidget(self.lineEdit_spawnYaw, 2, 3)
        spawn_layout.addWidget(self.pushButton_spawnCar, 3, 0, 1, 2)
        spawn_layout.addWidget(self.pushButton_spawnCarPygame, 3, 2, 1, 2)

        main_layout.addWidget(spawn_group)

        actor_list_group = QGroupBox("车辆列表与操作")
        # 使用水平布局实现 1x2 结构
        list_layout = QHBoxLayout(actor_list_group)

        # --- 左侧栏: 控制按钮 ---
        left_controls_widget = QWidget()
        left_v_layout = QVBoxLayout(left_controls_widget)
        left_v_layout.setContentsMargins(0, 0, 10, 0)  # 右边距，与右侧状态栏分隔

        left_v_layout.addWidget(QLabel("选择车辆:"))

        # 用于 ComboBox 和刷新按钮的水平布局
        combo_refresh_layout = QHBoxLayout()
        self.comboBox_carRolename = QComboBox()
        self.pushButton_refreshCars = QPushButton("\u21BB")  # 刷新图标 (↻)

        # 设置刷新按钮的样式，使其看起来像一个图标按钮
        font = QtGui.QFont("Arial", 12)
        self.pushButton_refreshCars.setFont(font)
        self.pushButton_refreshCars.setFixedSize(QtCore.QSize(36, 36))

        combo_refresh_layout.addWidget(self.comboBox_carRolename)
        combo_refresh_layout.addWidget(self.pushButton_refreshCars)

        left_v_layout.addLayout(combo_refresh_layout)

        # 垂直添加其他操作按钮
        self.pushButton_connectCar = QPushButton()
        self.pushButton_clearActor_roleneme = QPushButton()
        left_v_layout.addWidget(self.pushButton_connectCar)
        left_v_layout.addWidget(self.pushButton_clearActor_roleneme)

        left_v_layout.addStretch()  # 添加伸缩，使控件保持在顶部

        # --- 右侧栏: 状态显示 ---
        right_status_widget = QWidget()
        right_v_layout = QVBoxLayout(right_status_widget)
        right_v_layout.setContentsMargins(0, 0, 0, 0)

        self.label_current_car_info = QLabel()
        self.textBrowser_carState = QTextBrowser()  # 移除最小高度限制，使其可自由伸展

        right_v_layout.addWidget(self.label_current_car_info)
        right_v_layout.addWidget(QLabel("场景中全部车辆:"))
        right_v_layout.addWidget(self.textBrowser_carState)

        # 将左右两栏添加到主布局，并设置伸缩比例
        list_layout.addWidget(left_controls_widget, 1)
        list_layout.addWidget(right_status_widget, 2)  # 右侧空间占比更大

        main_layout.addWidget(actor_list_group)
        parent_layout.addWidget(main_group)

    def create_vehicle_spectator_group(self, parent_layout):
        group = QGroupBox("车辆/观察者控制")
        main_v_layout = QVBoxLayout(group)

        # Sub-group for moving the car
        move_car_group = QGroupBox("移动当前车辆")
        move_car_layout = QGridLayout(move_car_group)
        self.pushButton_setCarPose = QPushButton()
        self.lineEdit_moveX = QLineEdit()
        self.lineEdit_moveY = QLineEdit()
        self.lineEdit_moveZ = QLineEdit()
        self.lineEdit_moveYaw = QLineEdit()
        move_car_layout.addWidget(QLabel("X:"), 0, 0);
        move_car_layout.addWidget(self.lineEdit_moveX, 0, 1)
        move_car_layout.addWidget(QLabel("Y:"), 0, 2);
        move_car_layout.addWidget(self.lineEdit_moveY, 0, 3)
        move_car_layout.addWidget(QLabel("Z:"), 1, 0);
        move_car_layout.addWidget(self.lineEdit_moveZ, 1, 1)
        move_car_layout.addWidget(QLabel("Yaw:"), 1, 2);
        move_car_layout.addWidget(self.lineEdit_moveYaw, 1, 3)
        move_car_layout.addWidget(self.pushButton_setCarPose, 2, 0, 1, 4)
        main_v_layout.addWidget(move_car_group)

        # Sub-group for spectator control
        spectator_group = QGroupBox("观察者控制")
        spectator_layout = QGridLayout(spectator_group)
        self.pushButton_setSpectatorPose_tocar = QPushButton()
        self.pushButton_SpectatorFollower_easy = QPushButton()
        self.pushButton_SpectatorFollower_pro = QPushButton()
        self.pushButton_StopSpectatorFollower = QPushButton()
        spectator_layout.addWidget(QLabel("快捷操作:"), 0, 0, 1, 4)
        spectator_layout.addWidget(self.pushButton_setSpectatorPose_tocar, 1, 0, 1, 2)
        spectator_layout.addWidget(self.pushButton_StopSpectatorFollower, 1, 2, 1, 2)
        spectator_layout.addWidget(self.pushButton_SpectatorFollower_easy, 2, 0, 1, 2)
        spectator_layout.addWidget(self.pushButton_SpectatorFollower_pro, 2, 2, 1, 2)

        line = QFrame();
        line.setFrameShape(QFrame.HLine);
        line.setFrameShadow(QFrame.Sunken)
        spectator_layout.addWidget(line, 3, 0, 1, 4)

        self.pushButton_setSpectatorPose = QPushButton()
        self.lineEdit_spectatorX = QLineEdit()
        self.lineEdit_spectatorY = QLineEdit()
        self.lineEdit_spectatorZ = QLineEdit()
        self.lineEdit_spectatorYaw = QLineEdit()
        spectator_layout.addWidget(QLabel("精确位置:"), 4, 0, 1, 4)
        spectator_layout.addWidget(QLabel("X:"), 5, 0);
        spectator_layout.addWidget(self.lineEdit_spectatorX, 5, 1)
        spectator_layout.addWidget(QLabel("Y:"), 5, 2);
        spectator_layout.addWidget(self.lineEdit_spectatorY, 5, 3)
        spectator_layout.addWidget(QLabel("Z:"), 6, 0);
        spectator_layout.addWidget(self.lineEdit_spectatorZ, 6, 1)
        spectator_layout.addWidget(QLabel("Yaw:"), 6, 2);
        spectator_layout.addWidget(self.lineEdit_spectatorYaw, 6, 3)
        spectator_layout.addWidget(self.pushButton_setSpectatorPose, 7, 0, 1, 4)
        main_v_layout.addWidget(spectator_group)

        parent_layout.addWidget(group)

    def setup_menubar_statusbar(self, MainWindow):
        self.statusbar = QtWidgets.QStatusBar(MainWindow)
        MainWindow.setStatusBar(self.statusbar)
        self.menubar = QtWidgets.QMenuBar(MainWindow)
        self.menubar.setGeometry(QtCore.QRect(0, 0, 1000, 26))
        self.menuCARLA = QtWidgets.QMenu(self.menubar)
        self.menubar.addAction(self.menuCARLA.menuAction())
        MainWindow.setMenuBar(self.menubar)

    def apply_stylesheet(self, app_window):
        app_window.setStyleSheet("""
            QMainWindow, QWidget {
                background-color: #f0f0f0;
            }
            QGroupBox {
                font-weight: bold;
                border: 1px solid #ccc;
                border-radius: 5px;
                margin-top: 10px;
                padding: 10px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                subcontrol-position: top left;
                padding: 0 3px;
                background-color: #f0f0f0;
            }
            QLabel {
                font-weight: normal;
            }
            QLineEdit, QTextBrowser, QComboBox {
                border: 1px solid #ccc;
                border-radius: 4px;
                padding: 5px;
                background-color: #ffffff;
            }
            QLineEdit:focus, QTextBrowser:focus {
                border-color: #0078d7;
            }
            QPushButton {
                background-color: #e0e0e0;
                border: 1px solid #ccc;
                border-radius: 4px;
                padding: 8px 12px;
                color: #333;
            }
            QPushButton:hover {
                background-color: #d0d0d0;
                border-color: #999;
            }
            QPushButton:pressed {
                background-color: #c0c0c0;
            }
        """)

    def retranslateUi(self, MainWindow):
        _translate = QtCore.QCoreApplication.translate

        # --- 设置所有控件的文本 ---
        self.pushButton_startCARLA.setText(_translate("MainWindow", "启动 CARLA"))
        self.pushButton_closeCARLA.setText(_translate("MainWindow", "关闭 CARLA"))
        self.pushButton_connectCARLA.setText(_translate("MainWindow", "连接 CARLA"))
        self.pushButton_chooseMap.setText(_translate("MainWindow", "修改地图"))
        self.pushButton_chooseWeather.setText(_translate("MainWindow", "设置天气"))
        self.pushButton_setAsyn.setText(_translate("MainWindow", "异步模式"))
        self.pushButton_clearAllActor.setText(_translate("MainWindow", "清除全部actor"))
        self.pushButton_render.setText(_translate("MainWindow", "启用渲染"))
        self.pushButton_norender.setText(_translate("MainWindow", "禁用渲染"))
        self.pushButton_HUD2d.setText(_translate("MainWindow", "启用2D渲染"))
        self.pushButton_showSpeed.setText(_translate("MainWindow", "显示速度"))
        self.pushButton_hideSpeed.setText(_translate("MainWindow", "关闭速度显示"))
        self.pushButton_spawnCar.setText(_translate("MainWindow", "生成车辆"))
        self.pushButton_spawnCarPygame.setText(_translate("MainWindow", "在pygame\n生成车辆"))
        self.pushButton_refreshCars.setToolTip(_translate("MainWindow", "刷新车辆列表"))
        self.pushButton_connectCar.setText(_translate("MainWindow", "连接车辆"))
        self.pushButton_clearActor_roleneme.setText(_translate("MainWindow", "清除此actor"))
        self.pushButton_setCarPose.setText(_translate("MainWindow", "移动车辆到坐标位置"))
        self.pushButton_setSpectatorPose_tocar.setText(_translate("MainWindow", "设置spectator\n到此车位置"))
        self.pushButton_SpectatorFollower_easy.setText(_translate("MainWindow", "spectator\n跟随车辆(标准版)"))
        self.pushButton_StopSpectatorFollower.setText(_translate("MainWindow", "停止spectator\n跟随车辆"))
        self.pushButton_SpectatorFollower_pro.setText(_translate("MainWindow", "spectator\n跟随车辆(pro)"))
        self.pushButton_setSpectatorPose.setText(_translate("MainWindow", "设置观测者位置"))
        self.label_current_car_info.setText(_translate("MainWindow", "当前未连接车辆"))
        self.label_current_car_info.setStyleSheet("font-weight: normal; color: #555; padding: 5px; border: 1px solid #ddd; border-radius: 4px; background-color: #f0f0f0;")

        # --- ComboBox ---
        self.comboBox_quality.addItem(_translate("MainWindow", "Low"))
        self.comboBox_quality.addItem(_translate("MainWindow", "Epic"))
        self.rendering_mode.addItem(_translate("MainWindow", "正常"))
        self.rendering_mode.addItem(_translate("MainWindow", "离屏渲染"))

        # --- 设置默认值和静态文本 ---
        self.lineEdit_IP.setText(_translate("MainWindow", "localhost"))
        self.lineEdit_port.setText(_translate("MainWindow", "2000"))
        self.textBrowser_connectState.setHtml(_translate("MainWindow", "<p>未连接</p>"))

        maps = ["gaoshu3800"] + [f"Town{i:02}" for i in range(1, 13)]
        for i, map_name in enumerate(maps):
            self.comboBox_map.addItem("")
            self.comboBox_map.setItemText(i, _translate("MainWindow", map_name))

        weathers = [
            "晴朗 正午", "多云 正午", "湿润 正午", "湿润多云 正午",
            "小雨 正午", "中雨 正午", "大雨 正午", "晴朗 日出",
            "多云 日出", "湿润 日出", "小雨 日出", "中雨 日出", "大雨 日出"
        ]
        for i, weather_name in enumerate(weathers):
            self.comboBox_weather.addItem("")
            self.comboBox_weather.setItemText(i, _translate("MainWindow", weather_name))

        self.lineEdit_spawnname.setText(_translate("MainWindow", "ego_car"))
        self.lineEdit_spawnX.setText(_translate("MainWindow", "-1930"))
        self.lineEdit_spawnY.setText(_translate("MainWindow", "48.25"))
        self.lineEdit_spawnZ.setText(_translate("MainWindow", "0.3"))
        self.lineEdit_spawnYaw.setText(_translate("MainWindow", "0"))

        self.lineEdit_moveX.setText(_translate("MainWindow", "-1930"))
        self.lineEdit_moveY.setText(_translate("MainWindow", "48.25"))
        self.lineEdit_moveZ.setText(_translate("MainWindow", "0.3"))
        self.lineEdit_moveYaw.setText(_translate("MainWindow", "0"))

        self.lineEdit_spectatorX.setText(_translate("MainWindow", "0"))
        self.lineEdit_spectatorY.setText(_translate("MainWindow", "0"))
        self.lineEdit_spectatorZ.setText(_translate("MainWindow", "5"))
        self.lineEdit_spectatorYaw.setText(_translate("MainWindow", "0"))

        self.textBrowser_carState.setHtml(_translate("MainWindow", "<p>未连接</p>"))

        self.menuCARLA.setTitle(_translate("MainWindow", "CARLA启动"))


if __name__ == "__main__":
    import sys

    app = QtWidgets.QApplication(sys.argv)
    MainWindow = QtWidgets.QMainWindow()
    ui = Ui_MainWindow()
    ui.setupUi(MainWindow)
    MainWindow.show()
    sys.exit(app.exec_())

