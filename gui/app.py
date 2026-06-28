import sys
from PySide6.QtWidgets import QApplication
from .event_bridge import EventBridge
from .main_window import MainWindow

class BackendController:
    """简单的后端接口封装，负责 start/pause/stop"""
    def __init__(self, application):
        self.app = application
        self.is_running = False

    def start(self):
        if not self.is_running:
            self.app.start()   # 假设是非阻塞启动（开启线程）
            self.is_running = True

    def pause(self):
        # 暂停录音，若支持
        pass

    def stop(self):
        self.app.stop()
        self.is_running = False

def start_gui(config, application):
    """application 是后端的 Application 实例"""
    app = QApplication(sys.argv)
    # 共享 EventBus
    event_bus = application.event_bus
    bridge = EventBridge(event_bus)
    controller = BackendController(application)
    window = MainWindow(config, bridge, controller)
    window.show()
    # 自动开始录音（可根据需要注释掉）
    controller.start()
    sys.exit(app.exec())