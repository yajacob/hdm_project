from django.conf import settings
from django.db import connection

def getHdmById(request, hdm_id):
    cursor = connection.cursor()
    if hdm_id == "":
        if request.user.is_staff:
            query = "SELECT * FROM hdm_hdm ORDER BY id DESC LIMIT 1"
        else:
            query = "SELECT * FROM hdm_hdm WHERE registrant_id='%s' ORDER BY id DESC LIMIT 1" % (request.user.id)
    else:
        query = "SELECT * FROM hdm_hdm WHERE id='%s'" % (hdm_id)

    cursor.execute(query)
    hdm = cursor.fetchone()
    hdm_dict = dict()
    hdm_dict['hdm_id'] = hdm[0]
    hdm_dict['hdm_objective'] = hdm[1]
    hdm_dict['hdm_criteria'] = hdm[2]
    hdm_dict['hdm_factors'] = hdm[3]
    hdm_dict['hdm_alternatives'] = hdm[4]
    hdm_dict['hdm_uuid'] = hdm[8]
    
    return hdm_dict 
    

def isExpertParticipated(uuid, exp_email):
    cursor = connection.cursor()

    query = """select count(*) cnt from hdm_evaluation a join (
            select id from hdm_hdm
            where hdm_uuid='%s') b
            on a.hdm_id = b.id
            where a.expert_email='%s'""" % (uuid, exp_email)
    cursor.execute(query)

    row = cursor.fetchone()
    if row[0] > 0:
        return True
    else:
        return False

def getIDbyUUID(uuid):
    cursor = connection.cursor()
    query = "SELECT id FROM hdm_hdm WHERE hdm_uuid='%s'" % (uuid)
    cursor.execute(query)

    row = cursor.fetchone()
    result = None
    if not row:
        result = None
    else:
        result = row[0] 
    return result
    

def getHDMbyUUID(uuid):
    cursor = connection.cursor()
    query = "SELECT count(*) cnt FROM hdm_hdm WHERE hdm_uuid='%s'" % (uuid)
    cursor.execute(query)

    row = cursor.fetchone()
    if row[0] < 1:
        return None
    
    query = "SELECT id, registrant_id FROM hdm_hdm WHERE hdm_uuid = '%s'" % (uuid)
    cursor.execute(query)
    row = cursor.fetchone()
    hdm_dict = {"hdm_id":row[0], "registrant_id":row[1]}
    return hdm_dict

def getUserInfoBy(user_id):
    cursor = connection.cursor()
    query = "SELECT first_name, last_name, email FROM auth_user WHERE id='%s'" % (user_id)
    cursor.execute(query)
    row = cursor.fetchone()
    user_dict = {"fname":row[0], "lname":row[1], "email":row[2]}
    return user_dict
    
def getEvalCount(hdm_id):
    cursor = connection.cursor()
    query = "SELECT count(DISTINCT expert_email) FROM hdm_evaluation WHERE hdm_id = '%s'" % (hdm_id)
    cursor.execute(query)
    row = cursor.fetchone()
    return row[0]

def main():
    cursor = connection.cursor()
    hdm_id = 19
    query = "SELECT count(DISTINCT expert_email) FROM hdm_evaluation WHERE hdm_id = '%s'" % (hdm_id)
    cursor.execute(query)
    row = cursor.fetchone()
    print(row)
    
if __name__ == "__main__":
    main()
