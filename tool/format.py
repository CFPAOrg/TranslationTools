from collections import OrderedDict
import shutil
import json5
import json
import logging
import os
import yaml
import re

################################################
# 统一格式化 zh_cn.json 文件的工具
# 会一口气读取所有的 zh_cn.json 文件
# 并剔除其所有的 json5 注释、重复 key
# 并按照 2 空格缩进格式化
################################################


def checkFile(folder):
    for file in os.listdir(folder):
        filePath = "{}/{}".format(folder, file)
        if os.path.isfile(filePath) and filePath.endswith("zh_cn.json"):
            newZh = readLanguageFile(filePath)
            with open(filePath, "w", encoding="utf-8") as newZhFile:
                json.dump(newZh, newZhFile, indent=2,
                          ensure_ascii=False)
        if os.path.isdir(filePath):
            checkFile(filePath)


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


if __name__ == "__main__":
    with open("./config.yml", "r", encoding="utf-8") as configFile:
        config = yaml.load(configFile)
    checkFile(config["local-repo"])
