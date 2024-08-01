# main.py

import kivy
from kivy.app import App
from application_gui import Application

kivy.require('2.0.0')

class SerialMonitorApp(App):
    def build(self):
        self.monitor = Application()
        return self.monitor

    def on_stop(self):
        # Ensure the serial connection is closed when the app exits
        self.monitor.control.disconnect_from_serial()

if __name__ == '__main__':
    SerialMonitorApp().run()
