from gettext import gettext as _

from somewhere import ngettext

print(_('Hello, world!'))  # literal

print(_('User {user} logged in').format(user='arya'))  # .format

print(_(f'Welcome {name}'))  # f-string approx

print(ngettext('1 item', '{0} items', count))  # plural

print('Not extracted')