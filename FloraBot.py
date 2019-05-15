# -*- coding: UTF-8 -*-

from linebot import (
    LineBotApi
)

from linebot.models import (
    MessageEvent, TextMessage, TextSendMessage,
    SourceUser, SourceGroup, SourceRoom,
    TemplateSendMessage, ConfirmTemplate, MessageAction,
    ButtonsTemplate, ImageCarouselTemplate, ImageCarouselColumn, URIAction,
    PostbackAction, DatetimePickerAction,
    CameraAction, CameraRollAction, LocationAction, MessageImagemapAction,
    CarouselTemplate, CarouselColumn, PostbackEvent,
    StickerMessage, StickerSendMessage, LocationMessage, LocationSendMessage,
    ImageMessage, VideoMessage, AudioMessage, FileMessage, ImageSendMessage, ImagemapSendMessage, BaseSize, ImagemapArea,
    UnfollowEvent, FollowEvent, JoinEvent, LeaveEvent, BeaconEvent,
    FlexSendMessage, BubbleContainer, ImageComponent, BoxComponent,
    TextComponent, SpacerComponent, IconComponent, ButtonComponent,
    SeparatorComponent, QuickReply, QuickReplyButton, VideoSendMessage,
    URITemplateAction
)

from BotError import *
import json
from urllib.parse import unquote, quote

DEFAULT_RICHMENU_ID = "richmenu-9ea73cf0bc89e63a592e49ec8376576e"

