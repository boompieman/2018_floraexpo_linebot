# coding=UTF-8
# -*- coding: UTF-8 -*-

import time,sched
import threading

class ScheduleManager:
    
    def __init__(self):
        
        self.s = sched.scheduler(time.time,time.sleep)
    
    
    def reset_venue(self, bot, venue):
        
        print("reset venue")
        
        for q in self.s.queue:
            if venue in q.kwargs["venue"]:
                print("cancel venue")
                self.s.cancel(q)
        
        self.s.enter(3600,1,bot.send_non_update_venues, kwargs={"venue":venue})
#         self.s.enter(3,1,bot.send_non_update_venues, kwargs={"venue":venue})
        
    def run_loop(self):
        
        print("run loop:", time.time())
        self.s.run(blocking=False)
        threading.Timer(60,self.run_loop).start()
#         threading.Timer(1,self.run_loop).start()
    
    def run_once(self):
        
        return self.s.run(blocking=False)
        
    def get_queue(self):
        print(len(self.s.queue))
        return len(self.s.queue)

    def test(self):
        
        self.s.enter(5,1,self.test_func)
        self.s.run()
        
    def test_func(self):
        print("testXXX")