class Singleton(object):
    __instance = None

    def __new__(cls):
        if cls.__instance is None:
            instance = super().__new__(cls)
            cls.__instance = instance
            instance.init_instance()
        return cls.__instance
    
    def init_instance(self):
        pass

    @classmethod
    def reset_instance(cls):
        cls.__instance = None
