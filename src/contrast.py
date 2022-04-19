import json
import logging


def readOldInfoFile(config):
    localRepo = config["local-repo"]
    infoFilePath = "{}/data/info.json".format(localRepo)
    with open(infoFilePath, "r", encoding="utf-8") as infoFile:
        return json.load(infoFile)


def checkFiles(latestFilesOld, latestFilesNew):
    latestFiles = {}
    for version in latestFilesNew.keys():
        if version in latestFilesOld.keys():
            fileIdOld = latestFilesOld[version]
            fileIdNew = latestFilesNew[version]
            if fileIdOld != fileIdNew:
                latestFiles[version] = fileIdNew
        else:
            latestFiles[version] = latestFilesNew[version]
    return latestFiles


def setup(config, newInfo):
    oldInfo = readOldInfoFile(config)
    contrastInfo = {}
    for slug in newInfo.keys():
        newItem = newInfo[slug]
        if slug in oldInfo.keys():
            oldItem = oldInfo[slug]
            latestFilesOld = oldItem["latestFiles"]
            latestFilesNew = newItem["latestFiles"]
            latestFiles = checkFiles(latestFilesOld, latestFilesNew)
            if latestFiles:
                contrastInfo[slug] = {
                    "downloadCount": newItem["downloadCount"],
                    "id": newItem["id"],
                    "latestFiles": latestFiles,
                    "name": newItem["name"]
                }
        else:
            contrastInfo[slug] = {
                "downloadCount": newItem["downloadCount"],
                "id": newItem["id"],
                "latestFiles": newItem["latestFiles"],
                "name": newItem["name"]
            }
    logging.info("需要更新 %d 个模组", len(contrastInfo.keys()))
    return contrastInfo
