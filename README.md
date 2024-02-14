# chagptplugin
Crawler behavior for chatgpt plugin
其中，source/plugin.xlsx为输出结果，数据源为2024-01-05版的chatgpt plugin的网址清单
字段解释：
complete：解释最终处理结果
    'Y'：成功获取到最后api具体信息
    '原始网址'：多次清洗网址匹配未获得正确json路径
    ‘其他html占据’：路径可以返回，但是通往其他无关网页
    ‘json文件有问题’：json相关网址状态为200，但是网页本身不正常，出现空页面等情况
    ‘api文件不可读’：api url存在，但是网页本身不正常，出现空页面等情况
url_parsed：
    多次清洗出的原网址，或者网址主页
state：
    三次尝试失败，不同后缀出现的错误信息，按照数组位置，分别体现api_1,api_2,api_3的状态
            api_1 = f"{new_url}/{'.well-known/ai-plugin.json'}"
            api_2 = f"{new_url}/{'api/ai.chatgpt.get-plugin-config'}"
            api_3 = f"{new_url}/{'.well-known'}"
json_info 和 json_url：
   后缀尝试成功后返回的具体信息  json_info 和 成功的后缀+网址 json_url，其中，json_url的wrong和timeout都是失败的意思

api_url、api_info 和 clear_api_info：
   成功得到json'信息后，解析的api网址（api_url），api的具体信息（api_info），清理掉‘responses’后的api具体信息（clear_api_info）
