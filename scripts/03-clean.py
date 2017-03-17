from json import load, dump
from os.path import join

from pathlib import Path

from shutil import rmtree

from os import remove

from config import DC_DIR
from util import DC_REPOS_DIR


def get_relevant_repos(oclas):
    relevant_repos = set()
    for md5hash in oclas:
        for filepath in oclas[md5hash]:
            user, repo = Path(filepath).parts[:2]
            relevant_repos.add(user + '/' + repo)
    return relevant_repos


def clean(meta):
    relevant_repos = get_relevant_repos(meta['oclas'])
    for repo in meta['repos']:
        if repo not in relevant_repos:
            rmtree(join(DC_REPOS_DIR, repo))
            remove(join(DC_REPOS_DIR, repo + '.json'))
    users = set([repo.split('/')[0] for repo in meta['repos']])
    relevant_users = set([repo.split('/')[0] for repo in relevant_repos])
    for user in users:
        if user not in relevant_users:
            rmtree(join(DC_REPOS_DIR, user))
    meta['repos'] = {repo: meta['repos'][repo] for repo in meta['repos'] if repo in relevant_repos}
    return meta


def main():
    with open(join(DC_DIR, 'meta.json'), 'r+') as file:
        meta = load(file)
        meta = clean(meta)
        file.seek(0)
        dump(meta, file, indent=2)
        file.truncate()


main()
