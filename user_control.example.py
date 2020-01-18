def get_info_from_user_token(token):
    """ Retrive info for a given user_token.
    Used to determine whether the user is registered (`unique_id`).
    Return value will be written into `users` table after registration.

    :param token: user_token string
    :return: {'unique_id', 'name', 'remarks'} if found; None otherwise (will prevent the user from registering)
    """
    if token=='bad':
        return None # cannot register
    else: # can register
        return {
            'unique_id': '666', # this will determine if the user is already registered
            'name': '祖师爷',
            'remarks': '',
        }

def check_registration_code(regcode,userinfo):
    """ Check whether a user can register.

    :param regcode: registration code the user inputted
    :param userinfo: return value from `get_info_from_user_token` function
    :return: {'error': 'reject reason'} or {'error': None, 'remarks': '...', 'ring': int, 'splash_index': int or None for INITIAL_SPLASH_INDEX}
    """
    if regcode!='42' or userinfo['name']=='小龙虾':
        return {
            'error': '不允许注册',
        }
    else: # ok
        return {
            'error': None,
            'remarks': 'regcode is %r'%regcode,
            'ring': 3,
            'splash_index': None,
        }