import MySQLdb
class DbHandler:
    def __init__(self):
        self.db = MySQLdb.connect("localhost","dbUser","yyyy","android_sms" )
        self.duplicateIds = []
        self.insertId = 0
    def createUser(self,mobile,otp):
        
        if (self.isUserExists(mobile) == True):
            #write code to deactivate the user. Mark these as 2
            if (self.deActivateUser() == True):
                pass
            else:
                #return false and break out. test it by failing self.cursor.execute in deactivateuser
                pass
        self.cursor = self.db.cursor()
        self.query = "INSERT INTO users(name, email, mobile, apikey, status) values(%s, %s, %s, %s, 0)"
        try:
            self.cursor.execute(self.query, ('', '', mobile, 'abdd'))
            self.db.commit()
            # Check that multiple inserts (different sessions should not interfere in getting insert id
            self.insertId = self.cursor.lastrowid
            if (self.insertId == 0):
                return False
            #self.createOtp(self.insertId,otp)

        #Generate OTP for user now
        except Exception,e:
            print str(e)
            self.db.rollback()
            return False
        self.createOtp(self.insertId,otp)
        #self.db.close()
    def isUserExists(self, mobile):
        self.cursor = self.db.cursor()
        self.query = "SELECT id from users WHERE mobile = %s and status = 1"
        try:
            self.cursor.execute(self.query, [mobile])
            ids = self.cursor.fetchall()
            print len(ids)
            if (len(ids) == 0):
                return False
            else:
                for id in ids:
                    self.duplicateIds.append(id[0])
                return True
        except Exception,e:
            print str(e)
            print "Error: unable to fecth data"

    def deActivateUser(self):
        self.cursor =  self.db.cursor()
        self.query = "UPDATE users set status = 2 where id = %s"
        try:
            for id in self.duplicateIds:
                print id
                self.cursor.execute(self.query, [id])
            self.db.commit()
            return True
        except Exception,e:
            print str(e)
            self.db.rollback()
            return False


    def createOtp(self, userId, otp):
        self.cursor =  self.db.cursor()
        self.query = "INSERT INTO sms_codes(user_id, code, status) values(%s, %s, 0)"
        try:
            self.cursor.execute(self.query, (userId, otp))
            self.db.commit()
            return True
        except Exception,e:
            print str(e)
            return False

    def activateUser(self,otp):
       self.cursor =  self.db.cursor()
       self.query = "Select u.id,sms_codes.id,u.mobile from users u, sms_codes where sms_codes.code = %s AND sms_codes.user_id = u.id AND u.status=0 AND (sms_codes.created_at <= NOW() AND sms_codes.created_at >= DATE_SUB(NOW(), INTERVAL 15 MINUTE))"
       try:
            self.cursor.execute(self.query, [otp])
            self.db.commit()
            # What  to return here
            self.candidateUsersCount = self.cursor.rowcount
            print self.candidateUsersCount
            if self.candidateUsersCount == 1:
                self.query1 = "UPDATE users set status = 1 where id = %s"
                self.query2 = "UPDATE sms_codes set status = 1 where id = %s"
                try:
                    self.idsToActivate = self.cursor.fetchone()
                    self.userIdToActivate = self.idsToActivate[0]
                    self.smsIdToActivate = self.idsToActivate[1]
                    print "User Id to be activated is "
                    print self.userIdToActivate
                    print "Sms id to be activated is "
                    print self.smsIdToActivate
                    self.mobileToActivate = self.idsToActivate[2]
                    self.cursor.execute(self.query1, [self.userIdToActivate])
                    self.cursor.execute(self.query2, [self.smsIdToActivate])
                    self.db.commit()
                    return self.mobileToActivate
                except Exception,e:
                    print str(e)
                    #What to return
            elif self.candidateUsersCount == 0:
                pass #What to return here
            else:
                pass #What to return here (Case of 2 users satisfying condition of otp in 15 minutes)
       except Exception,e:
            print str(e)
            #Again, what to return here?
               

    def __del__(self):
        self.db.close()
#dbh = DbHandler()
#dbh.activateUser('593695')
        

