from PIL import Image

rint = lambda val: int(round(val))

def crop(img, target_size=None):
    old_size = img.size
    left = (old_size[0] - target_size[0]) / 2
    top = (old_size[1] - target_size[1]) / 2
    right = old_size[0] - left
    bottom = old_size[1] - top
    rect = [rint(x) for x in (left, top, right, bottom)]
    crop = img.crop(rect)
    return crop

def resize(img, target_size=None, scale=None, resample=Image.LANCZOS):
    img_size = img.size
    if target_size == None:
        assert 1 >= scale >= 0
        target_size = [
            rint(img_size[0] * scale),
            rint(img_size[1] * scale)
        ]
    ratio = max(target_size[0] / img_size[0], target_size[1] / img_size[1])
    new_size = [
        int(round(img_size[0] * ratio)),
        int(round(img_size[1] * ratio))
    ]
    return img.resize(new_size, resample)

def resize_and_crop(img, target_size=None, scale=None, resample=Image.LANCZOS):
    img = resize(img, target_size, scale, resample)
    if (img.size != target_size):
        img = crop(img, target_size)
    return img
