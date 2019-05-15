import apiai
import os

class dialogflowManager:
    
    def __init__(self):
        
        DIALOGFLOW_CLIENT_ACCESS_TOKEN = os.environ.get("DIALOGFLOW_CLIENT_ACCESS_TOKEN")
        self.ai = apiai.ApiAI(DIALOGFLOW_CLIENT_ACCESS_TOKEN)
    
    def get_intent(self,msg, uid):
        ai_request = self.ai.text_request()
        
        ai_request.lang = self._is_alphabet(msg)
        ai_request.session_id = uid
        ai_request.query = msg
        ai_response = json.loads(ai_request.getresponse().read())
        return ai_response['result']['metadata']['intentName']        

    # 判斷中文還英文
    def _is_alphabet(self, uchar):
        if ('\u0041' <= uchar<='\u005a') or ('\u0061' <= uchar<='\u007a'):
            print('English')
            return "en"
        elif '\u4e00' <= uchar<='\u9fff':
            #print('Chinese')
            print('Chinese')
            return "zh-tw"
        else:
            return "en"        