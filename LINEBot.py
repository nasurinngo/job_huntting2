import os
import logging
logger = logging.getLogger()
logger.setLevel(logging.INFO)
from linebot import (
    LineBotApi, WebhookHandler
)
from linebot.models import (
    MessageEvent, TextMessage, TextSendMessage,
    TemplateSendMessage, ButtonsTemplate,
    PostbackEvent
)
LINE_CHANNEL_ACCESS_TOKEN   = os.environ['LINE_CHANNEL_ACCESS_TOKEN']
LINE_CHANNEL_SECRET         = os.environ['LINE_CHANNEL_SECRET']
LINE_BOT_API = LineBotApi(LINE_CHANNEL_ACCESS_TOKEN)
LINE_HANDLER = WebhookHandler(LINE_CHANNEL_SECRET)

flag = 0    #質問受付中か否かの判定、「flag == 0」の場合は初期状態、「flag == 1」の場合は質問受付状態

def lambda_handler(event, context):
    
    logger.info(event)
    signature = event["headers"]["x-line-signature"]
    body = event["body"]

    # テキストメッセージを受け取った時に呼ばれるイベント
    @LINE_HANDLER.add(MessageEvent, message=TextMessage)
    def on_message(line_event):
        global flag
        # ユーザー情報を取得する
        profile = LINE_BOT_API.get_profile(line_event.source.user_id)
        logger.info("下記ログは「flag」と「line_event」と「profile」である")    #以下三行はCloudWatchにてデバッグ時に確認用のコードである
        logger.info(flag)
        logger.info(line_event)
        logger.info(profile)
        message = line_event.message.text.lower()
        if message == '質問' and flag == 0:     #テキストが「質問」かつflagが「0」
            LINE_BOT_API.reply_message(line_event.reply_token, make_requirement_message())
        elif message == 'サイト' and flag == 0: #テキストが「サイト」かつflagが「0」
            LINE_BOT_API.reply_message(line_event.reply_token, TextSendMessage("HoPs質問サイトのURLになります！\nhttps://www.hus.ac.jp/"))  #今は北海道科学大学方式HPのURL
        elif message == '初期化':               #テキストが「初期化」
            flag = 0                            #flagを「0」にする
            LINE_BOT_API.reply_message(line_event.reply_token, TextSendMessage("これは開発用デバッグコマンドです。\nflagを0に初期化しました。"))
        elif flag == 0:                         #flagが0の時は初期状態のため、質問を受け取らない。
            LINE_BOT_API.reply_message(line_event.reply_token, TextSendMessage("こんにちは！\n何か質問がある場合は「質問」と、HoPs質問サイトが知りたい場合は「サイト」と送信してください！"))
        else:                                   #elseでまとめているが、「flag == 1」の質問受付状態のことである
            flag = 0                            #flagを「0」に初期化する
            LINE_BOT_API.reply_message(line_event.reply_token, TextSendMessage("質問を受け取りました！\nWebサイトで回答を掲示いたしますので数日お待ち下さい\n回答が完成しましたらまたご連絡します"))

    # 質問から選ばれた時(postback)に呼ばれるイベント
    @LINE_HANDLER.add(PostbackEvent)
    def on_postback(line_event):
        global flag
        logger.info("下記ログは「line_event.postback」である")
        logger.info(line_event.postback)
        data = line_event.postback.data
        #if文で質問を押した後にどの質問に移るかの記述を「line_event.postback.data」を参照することでどの処理に移るかを制御する
        if data =="entrance_examination":
            LINE_BOT_API.reply_message(line_event.reply_token, make_entrance_examination_message())
        elif data =="college_life":
            LINE_BOT_API.reply_message(line_event.reply_token, make_college_life_message())
        elif data =="cancel":       #キャンセル処理も作ってみたが、使用していない。悲しいね。
            LINE_BOT_API.reply_message(line_event.reply_token, TextSendMessage("キャンセル承りました！\nまた質問がある場合は「質問」と送信してください"))
        elif data =="other":
            flag = 1                #flagを「1」にする
            LINE_BOT_API.reply_message(line_event.reply_token, TextSendMessage("質問をお書きください！"))
        elif data =="hops":
            LINE_BOT_API.reply_message(line_event.reply_token, TextSendMessage("HoPsとは高校と大学を繋げることを目的とした団体です！\n何かHoPsに連絡をしたい場合は、その他の質問の方に書いていただければこちらで確認します！"))
        else:
            flag = 0
            LINE_BOT_API.reply_message(line_event.reply_token, TextSendMessage("承知しました！\nまた質問がある場合は「質問」と送信してください"))
    LINE_HANDLER.handle(body, signature)
    return 0

def make_requirement_message():         #質問要件の提示関数
    return TemplateSendMessage(
        alt_text="質問",
        template=ButtonsTemplate(
            title="どのような質問ですか？",
            text="下から1つ選んでね！",
            actions=[
                {
                    "type": "postback",
                    "data": "college_life",
                    "label": "大学生活について"
                },
                {
                    "type": "postback",
                    "data": "entrance_examination",
                    "label": "大学入試について"
                },
                {
                    "type": "postback",
                    "data": "hops",
                    "label": "HoPsとは何ですか？"
                },
                {
                    "type": "postback",
                    "data": "other",
                    "label": "その他"
                }
            ]
        )
    )

def make_entrance_examination_message():
    return TemplateSendMessage(
        alt_text="質問",
        template=ButtonsTemplate(
            title="入試形態は決まっていますか？",
            text="下から1つ選んでね！",
            actions=[
                {
                    "type": "postback",
                    "data": "other",
                    "label": "一般入試"
                },
                {
                    "type": "postback",
                    "data": "other",
                    "label": "推薦入試"
                },
                {
                    "type": "postback",
                    "data": "other",
                    "label": "ガリレオ"
                },                
                {
                    "type": "postback",
                    "data": "other",
                    "label": "未定"
                }
            ]
        )
    )

def make_college_life_message():
    return TemplateSendMessage(
        alt_text="質問",
        template=ButtonsTemplate(
            title="どういった大学生活への質問ですか？",
            text="下から1つ選んでね！",
            actions=[
                {
                    "type": "postback",
                    "data": "other",
                    "label": "大学での講義について"
                },
                {
                    "type": "postback",
                    "data": "other",
                    "label": "大学での部活動について"
                },
                {
                    "type": "postback",
                    "data": "other",
                    "label": "アルバイトについて"
                },                
                {
                    "type": "postback",
                    "data": "other",
                    "label": "その他"
                }
            ]
        )
    )