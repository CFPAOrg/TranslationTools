import yaml
import logging
from src import update_info as updateInfo
from src import contrast
from src import download
from src import handle

########################################################################
# 模组更新爬虫工具
# 
# 依据配置文件，自动检索仓库内 1.16 版本以上翻译
# 获取基础的模组信息（下载量，CurseForge ID 和各个版本最新文件地址）
# 自动抽出模组文件中的英文文本，并对比更新中文文本
# 英文词条发生变动的词条，会直接移除对应中文文本内容
#
# 使用须知：
# - 配合配置文件 config.yml 使用
# - 设置环境变量 CURSE_FORGE_API_KEY（为 CurseForge 官方 API Key）
# - Python3.6 及以上环境运行
# - 需要 requests json5 wget 三个 Python 库
########################################################################

LOG_FORMAT = "[%(asctime)s] [%(threadName)s/%(levelname)s] [%(module)s] %(message)s"
LOG_DATE_FORMAT = "%H:%M:%S"

if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG,
                        format=LOG_FORMAT, datefmt=LOG_DATE_FORMAT)

    logging.info("读取配置文件……")
    with open("./config.yml", "r", encoding="utf-8") as configFile:
        config = yaml.load(configFile)

    logging.info("检索翻译仓库，更新模组信息……")
    # TODO：自动 clone 翻译主仓库

    logging.info("更新模组信息……")
    updatedInfo = updateInfo.setup(config)

    logging.info("对比先前数据，检查需要更新下载的模组……")
    downloadInfo = contrast.setup(config, updatedInfo)

    logging.info("开始下载模组，解压获取语言文件……")
    download.setup(config, downloadInfo)

    logging.info("对比更新中文文本……")
    handle.checkFile("./projects", config)
