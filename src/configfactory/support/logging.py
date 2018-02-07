def debug_logging(logging_dict, handler=None):
    """
    Debug logging.
    """

    # Set default debug handler
    if handler is None:
        handler = 'console'

    if handler not in logging_dict['handlers']:
        logging_dict['handlers'][handler] = {
            'level': 'DEBUG',
            'class': 'logging.StreamHandler',
        }

    # Add debug handler to all loggers
    for logger in logging_dict['loggers'].values():
        logger['level'] = 'DEBUG'
        if 'handlers' in logger:
            logger['handlers'].append(handler)
