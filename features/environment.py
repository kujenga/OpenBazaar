from test_util import remove_settings

def before_all(context):
    # -- SET LOG LEVEL: behave --logging-level=ERROR ...
    # on behave command-line or in "behave.ini".
    context.config.setup_logging()

def after_scenario(context, scenario):
    if hasattr(context, 'proc'):
        for i, proc in enumerate(context.proc):
            proc.terminate()
            proc.join()
            remove_settings(i)
