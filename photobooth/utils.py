def enable_profiler():
    import cProfile as profile
    import atexit
    profiler = profile.Profile()
    profiler.enable()
    def save_profiler():
        profiler.dump_stats("photobooth.prof")
    atexit.register(save_profiler)

