class Singleton(object):
    __instance = None

    def __new__(cls):
        if cls.__instance is None:
            instance = super().__new__(cls)
            cls.__instance = instance
        return cls.__instance
