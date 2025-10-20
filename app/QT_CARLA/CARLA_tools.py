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
    QFrame, QSizePolicy, QTabWidget
)


class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(1000, 800)
        MainWindow.setWindowTitle("CARLA 工具箱 by 王则祺 (Gemini 北境风版)")

        # 设置全局字体和样式
        font = QtGui.QFont("Segoe UI", 9)
        MainWindow.setFont(font)

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

        left_layout.addStretch(1)

        # --- 右侧面板 ---
        right_panel = QWidget()
        right_layout = QVBoxLayout(right_panel)
        right_layout.setSpacing(15)

        # Actor 列表与操作
        self.create_actor_list_group(right_layout)
        # 核心控制区 (使用 TabWidget)
        self.create_main_control_tabs(right_layout)

        right_layout.addStretch(1)

        # 调整主面板伸缩比例
        main_layout.addWidget(left_panel, 2)
        main_layout.addWidget(right_panel, 3)

        MainWindow.setCentralWidget(self.centralwidget)
        self.setup_menubar_statusbar(MainWindow)

        # 应用样式表必须在所有控件创建之后
        self.apply_stylesheet(MainWindow)
        self.retranslateUi(MainWindow)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)
        self.apply_effects(MainWindow)

    def apply_effects(self, MainWindow):
        """
        应用紧凑布局等微调。
        """

        def _compact_layout(widget: QWidget):
            layouts = widget.findChildren(QtWidgets.QLayout)
            for lay in layouts:
                lay.setSpacing(8)
                lay.setContentsMargins(12, 12, 12, 12)

        _compact_layout(MainWindow.centralWidget())

    def create_server_control_group(self, parent_layout):
        group = QGroupBox("CARLA 服务器")
        layout = QGridLayout(group)

        self.pushButton_chooseCARLA = QPushButton("...")
        self.textBrowser_chooseCARLA = QLineEdit()
        self.textBrowser_chooseCARLA.setPlaceholderText("点击右侧按钮选择 CARLA.exe 路径")

        self.pushButton_startCARLA = QPushButton()
        self.pushButton_startCARLA.setObjectName("startCarlaButton")
        self.pushButton_closeCARLA = QPushButton()
        self.pushButton_closeCARLA.setObjectName("closeCarlaButton")

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
        self.pushButton_connectCARLA.setObjectName("connectCarlaButton")
        self.textBrowser_connectState = QTextBrowser()

        layout.addWidget(QLabel("IP:"), 0, 0)
        layout.addWidget(self.lineEdit_IP, 0, 1)
        layout.addWidget(QLabel("端口:"), 1, 0)
        layout.addWidget(self.lineEdit_port, 1, 1)
        layout.addWidget(self.pushButton_connectCARLA, 2, 0, 1, 2)
        layout.addWidget(QLabel("连接状态:"), 3, 0, 1, 2)
        layout.addWidget(self.textBrowser_connectState, 4, 0, 1, 2)
        layout.setRowStretch(4, 1)  # 让状态框填充剩余空间

        parent_layout.addWidget(group)

    def create_actor_list_group(self, parent_layout):
        actor_list_group = QGroupBox("车辆列表与操作")
        list_layout = QHBoxLayout(actor_list_group)

        left_controls_widget = QWidget()
        left_grid_layout = QGridLayout(left_controls_widget)
        left_grid_layout.setContentsMargins(0, 0, 10, 0)
        left_grid_layout.setSpacing(8)

        self.comboBox_carRolename = QComboBox()
        self.pushButton_refreshCars = QPushButton("\u21BB")
        self.pushButton_refreshCars.setObjectName("refreshCarsButton")
        font = QtGui.QFont("Arial", 12);
        self.pushButton_refreshCars.setFont(font)
        self.pushButton_refreshCars.setFixedSize(QtCore.QSize(36, 36))

        self.pushButton_connectCar = QPushButton()
        self.pushButton_connectCar.setObjectName("connectVehicleButton")
        self.pushButton_clearActor_roleneme = QPushButton()
        self.pushButton_clearActor_roleneme.setObjectName("clearActorButton")

        left_grid_layout.addWidget(QLabel("选择车辆:"), 0, 0, 1, 2)
        left_grid_layout.addWidget(self.comboBox_carRolename, 1, 0)
        left_grid_layout.addWidget(self.pushButton_refreshCars, 1, 1)
        left_grid_layout.addWidget(self.pushButton_connectCar, 2, 0, 1, 2)
        left_grid_layout.addWidget(self.pushButton_clearActor_roleneme, 3, 0, 1, 2)
        left_grid_layout.setColumnStretch(0, 1)
        left_grid_layout.setRowStretch(4, 1)

        right_status_widget = QWidget();
        right_v_layout = QVBoxLayout(right_status_widget)
        right_v_layout.setContentsMargins(0, 0, 0, 0)
        self.label_current_car_info = QLabel()
        self.textBrowser_carState = QTextBrowser()
        right_v_layout.addWidget(self.label_current_car_info)
        right_v_layout.addWidget(QLabel("场景中全部车辆:"))
        right_v_layout.addWidget(self.textBrowser_carState)

        list_layout.addWidget(left_controls_widget, 2)
        list_layout.addWidget(right_status_widget, 3)
        parent_layout.addWidget(actor_list_group)

    def create_main_control_tabs(self, parent_layout):
        main_group = QGroupBox("核心控制")
        main_layout = QVBoxLayout(main_group)

        tab_widget = QTabWidget()

        # --- Tab 1: 世界控制 (Moved from left panel) ---
        world_tab = QWidget()
        layout = QGridLayout(world_tab)
        self.comboBox_map = QComboBox()
        self.pushButton_chooseMap = QPushButton()
        self.comboBox_weather = QComboBox()
        self.pushButton_chooseWeather = QPushButton()
        self.pushButton_setAsyn = QPushButton()
        self.pushButton_clearAllActor = QPushButton()
        self.pushButton_clearAllActor.setObjectName("clearAllActorButton")
        self.pushButton_render = QPushButton()
        self.pushButton_render.setObjectName("renderButtonSpecial")
        self.pushButton_norender = QPushButton()
        self.pushButton_norender.setObjectName("noRenderButtonSpecial")
        self.pushButton_HUD2d = QPushButton()
        self.pushButton_HUD2d.setObjectName("hud2dButtonSpecial")
        self.pushButton_showSpeed = QPushButton()
        self.pushButton_showSpeed.setObjectName("showSpeedButtonSpecial")
        self.pushButton_hideSpeed = QPushButton()
        self.pushButton_hideSpeed.setObjectName("hideSpeedButtonSpecial")

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
        world_tab.setLayout(layout)

        # --- Tab 2: 生成车辆 ---
        spawn_tab = QWidget()
        spawn_layout = QGridLayout(spawn_tab)
        self.lineEdit_spawnname = QLineEdit()
        self.lineEdit_spawnX = QLineEdit();
        self.lineEdit_spawnY = QLineEdit()
        self.lineEdit_spawnZ = QLineEdit();
        self.lineEdit_spawnYaw = QLineEdit()
        self.pushButton_spawnCar = QPushButton()
        self.pushButton_spawnCar.setObjectName("spawnCarButton")
        self.pushButton_spawnCarPygame = QPushButton()

        spawn_layout.addWidget(QLabel("Role Name:"), 0, 0);
        spawn_layout.addWidget(self.lineEdit_spawnname, 0, 1, 1, 3)
        spawn_layout.addWidget(QLabel("X:"), 1, 0);
        spawn_layout.addWidget(self.lineEdit_spawnX, 1, 1)
        spawn_layout.addWidget(QLabel("Y:"), 1, 2);
        spawn_layout.addWidget(self.lineEdit_spawnY, 1, 3)
        spawn_layout.addWidget(QLabel("Z:"), 2, 0);
        spawn_layout.addWidget(self.lineEdit_spawnZ, 2, 1)
        spawn_layout.addWidget(QLabel("Yaw:"), 2, 2);
        spawn_layout.addWidget(self.lineEdit_spawnYaw, 2, 3)
        spawn_layout.addWidget(self.pushButton_spawnCar, 3, 0, 1, 2)
        spawn_layout.addWidget(self.pushButton_spawnCarPygame, 3, 2, 1, 2)
        spawn_tab.setLayout(spawn_layout)

        # --- Tab 3: 移动车辆 ---
        move_tab = QWidget()
        move_layout = QGridLayout(move_tab)
        self.pushButton_setCarPose = QPushButton()
        self.pushButton_setCarPose.setObjectName("setCarPoseButton")
        self.lineEdit_moveX = QLineEdit();
        self.lineEdit_moveY = QLineEdit()
        self.lineEdit_moveZ = QLineEdit();
        self.lineEdit_moveYaw = QLineEdit()
        move_layout.addWidget(QLabel("X:"), 0, 0);
        move_layout.addWidget(self.lineEdit_moveX, 0, 1)
        move_layout.addWidget(QLabel("Y:"), 0, 2);
        move_layout.addWidget(self.lineEdit_moveY, 0, 3)
        move_layout.addWidget(QLabel("Z:"), 1, 0);
        move_layout.addWidget(self.lineEdit_moveZ, 1, 1)
        move_layout.addWidget(QLabel("Yaw:"), 1, 2);
        move_layout.addWidget(self.lineEdit_moveYaw, 1, 3)
        move_layout.addWidget(self.pushButton_setCarPose, 2, 0, 1, 4)
        move_tab.setLayout(move_layout)

        # --- Tab 4: 观察者控制 ---
        spectator_tab = QWidget()
        spectator_layout = QGridLayout(spectator_tab)
        self.pushButton_setSpectatorPose_tocar = QPushButton()
        self.pushButton_setSpectatorPose_tocar.setObjectName("spectatorToCarButtonSpecial")
        self.pushButton_SpectatorFollower_easy = QPushButton()
        self.pushButton_SpectatorFollower_easy.setObjectName("followEasyButtonSpecial")
        self.pushButton_SpectatorFollower_pro = QPushButton()
        self.pushButton_SpectatorFollower_pro.setObjectName("followProButtonSpecial")
        self.pushButton_StopSpectatorFollower = QPushButton()
        self.pushButton_StopSpectatorFollower.setObjectName("stopFollowButtonSpecial")

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
        self.pushButton_setSpectatorPose.setObjectName("setSpectatorPoseButtonSpecial")
        self.lineEdit_spectatorX = QLineEdit();
        self.lineEdit_spectatorY = QLineEdit()
        self.lineEdit_spectatorZ = QLineEdit();
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
        spectator_tab.setLayout(spectator_layout)

        tab_widget.addTab(world_tab, "世界")
        tab_widget.addTab(spawn_tab, "生成")
        tab_widget.addTab(move_tab, "移动")
        tab_widget.addTab(spectator_tab, "观察者")

        main_layout.addWidget(tab_widget)
        parent_layout.addWidget(main_group)

    def setup_menubar_statusbar(self, MainWindow):
        self.statusbar = QtWidgets.QStatusBar(MainWindow)
        MainWindow.setStatusBar(self.statusbar)
        self.menubar = QtWidgets.QMenuBar(MainWindow)
        self.menubar.setGeometry(QtCore.QRect(0, 0, 1000, 26))
        self.menuCARLA = QtWidgets.QMenu(self.menubar)
        self.menubar.addAction(self.menuCARLA.menuAction())
        MainWindow.setMenuBar(self.menubar)

    def apply_stylesheet(self, app_window):
        # --- Nord Light Theme Palette ---
        NORD_PRIMARY = "#81A1C1"  # Calm Blue
        NORD_PRIMARY_HOVER = "#88C0D0"  # Lighter Blue for hover
        NORD_DANGER = "#BF616A"  # Muted Red
        NORD_DANGER_HOVER = "#d08770"  # Orange-ish Red for hover
        BG_WINDOW = "#ECEFF4"  # Light cool grey
        BG_PANEL = "#FFFFFF"  # White
        BORDER = "#D8DEE9"  # Lighter grey border
        TEXT_PRIMARY = "#2E3440"  # Dark slate grey
        TEXT_SECONDARY = "#4C566A"  # Lighter slate grey

        app_window.setStyleSheet(f"""
            QWidget {{
                background-color: transparent;
                color: {TEXT_PRIMARY};
                font-family: "Segoe UI", "Microsoft YaHei UI", sans-serif;
                font-size: 13px;
            }}
            QMainWindow {{
                background: {BG_WINDOW};
            }}
            QGroupBox {{
                background: {BG_PANEL};
                border: 1px solid {BORDER};
                border-radius: 6px; 
                margin-top: 10px;
                padding: 10px;
            }}
            QGroupBox::title {{
                subcontrol-origin: margin; subcontrol-position: top left;
                padding: 2px 8px; color: {TEXT_SECONDARY}; font-weight: 600;
            }}
            QLineEdit, QComboBox, QTextBrowser {{
                background: {BG_PANEL};
                border: 1px solid {BORDER};
                border-radius: 4px; padding: 6px 8px;
                color: {TEXT_PRIMARY};
            }}
            QTextBrowser {{
                max-height: 200px;
            }}
            QLineEdit:focus, QComboBox:focus {{ border: 1px solid {NORD_PRIMARY}; }}
            QComboBox::drop-down {{
                border-left: 1px solid {BORDER};
            }}
            QComboBox QAbstractItemView {{
                background-color: {BG_PANEL};
                border: 1px solid {BORDER};
                selection-background-color: {NORD_PRIMARY};
                min-height: 150px;
            }}
            QPushButton {{
                border: 1px solid {BORDER}; border-radius: 4px;
                padding: 6px 12px; background: #E5E9F0;
                font-weight: 500;
            }}
            QPushButton:hover {{ background: #D8DEE9; }}
            QPushButton:pressed {{ background: #C8CDD5; }}

            /* --- TabWidget Styles --- */
            QTabWidget::pane {{
                border: 1px solid {BORDER};
                background: {BG_PANEL};
            }}
            QTabBar::tab {{
                background: {BG_WINDOW};
                border: 1px solid {BORDER};
                border-bottom: none;
                padding: 8px 16px;
                font-weight: 600;
                color: {TEXT_SECONDARY};
            }}
            QTabBar::tab:selected {{
                background: {BG_PANEL};
                color: {TEXT_PRIMARY};
            }}
            QTabBar::tab:!selected:hover {{
                background: #E5E9F0;
                color: {TEXT_PRIMARY};
            }}

            #startCarlaButton, #connectCarlaButton, #spawnCarButton, #setCarPoseButton,
            #connectVehicleButton,
            #spectatorToCarButtonSpecial, #followEasyButtonSpecial, #followProButtonSpecial,
            #setSpectatorPoseButtonSpecial, #renderButtonSpecial, #hud2dButtonSpecial, #showSpeedButtonSpecial
            {{
                background-color: {NORD_PRIMARY};
                color: white; border: none; font-weight: bold;
            }}
            #startCarlaButton:hover, #connectCarlaButton:hover, #spawnCarButton:hover, #setCarPoseButton:hover,
            #connectVehicleButton:hover,
            #spectatorToCarButtonSpecial:hover, #followEasyButtonSpecial:hover, #followProButtonSpecial:hover,
            #setSpectatorPoseButtonSpecial:hover, #renderButtonSpecial:hover, #hud2dButtonSpecial:hover, #showSpeedButtonSpecial:hover
             {{
                background-color: {NORD_PRIMARY_HOVER};
            }}

            #closeCarlaButton, #clearAllActorButton, #clearActorButton,
            #stopFollowButtonSpecial, #noRenderButtonSpecial, #hideSpeedButtonSpecial
            {{
                background-color: {NORD_DANGER};
                color: white; border: none; font-weight: bold;
            }}
            #closeCarlaButton:hover, #clearAllActorButton:hover, #clearActorButton:hover,
            #stopFollowButtonSpecial:hover, #noRenderButtonSpecial:hover, #hideSpeedButtonSpecial:hover
            {{
                background-color: {NORD_DANGER_HOVER};
            }}

            #refreshCarsButton {{
                background-color: transparent; border: none;
            }}
            #refreshCarsButton:hover {{
                color: {NORD_PRIMARY};
            }}

            QFrame[frameShape="4"] {{ border: none; background: {BORDER}; max-height: 1px; }}
            QStatusBar {{ background: {BG_PANEL}; border-top: 1px solid {BORDER}; }}
            QLabel {{ color: {TEXT_SECONDARY}; }}
            QLabel[text="选择车辆:"], QLabel[text="场景中全部车辆:"] {{
                 color: {TEXT_PRIMARY}; font-weight: bold;
            }}
        """)

    def retranslateUi(self, MainWindow):
        _translate = QtCore.QCoreApplication.translate
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
        # 移除此处的内联样式，让其由主样式表控制
        # self.label_current_car_info.setStyleSheet(...)

        self.comboBox_quality.addItems(["Low", "Epic"])
        self.rendering_mode.addItems(["正常", "离屏渲染"])

        self.lineEdit_IP.setText("localhost")
        self.lineEdit_port.setText("2000")
        self.textBrowser_connectState.setHtml("<p>未连接</p>")

        maps = ["gaoshu3800"] + [f"Town{i:02}" for i in range(1, 13)]
        self.comboBox_map.addItems(maps)

        weathers = [
            "晴朗 正午", "多云 正午", "湿润 正午", "湿润多云 正午",
            "小雨 正午", "中雨 正午", "大雨 正午", "晴朗 日出",
            "多云 日出", "湿润 日出", "小雨 日出", "中雨 日出", "大雨 日出"
        ]
        self.comboBox_weather.addItems(weathers)

        self.lineEdit_spawnname.setText("ego_car")
        self.lineEdit_spawnX.setText("-1930");
        self.lineEdit_spawnY.setText("48.25")
        self.lineEdit_spawnZ.setText("0.3");
        self.lineEdit_spawnYaw.setText("0")
        self.lineEdit_moveX.setText("-1930");
        self.lineEdit_moveY.setText("48.25")
        self.lineEdit_moveZ.setText("0.3");
        self.lineEdit_moveYaw.setText("0")
        self.lineEdit_spectatorX.setText("0");
        self.lineEdit_spectatorY.setText("0")
        self.lineEdit_spectatorZ.setText("5");
        self.lineEdit_spectatorYaw.setText("0")

        self.textBrowser_carState.setHtml("<p>未连接</p>")
        self.menuCARLA.setTitle(_translate("MainWindow", "CARLA启动"))


if __name__ == "__main__":
    import sys

    app = QtWidgets.QApplication(sys.argv)
    MainWindow = QtWidgets.QMainWindow()
    ui = Ui_MainWindow()
    ui.setupUi(MainWindow)
    MainWindow.show()
    sys.exit(app.exec_())

