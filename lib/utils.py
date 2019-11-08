import os

import logging
logging.basicConfig(format='{levelname}: {message!s}', style='{',
                    level=logging.INFO)
logger = logging.getLogger()


def filename(path, isurl=False):
    if isurl:
        return path.split('/')
    else:
        return os.path.basename(path)


def download(url, dst=None, overwrite=False):
    """
    @param: url to download file
    @param: dst place to put the file
    @param: overwrite 'dst' if already there
    """
    import requests
    try:
        from tqdm import tqdm
    except:
        tqdm = None

    if dst is None or dst.strip() is '':
        dst = filename(url)
    elif os.path.isdir(dst):
        dst = os.path.join(dst, filename(url))

    file_size = int(requests.head(url).headers["Content-Length"])
    if os.path.exists(dst):
        if overwrite:
            os.remove(dst)
        else:
            first_byte = os.path.getsize(dst)
    else:
        first_byte = 0

    if first_byte >= file_size:
        msg = "File '{}', size '{}' bytes, was already there."
        logger.info(msg.format(dst, first_byte))
    else:
        header = {"Range": "bytes=%s-%s" % (first_byte, file_size)}
        if tqdm:
            pbar = tqdm(total=file_size, initial=first_byte,
                        unit='B', unit_scale=True, desc=dst)
        else:
            pbar = None
        req = requests.get(url, headers=header, stream=True)
        with(open(dst, 'ab')) as f:
            for chunk in req.iter_content(chunk_size=1024):
                if chunk:
                    f.write(chunk)
                    if pbar:
                        pbar.update(1024)
        if pbar:
            pbar.close()

        msg = "File named '{}', sized {} bytes, downloaded succesfully."
        logger.info(msg.format(dst, file_size))

    return dst
