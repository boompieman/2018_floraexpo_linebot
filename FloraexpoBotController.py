# coding=UTF-8

# -*- coding: UTF-8 -*-

from flask import Flask, request, abort, make_response, jsonify

from linebot import (
    LineBotApi, WebhookHandler
)
from linebot.exceptions import (
    InvalidSignatureError
)

from linebot.models import (
    MessageEvent, TextMessage, TextSendMessage,
    SourceUser, SourceGroup, SourceRoom,
    TemplateSendMessage, ConfirmTemplate, MessageAction,
    ButtonsTemplate, ImageCarouselTemplate, ImageCarouselColumn, URIAction,
    PostbackAction, DatetimePickerAction,
    CameraAction, CameraRollAction, LocationAction,
    CarouselTemplate, CarouselColumn, PostbackEvent,
    StickerMessage, StickerSendMessage, LocationMessage, LocationSendMessage,
    ImageMessage, VideoMessage, AudioMessage, FileMessage,
    UnfollowEvent, FollowEvent, JoinEvent, LeaveEvent, BeaconEvent,
    FlexSendMessage, BubbleContainer, ImageComponent, BoxComponent,
    TextComponent, SpacerComponent, IconComponent, ButtonComponent,
    SeparatorComponent, QuickReply, QuickReplyButton
)

import tempfile
import os, datetime
from urllib.parse import unquote, quote


from FloraBot import FloraBot
import json
from RedisManager import RedisManager
from all_venues import all_venues
from ScheduleManager import ScheduleManager
from AdvancedScheduleManager import AdvancedScheduleManager

from chatbase import Message

application = Flask(__name__)

with open("./sources/line_bot_token.json", 'r') as f:
    
    
    json_data = json.load(f)
    access_token = json_data["access_token"]
    channel_secret = json_data["channel_secret"]

line_bot_api = LineBotApi(access_token)
handler = WebhookHandler(channel_secret)

flora = FloraBot()
redisManager = RedisManager()


## test advanced schedule manager

advancedScheduleManager = AdvancedScheduleManager()

STATIC_TMP_PATH = os.path.join(os.path.dirname(__file__), 'static', 'tmp')
    

@application.route("/callback", methods=['POST'])
def callback():
    
    # get X-Line-Signature header value
    signature = request.headers['X-Line-Signature']

    # get request body as text
    body = request.get_data(as_text=True)
    
    application.logger.info("Request body: " + body)

    # handle webhook body
    try:
        handler.handle(body, signature)

    except InvalidSignatureError:

        abort(400)
    
    return 'OK'


@handler.add(FollowEvent)
def handle_follow(event):

    flora.send_greeting_message(event.reply_token)
    flora.link_rich_menu(event.source.user_id)


@handler.add(JoinEvent)
def handle_join(event):
    
    flora.send_greeting_message(event.reply_token)
    
@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    
    text = event.message.text.lower()

#     秀出三個園區分別的展館
    if text == "聯絡客服":
        
        flora.send_customerService_message(event.reply_token)

    elif text == "后里馬場" or text == "森林園區" or text == "外埔園區" or text == "葫蘆墩公園":
        
        chatbase_msg = Message(
            api_key="api_key", 
            type="user",
            platform="Line",
            version="1.0",
            user_id=event.source.user_id,
            message=event.message.text,
            intent="start_" + event.message.text
        )

        resp =chatbase_msg.send() 

        redisManager.set_userDist(event.source.user_id, dist=text)
        
        flora.send_functionList_message(event.reply_token, dist=text)     
        
    elif text == "查詢不用排隊的展館":
        
        dist = redisManager.get_userDist(event.source.user_id)
        
        if dist == None:
            
            flora.send_no_dist_message(event.reply_token)
            
            return
        
        chatbase_msg = Message(
            api_key="api_key", 
            type="user",
            platform="Line",
            version="1.0",
            user_id=event.source.user_id,
            message=event.message.text,
            intent="查詢不用排隊的展館_" + dist
        )

        resp =chatbase_msg.send()            
        
        
        dist_venues = get_currentDist_venues(dist)      
        
        noLine_venues = redisManager.get_noLine_dist_venues(dist_venues)
        
        flora.send_dist_noLine_venues(event.reply_token, dist=dist, noLine_venues=noLine_venues)
        
    elif text == "查詢特定展館資訊":

        dist = redisManager.get_userDist(event.source.user_id)
        
        if dist == None:
            
            flora.send_no_dist_message(event.reply_token)
            
            return
        
        chatbase_msg = Message(
            api_key="api_key",
            type="user",
            platform="Line",
            version="1.0",
            user_id=event.source.user_id,
            message=event.message.text,
            intent="查詢特定展館資訊_" + dist
        )

        resp =chatbase_msg.send()          
        
    
        dist_venues = get_currentDist_chosenVenues(dist)
        
        flora.send_askDistVenues_message(event.reply_token ,dist_venues)
        
        
    elif "排隊提醒" in text:
        
        venue = get_venue(text)
        
        flora.send_ensureIfLine_message(event.reply_token, venue)        
    
    
