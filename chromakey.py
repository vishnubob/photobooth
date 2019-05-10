from PIL import Image as Image, ImageColor, ImageFilter
import numpy as np

class ColorSpace(object):
    ColorSpaces = {
        "rgb": {
            "ycc": {
                "constants": np.array([0, 128, 128]),
                "factors": np.array([
                    [0.299, 0.587, 0.114],
                    [-0.168736, -0.331264, 0.5],
                    [0.5, -0.418688, -0.081312]
                ]).T,
            }
        }
    }

    def __init__(self, in_space="rgb", out_space="ycc"):
        self.in_space = in_space
        self.out_space = out_space
        func_name = "%s_to_%s" % (self.in_space, self.out_space)
        self.func = getattr(self, func_name)

    def __call__(self, *args, **kw):
        return self.func(*args, **kw)

    def rgb_to_ycc(self, rgb):
        const = self.ColorSpaces["rgb"]["ycc"]["constants"]
        factors = self.ColorSpaces["rgb"]["ycc"]["factors"]
        res = const + np.dot(rgb, factors)
        return np.round(res).astype(np.int32)

class ChromaKey(object):
    def __init__(self, min_distance=10, max_distance=50, bins=127, key=None):
        self.min_distance = 10
        self.max_distance = 50
        self.bins = bins
        self.key = key

    def get_key(self, img):
        cs = ColorSpace()
        img_ycc = cs(img)
        # Cr
        cr = img_ycc[:,:,1].flatten()
        (cr_freq, cr_val) = np.histogram(cr, bins=self.bins)
        cr_key = cr_val[np.argmax(cr_freq)]
        # Cb
        cb = img_ycc[:,:,2].flatten()
        (cb_freq, cb_val) = np.histogram(cb, bins=self.bins)
        cb_key = cb_val[np.argmax(cb_freq)]
        return (cr_key, cb_key)

    def get_mask(self, img):
        cs = ColorSpace()
        cc_img = cs(img)[:,:,1:]
        key_shape = cc_img.shape[:-1] + (1,)
        cc_key = self.key
        if cc_key == None:
            cc_key = self.get_key(img)
        cc_key = np.tile(np.array(cc_key), key_shape)
        distance = np.sqrt(np.sum((cc_key - cc_img) ** 2, axis=2))
        mask = np.ones(distance.shape)
        idx = np.where(distance < self.min_distance)
        mask[idx] = 0
        distance[idx] = self.max_distance
        idx = np.where((distance >= self.min_distance) & (distance < self.max_distance))
        mask[idx] = (distance[idx] - self.min_distance) / (self.max_distance - self.min_distance)
        return mask

    def blend(self, front, back, mask):
        mask = np.expand_dims(mask, axis=2)
        img = front * mask + back * (1.0 - mask)
        img = np.round(img).astype("uint8")
        return Image.fromarray(img)

    def __call__(self, front, back):
        mask = self.get_mask(front)
        return self.blend(front, back, mask)