class FloraBot:
    
    def __init__(self):

        with open("./sources/line_bot_token.json", 'r') as f:
            access_token = json.load(f)["access_token"]        
        
        self.line_bot_api = LineBotApi(access_token)
    
    def send_greeting_message(self, reply_token):
        
        newcoming_text = "能為您提供熱門展館的即時資訊，首先請您先選擇想查詢的園區："  
        
        buttons_template = ButtonsTemplate(
            title="您好，我是台中花博的智能小幫手！", text=newcoming_text, actions=[

                MessageAction(label='后里馬場',text='后里馬場'),
                MessageAction(label='森林園區',text='森林園區'),
                MessageAction(label='外埔園區',text='外埔園區'),
                MessageAction(label='葫蘆墩公園',text='葫蘆墩公園'),                 
            ])

        template_message = TemplateSendMessage(
            alt_text=newcoming_text, template=buttons_template)
        
        self.line_bot_api.reply_message(reply_token, template_message)
        
    def send_customerService_message(self, reply_token):
        
        buttons_template = ButtonsTemplate(
            title="如果人在臺中市，我們有不同服務喔！", text="於臺中市請撥市民一碼通1999，\n於外縣市請撥0422203585", actions=[
                URITemplateAction(label="於台中市", uri="tel://1999"),
                URITemplateAction(label="於外縣市", uri="tel://04-22203585"),
            ])

        template_message = TemplateSendMessage(
            alt_text="你現在在哪個園區呢？可以先告訴我嗎？", template=buttons_template)
        
        self.line_bot_api.reply_message(reply_token, template_message)            
        
        
    def send_no_dist_message(self, reply_token):
        
        buttons_template = ButtonsTemplate(
            title="你現在在哪個園區呢？", text="可以先告訴我嗎？", actions=[

                MessageAction(label='后里馬場',text='后里馬場'),
                MessageAction(label='森林園區',text='森林園區'),
                MessageAction(label='外埔園區',text='外埔園區'),
                MessageAction(label='葫蘆墩公園',text='葫蘆墩公園'),                      
            ])

        template_message = TemplateSendMessage(
            alt_text="你現在在哪個園區呢？", template=buttons_template)
        
        self.line_bot_api.reply_message(reply_token, template_message)        
        
    def link_rich_menu(self,user_id):
        self.line_bot_api.link_rich_menu_to_user(user_id,DEFAULT_RICHMENU_ID)
    
    
    def send_menu_message(self, reply_token):
        buttons_template = ButtonsTemplate(
            title='您好，我是台中花博的智能小幫手！', text='請問你在哪個園區呢？', actions=[

                MessageAction(label='后里馬場',text='后里馬場'),
                MessageAction(label='森林園區',text='森林園區'),
                MessageAction(label='外埔園區',text='外埔園區'),
                MessageAction(label='葫蘆墩公園',text='葫蘆墩公園'),            
            ])

        template_message = TemplateSendMessage(
            alt_text='我是你的智能小幫手', template=buttons_template)

        self.line_bot_api.reply_message(reply_token, messages=template_message)
        
    
    def send_functionList_message(self, reply_token, dist):
            
        buttons_template = ButtonsTemplate(
            title= dist + '智能小幫手', text='請問你想要知道' + dist + '目前的什麼資訊呢？', actions=[

                MessageAction(label='查詢特定展館資訊', text='查詢特定展館資訊'),
                MessageAction(label='查詢不用排隊的展館', text='查詢不用排隊的展館'),          
            ])

        template_message = TemplateSendMessage(
            alt_text='我是你的智能小幫手', template=buttons_template)

        self.line_bot_api.reply_message(reply_token, messages=template_message)
        
    def send_ask_venue(self, reply_token, signal):
        
        if  "guest" in signal:
        
            text_message = TextMessage(text='請問你是要問哪個館呢？')

            template_message = self._generate_venue(signal=signal)

            self.line_bot_api.reply_message(reply_token, messages=[text_message, template_message])
            
        elif "manager" in signal:
            
            text_message = TextMessage(text='OKOK！那想再請問你是哪個館區的管理人員呢？')

            template_message = self._generate_venue(signal=signal)
            
            self.line_bot_api.reply_message(reply_token, messages=[text_message, template_message])
            
    def send_noLine_venues(self, reply_token, noLine_venues):
        
        text = ""
        
        for venue in noLine_venues:
            text = text + venue["title"] + "\n"
        
        text += "目前以上展館不用排隊，歡迎民眾前往參觀。"
        
        text_message = TextMessage(text=text)
        
        template_message = self._generate_anotherQuestion_confirmTemplate()       
        
        self.line_bot_api.reply_message(reply_token, messages=[text_message, template_message])
        
    def send_dist_noLine_venues(self, reply_token, dist, noLine_venues):
        
        text_message = TextMessage(text= "以下是" + dist + "目前不用排隊的展館")
        
        carousel_template_message = self._generate_noLine_venues_message(noLine_venues=noLine_venues)
        
        buttons_template = ButtonsTemplate(
            title= '想看看' + dist + '的其他資訊嗎？', text=dist, actions=[

                MessageAction(label='查詢特定展館資訊', text='查詢特定展館資訊'),  
            ])

        buttons_template_message = TemplateSendMessage(
            alt_text='想看看' + dist + '的其他資訊嗎？', template=buttons_template)        
                           
        self.line_bot_api.reply_message(reply_token, messages=[text_message, carousel_template_message, buttons_template_message])
        
    def send_askDistVenues_message(self, reply_token, dist_venues):
        
        template_message = self._generate_dist_venues(dist_venues=dist_venues)

        self.line_bot_api.reply_message(reply_token, messages=[template_message])


    def send_venueFunction_message(self, reply_token, venue):
        
        buttons_template = ButtonsTemplate(
            title='想知道' + venue + '的哪個即時資訊呢？', text='即時資訊引導', actions=[

                PostbackAction(label= "現場要排隊嗎？", data='guest-ifLine_'+ venue ,text= "現場要排隊嗎？"),
                PostbackAction(label= "現場人潮狀況如何呢？（照片）", data='guest-currentSituation_'+ venue ,text= "現場人潮狀況如何呢？"),
                URIAction(label='連結花博app (iOS)',uri='https://itunes.apple.com/tw/app/taichung-worldfloraexposition/id1438719939?l=en&mt=8&fbclid=IwAR2ZE2bFKVdNjHNCu6W2ONGRuk4LsLJ7gDyAZxVkV1vu6rfSIHPVT2oIb0s'),
                URIAction(label='連結花博app (Android)',uri='https://play.google.com/store/apps/details?id=com.luci.TaichungWorldFloraExposition&fbclid=IwAR0UEQFl1NzkkuSxro6JrDKGOM5oyHjNgwm7Y47-xgkJg66SHwEvB7Xv_Aw') 
            ])

        template_message = TemplateSendMessage(
            alt_text='想知道' + venue + '的什麼資訊呢？', template=buttons_template)

        self.line_bot_api.reply_message(reply_token, messages=template_message)        
        
        
    def send_ifLineResult_message(self, reply_token, venue, status, dist, noLine_venues):
        
        if venue == "臺中市不動產開發公會竹跡館" or venue == "楷模創生館":
            buttons_template = ButtonsTemplate(
                title='想看看' + dist + '的其他資訊嗎？', text='請點擊以下按鈕', actions=[
                    MessageAction(label='查詢其他展館資訊', text='查詢特定展館資訊'),
                    MessageAction(label='查詢不用排隊的展館', text='查詢不用排隊的展館')         
                ])            
            
        else:    
            buttons_template = ButtonsTemplate(
                title='想看看' + dist + '的其他資訊嗎？', text='請點擊以下按鈕', actions=[

                    PostbackAction(label="現場人潮照片", data='guest-currentSituation_'+ venue),
                    MessageAction(label='查詢其他展館資訊', text='查詢特定展館資訊'),
                    MessageAction(label='查詢不用排隊的展館', text='查詢不用排隊的展館')         
                ])

        buttons_template_message = TemplateSendMessage(
            alt_text='想看看' + dist + '的其他資訊嗎？', template=buttons_template)
        
        if "不用排隊" in status:
            pic_url = quote(venue + "_0" + ".png")

            imagemap_message = ImagemapSendMessage(
                base_url= "https://2018floraexpo.tk/static/sources/ifLine/" + pic_url + "#v1.0/1024",
                alt_text= venue + status,
                base_size= BaseSize(height=1024, width=1024),
                actions=[
                    MessageImagemapAction(
                        text="目前不用排隊，\n可以快快去" + venue + "卡位喔^_^",
                        area=ImagemapArea(
                            x=0, y=0, width=1024, height=1024
                        )
                    )
                ]
            )

            self.line_bot_api.reply_message(reply_token, [imagemap_message, buttons_template_message])
            
            return        
        
        if "15" in status:
            pic_url = quote(venue + "_15" + ".png") 

            imagemap_message = ImagemapSendMessage(
                base_url= "https://2018floraexpo.tk/static/sources/ifLine/" + pic_url + "#v1.1/1024",
                alt_text= venue + status,
                base_size= BaseSize(height=1024, width=1024),
                actions=[
                    MessageImagemapAction(
                        text="目前排隊時間很少，\n可以快快去" + venue + "卡位喔^_^",
                        area=ImagemapArea(
                            x=0, y=0, width=1024, height=1024
                        )
                    )
                ]
            )

            self.line_bot_api.reply_message(reply_token, [imagemap_message, buttons_template_message])
            
            return
        
        
        
        if "30分鐘" in status or "45分鐘" in status:
            minute = status.split("分")[0].split("約莫")[1]
            pic_url = quote( venue + "_" + minute + ".png")
            

            
        elif "1小時" in status:
            pic_url = quote(venue + "_60" + ".png")
            
        imagemap_message = ImagemapSendMessage(
            base_url= "https://2018floraexpo.tk/static/sources/ifLine/" + pic_url + "#v1.2/1024",
            alt_text= venue + status,
            base_size= BaseSize(height=1024, width=1024),
            actions=[
                MessageImagemapAction(
                    text="我要申請排隊提醒_" + venue,
                    area=ImagemapArea(
                        x=0, y=0, width=1024, height=1024
                    )
                )
            ]
        )
        
        text_message = TextMessage(text= venue + "等待入館時間較久，歡迎您先前往" + dist + "內其他不用排隊的展館喔")
        
        carousel_template_message = self._generate_noLine_venues_message(noLine_venues=noLine_venues)

        self.line_bot_api.reply_message(reply_token, [imagemap_message, buttons_template_message])
        
        
