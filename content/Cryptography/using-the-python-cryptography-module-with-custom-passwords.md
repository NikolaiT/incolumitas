Title: Using the Python cryptography module with custom passwords
Date: 2014-10-19 11:50
Author: Nikolai Tschacher
Category: Cryptography
Tags: Cryptography, Programming, Uncategorized
Slug: using-the-python-cryptography-module-with-custom-passwords
Status: published

Hey all

I recently discovered a [quite cute crypto
module](https://cryptography.io/en/latest/ "cryptography") for Python.
It is divided in two logical security layers. The first
([Fernet](https://cryptography.io/en/latest/fernet/ "Fernet")) can be
used by cryptology unaware programmers in a way that makes it unlikely
to introduce any security flaws. The seconds layer (called
[Hazmat](https://cryptography.io/en/latest/hazmat/primitives/ "hazmat"))
allows access to all kinds of cryptographical primitives, such as HMACS
and asymmetric encryption functions.

### The Problem

Normally you don't want to use primitives, because it is tricky to do
correct (event for advanced programmers). But unfortunately the secure
and simple API functionality Fernet:

    :::python
    >>> from cryptography.fernet import Fernet
    >>> key = Fernet.generate_key()
    >>> f = Fernet(key)
    >>> token = f.encrypt(b"my deep dark secret")
    >>> token
    '...'
    >>> f.decrypt(token)
    'my deep dark secret

suffers from the huge inconvenience that you need to store (or
imagine:remember!) a 32 byte key in order to decrypt the tokens that
Fernet outputs.  
It would be much more convenient to just pass a password to Fernet
which in turn makes a 32 byte, Base 64 encoded encryption token out of
it. Of course your own  
password is much less secure then 32 bytes from `os.urandom(32)`, but
at least it is somehow usable.

So I came up with this little extra code to use Fernet with a custom
password:

    :::python
    import base64
    from cryptography.fernet import Fernet
    from cryptography.hazmat.primitives import hashes
    from cryptography.hazmat.backends import default_backend

    def get_key(password):

        digest = hashes.Hash(hashes.SHA256(), backend=default_backend())
        digest.update(password)
        return base64.urlsafe_b64encode(digest.finalize())

    def encrypt(password, token):
        f = Fernet(get_key(key))
        return f.encrypt(bytes(token))

    def decrypt(password, token):
        f = Fernet(get_key(password))
        return f.decrypt(bytes(token))

I hope it helps anybody!
