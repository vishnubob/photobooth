class LightControl(object):
    def __init__(self):
        import paho.mqtt.client as mqtt
        self.client = mqtt.Client()
        self.client.connect("mqtt")

    def on(self):
        client.publish("home/switch/booth", "on")

    def off(self):
        client.publish("home/switch/booth", "off")