#         confirm_template = ConfirmTemplate(
#             text= venue + "目前" + status +'，請問您是否要註冊提醒呢？我們會在人數變少後提醒您！',
#             actions=[
#                 PostbackAction(label='好', data= "remind-ifLine_" + venue, text='好!'),
#                 PostbackAction(label='先不要', data= "remind-ifLine-no", text='先不要!')
#             ])
        
#         confirm_template_message = TemplateSendMessage(
#             alt_text='註冊提醒', template=confirm_template)
        
#         self.line_bot_api.reply_message(reply_token, confirm_template_message) 
        
    def send_ensureIfLine_message(self,reply_token, venue):
        
        confirm_template = ConfirmTemplate(
            title='你確定要開啟' + venue + '的排隊提醒嗎？',text= '我們會在排隊時間小於15分鐘時提醒你',
            actions=[
                PostbackAction(label='好', data= "remind-ifLine_" + venue, text='好!'),
                PostbackAction(label='先不要', data= "remind-ifLine-no", text='先不要!')
            ])
        
        confirm_template_message = TemplateSendMessage(
            alt_text='註冊提醒', template=confirm_template)
        
        self.line_bot_api.reply_message(reply_token, confirm_template_message)
        
    def send_remind_yes_message(self,reply_token):
        
        text_message = TextMessage(text='好的，那我們等等見了，如果發現都沒有提醒，也可以再次主動詢問喔。')
        
        template_message = self._generate_anotherQuestion_confirmTemplate()       
        
        self.line_bot_api.reply_message(reply_token, messages=[text_message, template_message])
        
    def send_remind_no_message(self, reply_token):
        
        text_message = TextMessage(text='好的，祝您玩得愉快啊。')
        
        template_message = self._generate_anotherQuestion_confirmTemplate()
        
        self.line_bot_api.reply_message(reply_token, messages=[text_message, template_message])        
        
        
    def send_endConversation_message(self,reply_token):

        buttons_template = ButtonsTemplate(
            title="感謝使用",text='如果有問題就問我，儘管呼叫我！', actions=[

                MessageAction(label='后里馬場',text='后里馬場'),
                MessageAction(label='森林園區',text='森林園區'),
                MessageAction(label='外埔園區',text='外埔園區'),
                MessageAction(label='葫蘆墩公園',text='葫蘆墩公園'),        
            ])

        template_message = TemplateSendMessage(
            alt_text='對話完畢', template=buttons_template)
        
        self.line_bot_api.reply_message(reply_token, template_message)        
    
    def send_currentSituation_picture_message(self, reply_token, pictures):
        
        template_message = self._generate_anotherQuestion_confirmTemplate()

        if len(pictures) == 0:
            text_message = TextMessage(text='目前還沒更新照片，你可以看看其他館喔：）') 
            self.line_bot_api.reply_message(reply_token, messages=[text_message, template_message])  
            return
        
        imageCarouselColumns = []
        
        for picture in pictures:
            
            imageCarouselColumn = ImageCarouselColumn(
                image_url="https://2018floraexpo.tk/" + picture["path"],
                action=URIAction(

                    uri="https://2018floraexpo.tk/" + picture["path"]
                )
            )
            
            imageCarouselColumns.append(imageCarouselColumn)
            
        
        
        image_carousel_template_message = TemplateSendMessage(
            alt_text='照片如下',
            template=ImageCarouselTemplate(
                columns= imageCarouselColumns
            )
        )
        
        
        text_message = TextMessage(text='以上是展館的前三張照片，希望可以幫助到您：）')
            
        self.line_bot_api.reply_message(reply_token, messages=[image_carousel_template_message, text_message, template_message])  
        
