import re

from django.shortcuts import render
from django.shortcuts import HttpResponse
from django.http.response import JsonResponse
from user import models

global crawlSp
global crawlFp

# Create your views here.
def register(request):
    print('进入接口register')
    json = {}
    if request.method == 'POST':
        name = request.POST.get('name').strip()
        phone = request.POST.get('phone').strip()
        email = request.POST.get('email').strip()
        password = request.POST.get('password').strip()
        checkpwd = request.POST.get('checkpwd').strip()

        if name == '' or phone == '' or email == '' or password == '' or checkpwd == '':
            json['resultCode'] = '20001'
            json['resultDesc'] = '参数不全'
        else:
            try:
                user = models.User.objects.get(u_phone=phone)
                json['resultCode'] = '10002'
                json['resultDesc'] = '该手机号已被注册'
            except:
                try:
                    user = models.User.objects.get(u_email=email)
                    json['resultCode'] = '10003'
                    json['resultDesc'] = '该邮箱已被注册'
                except:
                    phoneRe = re.match(r'^1[35678]\d{9}$', phone)
                    emailRe = re.match(r'^[0-9a-zA-Z_]{0,19}@[0-9a-zA-Z]{1,13}\.[com,cn,net]{1,3}$', email)
                    if phoneRe and emailRe and len(password) >= 6:
                        if password == checkpwd:
                            try:
                                user = models.User.objects.create(u_name=name, u_password=password, u_phone=phone, u_email=email)
                                json['resultCode'] = '10001'
                                json['resultDesc'] = '注册成功'
                            except:
                                json['resultCode'] = '30000'
                                json['resultDesc'] = '服务器故障'
                        else:
                            json['resultCode'] = '20002'
                            json['resultDesc'] = '两次密码不一致'
                    else:
                        json['resultCode'] = '10005'
                        json['resultDesc'] = '参数格式错误'

    return JsonResponse(json)

def login(request):
    print('进入接口login')
    json = {}
    if request.method == "POST":
        username = request.POST.get("username").strip()
        password = request.POST.get("password").strip()

        if username == '' or password == '':
            json['resultCode'] = '20000'
            json['resultDesc'] = '参数不全'
        else:
            phoneFlag = True
            emailFlag = True
            try:
                user = models.User.objects.get(u_phone=username)
            except:
                phoneFlag = False

            if phoneFlag:
                if user.u_password == password:
                    json['resultCode'] = '10001'
                    json['resultDesc'] = '登陆成功'
                    request.session['u_id'] = user.u_id
                else:
                    json['resultCode'] = '10003'
                    json['resultDesc'] = '密码错误'
            else:
                try:
                    user = models.User.objects.get(u_email=username)
                except:
                    emailFlag = False

                if emailFlag:
                    print("邮箱存在")
                    if user.u_password == password:
                        json['resultCode'] = '10001'
                        json['resultDesc'] = '登陆成功'
                        request.session['u_id'] = user.u_id
                    else:
                        json['resultCode'] = '10003'
                        json['resultDesc'] = '密码错误'
                else:
                    json['resultCode'] = '10002'
                    json['resultDesc'] = '用户不存在'

    return JsonResponse(json)

def updatePwd(request):
    print('进入接口updatePwd')
    json = {}
    if request.method == "POST":
        oldpwd = request.POST.get("oldpwd").strip()
        newpwd = request.POST.get("newpwd").strip()
        checkpwd = request.POST.get("checkpwd").strip()

        if oldpwd == '' or newpwd == '' or checkpwd == '':
            json['resultCode'] = '20000'
            json['resultDesc'] = '参数不全'
        else:
            u_id = request.session.get('u_id')
            try:
                user = models.User.objects.get(u_id=u_id)
                if user.u_password == oldpwd:
                    if len(newpwd) >= 6:
                        if newpwd == checkpwd:
                            user.u_password = newpwd
                            user.save()
                            json['resultCode'] = '10001'
                            json['resultDesc'] = '修改成功'
                        else:
                            json['resultCode'] = '10007'
                            json['resultDesc'] = '两次新密码不一致'
                    else:
                        json['resultCode'] = '10006'
                        json['resultDesc'] = '新密码格式错误'
                else:
                    json['resultCode'] = '10005'
                    json['resultDesc'] = '原密码错误'
            except:
                json['resultCode'] = '30000'
                json['resultDesc'] = '服务器故障'

    return JsonResponse(json)

