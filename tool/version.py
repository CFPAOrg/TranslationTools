import json
import os
import yaml
################################################
# 用来检查模组语言文件所处的 project 是否正确
# 比如 slug 为 xxx 的模组只有 1.16 fabric 版
# 但却错误放置在了 1.18 forge 文件夹下
################################################

def readInfoFile(config):
    localRepo = config["local-repo"]
    infoFilePath = "{}/data/info.json".format(localRepo)
    with open(infoFilePath, "r", encoding="utf-8") as infoFile:
        return json.load(infoFile)


def handle(config):
    versionList = config["version"]
    localRepo = config["local-repo"]
    info = readInfoFile(config)
    for version in versionList:
        fabricVersion = "{}-fabric".format(version)
        for file in os.listdir("{}/projects/{}/assets".format(localRepo, version)):
            if not checkVersion(version, file, info):
                print(file, version)
        for file in os.listdir("{}/projects/{}/assets".format(localRepo, fabricVersion)):
            if not checkVersion(fabricVersion, file, info):
                print(file, fabricVersion)


def checkVersion(version, file, info):
    if file in info.keys():
        infoItem = info[file]
        latestFiles = infoItem["latestFiles"]
        return version in latestFiles.keys()
    return True


if __name__ == "__main__":
    with open("./config.yml", "r", encoding="utf-8") as configFile:
        config = yaml.load(configFile)
    handle(config)
