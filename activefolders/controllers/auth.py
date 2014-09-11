import activefolders.db as db
import hashlib
import activefolders.conf as conf
from datetime import datetime, timedelta


def init():
    now, valid = datetime.now(), datetime.max

    try:
        user = db.User.get(db.User.name == 'root')
    except db.User.DoesNotExist:
        user = db.User.create(name='root', reg_date=now)

    try:
        token = db.Token.get(db.Token.data == conf.settings['dtnd']['root_secret'])
    except db.Token.DoesNotExist:
        token = db.Token.create(user=user,
                                data=conf.settings['dtnd']['root_secret'],
                                valid_from=now,
                                valid_to=valid)

    print("Root token:\t", token.data) # Might want to hide it in production


def check(token, _):
    # Check for token only. This works only if token distribution is secure
    try:
        t = db.Token.get(db.Token.data == token)
    except db.Token.DoesNotExist:
        return False
    # Time validation
    if t.valid_from < datetime.now() < t.valid_to:
        return True
    # Delete outdated tokens
    t.delete()
    return False