#     elif text == "查詢展館是否需要排隊":
#         flora.send_ask_venue(event.reply_token, signal="guest-ifLine")
        
    
#     elif text == "查詢展館人潮現況":
        
#         flora.send_ask_venue(event.reply_token, signal="guest-currentSituation")
        
#     elif text == "查詢哪些展館不用排隊":
        
#         noLine_venues = redisManager.get_noLine_venues()
#         flora.send_noLine_venues(event.reply_token, noLine_venues)
    
#     elif text == "查詢展館如何到達":
#         flora.send_ask_venue(event.reply_token, signal="guest-askLocation")
        
#     elif text == "我在哪裡":
#         flora.send_myLocation_message(event.reply_token)
        
        
        
    # 管理小幫手    
        
    
    elif "管理" in text:
        flora.send_manager_menu_message(event.reply_token)

    elif text == "登入" or text == "login":
        flora.send_ask_venue(event.reply_token, signal="manager-login")        
        
    elif text == "更正展館排隊資訊":
        flora.send_ask_venue(event.reply_token, signal="manager-ifLine")
        
    elif text == "新增展館人潮現況照片":
        flora.send_ask_venue(event.reply_token, signal="manager-currentSituation")
        
        
    # 比較是不是展館名稱 （因為演算法速度把它放最下面）
    elif isVenueEqualMessage(text):
        
        # 未來會有簡寫表，可能要有正名的 code，用dict去轉換
        
        dist = redisManager.get_userDist(event.source.user_id)
        
        title = synonym2title(text)
        
        status = get_status(title)

        if dist == None:

            flora.send_no_dist_message(event.reply_token)

            return
        
        chatbase_msg = Message(
            api_key="api_key",
            type="user",
            platform="Line",
            version="1.0",
            user_id=event.source.user_id,
            message="展館資訊_" + title,
            intent="展館資訊"
        )

        resp =chatbase_msg.send()   

        dist_venues = get_currentDist_venues(dist)            

        noLine_venues = redisManager.get_noLine_dist_venues(dist_venues)

        flora.send_ifLineResult_message(event.reply_token, venue=title.lower(), status=status, dist=dist, noLine_venues=noLine_venues)        
        
#         flora.send_venueFunction_message(event.reply_token, venue = title)           
    
    # 給我檢測用
    elif text == "get queue":
        len_queue = advancedScheduleManager.get_queue()
        flora.pprint(str(len_queue))
        
#     elif text == "run once":
        
#         if scheduleManager.run_once() != None:
#             flora.pprint(scheduleManager.run_once())
#         else:
#             flora.pprint("queue is empty")
            
    elif text == "test":
        
        advancedScheduleManager.test_scheduler(bot=flora)
        
    elif text == "get id":
        if isinstance(event.source, SourceGroup):
            print(event.source)
            print('group id: ' + event.source.group_id)
            line_bot_api.reply_message(
                event.reply_token, TextSendMessage(text='group id: ' + event.source.group_id))
            
        elif isinstance(event.source, SourceRoom):
            print('group id: ' + event.source.room_id)
            line_bot_api.reply_message(
                event.reply_token, TextSendMessage(text='room id: ' + event.source.room_id))
        else:
            print(event.source)
            print('user id: ' + event.source.user_id)
            line_bot_api.reply_message(
                event.reply_token, TextSendMessage(text="user id: " + event.source.user_id))        

