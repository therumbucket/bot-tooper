"""Quick and dirty script to grab eve-sde sqlite dump from fuzzwork.co.uk"""
from __future__ import print_function
from __future__ import with_statement
import os
import requests
import bz2
import hashlib
import sys

if sys.version_info < (3, 0):
    reload(sys)
    sys.setdefaultencoding('utf8')

sde_url = "https://www.fuzzwork.co.uk/dump/sqlite-latest.sqlite.bz2"
sde_hash_url = sde_url + ".md5"


def md5_for_file(afile, blocksize=65536):
    buf = afile.read(blocksize)
    hasher = hashlib.md5()
    while len(buf) > 0:
        hasher.update(buf)
        buf = afile.read(blocksize)
    return hasher.hexdigest()


def download_file(url, destpath):
    local_filename = os.path.join(destpath, url.split('/')[-1])
    r = requests.get(url, stream=True)
    with open(local_filename, 'wb') as f:
        for chunk in r.iter_content(chunk_size=4086):
            if chunk:
                f.write(chunk)
                f.flush()
    return local_filename

if __name__ == "__main__":
    destpath = os.path.join(os.path.dirname(__file__), 'db')
    print("Downloading Eve SDE...")
    sde_path = download_file(sde_url, destpath)
    print("Verifying Eve SDE...")
    sde_md5_path = download_file(sde_hash_url, destpath)
    with open(sde_md5_path) as sde_md5_file:
        verification_hash = sde_md5_file.readline().split()[0]
    with open(sde_path, 'rb') as sde_file:
        sde_hash = md5_for_file(sde_file)
    if sde_hash == verification_hash:
        print("Verify OK.")
        print("Decompressing archive...")
        with bz2.BZ2File(sde_path) as archive:
            with open(os.path.join(destpath, 'sqlite-latest.sqlite'), 'wb') as destfile:
                data = archive.read()
                destfile.write(data)
        print("Done.")
    else:
        print("Verify FAIL. Stopping.")
