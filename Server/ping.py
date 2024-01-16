import os
import time
import firebase_admin
from firebase_admin import credentials, firestore

# Fetch the service account key JSON file contents
cred = credentials.Certificate('key.json')

# Initialize the app with a service account, granting admin privileges
firebase_admin.initialize_app(cred, {
    'databaseURL': 'https://remote-system-monitor-ca3d8-default-rtdb.asia-southeast1.firebasedatabase.app'
})

db = firestore.client()
DbName = 'Device_Monitor'
pre = 'Device_'


def check_ip():
    # declare ip object
    ip = []

    # open text file and add each line to ip object set to False
    with open('ip.txt') as txt:    
        for line in txt:
            ip.append([line.strip(), False ])
        

    # check each line of ip and see if they are online
    for i in ip:
        response = os.system("ping -n 1 " + i[0])

        # initialise each ip to False
        i[1] = False

        # process action for ip address if found online or not
        if response == 0:
            i[1] = True

    # create result object to print
    result = []

    
    db_collection = db.collection(u'%s' %DbName)

    # loop over ip list and update database 
    db_id = 1
    for p in ip:
        db_ip = p[0]
        db_status = p[1]
        doc_ref = db_collection.document(u'%s%s' %(pre, db_id))
        doc_ref.set({
            u'id': db_id,
            u'ip': u'%s' %db_ip,
            u'status': db_status,
        })
        print('Updating %s%s' %(pre, db_id))
        db_id += 1
        
        # print result to result object
        line = '%s %s' % (p[0], p[1])
        result.append(line)

    # remove legacy Devices (documents) from database continuing from where the update db loop finished
    legacy_device_query = db_collection.where(u'id', u'>=', db_id).stream()
    
    for d in legacy_device_query:
            print(f'Deleting {d.id}')
            db_collection.document(f'{d.id}').delete()

    # print out result from result object to ip_result.txt
    for line in result:
        print(line)

    # open ip_result.txt and overwrite contents, write result to file, close file
    with open("ip_result.txt", "w+") as ip_result:
        
        #write elements of list
        for line in result:
            ip_result.write('%s\n' %line)
    
    ip_result.close()

    # pause operation for x amount of seconds
    time.sleep(5)

    # run function recursively
    check_ip()

    
# run program on startup
check_ip()