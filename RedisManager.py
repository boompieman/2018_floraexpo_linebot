# coding=UTF-8

# -*- coding: UTF-8 -*-

import redis
from all_venues import all_venues

class RedisManager:
    
    def __init__(self):
        
        pool = redis.ConnectionPool(host='localhost', port=6379, decode_responses=True)
        self.r = redis.Redis(connection_pool=pool)
        
    def get(self, key):
        return self.r.get(key)
    
    def set(self, key, value):
        self.r.set(key, value)
        
    
    def set_ifLine_remind(self, postback_data, user_id):
        
        # postback_data = remind-ifLine_venue
        if self.r.get(postback_data) == None:
            self.r.set(postback_data, user_id)

        elif user_id not in self.r.get(postback_data):
            self.r.append(postback_data, "-"+ user_id)
    
    
    def set_ifLine_status(self, venue, status):
        
        self.r.set("ifLine_" + venue , status)
        
    def get_ifLine_status(self, venue):
        
        return self.r.get("ifLine_" + venue)
    
    def get_remind_list(self, venue):
        
        if self.r.get("remind-ifLine_" + venue) != None:
        
            return self.r.get("remind-ifLine_" + venue).split("-")
    
    def delete_remind_list(self, venue):
        
        self.r.delete('remind-ifLine_' + venue)
        
    def get_locationInfoDict(self, venue):
        
        infoString = self.r.get("locationInfo_" + venue)
        
        if infoString != None:
            infoDict = {
                "title": infoString.split("_")[0],
                "address":infoString.split("_")[1],
                "latitude":infoString.split("_")[2],
                "longitude":infoString.split("_")[3]
            }
            return infoDict
        else:
            return None
    
    def get_account(self, uid, venue):
        
        return self.r.get("account_" + uid + "_" + venue)
    
    def set_account(self, uid, venue):
        
        self.r.set("account_" + uid + "_" + venue, "true", ex=3600)
        
        
    def get_noLine_dist_venues(self, dist_venues):
        
        noLine_venues = []
        
        for venue in dist_venues:
            if self.r.get("ifLine_" + venue["title"]) == None or ("15" in self.r.get("ifLine_" + venue["title"])) or ("不用排隊" in self.r.get("ifLine_" + venue["title"])):
                noLine_venues.append(venue)
        
        return noLine_venues        
        
    def get_noLine_venues(self):
        
        noLine_venues = []
        
        for venue in all_venues:
            
            if self.r.get("ifLine_" + venue["title"]) == None or ("15" in self.r.get("ifLine_" + venue["title"])):
                noLine_venues.append(venue)
        
        return noLine_venues
    
    
    def set_userDist(self, uid, dist):
        
        self.r.set(uid+ "_dist", dist, ex=86400)
    
    def get_userDist(self, uid):
        
        return self.r.get(uid+ "_dist")
        
        
        
        