@handler.add(PostbackEvent)
def handle_postback(event):
    
    ## ifLine StroyLine
    if "ifLine" in event.postback.data:
        
        venue = get_venue(event.postback.data)
        status = get_status(venue)
        
        if "guest-ifLine" in event.postback.data:
            
            dist = redisManager.get_userDist(event.source.user_id)
            
            if dist == None:
                
                flora.send_no_dist_message(event.reply_token)
            
                return                
            
            dist_venues = get_currentDist_venues(dist)      
        
            noLine_venues = redisManager.get_noLine_dist_venues(dist_venues)

            flora.send_ifLineResult_message(event.reply_token, venue=venue, status=status, dist=dist, noLine_venues=noLine_venues)
        
        elif "remind-ifLine" in event.postback.data:

            if "no" in event.postback.data:
                flora.send_remind_no_message(event.reply_token)

            else:
                
                chatbase_msg = Message(
                    api_key="api_key",
                    type="user",
                    platform="Line",
                    version="1.0",
                    user_id=event.source.user_id,
                    message="註冊提醒_" + venue,
                    intent="註冊提醒"
                )

                resp =chatbase_msg.send()                 
                
                redisManager.set_ifLine_remind(postback_data = event.postback.data, user_id = event.source.user_id)
                flora.send_remind_yes_message(event.reply_token)
            
        elif "manager-ifLine" in event.postback.data:
            
            if redisManager.get_account(event.source.user_id, venue) != None:
            
                flora.send_correctIfLine_message(event.reply_token, status=status, venue=venue)
                
            else:
                
                flora.send_login_message(event.reply_token, venue=venue, ifRemind=True, action="ifLine")

        elif "correct-ifLine" in event.postback.data:
                
            if "no" in event.postback.data:
                
                flora.send_manager_menu_message(event.reply_token)

            else:

                newStatus = get_ifLine_newStatus(event.postback.data)

                flora.send_ensure_correctIfLine_message(event.reply_token, venue = venue, status=newStatus)

        elif "ensure-ifLine" in event.postback.data:

            if "no" in event.postback.data:

                flora.send_manager_menu_message(event.reply_token)

            # after manager ensure ifLine status, bot will set status and push notification to registed users.
            else:

                newStatus = get_ifLine_newStatus(event.postback.data)
                
                redisManager.set_ifLine_status(venue=venue,status=newStatus)
                
                if isNewStatusOkayForRemind(newStatus=newStatus):

                    push_remind_list = redisManager.get_remind_list(venue=venue)

                    if push_remind_list != None:

                        flora.push_remind_notification(to=push_remind_list, venue=venue, status=newStatus)

                        redisManager.delete_remind_list(venue=venue)

                flora.send_finishCorrect_message(event.reply_token)

    ## currentSituation StroyLine        
    elif "currentSituation" in event.postback.data:
        
        if "guest-currentSituation" in event.postback.data:
            
            venue = get_venue(event.postback.data)
            
            listOfFiles = os.listdir(STATIC_TMP_PATH + "/" + venue)

            listOfFiles.sort(key=lambda x:int(x.split("-")[1]), reverse=True)
            
            listOfFiles = listOfFiles[:3]
            
            pictures = []
            
            for entry in listOfFiles:
                
                picture_path = STATIC_TMP_PATH + "/" + venue + "/" + entry
                
                pic = quote(picture_path)

                timeStamp = entry.split("-")[1][:-3]
                
                struct_time = datetime.datetime.utcfromtimestamp(int(timeStamp))
                
                struct_time = struct_time + datetime.timedelta(hours = 8)
                
                ctime = struct_time.strftime("%Y-%m-%d %H:%M:%S")
                
                picture_dict = { "path": pic, "ctime": ctime } 
                
                pictures.append(picture_dict)
                
            chatbase_msg = Message(
                    api_key="api_key",
                    type="user",
                    platform="Line",
                    version="1.0",
                    user_id=event.source.user_id,
                    message="查看場館照片_" + venue,
                    intent="查看場館照片"
                )

            resp =chatbase_msg.send()

            flora.send_currentSituation_picture_message(event.reply_token, pictures)
                
#             flora.send_ifProblem_message(event.reply_token)
        
        if "manager-currentSituation" in event.postback.data:

            venue = get_venue(event.postback.data)
            
            if redisManager.get_account(event.source.user_id, venue) != None:
            
                flora.send_correctCurrent_message(event.reply_token,venue=venue)

                redisManager.set(key=event.source.user_id + "_correct_currentSituation_venue", value= venue)
                
            else:
                                                                                    
                flora.send_login_message(event.reply_token, venue=venue, ifRemind=True, action="currentSituation")

        elif event.postback.data == "correct-currentSituation-no":

            flora.send_manager_menu_message(event.reply_token)

        elif event.postback.data == "ensure-currentSituation-no":

            path = redisManager.get(event.source.user_id + "_tmp_picture")
            os.remove(path)
            flora.send_manager_menu_message(event.reply_token)

        elif event.postback.data == "ensure-currentSituation-yes":

            flora.send_finishCorrect_message(event.reply_token)

    
    ## askLocation StroyLine         
#     elif "askLocation" in event.postback.data:

#         venue = get_venue(event.postback.data)
       
#         locationInfoDict = redisManager.get_locationInfoDict(venue=venue)
        
