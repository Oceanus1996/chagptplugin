#!/usr/bin/python
import random
import re
import string
import time
import json
import pandas as pd
import requests
from bs4 import BeautifulSoup
import yaml
import math

execl_path = r'C:\Users\rrm_a\Desktop\1\source\plugin.xlsx'
df = pd.read_excel(execl_path)  # df是已经阅读的json格式
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/97.0.4692.71 Safari/537.36',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
    'Accept-Encoding': 'gzip, deflate, br',
    'Accept-Language': 'en-US,en;q=0.9',
    'Connection': 'keep-alive',
    # 添加其他可能需要的请求头字段，比如Referer等
}

class Json:
    # def  operator_file(self):
        # 抓取所有列表i

    #
    # def change_address(self,url):#改变再次载入
    #     try:
    #         webbrowser.open(url)
    #     except:
    #         print('error')
    #     pass

    """解析重组网址"""
    def clean_urls_2(self,url):
        stop_words_pattern = re.compile(r'/(terms|home|legal|policy|privacy|about)[/\w-]*', re.IGNORECASE)

        # 使用正则表达式模式处理每个URL
        cleaned_urls = stop_words_pattern.sub('', url)
        cleaned_urls = re.sub(r'\/?$', '', cleaned_urls)  # 多了一个/
        cleaned_urls = re.sub(r'\.html$', '', cleaned_urls)  # 去掉末尾的.html
        cleaned_urls = re.sub(r'/(static|tos|term).*$', '', cleaned_urls)  # 去掉static或者tos
        return cleaned_urls

    def clean_url_3(self,url):
        # 含有 =sharing plugin  plugin  (没动)
        cleaned_urls = re.sub(r'\.(htm|php|txt|pdf)$', '', url)  # 去掉末尾的.htm .php .txt .pdf
        # 去掉开头的policies .well-known /us  /en  /pages |page|#legal|.well-knonw|terms|api|%
        cleaned_urls = re.sub(r'/(policies|.well-known|us|en|pages|page|#legal|.well-knonw|terms|api|%|live).*$',
                              '', cleaned_urls)
        cleaned_urls = re.sub(r'/.*(term|static|=sharing|=en|terms).*$', '', cleaned_urls)  # 移除任意term
        return cleaned_urls

    def clear_urls_4(self,url):
        #只提取最前面两位
        match = re.match(r'(https?)://([^/]+)/?', url)

        if match:
            protocol, domain = match.groups()
            extracted_url = f"{protocol}://{domain}"
            return extracted_url
        else:
            return ' '

    def clear_urls_5(self,url):
        #取前三位，去掉后缀html，htm，php，pdf，/
        match = re.match(r'(https?)://([^/]+)/([^/]+)', url)

        if match:
            protocol, domain, path1 = match.groups()
            extracted_url = f"{protocol}://{domain}/{path1}"
            extracted_url = re.sub(r'\.(html|htm|pdf|php|txt)$', '', extracted_url)  # 去掉末尾的.html

            return extracted_url
        else:
            return ''

    def clean_urls(self,url):
        # 编译一个正则表达式模式，用于匹配指定的关键词及其之后的任何内容
        stop_words_pattern = re.compile(r'/(terms|home|legal|policy|privacy|about)[/\w-]*', re.IGNORECASE)

        # 使用正则表达式模式处理每个URL
        cleaned_urls = stop_words_pattern.sub('', url)
        # 正则表达式匹配域名，并忽略末尾的 .html（如果存在）
        cleaned_urls = re.sub(r'\.(html|htm|php)$', '', cleaned_urls)  # 去掉末尾的.html|htm|php
        ##/ca/en
        #static api
        cleaned_urls = re.sub(r'\.html$', '', cleaned_urls)  # 去掉末尾的.html
        cleaned_urls = re.sub(r'/(static|tos|term).*$', '', cleaned_urls)#去掉static|tos|term
        cleaned_urls = re.sub(r'\/?$', '', cleaned_urls)#去掉/
        cleaned_urls = re.sub(r'/.*term.*$', '', cleaned_urls)#去掉任意term

        return cleaned_urls

    """载入api，如果返回200，就抓取页面内容，并返回正确的api，如果不能，就使用另一个网址，如果都不行，就记录：wrong"""
    def parse_json(self,new_url):
        api_1 = f"{new_url}/{'.well-known/ai-plugin.json'}"
        api_2 = f"{new_url}/{'api/ai.chatgpt.get-plugin-config'}"
        api_3 = f"{new_url}/{'.well-known'}"
        result=[]#第一个表示状态，第二个表示其他信息
        #result成功时，返回（网址，解析）
        #result。code不等于200时，返回（'state',state码）
        #result超时，返回('timeout',0)
        #result请求出错的时候，返回(False,0)
        print(api_1, api_2)

        try:
            response_1 = requests.get(api_1,timeout = 10)
            if response_1.status_code == 200:
                print('开始检测网址1')
                # 假设这里你想要解析JSON而非使用BeautifulSoup，因为你期望的是JSON响应
                print(response_1.text)
                soup = BeautifulSoup(response_1.text, 'html.parser')
                #找到pre里的内容
                # pre_tags = soup.body.find_all('pre')
                result = (('success',api_1,soup),)
                return result
            else:
                result.append(('state',  response_1.status_code))#result。code不等于200时，（'state',state码）,不返回，测下一个
        except requests.exceptions.Timeout as e2:
            print(f"超时超时超时超时超时 {api_3} ")
            result.append(('timeout', api_1))##result超时，不反回
        except requests.exceptions.RequestException as e:
            print(f"请求 {api_1} 时出错")
            result.append((False,e))#result请求出错的时候，(False,0),不返回

        try:
            response_2 = requests.get(api_2,timeout = 10)

            if response_2.status_code == 200:
                print('开始检测网址2')
                json_txt = response_2.text  # 转成txt格式
                soup = BeautifulSoup(json_txt, 'html.parser')
                result = (('success',api_2, soup),)
                return result
            else:
                print(('state', response_2.status_code))
                result.append(
                    ('state', response_2.status_code))  # result。code不等于200时，（'state',state码）,不返回，测下一个
        except requests.exceptions.Timeout as e2:
            print(f"超时超时超时超时超时 {api_3} ")
            result.append(('timeout', api_2))  ##result超时，不反回
        except requests.exceptions.RequestException as e:
            print(f"请求 {api_1} 时出错")
            result.append((False, e))  # result请求出错的时候，(False,0),不返回


        try:
            response_3 = requests.get(api_3,timeout = 10)

            if response_3.status_code == 200:
                print('开始检测网址3')
                json_txt = response_3.text  # 转成txt格式
                soup = BeautifulSoup(json_txt, 'html.parser')
                # 找到pre里的内容
                # pre_tags = soup.body.find_all('pre')
                result = (('success',api_3, soup),)
                return result
            else:
               result.append(('state', response_3.status_code))  # result。code不等于200时，（'state',state码）,不返回，测下一个
        except requests.exceptions.Timeout as e2:
            print(f"超时超时超时超时超时 {api_3} ")
            result.append(('timeout', api_3))  ##result超时，不反回
        except requests.exceptions.RequestException as e:
            print(f"请求 {api_1} 时出错")
            result.append((False, e))  # result请求出错的时候，(False,0),不返回


        # 如果3个请求都失败了
        return result

    def write_to_excel(self,row_index:int,column:string,txt):
        df=pd.read_excel(execl_path)

        if txt is not None:
            df.at[row_index,column] = txt
        else:
            df.at[row_index, column] = float("error sign")

        df.to_excel(execl_path,index=False)

    def verify_url(self,num):
        urls=df['json_url'].tolist()
        infos = df['json_info'].tolist()
        count = num

        for url in urls[num:]:
            if url is None:
                count +=1
                continue
            if 'http' in url:
                print('检测到第几个',count)
                try:
                    response = requests.get(url,timeout=10)
                    if response.status_code==200:
                        soup = BeautifulSoup(response.text, 'html.parser')
                        print(soup,infos[count])
                        if str(soup) == str(infos[count]):
                            print('对的')
                            result = "Y"
                        else:
                            print('错的')
                            result = soup
                        print(result)
                        self.write_to_excel(count,'tips',result)
                    else:
                        self.write_to_excel(count, 'tips', '没有成功请求')
                except requests.exceptions.Timeout as e1:
                    self.write_to_excel(count, 'tips', 'timeout')
                except requests.exceptions.RequestException as e2:
                    self.write_to_excel(count, 'tips', e2)

            count += 1

    def get_api(self, num):

        json_docs= df['json_info']
        complete = df['complete']
        urls = df['json_url'].tolist()
        count =num
        #重新读取json，再做

        for url in urls[num:]:
            if complete[count]=='Y':#能读取的才实现
                try:
                    response = requests.get(url, timeout=10)
                    if response.status_code == 200:
                        try:
                            data = json.loads(response.text)
                            api_url = data.get("api")
                            if api_url is None:
                                print('没有api，json文件有问题',count,data)
                                self.write_to_excel(count, 'tips', '没有api，json文件有问题')
                                count +=1
                                continue
                            api_url = api_url.get("url")
                            if api_url is None:
                                print('没有api/url，json文件有问题',count,data)
                                self.write_to_excel(count, 'tips', '没有api/url，json文件有问题')
                                count += 1
                                continue
                            self.write_to_excel(count, 'tips',api_url )
                            print('成功',count,api_url)
                        except json.decoder.JSONDecodeError as e:
                            print(count,"JSON 解析错误:", e)
                            self.write_to_excel(count, 'tips','其他html占据')
                    else:
                        print(count,'code不对',response.status_code)
                        self.write_to_excel(count, 'tips', response.status_code)
                except requests.exceptions.Timeout as e1:
                    print(count,'timeout')
                    self.write_to_excel(count, 'tips', 'timeout')
                except requests.exceptions.RequestException as e2:
                    print(count,'其他错误',e2)
                    self.write_to_excel(count, 'tips', e2)
            count += 1

    def get_api_info(self,num):
        count = num
        urls=df['tips']
        complete=df['complete']
        redetect=df['redetect']
        for api in urls[num:]:
            #去掉乱七八糟的情况
            # if complete[count] != 'Y':
            #     print(count, '暂时不考虑的情况')
            #     count += 1
            #     continue
            #
            # if api is None:
            #     print(count, '暂时不考虑的情况')
            #     count+=1
            #     continue
            #
            # if "http" not in api:
            #     print(count,'暂时不考虑的情况')
            #     count+=1
            #     continue

            if redetect[count]!='补全网址':
                print(count, '暂时不考虑的情况')
                count += 1
                continue

            try:
                response = requests.get(api,timeout=10)
                time.sleep(random.randint(1,3))
                if response.status_code==200:#成功取到
                    content_type = response.headers.get('Content-Type')
                    #处理不同格式
                    print(count,'准备检测格式头',api,content_type)

                    if api.endswith('.yaml') or api.endswith('.yml'):
                        response_text = re.sub(r'[\x00-\x08\x0B\x0C\x0E-\x1F\x7F-\x9F]', '', response.text)
                        api_info = yaml.safe_load(response_text)
                    elif 'application/json' in content_type:
                        api_info = response.json()
                    elif 'application/x-yaml' in content_type or 'text/yaml' in content_type:
                        api_info = yaml.safe_load(response.text)
                    else:
                        print(count,"Unsupported Content-Type")
                        api_info = response.json()

                    if api_info is None:#api取得不对
                        print(count,'api info是0',api_info)
                        count += 1
                        continue

                    print(count,'写入源数据',type(api_info))
                    self.write_to_excel(count,'api_url',api)#成功找到的api补上
                    self.write_to_excel(count,'api_info',api_info)#把源数据写道api_info中

                    #处理response
                    # cleaned_api_data = {}
                    # for path, method_data in api_info.items():
                    #     # 创建存储操作数据的新字典
                    #     cleaned_method_data = {}
                    #     print(method_data)
                    #
                    #     # 遍历每个操作的数据
                    #     for method, data in method_data.items():
                    #         # 检查并删除响应字段
                    #         if "responses" in cleaned_method_data[method]:
                    #             del cleaned_method_data[method]["responses"]
                    #
                    #         # 复制操作数据到新字典
                    #         cleaned_method_data[method] = data.copy()
                    #
                    #     # 将清理后的操作数据存储到新的路径下
                    #     cleaned_api_data[path] = cleaned_method_data
                    # self.write_to_excel(count,'clear_api_info',cleaned_api_data)#写入clear好的api info
                else:
                    print(count,'没有200回应',response.status_code)
                    self.write_to_excel(count, 'api_info', response.status_code)  # 没有200回应
            except requests.exceptions.Timeout as e:
                print(count,'超时了')
                self.write_to_excel(count, 'api_info', '超时了')  # 超时
            except requests.exceptions.RequestException as e2:
                print(count, '其他错误')
                self.write_to_excel(count, 'api_info', e2)  # 其他错误

            count += 1


    def handle_list_2(self,num):
        count = num #记录抓取到哪一行
        #打开，抓取，解析
        #依次读取url，循环操作
        urls = df['info'].tolist()
        complete=df['complete']
        json_urls = df['json_url']
        redetect= df['redetect']
        detect = df['detect']
        api_tips = df['tips']
        for url in urls[num:]:

            # if complete[count] == 'Y' :#正确的滤过
            #     # print('掠过，记录为正确',count)
            #     count += 1
            #     continue
            # if json_urls[count] !='timeout':
            #     count += 1
            #     continue
            if detect[count]!= "再次检测-json" and detect[count]!= "再次检测":
                count += 1
                print('滤过',count)
                continue
            print(url, 'url')
            time.sleep(1)
            new_url = self.clear_urls_4(url)
            # new_url = self.clean_urls_2(url)
            # new_url = self.clean_url_3(new_url)#再清理一遍
            self.write_to_excel(count, 'url_parsed', new_url)
            #加上后缀，寻找json文件
            print("开始处理", count, new_url)
            result = self.parse_json(new_url)
            if result[0][0] is False or result[0][0] == 'state' or result[0][0] == 'timeout':
                print('一整个大失败')
                api_state = result
                print(api_state)
                print(api_state)
                self.write_to_excel(count,'state',str(api_state))
            else:
                json_url=result[0][1]
                json_info=result[0][2]
                self.write_to_excel(count,'json_info',json_info)
                self.write_to_excel(count, 'json_url', json_url)

            #计数
            count += 1

    def veryify_url(self):
        count=0
        info= df['info']
        url_parsed=df['url_parsed']
        json_url=df['json_url']
        for url in url_parsed:
            if url in info[count]:
                pass
            else:
                print(count,"匹配有误1",url,info[count])
                self.write_to_excel(count,'redetect','匹配有误1')

            if url in json_url[count] or json_url[count]=='wrong' or json_url[count]=='timeout':
                pass
            else:
                print(count, "匹配有误2",url,json_url[count])
                self.write_to_excel(count, 'redetect', '匹配有误2')
            count +=1

    def veryify_api(self):
        count = 0
        json_info = df['json_info']
        api_url = df['api_url']
        for url in api_url:
            if isinstance(url, float) and math.isnan(url):
                # print(count,"The number is NaN.")
                count+=1
                continue

            if url in json_info[count] :
                pass
            else:
                print(count, "json有误", url)

                # self.write_to_excel(count, 'redetect', 'json有误')
            count += 1

    def verify_and_clear_api_info(self,num):
        count = num
        api_infos = df['api_info']
        api_url = df['api_url']
        detect=df['detect']
        for api in api_url[num:]:
            if isinstance(api, float) and math.isnan(api):
                # print(count,"空的不测")
                count+=1
                continue

            if detect[count] != '再次检测':
                # print(count, "本次不测")
                count += 1
                continue

            #搞一下response C:\Users\rrm_a\PycharmProjects\pythonProject1\.venv
            try:
                response = requests.get(api,timeout=10)
                time.sleep(random.randint(1,3))
                if response.status_code==200:#成功取到
                    content_type = response.headers.get('Content-Type')
                    #处理不同格式
                    print(count,'准备检测格式头',api,content_type)

                    # if content_type is None:
                    #     print(count, "Unsupported Content-Type")
                    #     api_info = response.json()
                    if api.endswith('.yaml') or api.endswith('.yml'):
                        response_text = re.sub(r'[\x00-\x08\x0B\x0C\x0E-\x1F\x7F-\x9F]', '', response.text)
                        api_info = yaml.safe_load(response_text)
                    elif 'application/json' in content_type:
                        api_info = response.json()
                    elif 'application/x-yaml' in content_type or 'text/yaml' in content_type:
                        api_info = yaml.safe_load(response.text)
                    else:
                        print(count,"Unsupported Content-Type2")
                        api_info = response.json()

                    if api_info is None:#api取得不对
                        print(count,'api info是0',api_info)
                        count += 1
                        continue

                    print(count,'开始清洗',type(api_info),str(api_info))

                    #
                    # self.write_to_excel(count,'redetect',api_info==api_infos[count])#成功找到的api补上
                    # self.write_to_excel(count,'redetect2',str(api_info))#把源数据写道api_info中

                    #清洗掉responses,清洗到第三层
                    for path, methods in api_info['paths'].items():
                        for method, details in methods.items():
                            # 检查是否存在responses键
                            if 'responses' in details:
                                print('检测到responses在第二层', details)
                                del details['responses']
                            else:
                                # 遍历第三层
                                for key, value in details.items():
                                    if isinstance(value, dict) and 'responses' in value:
                                        print('检测到responses在第三层', value)
                                        del value['responses']
                    print('清洗完了',count,api_info)
                    self.write_to_excel(count, 'clear_api_info', str(api_info))  # 把清洗数据写道api_info中

                else:
                    print(count,'没有200回应',response.status_code)
                    self.write_to_excel(count, 'redetect', response.status_code)  # 没有200回应
            except requests.exceptions.Timeout as e:
                print(count,'超时了')
                self.write_to_excel(count, 'redetect', '超时了')  # 超时
            except requests.exceptions.RequestException as e2:
                print(count, '其他错误',e2)
                self.write_to_excel(count, 'redetect', e2)  # 其他错误

            count += 1


    def clear_path(self,num):#从yaml链接中，清洗出path，然后将path进行测试，记录返回值
        api_url=df['api_url']
        complete=df['complete']
        count = num
        error_list= df['error']
        #读取api内容
        for api in api_url[num:]:
            if complete[count]!='Y':
                count+=1
                continue
            if error_list[count]=='wrong_req':
                count += 1
                continue
            try:
                response = requests.get(api,timeout=10)
                time.sleep(random.randint(1,3))
                if response.status_code==200:#成功取到
                    content_type = response.headers.get('Content-Type')
                    #处理不同格式
                    print(count,'准备检测格式头',api,content_type)

                    # if content_type is None:
                    #     print(count, "Unsupported Content-Type")
                    #     api_info = response.json()
                    if api.endswith('.yaml') or api.endswith('.yml'):
                        response_text = re.sub(r'[\x00-\x08\x0B\x0C\x0E-\x1F\x7F-\x9F]', '', response.text)
                        api_info = yaml.safe_load(response_text)
                    elif 'application/json' in content_type:
                        api_info = response.json()
                    elif 'application/x-yaml' in content_type or 'text/yaml' in content_type:
                        api_info = yaml.safe_load(response.text)
                    else:
                        print(count,"Unsupported Content-Type2")
                        api_info = response.json()

                    if api_info is None:#api取得不对
                        print(count,'api info是0',api_info)
                        count += 1
                        continue

                    print(self.handle_get(api_info,count))



                else:
                    print(count,'没有200回应',response.status_code)
                    self.write_to_excel(count, 'redetect', response.status_code)  # 没有200回应
            except requests.exceptions.Timeout as e:
                print(count,'超时了')
                self.write_to_excel(count, 'redetect', '超时了')  # 超时
            except requests.exceptions.RequestException as e2:
                print(count, '其他错误',e2)
                self.write_to_excel(count, 'redetect', e2)  # 其他错误

            count+=1

    def handle_get(self,body,count):
        # Given a list of API specifications, we'll write a function to extract the URLs for GET and POST requests
        # Initialize a dictionary to hold the extracted URLs
        urls = {"GET": [], "POST": []}

        # Loop through each API spec
        try:
            # 尝试提取基础URL
            base_url = body['servers'][0]['url']
        except (KeyError, IndexError):
            # 如果提取失败，打印消息并返回None
            print(count,"无法提取基础URL，请检查OpenAPI规范文件。")
            # self.write_to_excel(count,'error','base_url')
            base_url = df['url_parsed'][count]
            # return
        paths = body['paths']  # 提取定义的路径
        api_endpoints = []
        idx=1
        self.reset_df()


       # 遍历每个路径和方法
        for path, path_item in body['paths'].items():
            for http_method in ['get', 'post']:
                if http_method in path_item:
                    full_url = f"{base_url}{path}"
                    params = None
                    data = None

                    # 对于GET请求，提取查询参数
                    if http_method == 'get':
                        params = path_item[http_method].get('parameters', {})
                        if params is not None:
                            params=self.construct_params(params)

                    # 对于POST请求，提取请求体
                    elif http_method == 'post':
                        request_body = path_item[http_method].get('requestBody', {})
                        if 'content' in request_body and 'application/json' in request_body['content']:
                            data = request_body['content']['application/json'].get('schema', {})
                        # 添加判断条件，如果存在参数则提取参数的名称
                    elif http_method in ['patch', 'put']:
                        request_body = path_item[http_method].get('requestBody', {})
                        if 'content' in request_body and 'application/json' in request_body['content']:
                            data = request_body['content']['application/json'].get('schema', {})
                    elif http_method == 'delete':
                        # 对于 DELETE 请求不包含请求体
                        pass

                    request_1={
                        'method': http_method.upper(),
                        'path': path,
                        'full_url': full_url,
                        'params': params,
                        'data': data
                    }

                    api_endpoints.append(request_1)
                    print(idx,type(request_1),request_1)
                    response = self.send_api_request(http_method.upper(), full_url, params, data)
                    response_text=response.text
                    if response.headers.get('Content-Type') == 'image/png':
                        response_text='picture!'
                    print(response.status_code, response_text)


                    self.write_to_excel(count,f'request_{idx}', json.dumps(request_1))
                    self.write_to_excel(count,f'response_{idx}',f'{response.status_code}{response_text}')

                    idx+=1

    def send_api_request(self,method, url, params=None, data=None):
        """
        发送API请求。

        :param method: 请求方法，如'GET'或'POST'
        :param url: 完整的API端点
        :param params: GET请求的查询参数
        :param data: POST请求的JSON数据体
        :return: 响应对象
        """
        headers = {
            'Content-Type': 'application/json',
            # 如果需要的话，还可以添加其他如认证的头部
        }
        # 发送请求
        if method == 'GET':
            response = requests.get(url, params=params, headers=headers)
        elif method == 'POST':
            response = requests.post(url, json=data, headers=headers)
        elif method == 'PUT':
            response = requests.put(url, json=data, headers=headers)
        elif method == 'PATCH':
            response = requests.patch(url, json=data, headers=headers)
        elif method == 'DELETE':
            response = requests.delete(url, headers=headers)
        else:
            raise ValueError("请求方法只能是 'GET'、'POST'、'PUT'、'PATCH' 或 'DELETE'。")
        return response

    def construct_params(self,param_definition):
        params = {}
        for param in param_definition:
            param_name = param['name']
            param_required = param.get('required',False)
            if param_required:
                # 如果参数是必需的，可以根据实际情况设置参数值
                param_value = 'default_value'
                params[param_name] = param_value
            else:
                # 如果参数不是必需的，可以选择性地设置参数值，或者根据实际情况跳过该参数
                pass
        return params
    def wrong_request(self):
        error_list=df['error']
        count =823
        api_url = df['api_url']
        url_parsed=df['url_parsed']
        for api in api_url[count:]:
            if error_list[count]!='wrong_req':
                count+=1
                continue
            idx=1
            for _ in range(7):
                print(count,idx,df[f'request_{idx}'][count])

                if df[f'request_{idx}'][count]!=None:
                    request= str(df[f'request_{idx}'][count])
                    if request.strip().lower() == 'nan':
                        continue
                    request_dict = json.loads(request)

                    #发送请求
                    full_url=request_dict.get('full_url')
                    if full_url is None:
                        full_url=f'{url_parsed[count]}{request_dict.get('path')}'
                    print(request_dict)
                    response = self.send_api_request(request_dict.get('method'), full_url, request_dict.get('params'), request_dict.get('data'))
                    self.write_to_excel(count, f'response_{idx}', f'{response.status_code}{response.text}')
                    print(response.status_code)
                idx+=1
            count+=1


    def request_result(self):
        result= df['request_result']
        complete=df['complete']
        count =0
        for _ in result:
            if complete[count]!='Y':
                count+=1
                continue

            success=False
            for idx in range(1,38):
                response = df[f'response_{idx}'][count]
                if str(response).strip().lower() == 'nan':
                    continue
                res_code = response[:3]
                res_content = response[3:]
                print(res_code)
                print(res_content)
                if res_code == '200':
                    try:
                        json_dict = json.loads(res_content)
                        if isinstance(json_dict, dict) and 'error' in json_dict :#只有这种情况是false，其余都是true
                           continue
                        success = True
                    except ValueError:
                        success = True
                        pass

                if success is True:
                    self.write_to_excel(count,'request_result','success')
                    break
            if success is False:
                self.write_to_excel(count, 'request_result', 'unsuccess')

            count += 1



    def reset_df(self):

        df['response_1'] = df['response_1'].astype('object')
        df['response_2'] = df['response_2'].astype('object')
        df['response_3'] = df['response_3'].astype('object')
        df['response_4'] = df['response_4'].astype('object')
        df['response_5'] = df['response_5'].astype('object')
        df['response_6'] = df['response_6'].astype('object')
        df['response_7'] = df['response_7'].astype('object')
        df['response_8'] = df['response_8'].astype('object')
        df['response_9'] = df['response_9'].astype('object')

        df['request_1'] = df['request_1'].astype('object')
        df['request_2'] = df['request_2'].astype('object')
        df['request_3'] = df['request_3'].astype('object')
        df['request_4'] = df['request_4'].astype('object')
        df['request_5'] = df['request_5'].astype('object')
        df['request_6'] = df['request_6'].astype('object')
        df['request_7'] = df['request_7'].astype('object')
        df['request_8'] = df['request_8'].astype('object')
        df['request_9'] = df['request_9'].astype('object')


    def check_name(self,num):
        json_info=df['json_info']
        complete= df['complete']
        titles=df['title']
        name_issue=df['name_issue']
        count=num
        for api in json_info[count:]:

            if complete[count]!='api文件不可读' and complete[count]!='Y(有点问题）':
                count+=1
                continue
            # print(count,'api,',api)
            try:
                # 尝试解析JSON字符串
                api_dict = json.loads(api)
                name = api_dict.get('name_for_human')
                title=titles[count]
                print(count, name,title, api_dict)
                self.write_to_excel(count, 'name_for_human',name)
                self.write_to_excel(count,'name_issue',name == title)

            except json.decoder.JSONDecodeError:
                # 如果捕获到JSON解析错误，可以选择记录错误、跳过当前循环迭代或执行其他操作
                self.write_to_excel(count,'name_issue','_cannot parse')
                print(f"JSON解析错误在索引 {count}: 无法解析数据。跳过并继续。")
                # 可以在这里添加更多的错误处理逻辑，比如记录有问题的数据等

            count+=1

    def check_auth(self,num):
        json_info=df['json_info']
        complete = df['complete']
        count=num
        self.reset_df()
        for api in json_info[num:]:
            if complete[count]!='api文件不可读' and 'Y' not in complete[count] :
                count+=1
                continue

            try:
                json_dict = json.loads(api)
                if 'auth' in json_dict:
                    auth_info = json_dict['auth']
                else:
                    # 处理键不存在的情况
                    # 例如，设置一个默认值或者抛出一个异常
                    auth_info = "not exist"  # 或者 raise KeyError("auth key not found")
                print(count,auth_info)
                self.write_to_excel(count,'auth',str(auth_info))
            except json.decoder.JSONDecodeError:
                self.write_to_excel(count, 'auth', 'cannot parse')

            count+=1

    def check_auth_token(self,num):
        auth_states=df['auth_state']
        auth=df['auth']
        api_info=df['api_info']
        count=num
        for auth_state in auth_states[count:]:
            if auth_state!='有auth未施加影响':
                count+=1
                continue

            if 'token' in auth[count] and api_info[count] is not None :
                self.write_to_excel(count,'auth_state','token无效')

            count+=1

    def check_legal(self,num):
        json_info = df['json_info']
        complete = df['complete']
        infos=df['info']
        count = num
        for api in json_info[count:]:
            if complete[count] != 'api文件不可读' and complete[count] !='Y(有点问题）':
                count += 1
                continue
            print(count,'api,',api)
            try:
                # 尝试解析JSON字符串
                api_dict = json.loads(api)

                if type(api_dict)!=dict or api_dict.get('legal_info_url') is None:
                    self.write_to_excel(count,'legal_state','無legal的url')
                    count+=1
                    continue
                legal_url = api_dict.get('legal_info_url')
                self.write_to_excel(count, 'legal',legal_url)
                self.write_to_excel(count, 'legal_state',legal_url==infos[count])
                print(count,legal_url==infos[count],legal_url,infos[count])
            except json.decoder.JSONDecodeError:
                # 如果捕获到JSON解析错误，可以选择记录错误、跳过当前循环迭代或执行其他操作
                print(f"JSON解析错误在索引 {count}: 无法解析数据。跳过并继续。")
                self.write_to_excel(count, 'legal_state', '無法解析')
                # 可以在这里添加更多的错误处理逻辑，比如记录有问题的数据等

            count+=1


if __name__=="__main__":
    a=Json()
    a.check_legal(0)
    # a.check_auth_token(0)
    # print(pd.read_excel(execl_path)['request_1'][0])
    # a.clear_path(536)#143 535  #150 294 535 58
    # a.wrong_request()
    # a.request_result()


    # a.verify_and_clear_api_info(0)#11,717 792
    # a.handle_list_2(0)

    # a.get_api_info(293)#82有问题，169有问题 292 325


    # a.handle_list_2(0)
            #.well-known/ai-plugin.json
    #/api/ai.chatgpt.get-plugin-config
    #/ca/en
    #static api
    #一级目录
    #多了一个/
    #tos小调   subscription-agreement
    #term,含有

    #.php policies .well-known /us .txt .htm /en .pdf /pages
    #含有static =sharing plugin /page =en /live plugin /% .well-knonw  /#legal terms /api
    #1 取/前两位，测试 取前三位测试
    #2 取原网址，测试
    #clean url2+url3
    #手动检测网址134个，先取前两位检测
    #timeout手动测验
    #匹配有误1，2 手动重新执行一下

    # a.parse_json('https://chatgpt-plugin-7npmcik6ca-uc.a.run.app/static/bestever-tos.html')







