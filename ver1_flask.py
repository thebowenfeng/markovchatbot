from flask import Flask, request
import ftplib
import random
import io

app = Flask(__name__)

server = ftplib.FTP()
server.connect('ftpupload.net', 21)
server.login('epiz_24752918','kstyJYVbH3ecj3')

server.cwd("/htdocs")

ftplib.FTP.maxline = 99999999999999

def compute_response(message):
    response_string = ""
    database = []
    message_array = []

    r = io.StringIO()
    server.retrlines("RETR chatbot_database.txt", r.write)
    db = str(r.getvalue())
    if db == "":
        pass
    else:
        for line in db.split("|"):
            if line == "":
                break
            msg_array = []
            if len(line.split()) < 3:
                continue
            for words in line.split():
                msg_array.append(words)
            database.append([[msg_array[0], msg_array[1]], msg_array[2]])

    message = message.lower()

    for i in message.split():
        message_array.append(i)

    for i in range(0, len(message_array)):
        if i + 2 == len(message_array):
            bio = io.BytesIO(
                str.encode(message_array[i]) + str.encode(" ") + str.encode(message_array[i + 1]) + str.encode(
                    " ") + str.encode(
                    "!@#$|"))
            server.storbinary('APPE chatbot_database.txt', bio, 1)
            database.append([[message_array[i], message_array[i + 1]], "!@#$"])
            break
        else:
            bio = io.BytesIO(
                str.encode(message_array[i]) + str.encode(" ") + str.encode(message_array[i + 1]) + str.encode(
                    " ") + str.encode(message_array[i + 2]) + str.encode("|"))
            server.storbinary('APPE chatbot_database.txt', bio, 1)
            database.append([[message_array[i], message_array[i + 1]], message_array[i + 2]])

    trigger_key = [message_array[0], message_array[1]]
    response = []
    response.append(trigger_key[0])

    while True:
        indices = []
        if trigger_key[1] == "!@#$":
            break
        for i in database:
            if i[0] == trigger_key:
                indices.append(database.index(i))
        rand_index = random.choice(indices)
        response.append(trigger_key[1])
        trigger_key = [database[rand_index][0][1], database[rand_index][1]]

    for i in response:
        response_string += i + " "

    return response_string

isChinese = ["False"]

