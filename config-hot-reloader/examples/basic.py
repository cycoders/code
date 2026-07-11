from config_hot_reloader import ConfigReloader

reloader = ConfigReloader('config.yaml')
with reloader:
    print(reloader.current)