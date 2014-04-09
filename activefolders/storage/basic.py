import os
import shutil


def join_and_verify(folder, *args):
    path = os.path.join(folder.path(), *args)
    path = os.path.realpath(path)
    # TODO: Verify path is below folder.path()
    return path


def create_folder(folder):
    os.mkdir(folder.path())


def create_dir(folder, path):
    path = join_and_verify(folder, path)
    os.mkdir(path)


def copy(folder, src_path, dst_path):
    src_path = join_and_verify(folder, src_path)
    dst_path = join_and_verify(folder, dst_path)
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