def updateInfo(request):
    print('进入接口updateInfo')
    json = {}
    if request.method == "POST":
        name = request.POST.get("name").strip()
        phone = request.POST.get("phone").strip()
        email = request.POST.get("email").strip()

        if name == '' or phone == '' or email == '':
            json['resultCode'] = '20000'
            json['resultDesc'] = '参数不全'
        else:
            u_id = request.session.get('u_id')
            json['resultCode'] = '10001'
            json['resultDesc'] = '修改成功'
            try:
                user = models.User.objects.get(u_id=u_id)

                phoneNotUsed = False
                emailNotUsed = False

                if user.u_phone != phone:
                    try:
                        other_user = models.User.objects.get(u_phone=phone)
                        json['resultCode'] = '10002'
                        json['resultDesc'] = '新手机号已被注册'
                    except:
                        phoneNotUsed = True

                if user.u_email != email:
                    try:
                        other_user = models.User.objects.get(u_email=email)
                        json['resultCode'] = '10003'
                        json['resultDesc'] = '新邮箱已被注册'
                    except:
                        emailNotUsed = True

                if phoneNotUsed or emailNotUsed:
                    phoneRe = re.match(r'^1[35678]\d{9}$', phone)
                    emailRe = re.match(r'^[0-9a-zA-Z_]{0,19}@[0-9a-zA-Z]{1,13}\.[com,cn,net]{1,3}$', email)
                    if not phoneRe or not emailRe:
                        json['resultCode'] = '10005'
                        json['resultDesc'] = '手机号或邮箱格式错误'

            except:
                json['resultCode'] = '30000'
                json['resultDesc'] = '服务器故障'

            if json['resultCode'] == '10001':
                user.u_name = name
                user.u_phone = phone
                user.u_email = email
                user.save()

    return JsonResponse(json)

