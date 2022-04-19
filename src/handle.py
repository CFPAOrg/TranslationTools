from collections import OrderedDict
import shutil
import json5
import json
import os
import yaml


def checkFile(folder, config):
    localRepo = config["local-repo"]
    for file in os.listdir(folder):
        filePath = "{}/{}".format(folder, file)
        if os.path.isfile(filePath):
            oldFilePath = "{}/{}".format(localRepo, filePath)
            if os.path.isfile(oldFilePath) and oldFilePath.endswith("en_us.json"):
                updateLanguageFile(filePath, oldFilePath)
        if os.path.isdir(filePath):
            checkFile(filePath, config)


def readLanguageFile(filePath):
    if os.path.isfile(filePath):        
        print(os.path.abspath(filePath))
        with open(filePath, "r", encoding="utf-8", errors="ignore") as file:
            fileText = file.read()
            try:
                return json.loads(fileText, object_pairs_hook=OrderedDict)
            # 因为直接用 json5 库读取速度极慢
            # 这里就用 try except 结构，利用自带 json 库读取一次
            # 如果有问题再用 json5 读取，提升速度
            except ValueError:
                try:
                    return json5.loads(fileText, object_pairs_hook=OrderedDict)
                except ValueError:
                    file.close()
                    shutil.move(filePath, filePath[:-4]+"error")
    return {}


def updateLanguageFile(filePath, oldFilePath):
    oldChineseFilePath = oldFilePath[:-10]+"zh_cn.json"
    newChineseFilePath = filePath[:-10]+"zh_cn.json"
    oldEn = readLanguageFile(oldFilePath)
    oldZh = readLanguageFile(oldChineseFilePath)
    newEn = readLanguageFile(filePath)

    newZh = OrderedDict()
    for k, v in newEn.items():
        if k in oldEn.keys() and k in oldZh.keys():
            if v.strip() == oldEn[k].strip():
                newZh[k] = oldZh[k]
        if k not in oldEn.keys() and k in oldZh.keys():
            newZh[k] = oldZh[k]

    with open(newChineseFilePath, "w", encoding="utf-8") as newZhFile:
        json.dump(newZh, newZhFile, indent=2,
                  ensure_ascii=False)


if __name__ == "__main__":
    with open("./config.yml", "r", encoding="utf-8") as configFile:
        config = yaml.load(configFile)
    checkFile("./projects", config)