#         flora.send_venueLocation_message(event.reply_token, locationInfoDict)
    
    elif "login" in event.postback.data:
        
        venue = get_venue(event.postback.data)
        
        flora.send_login_message(event.reply_token, venue=venue)
        
#         直接給展館位置 + 花博官網交通資訊
                
    elif event.postback.data == "another_question_no":
        flora.send_endConversation_message(event.reply_token)

    elif event.postback.data == "another_question_yes":
        flora.send_menu_message(event.reply_token)
    
@handler.add(MessageEvent, message=(ImageMessage, VideoMessage))
def handle_content_message(event):
    
    if isinstance(event.message, ImageMessage):
        ext = 'jpg'
    else:
        return
    
    

    venue = redisManager.get(event.source.user_id + "_correct_currentSituation_venue")
    
    if redisManager.get_account(event.source.user_id, venue) != None:
        
        venue = venue.lower()
        
#         print(event.message.id)
    
        message_content = line_bot_api.get_message_content(event.message.id)

        if not os.path.isdir(STATIC_TMP_PATH + "/" + venue):
            os.mkdir(STATIC_TMP_PATH + "/" + venue)


        ## 幫忙做圖
        with tempfile.NamedTemporaryFile(dir=STATIC_TMP_PATH + "/" + venue, suffix= '-' + str(event.timestamp) + '-_' + venue, delete=False) as tf:
            for chunk in message_content.iter_content():
                tf.write(chunk)
            tempfile_path = tf.name


        dist_path = tempfile_path + '.' + ext
        dist_name = os.path.basename(dist_path)
        os.rename(tempfile_path, dist_path)

        redisManager.set(key=event.source.user_id + "_tmp_picture", value=dist_path)

        flora.send_ensure_correctCurrent_message(event.reply_token, venue=venue)
        
        advancedScheduleManager.reset_venue(bot=flora, venue=venue)
        

def get_status(venue):
    
    if redisManager.get_ifLine_status(venue=venue) == None:
        return "不用排隊"
    else:
        return redisManager.get_ifLine_status(venue=venue)

def get_venue(postback_data):
    
    return postback_data.split("_")[-1]

def get_ifLine_newStatus(postback_data):
    
    if postback_data.split("_")[-2] == "0":
        return "不用排隊"
    
    elif postback_data.split("_")[-2] == "15":
        return "排隊時間在15分鐘以內"
    
    elif postback_data.split("_")[-2] == "30" or postback_data.split("_")[-2] == "45":
        return "要排隊約莫" + postback_data.split("_")[-2] + "分鐘"
    
    elif postback_data.split("_")[-2] == "60":
        return "要排隊超過1小時"
    
    else:
        return postback_data.split("_")[-2]
    
    
def get_currentDist_venues(dist):
    
    dist_venues = [] 
    
    for venue in all_venues:
        if dist == venue["dist"]:

            dist_venues.append(venue)
            
                   
    return dist_venues

def get_currentDist_chosenVenues(dist):
    
    dist_venues = []
    
    for venue in all_venues:
        if dist == venue["dist"]:
            dist_venues.append(venue)
            
    return dist_venues

def isVenueEqualMessage(message):

    for venue in all_venues:
        for synonym in venue['synonyms']:
            if message == synonym.lower():
            
                return True
        
    return False

def synonym2title(message):
    for venue in all_venues:
        for synonym in venue['synonyms']:
            if message == synonym.lower():
            
                return venue['title']

def isNewStatusOkayForRemind(newStatus):
    
    if "15" in newStatus or '不用排隊' in newStatus:
        return True
    
    return False
    
#     if "小時" in status:
#         wait_minute = 60
    
#     elif "小時" in newStatus:
#         new_wait_minute = 60
        
#     else:
#         wait_minute = int(status[5:7])
#         new_wait_minute = int(newStatus[5:7])
        
    
#     if newStatus < status:
#         return True
    
#     return False
        
    
    

@application.route("/")
def hello():
    return "<h1 style='color:blue'>Hello World!</h1>"

@application.route('/manager' , methods=['POST'])
def create_manager():
    
    request_data = request.get_json()
    

    new_manager = {
        'uid': request_data['uid'],
        'venue': request_data['venue']
    }
    
    venue = unquote(unquote(new_manager['venue']))
    
    redisManager.set_account(new_manager['uid'], venue)
    
    return jsonify({"message": "login success"})    

@application.route('/manager/<string:venue>/<string:uid>')
def get_manager(uid, venue):
    
    if redisManager.get_account(uid, venue) != None:

        message = {
            'uid': uid,
            'venue': venue,
            'character': "manager"
        }

        return jsonify({"message": "true"})

if __name__ == "__main__":
    application.run(host='0.0.0.0')
    