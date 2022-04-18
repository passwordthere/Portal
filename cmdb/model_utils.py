import secrets


def hv_id_prefix():
    return 'hv{}'.format(secrets.randbits(26))


def vm_id_prefix():
    return 'vm{}'.format(secrets.randbits(26))
