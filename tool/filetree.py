import json
import os
import shutil
import yaml

########################################################################
# 检查每个翻译项目文件夹是否正确的工具
# 比如直接在 slug 下放置了 lang 文件夹或 patchouli_books 文件夹
########################################################################


def readInfoFile(config):
    localRepo = config["local-repo"]
    infoFilePath = "{}/data/info.json".format(localRepo)
    with open(infoFilePath, "r", encoding="utf-8") as infoFile:
        return json.load(infoFile)


def handle(config):
    versionList = config["version"]
    localRepo = config["local-repo"]
    for version in versionList:
        fabricVersion = "{}-fabric".format(version)
        for file in os.listdir("{}/projects/{}/assets".format(localRepo, version)):
            checkFolder(localRepo, version, file)
        for file in os.listdir("{}/projects/{}/assets".format(localRepo, fabricVersion)):
            checkFolder(localRepo, fabricVersion, file)


def checkFolder(localRepo, fabricVersion, file):
    path = "{}/projects/{}/assets/{}".format(localRepo, fabricVersion, file)
    if os.path.isdir(path):
        if "lang" in os.listdir(path):
            if len(os.listdir(path)) == 1:
                print(path)
                shutil.rmtree(path)
            else:
                print(path)
                shutil.rmtree("{}/lang".format(path))
        if "patchouli_books" in os.listdir(path):
            print(path)
    else:
        return True


if __name__ == "__main__":
    with open("./config.yml", "r", encoding="utf-8") as configFile:
        config = yaml.load(configFile)
    handle(config)