#     def send_ifProblem_message(self, reply_token):
        
#         text_message = TextMessage(text='以上就是展館最新狀況的前三張照片和他被拍照的時間，\n希望可以幫助到您：）')
        
#         template_message = self._generate_anotherQuestion_confirmTemplate()       
        
#         self.line_bot_api.reply_message(reply_token, messages=[text_message, template_message])
        
### 管理人員專區 ###

    def send_manager_menu_message(self,reply_token):
        
        buttons_template = ButtonsTemplate(
            title='管理員ＸＸＸ你好', text='請問您想要做什麼呢？', actions=[

                MessageAction(label='更正展館排隊資訊', text='更正展館排隊資訊'),
                MessageAction(label='新增展館人潮現況照片', text='新增展館人潮現況照片'),
                MessageAction(label='我要登入', text='登入'),
            ])

        template_message = TemplateSendMessage(
            alt_text='更改資訊', template=buttons_template)

        self.line_bot_api.reply_message(reply_token, messages=template_message)        
    
    def send_correctIfLine_message(self, reply_token, status, venue):
        
        choice_dict = {
            '不用排隊': "correct-ifLine_0_" + venue,
            '排隊時間在15分鐘以內':"correct-ifLine_15_" + venue,
            '要排隊約莫30分鐘':"correct-ifLine_30_" + venue,
            '要排隊約莫45分鐘':"correct-ifLine_45_" + venue,
            '要排隊超過1小時':"correct-ifLine_60_" + venue
        }
        
        del choice_dict[status]
        
        quickReply_message = TextSendMessage(
            text='你想要更改' + venue + '的排隊狀況為？',
            quick_reply=QuickReply(
                items=[
                    QuickReplyButton(
                        action=PostbackAction(label=list(choice_dict.keys())[0],data= list(choice_dict.values())[0])
                    ),
                    QuickReplyButton(
                        action=PostbackAction(label=list(choice_dict.keys())[1],data= list(choice_dict.values())[1])
                    ),
                    QuickReplyButton(
                        action=PostbackAction(label=list(choice_dict.keys())[2],data= list(choice_dict.values())[2])
                    ),
                    QuickReplyButton(
                        action=PostbackAction(label=list(choice_dict.keys())[3],data= list(choice_dict.values())[3])
                    ),                           
                    QuickReplyButton(
                        action=PostbackAction(label="取消更改", data="correct-ifLine_no")
                    ),            
                ]))

        self.line_bot_api.reply_message(reply_token, messages=quickReply_message)                
    
    def send_ensure_correctIfLine_message(self, reply_token, venue, status):
        
        quickReply_message = TextSendMessage(
            text= '你想將'+ venue +'的狀態改為目前' + status + '，你確定嗎？',
            quick_reply=QuickReply(
                items=[
                    QuickReplyButton(
                        action=PostbackAction(label='是', data= "ensure-ifLine-yes_" + status + "_" + venue, text='我確定')
                    ),
                    QuickReplyButton(
                        action=PostbackAction(label='否', data= "ensure-ifLine-no_" + venue, text='我不改了，幫我跳回管理表單吧！')
                    )   
                ]))
        
        self.line_bot_api.reply_message(reply_token, quickReply_message)
        
        
    def send_correctCurrent_message(self, reply_token, venue):
        
        buttons_template = ButtonsTemplate(
            text='你現在可以傳送照片更改' + venue +'人潮現況！', actions=[
                
                CameraAction(label='打開相機'),
                CameraRollAction(label="打開相簿"),
                PostbackAction(label='我不更改了', data= "correct-currentSituation-no", text='我不改了，幫我跳回管理表單吧！'),
            ])

        template_message = TemplateSendMessage(
            alt_text='修改狀態完畢', template=buttons_template)
        
        self.line_bot_api.reply_message(reply_token, template_message)

    def send_ensure_correctCurrent_message(self, reply_token, venue):
        
        confirm_template = ConfirmTemplate(
            text= venue +'最新的照片即將上傳，你確定嗎？',
            actions=[
                PostbackAction(label='是', data= "ensure-currentSituation-yes", text='我確定'),
                PostbackAction(label='否', data= "ensure-currentSituation-no", text='我不改了，幫我跳回管理表單吧！')
            ])
        
        template_message = TemplateSendMessage(
            alt_text='確認拍照是否上傳', template=confirm_template)
        
        self.line_bot_api.reply_message(reply_token, template_message)      

    def send_finishCorrect_message(self, reply_token):
        
        buttons_template = ButtonsTemplate(
            text='好的，已經更新完畢，如果還需要，請在呼喚我喔！', actions=[

                MessageAction(label='呼叫管理小幫手',text='呼叫管理小幫手'),
            ])

        template_message = TemplateSendMessage(
            alt_text='修改狀態完畢', template=buttons_template)
        
        self.line_bot_api.reply_message(reply_token, template_message)        
        
        
    ## push notification.
    def push_remind_notification(self, to, venue, status):
        
        buttons_template = ButtonsTemplate(
            title= "您剛剛所註冊的" + venue + "目前" + status,
            text="如果還要註冊提醒，歡迎再次呼叫我喔。", actions=[
                
                URIAction(label='帶我去 (iOS)',uri='https://itunes.apple.com/tw/app/taichung-worldfloraexposition/id1438719939?l=en&mt=8&fbclid=IwAR2ZE2bFKVdNjHNCu6W2ONGRuk4LsLJ7gDyAZxVkV1vu6rfSIHPVT2oIb0s'),
                URIAction(label='帶我去 (Android)',uri='https://play.google.com/store/apps/details?id=com.luci.TaichungWorldFloraExposition&fbclid=IwAR0UEQFl1NzkkuSxro6JrDKGOM5oyHjNgwm7Y47-xgkJg66SHwEvB7Xv_Aw') 
            ])

        template_message = TemplateSendMessage(
            alt_text='對話完畢', template=buttons_template)        
        
        self.line_bot_api.multicast(to, messages=template_message)
        
    
    def _generate_anotherQuestion_confirmTemplate(self):
        confirm_template = ConfirmTemplate(
            text='您還需要查詢其他 園區/展館 嗎？',
            actions=[
                PostbackAction(label='有', data= "another_question_yes", text='有!我還要問'),
                PostbackAction(label='沒有', data= "another_question_no", text='目前沒有，我等等再問你吧!')
            ])
        
        template_message = TemplateSendMessage(
            alt_text='是否還有問題呢？', template=confirm_template)    
        
        return template_message
    
    def _generate_dist_venues(self, dist_venues):
        
        actions = []
        columns = []
        
        if (len(dist_venues)/4) <= 1.0:
        
            for venue in dist_venues:

                actions.append(MessageAction(label=venue['title'],text=venue['title']))

            template_message = TemplateSendMessage(
                alt_text='請問你是要問' + dist_venues[0]['dist'] + '的哪個館呢？',
                template=ButtonsTemplate(
                    title=dist_venues[0]['dist'],
                    text='以下是' + dist_venues[0]['dist'] + '有提供資訊的展館',
                    actions= actions
                )
            )

            return template_message
        
        else:
            
            empty_action = PostbackAction(label='空白按鈕', data='empty')
            
            for venue in dist_venues:
                
                actions.append(MessageAction(label=venue['title'],text=venue['title']))
                
                if  (len(actions) % 3 == 0):
                    column = CarouselColumn(title=venue['dist'], text='以下是' + venue['dist'] + '有提供資訊的展館', actions=actions)
                    
                    columns.append(column)
                    actions = []
                    
                
            while len(actions) % 3 != 0:
                
                actions.append(empty_action)
                
            column = CarouselColumn(title=venue['dist'], text='以下是' + venue['dist'] + '有提供資訊的展館', actions=actions)

            columns.append(column)
                
                
            carousel_template = CarouselTemplate(columns=columns)

            template_message = TemplateSendMessage(
                alt_text='請問你是要問' + dist_venues[0]['dist'] + '的哪個館呢？', template=carousel_template)  

            return template_message
        
    def _generate_venue(self, signal):
        
        carousel_template = CarouselTemplate(columns=[
            CarouselColumn(text='后里', title='后里馬場園區', actions=[
                PostbackAction(label='花舞館', data=signal+'_花舞館'),
                PostbackAction(label='故宮花蝶館', data=signal+'_故宮花蝶館'),
                PostbackAction(label='馬場風華館', data=signal+'_馬場風華館')
            ]),
            CarouselColumn(text='后里', title='后里森林園區', actions=[
                PostbackAction(label='友達微美館', data=signal+'_友達微美館'),
                PostbackAction(label='發現館', data=signal+'_發現館'),
                PostbackAction(label='台開積木概念館', data=signal+'_台開積木概念館')
            ]),
            CarouselColumn(text='后里', title='后里森林園區', actions=[
                PostbackAction(label='森之屋', data=signal+'_森之屋'),
                PostbackAction(label='四口之家', data=signal+'_四口之家'),
                PostbackAction(label='Ayoi工藝之地', data=signal+'_Ayoi工藝之地')
            ]),
            CarouselColumn(text='后里', title='后里森林園區', actions=[
                PostbackAction(label='正隆森隆活虎館', data=signal+'_正隆森隆活虎館'),
                PostbackAction(label='台中精機奇幻森林樂園', data=signal+'_台中精機奇幻森林樂園'),
                PostbackAction(label='空白按鈕', data='empty')
            ]),            
            CarouselColumn(text='外埔', title='外埔園區', actions=[
                PostbackAction(label='智農館', data=signal+'_智農館'),
                PostbackAction(label='樂農館', data=signal+'_樂農館'),
                PostbackAction(label='大愛環保科技人文館', data=signal+'_大愛環保科技人文館')
            ]),
            CarouselColumn(text='豐原', title='豐原葫蘆墩園區', actions=[
                PostbackAction(label='囍香逢館', data=signal+'_囍香逢館'),
                PostbackAction(label='臺中市不動產開發公會竹跡館', data=signal+'_臺中市不動產開發公會竹跡館'),
                PostbackAction(label='楷模創生館', data=signal+'_楷模創生館')
            ])            
        ])
        
        template_message = TemplateSendMessage(
            alt_text='請問你是要問哪個館呢？', template=carousel_template)  
        
        return template_message
    
    def _generate_noLine_venues_message(self, noLine_venues):

        columns = []
        for venue in noLine_venues:
            
            columns.append(
                CarouselColumn(
                    thumbnail_image_url='https://2018floraexpo.tk/static/sources/venue_pic/' + venue["title"] + '.jpg?v=1.1',
                    title=venue["title"],
                    text=venue["dist"],
                    actions=[URIAction(label='前往官網', uri=venue["url"])]
                )
            )
        
        return TemplateSendMessage(alt_text='Carousel template', template=CarouselTemplate(columns=columns))
        
    
    def pprint(self, text):
        text_message = TextMessage(text=text)
        
        self.line_bot_api.push_message("DEVELOPER_ID", messages=text_message)        
      
        