@app.route("/", methods=["GET", "POST"])
def main():
    isLegal = True
    messages = []
    replies = []
    if request.method == "POST":
        if request.form["action"] == "中文翻译":
            isChinese[0] = "True"
        if request.form["action"] == "English Translation":
            isChinese[0] = "False"
        if request.form["action"] == "Message" or request.form["action"] == "发送消息":
            messages.append(request.form["phrase"])
            for i in request.form["phrase"]:
                if i.isalpha() or i.isdigit():
                    pass
                elif i == " ":
                    pass
                else:
                    replies.append("Your message contains an illegal character.")
                    isLegal = False
                    break
            if isLegal:
                if len(request.form["phrase"].split()) < 2:
                    replies.append("Your message has less than 2 words")
                    isLegal = False
            if isLegal:
                try:
                    replies.append(compute_response(request.form["phrase"]))
                except:
                    if isChinese[0] == "True":
                        replies.append("请刷新网页。如果还是不行就代表网站暂时不能使用")
                    else:
                        replies.append("Error, please refresh the website. If error continues then website is down for the moment.")

    message = ""
    reply = ""
    for i in messages:
        message = "<h3 style='text-align:center'>You: {}</h3>".format(i)
    for i in replies:
        reply = "<h3 style='text-align:center'>Bot: {}</h3>".format(i)

    if isChinese[0] == "True":
        return '''
                    <html>
                        <body>
                            {message}
                            {reply}
                            <h1 style="text-align:center">输入你的对话内容:</h1>
                            <form method="post" action=".">
                                <h2 style="text-align:center"><input type="submit" style="font-size:20pt;" name="action" value="English Translation" /></h2>
                                <h2 style="text-align:center"><input name="phrase" style="font-size:20pt;"/></h2>
                                <h2 style="text-align:center"><input type="submit" style="font-size:20pt;" name="action" value="发送消息" /></h2>
                                <h1 style="text-align:center">重要规则，请读</h1>
                                <h3 style="text-align:center">1. 只能用英语字母表或者数字. 不要发标点符号 (包括句号和逗号) 或者其他语言.</h3>
                                <h3 style="text-align:center">2. 消息至少要有2个单词，中间至少有一个空格</h3>
                                <h3 style="text-align:center">3. 当这个网站正在加载的时候，请不要连续按发消息的按钮</h3>
                                <h1 style="text-align:center">提示</h1>
                                <h3 style="text-align:center">如果这个机器人在重复说你的消息, 这代表你的消息很独特让后机器人正在学习你的消息.</h3>
                                <h3 style="text-align:center">如果这个网站有点慢, 这是因为这个机器人正在和两个网站进行沟通. 请耐心等待，不要忘了第三条规则</h3>
                                <h1 style="text-align:center">关于</h1>
                                <h3 style="text-align:center">这个机器人使用“马可夫链”. 它的目的是学习人类的对话, 让后写出合理的句子. 如果你想知道这个机器人怎么工作, <a href="/about"> 点这里</a></h3>
                            </form>
                        </body>
                    </html>
                '''.format(message=message, reply=reply)
    else:
        return '''
                <html>
                    <body>
                        {message}
                        {reply}
                        <h1 style="text-align:center">Enter your message:</h1>
                        <form method="post" action=".">
                            <h2 style="text-align:center"><input type="submit" style="font-size:20pt;" name="action" value="中文翻译" /></h2>
                            <h2 style="text-align:center"><input name="phrase" style="font-size:20pt;"/></h2>
                            <h2 style="text-align:center"><input type="submit" style="font-size:20pt;" name="action" value="Message" /></h2>
                            <h1 style="text-align:center">Important rules please read</h1>
                            <h3 style="text-align:center">1. Only use the English Alphabet and numbers. No symbols (include comma and full stops) or characters in other languages.</h3>
                            <h3 style="text-align:center">2. Message must be at least 2 words with a space in between it.</h3>
                            <h3 style="text-align:center">3. Please do not press message button again right after you pressed it, while the page is loading.</h3>
                            <h1 style="text-align:center">Tips</h1>
                            <h3 style="text-align:center">If the bot is repeating your message, that means your phrase is too original and the bot is learning your message.</h3>
                            <h3 style="text-align:center">If the page is a bit slow, that is because this bot is communicating with 2 websites. Please wait patiently and refer to rule 3</h3>
                            <h1 style="text-align:center">About</h1>
                            <h3 style="text-align:center">This bot is built using Markov chains. The aim is to learn messages written by human, in order to write realstic sentences. To learn more about Markov chains and how this bot functions, click<a href="/about"> Here</a></h3>
                        </form>
                    </body>
                </html>
            '''.format(message=message, reply=reply)

@app.route("/about")
def about():
    return '''
            <html>
                <body>
                    <h3 style="text-align:center">Markov chains attempts to build realistic sentences by breaking a sentence into small overlapping chunks. 
                    For instance, "hello how are you" would be broken into: (hello how are) (how are you) (are you STOPSIGNAL)
                    Each chunk consists of two bits. The first bit is the "trigger phrase", the second bit is the "word".
                    The bot will take the first two words of your message, and match it with "trigger phrases" inside its database.
                    Once it matches, then the particular chunk will be added to the response. Then, the trigger phrase
                    becomes the next two words, and the process repeats until the STOPSIGNAL is reached, and the response is finished.
                    For example, if my message was "hello how is your dad" and the bot has "hello how are you" in its database, then
                    the bot takes the first two words (trigger phrase), and tries to match "hello how" to any existing trigger phrases 
                    in its database. Since there is "hello how are you", the match succeeds, and then the bot's trigger phrase becomes 
                    "how are" instead. The other popular way to implement a chatbot is through deep learning, and deep learning is a more
                    widely accepted method of building a bot. The advantages of a Markov chain is that it is much faster to train, but at the 
                    same time it cannot produce reliable responses vs deep learning.</h3>
                </body>
            </html>
    '''

while True:
    app.run()