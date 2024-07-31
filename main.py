# main.py

import kivy
from kivy.app import App
from serial_monitor import SerialMonitor

kivy.require('2.0.0')

class SerialMonitorApp(App):
    def build(self):
        self.monitor = SerialMonitor()
        return self.monitor

    def on_stop(self):
        # Ensure the serial connection is closed when the app exits
        if self.monitor.serial_connection and self.monitor.serial_connection.is_open:
            self.monitor.disconnect_from_serial()

if __name__ == '__main__':
    SerialMonitorApp().run()