#     def send_venueLocation_message(self, reply_token, locationInfoDict):
        
#         locationMessage = LocationSendMessage(title=locationInfoDict["title"], address=locationInfoDict["address"], latitude= locationInfoDict["latitude"], longitude=locationInfoDict["longitude"])
            
#         self.line_bot_api.reply_message(reply_token, locationMessage) 
        
    def send_login_message(self, reply_token, venue, ifRemind=False, action=""):
        
        buttons_template = ButtonsTemplate(
            text='Hi! ' + venue +' 的管理員', actions=[
                
                    URITemplateAction(
                        label="點我登入",
                        uri="line://app/1633186920-WZK58bp2?" + "venue=" + venue + "&action=" + action
                    )
            ])

        template_message = TemplateSendMessage(
            alt_text='點我登入', template=buttons_template)
        
        
        if ifRemind:
            text_message = TextMessage(text="您尚未登入喔，請點選下面按鈕登入")
            self.line_bot_api.reply_message(reply_token, [text_message, template_message])
                
        else:
            self.line_bot_api.reply_message(reply_token, template_message)
            
            
    def send_non_update_venues(self, venue):
        
        manager_list = []
        
        text_message = TextMessage(text="提醒超過一小時沒有更新照片的展館： " + venue)
        

        self.line_bot_api.multicast(manager_list, messages=text_message) 
        
        
        
        
        