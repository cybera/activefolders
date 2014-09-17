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

    print("Root token:\t", token.data)  # Might want to hide it in production


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


def root_check(token, _):
    # Check for token only. This works only if token distribution is secure
    try:
        t = db.Token.get(db.Token.data == token, db.Token.user == user('root'))
    except db.Token.DoesNotExist:
        return False
    # Time validation
    if t.valid_from < datetime.now() < t.valid_to:
        return True
    # Delete outdated tokens
    t.delete()
    return False


def current_user_or_root(username, auth):
    token, _ = auth or (None, None)
    if root_check(token, _):
        return True

    try:
        db.Token.get(db.Token.data == token, db.Token.user == user(username))
    except db.Token.DoesNotExist:
        return False
    return True


def user(username):
    return db.User.get(db.User.name == username)


def get_user(username):
    user = db.User.select().where(db.User.name == username).dicts().get()
    return user.to_json()


def get_all_users():
    users = {"users": []}
    for user in db.User.select().dicts():
        users["users"].append(user)
    return users


def get_all_tokens(username):
    tokens = {"tokens": []}
    for token in db.Token.select().where(db.Token.user == user(username)).dicts():
        tokens["tokens"].append(token)
    return tokens


def get_token(username, token):
    token = db.Token.select().where(db.Token.user == user(username), db.Token.data == token).dicts().get()
    return token


def new_hash(string):
    now = str(datetime.now())
    dtn_name = conf.settings['dtnd']['name']
    h = hashlib.new('sha224')
    h.update(string.encode("utf-8"))
    h.update(now.encode("utf-8"))
    h.update(dtn_name.encode("utf-8"))
    return h.hexdigest()


def create_token(username):
    token = db.Token(
        user=user(username),
        data=new_hash(username),
        valid_from=datetime.now(),
        valid_to=datetime.now() + timedelta(weeks=72)
    )
    token.save()
    return token.to_json()


def delete_token(username, tokendata):
    q = db.Token.delete().where(db.Token.user == user(username), db.Token.data == tokendata)
    res = q.execute()
    return {"deleted": res}


def create_or_update_user(username):
    try:
        usr = user(username)
    except db.User.DoesNotExist:
        usr = db.User(name=username, reg_date=datetime.now())
        usr.save()
    return usr.to_json()


def delete_user(username):
    q = db.User.delete().where(db.User.name == username)
    res = q.execute()
    q = db.Token.delete().where(db.Token.user == user(username))
    q.execute()
    return {"deleted": res}
