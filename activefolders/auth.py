import activefolders.db as db
from datetime import datetime, timedelta


def populate_accounts(users):
    now = datetime.now()
    valid = now + timedelta(weeks=72)
    print("Active accounts:")
    for name, data in users:
        if not db.User.select(db.User.name == name).exists():
            user = db.User.create(name=name, reg_date=now)
        if not db.Token.select(db.Token.data == data).exists():
            token = db.Token.create(user=user, data=data, valid_from=now, valid_to=valid)
    for token in db.Token.select():
        print("\t", token.user.name, token.data)


def check(token, _):
    # We check only for token with the assumption they they are distributed in a secure manner
    try:
        t = db.Token.get(db.Token.data == token)
    except db.Token.DoesNotExist:
        return False

    if t.valid_from < datetime.now() < t.valid_to:
        return True

    t.delete()
    return False
