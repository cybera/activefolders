import os
import json
import shutil


def join_and_verify(folder, *args):
    path = os.path.join(folder.path(), *args)
    path = os.path.realpath(path)
    # TODO: Verify path is below folder.path()
    return path


def create_folder(folder):
    os.mkdir(folder.path())


def delete_folder(folder):
    shutil.rmtree(folder.path())


def create_dir(folder, path):
    path = join_and_verify(folder, path)
    try:
        os.makedirs(path)
    except OSError:
        if os.path.isdir(path):
            pass
        else:
            raise


def put_file(folder, path, filename, data, offset):
    path = join_and_verify(folder, path, filename)
    with open(path, 'ab') as f:
        f.seek(offset)
        f.write(data.read())


def get_file(folder, path, callback):
    fullpath = join_and_verify(folder, path)
    if os.path.isdir(fullpath):
        return 201, json.dumps([f for f in os.listdir(fullpath)])
    return 200, callback(path, root=folder.path())


def copy(folder, src_path, dst_path):
    src_path = join_and_verify(folder, src_path)
    dst_path = join_and_verify(folder, dst_path)
    if os.path.isdir(src_path):
        shutil.copytree(src_path, dst_path)
    else:
        shutil.copy(src_path, dst_path)


def move(folder, src_path, dst_path):
    src_path = join_and_verify(folder, src_path)
    dst_path = join_and_verify(folder, dst_path)
    shutil.move(src_path, dst_path)


def delete(folder, path):
    path = join_and_verify(folder, path)
    if os.path.isdir(path):
        shutil.rmtree(path)
    else:
        os.remove(path)


def save_file(folder, upload):
    path = join_and_verify(folder, upload.filename)
    if os.path.exists(path):
        raise IOError("File exists!")
    else:
        upload.save(folder.path())
