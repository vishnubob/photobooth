import time
from PIL import Image

from .. import bus
from .. chromakey import ChromaKey
from .. imgops import resize_and_crop

class PhotolabService(bus.Service):
    @bus.proxy
    def process(self, request):
        fn_source = request["fn_source"]
        fn_target = request["fn_target"]
        img_source = Image.open(fn_source)
        steps = request["steps"]
        for step in steps:
            if step == "resize":
                size = request["resize"]["size"]
                img_source = resize_and_crop(img_source, size)
            elif step == "chromakey":
                fn_backdrop = request["chromakey"]["fn_backdrop"]
                img_backdrop = Image.open(fn_backdrop)
                if img_backdrop.size != img_source.size:
                    img_backdrop = resize_and_crop(img_backdrop, img_source.size)
                ck = ChromaKey()
                img_source = ck(img_source, img_backdrop)
            else:
                raise ValueError("unknown step '%s' % step")
        img_source.save(fn_target)

    def run(self):
        self.running = True
        while self.running:
            time.sleep(1)

def run(**kw):
    service = PhotolabService(serve=True, **kw)
    service.run()
