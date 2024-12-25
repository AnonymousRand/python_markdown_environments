def init_extension_with_configs(obj, **kwargs):
    try:
        super(obj.__class__, obj).__init__(**kwargs)
    except KeyError as e:
        raise KeyError(f"{e} (did you pass in an invalid config key to {obj.__class__.__name__}.__init__()?)")
