from django.test import TestCase, override_settings

from configfactory.utils import security


class SecurityUtilsTestCase(TestCase):

    def test_cleanse_hidden_match(self):

        actual = security.cleanse(
            data={
                'name': 'test',
                'password': 'secret password',
                'connection': {
                    'host': 'localhost',
                    'password': '123123'
                },
                'secret': {
                    'key': '123123',
                    'salt': 'qwerty'
                },
                'list': [1, 2, 3],
                'secret-list': [111, 222, 333]
            },
            hidden='password secret',
            substitute='***'
        )

        assert actual == {
            'name': 'test',
            'password': '***',
            'connection': {
                'host': 'localhost',
                'password': '***'
            },
            'secret': {
                'key': '***',
                'salt': '***'
            },
            'list': [1, 2, 3],
            'secret-list': ['***', '***', '***']
        }

    @override_settings(ENCRYPT_ENABLED=False)
    def test_disabled_encryptor(self):

        assert security.encrypt_data('TEST') == 'TEST'
        assert security.decrypt_data('TEST') == 'TEST'

    @override_settings(ENCRYPT_ENABLED=True)
    def test_enabled_encryptor(self):

        assert security.encrypt_data('TEST') != 'TEST'

    @override_settings(ENCRYPT_ENABLED=True, ENCRYPT_PREFIX='$$$:')
    def test_encrypt_dict(self):

        encrypted_dict = security.encrypt_dict({
            'user': 'admin',
            'pass': 'secret',
        }, secure_keys=['pass'])

        assert encrypted_dict['user'] == 'admin'
        assert security.is_encrypted(encrypted_dict['pass'])

        decrypted_dict = security.decrypt_dict(encrypted_dict, secure_keys=['pass'])

        assert decrypted_dict['user'] == 'admin'
        assert decrypted_dict['pass'] == 'secret'

    @override_settings(ENCRYPT_ENABLED=True, ENCRYPT_PREFIX='$$$:')
    def test_encrypt_dict_nested(self):

        encrypted_dict = security.encrypt_dict({
            'db': {
                'user': 'admin',
                'pass': 'secret',
            }
        }, secure_keys=['db.pass'])

        assert encrypted_dict['db']['user'] == 'admin'
        assert security.is_encrypted(encrypted_dict['db']['pass'])

        decrypted_dict = security.decrypt_dict(encrypted_dict, secure_keys=['db.pass'])

        assert decrypted_dict['db']['user'] == 'admin'
        assert decrypted_dict['db']['pass'] == 'secret'

    @override_settings(ENCRYPT_ENABLED=True, ENCRYPT_PREFIX='$$$:')
    def test_encrypt_dict_keep_type(self):

        encrypted_dict = security.encrypt_dict({
            'token': 123123123
        }, secure_keys=['token'])

        assert encrypted_dict['token']

        decrypted_dict = security.decrypt_dict(encrypted_dict, secure_keys=['token'])

        assert decrypted_dict['token'] == 123123123

    @override_settings(ENCRYPT_ENABLED=True, ENCRYPT_PREFIX='$$$:')
    def test_encrypt_dict_inner_list(self):

        encrypted_dict = security.encrypt_dict({
            'tokens': [1, 2, 3]
        }, secure_keys=['tokens'])

        assert security.is_encrypted(encrypted_dict['tokens'][0])
        assert security.is_encrypted(encrypted_dict['tokens'][1])
        assert security.is_encrypted(encrypted_dict['tokens'][2])

        decrypted_dict = security.decrypt_dict(encrypted_dict, secure_keys=['tokens'])

        assert decrypted_dict['tokens'] == [1, 2, 3]
