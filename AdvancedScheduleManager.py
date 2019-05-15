# coding=UTF-8
# -*- coding: UTF-8 -*-

from apscheduler.schedulers.background import BackgroundScheduler
import time
from datetime import datetime, timedelta

class AdvancedScheduleManager:
    
    def __init__(self):
        
        self.s = BackgroundScheduler()
        self.s.start()
    
    
    def reset_venue(self, bot, venue):
        
        print("reset venue")

        if self.s.get_job(venue) != None:
            print("remove venue")
            self.s.remove_job(venue)
            
        self.s.add_job(bot.send_non_update_venues, 'date', run_date=datetime.now() + timedelta(seconds=3600), kwargs={"venue":venue}, id=venue)
        
    def test_scheduler(self, bot):
            
        self.s.add_job(bot.pprint, 'date', run_date=datetime.now() + timedelta(seconds=3), kwargs={"text":"Advanced schedule執行"}, id="test")
    
    def get_queue(self):
        
        return len(self.s.get_jobs())
