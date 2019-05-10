import numpy as np
from PIL import Image
from sklearn import cluster

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
    def __init__(self, min_distance=None, max_distance=None, bins=127, key=None):
        self.min_distance = min_distance
        self.max_distance = max_distance
        self.bins = bins
        self.key = key
    
    def get_thresholds(self, distance):
        if self.min_distance != None and self.max_distance != None:
            return (self.min_distance, self.max_distance)
        km = cluster.KMeans(n_init=1, n_clusters=2)
        distance = distance.reshape((-1, 1))
        km.fit(distance)
        values = list(km.cluster_centers_.squeeze())
        sorted_values = sorted(values)
        argmin = values.index(sorted_values[0])
        argmax = values.index(sorted_values[1])
        min_idx = np.where(km.labels_ == argmin)
        max_idx = np.where(km.labels_ == argmax)
        min_cluster = distance[min_idx]
        max_cluster = distance[max_idx]
        min_distance = self.min_distance if self.min_distance is not None else np.max(min_cluster)
        max_distance = self.max_distance if self.max_distance is not None else np.min(max_cluster)
        return (min_distance, max_distance)

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
    
    def get_distance(self, img):
        cs = ColorSpace()
        cc_img = cs(img)[:,:,1:]
        key_shape = cc_img.shape[:-1] + (1,)
        cc_key = self.get_key(img)
        cc_key = np.tile(np.array(cc_key), key_shape)
        distance = np.linalg.norm(cc_img - cc_key, axis=2)
        return distance
       
    def get_mask(self, img):
        distance = self.get_distance(img)
        (min_distance, max_distance) = self.get_thresholds(distance)
        mask = np.ones(distance.shape)
        idx = np.where(distance < min_distance)
        mask[idx] = 0
        idx = np.where((distance >= min_distance) & (distance < max_distance))
        mask[idx] = (distance[idx] - min_distance) / (max_distance - min_distance)
        return mask
    
    def blend(self, front, back, mask):
        mask = np.expand_dims(mask, axis=2)
        img = front * mask + back * (1.0 - mask)
        img = np.round(img).astype("uint8")
        return Image.fromarray(img)

    def __call__(self, front, back):
        mask = self.get_mask(front)
        return self.blend(front, back, mask)

if __name__ == "__main__":
    import sys
    front = sys.argv[1]
    back = sys.argv[2]
    front = Image.open(front)
    back = Image.open(back)
    front = front.resize(back.size)
    ck = ChromaKey()
    blend = ck(front, back)
    blend.save("blend.jpg")

