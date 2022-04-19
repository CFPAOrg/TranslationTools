import os
from time import sleep
import zipfile
import requests
import wget
import re
import shutil
import threading
from tempfile import TemporaryDirectory


def getHeaders():
    return {
        'Content-Type': 'application/json',
        'Accept': 'application/json',
        'x-api-key': os.getenv('CURSE_FORGE_API_KEY')
    }


threadLock = threading.Lock()


def extractZip(filePath, extractPath, slug):
    file = zipfile.ZipFile(filePath, "r")
    for name in file.namelist():
        matchResult = re.match("^assets/(.*?)/lang/en_us.json$", name)
        if matchResult:
            namespace = matchResult.group(1)
            extractSlugPath = "{}/{}/{}/lang".format(
                extractPath, slug, namespace)
            if not os.path.exists(extractSlugPath):
                os.makedirs(extractSlugPath)
            with TemporaryDirectory() as tmpDir:
                file.extract(name, tmpDir)
                shutil.move("{}/assets/{}/lang/en_us.json".format(tmpDir, namespace),
                            extractSlugPath)


def downloadFile(slug, infoItem, downloadPath, extractRootPath):
    id = infoItem["id"]
    latestFiles = infoItem["latestFiles"]
    for version, fileId in latestFiles.items():
        url = "https://api.curseforge.com/v1/mods/{}/files/{}/download-url".format(
            id, fileId)
        r = requests.get(url, headers=getHeaders())
        downloadFile = wget.download(r.json()["data"], downloadPath)
        extractPath = "{}/{}/assets".format(extractRootPath, version)
        if not os.path.exists(extractPath):
            os.makedirs(extractPath)
        extractZip(downloadFile, extractPath, slug)


class DownloadMod(threading.Thread):
    def __init__(self, slug, infoItem, extractRootPath):
        threading.Thread.__init__(self)
        self.slug = slug
        self.infoItem = infoItem
        self.extractRootPath = extractRootPath

    def run(self):
        with TemporaryDirectory() as downloadPath:
            downloadFile(self.slug, self.infoItem,
                         downloadPath, self.extractRootPath)


def setup(config, downloadInfo):
    threadCount = config["download-thread-count"]
    sleepTime = config["download-sleep-time"]

    extractRootPath = "./projects"
    if not os.path.exists(extractRootPath):
        os.makedirs(extractRootPath)

    index = 0
    threads = []
    for slug, infoItem in downloadInfo.items():
        download = DownloadMod(slug, infoItem, extractRootPath)
        download.start()
        index = index+1
        threads.append(download)
        if index == threadCount:
            for t in threads:
                t.join()
            index = 0
            sleep(sleepTime)
    if index != 0:
        for t in threads:
            t.join()