def crawl(request):
    print('进入接口crawl')
    json = {}
    if request.method == "POST":
        keyword = request.POST.get("keyword")
        pageNum = request.POST.get("pageNum")

        if keyword.strip() == '' or pageNum.strip() == '':
            json['resultCode'] = '20000'
            json['resultDesc'] = '参数不全'
        else:
            try:
                keyword_obj = models.Keyword.objects.get(k_keyword=keyword)
            except:
                keyword_obj = models.Keyword.objects.create(k_keyword=keyword)

            print(keyword_obj.k_id)
            request.session['k_id'] = keyword_obj.k_id

            crawl_obj = models.Crawl.objects.filter(k_id=keyword_obj.k_id)
            if len(crawl_obj) > 0:
                print(len(crawl_obj))
                print('查到了crawl表')
                json['resultCode'] = '10001'
                json['resultDesc'] = '爬取成功'
            else:
                print('没查到')
                from selenium import webdriver
                from selenium.webdriver.chrome.options import Options
                import time
                import hashlib

                # #正常模式
                # chrome_options = webdriver.ChromeOptions()
                # chrome_options.add_argument('--start-maximized')
                # #无头模式启动
                # chrome_options.add_argument('--headless')
                # #谷歌文档提到需要加上这个属性来规避bug
                # chrome_options.add_argument('--disable-gpu')
                # plugin_file = './spider/utils/proxy_auth_plugin.zip'
                # chrome_options.add_extension(plugin_file)

                # firefox-headless
                # from selenium import webdriver
                # options = webdriver.FirefoxOptions()
                # options.set_headless()
                # # options.add_argument('-headless')
                # options.add_argument('--disable-gpu')
                # driver = webdriver.Firefox(firefox_options=options)
                # driver.get('http://httpbin.org/user-agent')
                # driver.get_screenshot_as_file('test.png')
                # driver.close()

                # chrome-headless
                chrome_options = Options()
                # 无头模式启动
                chrome_options.add_argument('--headless')
                # 谷歌文档提到需要加上这个属性来规避bug
                chrome_options.add_argument('--disable-gpu')
                chrome_options.add_argument('--start-maximized')
                # 初始化实例
                driver = webdriver.Chrome(options=chrome_options)
                #    self.browser = webdriver.Chrome(chrome_options=self.chrome_options)
                # wait = WebDriverWait(driver, TIMEOUT)
                url = "https://www.itslaw.com/search?searchMode=judgements&sortType=1&conditions=searchWord%2B%E6%B3%95%E5%BE%8B%2B1%2B%E6%B3%95%E5%BE%8B&searchView=text"
                driver.get(url)
                # 点击登录

                crawlSp = 0
                crawlFp = 0

                while 1:
                    try:
                        driver.find_element_by_class_name("login-btn").click()
                        print("输入密码ing")
                        time.sleep(2)
                        driver.find_element_by_xpath("//input[@id='username']").click()
                        driver.find_element_by_xpath("//input[@id='username']").clear()
                        driver.find_element_by_xpath("//input[@id='username']").send_keys('13667272850')
                        driver.find_element_by_xpath("//input[@id='password']").click()
                        driver.find_element_by_xpath("//input[@id='password']").clear()
                        driver.find_element_by_xpath("//input[@id='password']").send_keys('mssjwow123')
                        driver.find_element_by_class_name("submit").click()
                        time.sleep(2)

                        driver.find_element_by_xpath("//input[@placeholder='输入“?”定位到当事人、律师、法官、法院、标题、法院观点']").click()
                        print("搜索关键词ing")
                        driver.find_element_by_xpath("//input[@placeholder='输入“?”定位到当事人、律师、法官、法院、标题、法院观点']").clear()
                        driver.find_element_by_xpath("//input[@placeholder='输入“?”定位到当事人、律师、法官、法院、标题、法院观点']").send_keys(
                            keyword)
                        driver.find_element_by_class_name("search-box-btn").click()
                        time.sleep(3)

                        # 加载更多
                        # j = 1
                        # for j in range(4):
                        #     element = driver.find_element_by_xpath("//button[@class='view-more ng-scope']")
                        #     element.click()
                        #     time.sleep(3)

                        lis = driver.find_elements_by_xpath(
                            '//div[@class = "judgements"]/div[@class="judgement ng-scope"]')

                        for i in range(len(lis)):
                            print("开始点击")
                            i = i + 1
                            print("在这里")
                            div_str = '//div[@class="judgements"]/div[{}]/div[2]/h3/a'.format(i)
                            # title
                            title = driver.find_element_by_xpath(div_str).text
                            hl = hashlib.md5()
                            hl.update(title.encode(encoding='utf-8'))
                            # md5
                            title_md5 = hl.hexdigest()

                            print(title, keyword_obj.k_id, title_md5)

                            # 存数据库
                            crawl_obj = models.Crawl.objects.create(c_title=title, k_id=keyword_obj.k_id, c_path=title_md5)

                            # models.Crawl.objects.create(c_keyword=keyword)
                            # models.Crawl.objects.create(c_title=title)
                            # models.Crawl.objects.create(c_path=title_md5)
                            div_str = '//div[@class="judgements"]/div[{}]/div[2]/h3/a'.format(i)
                            driver.find_element_by_xpath(div_str).click()
                            print("点击完成")
                            all_h = driver.window_handles
                            driver.switch_to.window(all_h[1])
                            h2 = driver.current_window_handle
                            print('已定位到元素')
                            time.sleep(3)
                            try:
                                wenshu = driver.find_element_by_xpath(
                                    '//section[@class="paragraphs ng-isolate-scope"]').text
                                f = open('./data/' + title_md5 + '.txt', 'a')
                                f.write(wenshu)
                                f.write('\n')
                                f.close()
                                print("成功")
                                crawlSp = crawlSp + 1
                            except:
                                print("失败")
                                crawlFp = crawlFp + 1

                            driver.close()
                            driver.switch_to.window(all_h[0])

                        driver.close()

                        result = "ok"
                        json['resultCode'] = '10001'
                        json['resultDesc'] = '爬取成功'
                        print(crawlSp)
                        print(crawlFp)
                        print('关闭')
                        # end = time.process_time()
                        break
                    except:
                        print("还未定位到元素!")

        # 存储到数据库
        # UserModel.objects.create()  # 增
        # UserModel.objects.get()  # 查（只查看一条数据）
        # UserModel.objects.filter()  # 查看多条数据
        # UserModel.objects.filter().update()  # 改
        # UserModel.objects.filter().delete()  # 删

    return JsonResponse(json)

def crawlRate(request):
    print('进入接口crawRate')
    json = {}
    json['data'] = crawlSp / (20-crawlFp)

    return JsonResponse(json)

