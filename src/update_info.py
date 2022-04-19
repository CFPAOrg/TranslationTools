import logging
import os
import json
import requests
import math

MINECRAFT_GAME_ID = 432
MC_MOD_SECTION_ID = 6
FORGE = 1
FABRIC = 4

NULL_ID = -1


def getHeaders():
    return {
        'Content-Type': 'application/json',
        'Accept': 'application/json',
        'x-api-key': os.getenv('CURSE_FORGE_API_KEY')
    }


def readInfoFile(config):
    localRepo = config["local-repo"]
    infoFilePath = "{}/data/info.json".format(localRepo)
    with open(infoFilePath, "r", encoding="utf-8") as infoFile:
        return json.load(infoFile)


def readEmptyFile(config):
    localRepo = config["local-repo"]
    emptyFilePath = "{}/data/empty.json".format(localRepo)
    with open(emptyFilePath, "r", encoding="utf-8") as emptyFile:
        return json.load(emptyFile)


def getAllSlugs(config):
    versionList = config["version"]
    localRepo = config["local-repo"]
    blackSlugList = config["black_list"]
    # 检索文件夹，获取所有需要检查的 slug
    slugs = set()
    for version in versionList:
        fabricVersion = "{}-fabric".format(version)
        for file in os.listdir("{}/projects/{}/assets".format(localRepo, version)):
            slugs.add(file)
        for file in os.listdir("{}/projects/{}/assets".format(localRepo, fabricVersion)):
            slugs.add(file)
    # 删除黑名单 slug
    for blackSlug in blackSlugList:
        if blackSlug in slugs:
            slugs.remove(blackSlug)
    # 返回排序好的列表
    logging.info("获取得到 %d 个模组 slug", len(slugs))
    return sorted(slugs)


def getIdFromInfo(slug, info):
    if slug in info.keys():
        return info[slug]["id"]
    else:
        return NULL_ID


def getIdFromSlug(slug):
    logging.info("检查 %s 的 curseforge id...", slug)
    r = requests.get('https://api.curseforge.com/v1/mods/search', params={
        'gameId': MINECRAFT_GAME_ID,
        "sectionId": MC_MOD_SECTION_ID,
        "slug": slug
    }, headers=getHeaders())
    result = r.json()
    if len(result["data"]) > 0:
        return result["data"][0]["id"]
    else:
        return NULL_ID


def getSlugIdMap(config):
    localRepo = config["local-repo"]
    info = readInfoFile(config)
    empty = readEmptyFile(config)

    # 获取 slug -> id 的映射，方便后续信息更新
    slugToId = {}
    for slug in getAllSlugs(config):
        # 那些不存在的 slug 就不需要查询了
        if slug in empty:
            pass
        else:
            id = getIdFromInfo(slug, info)
            if id == NULL_ID:
                id = getIdFromSlug(slug)
            if id == NULL_ID:
                empty.append(slug)
                with open("{}/data/empty.json".format(localRepo), "w", encoding="utf-8") as emptyFile:
                    json.dump(empty, emptyFile, indent=2,
                              sort_keys=True, ensure_ascii=False)
            if id != NULL_ID:
                slugToId[slug] = id
    logging.info("获取得到 %d 个模组 slug->id 映射表", len(slugToId.keys()))
    return slugToId


def getInfos(modIds, outputInfos, config):
    versionList = config["version"]
    logging.info("更新 %s 的模组信息...", json.dumps(modIds))
    r = requests.post('https://api.curseforge.com/v1/mods',
                      headers=getHeaders(), json={"modIds": modIds})
    result = r.json()
    for item in result["data"]:
        slug = item["slug"]
        # 获取基本信息
        outputInfos[slug] = {
            "id": item["id"],
            "name": item["name"],
            "downloadCount": math.floor(item["downloadCount"]),
        }
        # 获取最新的文件信息
        latestFilesIndexes = item["latestFilesIndexes"]
        latestFiles = {}
        for lastestFile in latestFilesIndexes:
            gameVersion = lastestFile["gameVersion"]
            # 遍历版本号，分析出各个版本 fabric 和 forge 模组
            for version in versionList:
                fabricVersion = "{}-fabric".format(version)
                if gameVersion.startswith(version):
                    modLoader = lastestFile["modLoader"]
                    if modLoader == FORGE and version not in latestFiles:
                        latestFiles[version] = lastestFile["fileId"]
                    if modLoader == FABRIC and fabricVersion not in latestFiles:
                        latestFiles[fabricVersion] = lastestFile["fileId"]
                    break
        # 存储最新文件信息
        outputInfos[slug]["latestFiles"] = latestFiles


def setup(config):
    outputInfos = {}
    slugToId = getSlugIdMap(config)

    modIds = []
    index = 0
    for slug in slugToId.keys():
        modIds.append(slugToId[slug])
        index = index+1
        if index == 50:
            getInfos(modIds, outputInfos, config)
            with open("./info.json", "w", encoding="utf-8") as infoFile:
                json.dump(outputInfos, infoFile, indent=2,
                          sort_keys=True, ensure_ascii=False)
            modIds.clear()
            index = 0

    if index != 0:
        getInfos(modIds, outputInfos, config)
        with open("./info.json", "w", encoding="utf-8") as infoFile:
            json.dump(outputInfos, infoFile, indent=2,
                      sort_keys=True, ensure_ascii=False)

    return outputInfos


if __name__ == "__main__":
    print(getHeaders())
