from json import dump
from multiprocessing.pool import Pool
from os import remove, makedirs
from os.path import join, dirname
from pathlib import Path
from re import search, IGNORECASE
from zipfile import ZipFile

from requests import get
from tqdm import tqdm

from config import DC_DIR, GITHUB_TOKEN
from util import DC_REPOS_DIR

headers = {'Authorization': 'token ' + GITHUB_TOKEN} if GITHUB_TOKEN else {}


def get_repo_zip_url(repo):
    return 'https://api.github.com/repos/' + repo + '/zipball'


def download_zip_file(url, path):
    r = get(url, stream=True, headers=headers)
    with open(path, 'wb') as f:
        for chunk in r.iter_content(chunk_size=1024):
            if chunk:
                f.write(chunk)


def get_json_file(url):
    response = get(url, allow_redirects=False, headers=headers)
    if response.status_code == 200:
        return response.json()
    else:
        print('error (' + str(response.status_code) + ') downloading ' + url)


def get_repo_zip_path(repo):
    return join(DC_DIR, repo.replace('/', '-') + '.zip')


def download_repo_zip(repo):
    url = get_repo_zip_url(repo)
    download_zip_file(url, get_repo_zip_path(repo))


def get_repo_path(repo):
    return join(DC_REPOS_DIR, repo)


def extract_repo_zip(repo):
    commit_hash = None
    with ZipFile(get_repo_zip_path(repo), 'r') as zipfile:
        for member in zipfile.infolist():
            commit_hash = Path(member.filename).parts[0].split('-')[-1]
            if search(r'.*\.(ecore|ocl)$', member.filename, IGNORECASE):
                path = join(get_repo_path(repo), *Path(member.filename).parts[1:])
                makedirs(dirname(path), exist_ok=True)
                with open(path, 'wb') as file:
                    file.write(zipfile.read(member))
    return commit_hash


def delete_repo_zip(repo):
    remove(get_repo_zip_path(repo))


def get_repo_meta_url(repo):
    return 'https://api.github.com/repos/' + repo


def get_repo_meta_path(repo):
    return get_repo_path(repo) + '.json'


def download_repo_meta(repo):
    url = get_repo_meta_url(repo)
    with open(get_repo_meta_path(repo), 'w') as file:
        dump(get_json_file(url), file, indent=2)


def process_repo(repo):
    download_repo_zip(repo)
    commit_hash = extract_repo_zip(repo)
    delete_repo_zip(repo)
    download_repo_meta(repo)
    return repo, commit_hash


def get_full_hash(repo, commit_hash):
    url = 'https://api.github.com/repos/' + repo + '/commits/' + commit_hash
    response = get(url, allow_redirects=False, headers={
        **headers,
        'Accept': 'application/vnd.github.sha'
    })
    if response.status_code == 200:
        return response.text
    else:
        print('error (' + str(response.status_code) + ') downloading ' + url)


def main():
    commit_hashes = {}
    with Pool(50) as pool, open('repos.txt') as file:
        repos = [line.rstrip('\n') for line in file][1:2]
        for repo, commit_hash in tqdm(pool.imap_unordered(process_repo, repos), total=len(repos), disable=False):
            full_hash = get_full_hash(repo, commit_hash)
            commit_hashes[repo] = full_hash
    with open(join(DC_DIR, 'meta.json'), 'w') as file:
        dump({'repos': commit_hashes}, file, indent=2)


main()