# from user.legalReadFunc import *
def readcomprehend(request):
    print('进入接口readcomprehend')
    json = {}

    # if request.method == "POST":
    #     questions = request.POST.get("questions")
    #     #print(questions)
    #     k_id = request.session.get('k_id')
    #
    #     # question_list通过questions用分号划分
    #     question_list = questions.split(";")
    #
    #     for question in question_list:
    #         q_id = models.Question.objects.create(q_name=question, k_id=k_id)
    #         #question_id_list.append(q_id)
    #
    #     #查询question_id
    #     question_id_list2 = models.Question.objects.filter(k_id=k_id).values_list('q_id')
    #     #print ("question_id_list2:", question_id_list2)
    #     question_id_list = [one_id[0] for one_id in question_id_list2]
    #
    #     # 1，根据当前的关键字id查询出question列表，question的id列表，篇章列表，篇章的id列表
    #    # passage_list, passage_id_list = models.Crawl.objects.filter(k_id=k_id).values_list('c_id', 'c_path')
    #     all_passage_list= models.Crawl.objects.filter(k_id=k_id).values_list('c_id', 'c_path')
    #     passage_list = [];  passage_id_list = []
    #     for one_passage_list in all_passage_list:
    #         passage_id_list.append(one_passage_list[0])
    #         passage_list.append(one_passage_list[1])
    #     #print ("查询结束")
    #
    #     passage_list2 = []
    #     for i in range(len(passage_list)):
    #         file = open("./data/"+passage_list[i]+".txt", "r")#, encoding="gbk"
    #         one_passage = file.read()
    #         file.close()
    #         passage_list2.append(one_passage)
    #     #print (passage_list2[0])
    #     #print ("成功")
    #
    #     # 2，得到四个列表之后开始分析
    #     # 下面为四个list的例子
    #     """
    #     file = open("legalReadFunc/data/wenshu.txt", "r", encoding="utf8")
    #     data = file.read()
    #     passage_list = data.split("\n\n\n\n")
    #     passage_id_list = range(len(passage_list))
    #     question_id_list = range(len(question_list))
    #     question_list = ["罪名是什么？", "刑期有多久？", "涉案金额是多少？", "作案人数有几人？"]
    #     """
    #
    #     # 3，进行分析
    #     all_predictions = main.main2(passage_list, question_list)
    #
    #     # 4，整理分析结果
    #     return_data = []
    #     for q_id in all_predictions.keys():
    #         one_return = {}
    #         position = q_id.split("_")
    #         one_return["passage_id"] = passage_id_list[int(position[0])]
    #         one_return['question_id'] = question_id_list[int(position[1])]
    #         one_return['answer'] = all_predictions[q_id]
    #         return_data.append(one_return)
    #
    #     #print (return_data)
    #
    # json['resultCode'] = '10001'
    # json['resultDesc'] = '操作成功'
    # json['data'] = return_data

    return JsonResponse(json)

def dataAnalysis(request):
    print('进入接口dataAnalysis')
    json = {}
    if request.method == "POST":
        questions = request.POST.get('questions')
        keyword = request.POST.get('keyword')

        questionList = questions.split(';')

        if len(questionList) > 0 and keyword.strip() != '':
            try:
                k_id = models.Keyword.objects.get(k_keyword=keyword)

                for question in questionList:
                    try:
                        q_id = models.Question.objects.get(q_name=question, k_id=k_id)
                        try:
                            answers = models.Answer.objects.filter(q_id=q_id, k_id=k_id).values_list('a_answer')
                            asw = models.Answer.objects.filter().va
                            answer_classes = list(set(answers))
                            if len(answer_classes) > 10:
                                answer_freq = {ans: answers.count(ans) for ans in answer_classes[:10]}
                            else:
                                answer_freq = {ans: answers.count(ans) for ans in answer_classes}

                            json['resultCode'] = '10001'
                            json['resultDesc'] = '分析成功'
                            json['data'] = answer_freq
                        except:
                            json['resultCode'] = '30000'
                            json['resultDesc'] = '服务器故障'
                    except:
                        json['resultCode'] = '30000'
                        json['resultDesc'] = '服务器故障'
            except:
                json['resultCode'] = '30000'
                json['resultDesc'] = '服务器故障'
        else:
            json['resultCode'] = '30000'
            json['resultDesc'] = '服务器故障'

    return JsonResponse(json)

def recommendkeyword(request):
    print('进入接口recommendkeyword')
    json = {}

    return JsonResponse(json)

def regressionAnalysis(request):
    print('进入接口regressionAnalysis')
    json = {}

    return JsonResponse(json)

def clusterAnalysis(request):
    print('进入接口clusterAnalysis')
    json = {}

    return JsonResponse(json)