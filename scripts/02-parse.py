from hashlib import md5
from json import load, dump
from multiprocessing.pool import Pool
from os import walk, remove, makedirs
from re import search, IGNORECASE

from os.path import join, relpath, dirname, basename
from subprocess import PIPE, Popen

from tqdm import tqdm

from config import JAR_PATH, DC_DIR
from util import DC_OCLAS_DIR, DC_REPOS_DIR


def run_jar(arguments, cwd=None):
    cmd = ['java', '-jar', JAR_PATH] + arguments
    process = Popen(cmd, stdout=PIPE, stderr=PIPE, cwd=cwd)
    out, _ = process.communicate()
    return out.decode()


def parse_file(fileinfo):
    md5hash, files = fileinfo
    filepath = files[0]
    filename = md5hash + '.oclas'
    result = run_jar(['save', basename(filepath), join(DC_OCLAS_DIR, filename)], dirname(filepath))
    try:
        ocl_count = int(result)
        if ocl_count > 0:
            return fileinfo
        else:
            remove(join(DC_OCLAS_DIR, filename))
    except ValueError:
        try:
            remove(join(DC_OCLAS_DIR, filename))
        except OSError:
            pass


def main():
    ocl_files = {}
    for root, subdir, files in walk(DC_REPOS_DIR):
        for filename in files:
            if search(r'.*\.(ecore|ocl)$', filename, IGNORECASE):
                filepath = join(root, filename)
                md5hash = md5(open(filepath, 'rb').read()).hexdigest()
                if md5hash not in ocl_files:
                    ocl_files[md5hash] = []
                ocl_files[md5hash].append(filepath)

    makedirs(DC_OCLAS_DIR, exist_ok=True)

    oclas = {}
    with Pool() as pool:
        for fileinfo in tqdm(pool.imap_unordered(parse_file, ocl_files.items()), total=len(ocl_files), disable=False):
            if fileinfo:
                md5hash, files = fileinfo
                oclas[md5hash] = [relpath(file, DC_REPOS_DIR) for file in files]
    with open(join(DC_DIR, 'meta.json'), 'r+') as file:
        meta = load(file)
        meta['oclas'] = oclas
        file.seek(0)
        dump(meta, file, indent=2)
        file.truncate()


main()
