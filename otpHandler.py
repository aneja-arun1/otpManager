import tornado.httpserver
import tornado.ioloop
import tornado.options
import tornado.web
import requests
import random
from random import randint
import json
import DbHandler
from DbHandler import DbHandler

from tornado.options import define, options
define("port", default=80, help="run on the given port", type=int)

class OTPGenerator(tornado.web.RequestHandler):
    def post(self):
        self.dbh = DbHandler()
        urlToPost = 'https://control.msg91.com/api/sendhttp.php'
        self.authkey = 'xxxx'
        self.mobileNo = self.get_argument('mobileno')
        #self.otpMsg = 'Welcome to SastaReporter! Your OTP for SastaReporter activation is '        
        self.otpMsg = "Welcome to Arun's app! Your OTP for activation is - "
        self.otp = randint(100000, 999999)
        self.otpMsg = self.otpMsg + str(self.otp)
        print self.otpMsg
        self.sender = 'SasRep'
        self.route = '4'
        self.response = 'json'
        self.responseData = {}
        self.payload = {'authkey':self.authkey,'mobiles':self.mobileNo,'message':self.otpMsg,'sender':self.sender,'route':self.route,'response':self.response}

        self.dbh.createUser(self.mobileNo, self.otp)

        requests.get(urlToPost, params=self.payload, verify=False)
        self.responseData["error"] = False
        self.responseData["message"] = "SMS request is initiated! You will be receiving it shortly."
        print self.responseData
        self.write(json.dumps(self.responseData))
        
        
        

class OTPVerifier(tornado.web.RequestHandler):
    def post(self):
        self.dbh1 = DbHandler()
        self.otpToVerify = self.get_argument('otp')
        self.responseData = {}
        self.mobileToActivate = self.dbh1.activateUser(self.otpToVerify)
        if self.mobileToActivate:
            self.responseData["error"] = False
            self.responseData["message"] = "User created successfully!"
            self.responseData["mobileToActivate"] = self.mobileToActivate
            print self.responseData
            self.write(json.dumps(self.responseData))

if __name__ == "__main__":
    tornado.options.parse_command_line()
    app = tornado.web.Application(
        handlers=[
            (r"/generateotp", OTPGenerator),
            (r"/verifyotp", OTPVerifier)
        ]
    )
    http_server = tornado.httpserver.HTTPServer(app)
    http_server.listen(options.port)
    tornado.ioloop.IOLoop.instance().start()

