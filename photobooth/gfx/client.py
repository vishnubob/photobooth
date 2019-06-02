from .. import bus

def display_text(text):
    bus.publish("display_text", text)

def display_image(fn_img):
    bus.publish("display_image", fn_img)
