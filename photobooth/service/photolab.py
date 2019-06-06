import time
from .. import bus
from .. chromakey import ChromaKey

class PhotolabService(bus.Service):
    @bus.proxy
    def process(self, request):
        print("processing", request)
        steps = request["steps"]
        for step in steps:
            if step == "chromakey":
                self.chromakey(request)
            else:
                raise ValueError("unknown step '%s' % step")

    def chromakey(self, request):
        print("chromakey!", request)
        ckreq = request["chromakey"]
        fn_image = ckreq["fn_image"]
        fn_background = ckreq["fn_background"]
        fn_blend = ckreq["fn_blend"]
        ck = ChromaKey()
        ck(fn_image, fn_background, fn_blend)

    def run(self):
        self.running = True
        while self.running:
            time.sleep(1)

def run(**kw):
    service = PhotolabService(serve=True, **kw)
    service.run()
