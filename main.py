#1909299458_5347a0093c9c724439
#mail386227
# coding=utf-8

import requests
import re
import sys
import os
import urllib
import json

# argv[1] = remixsid_cookie
# argv[2] = dialog_id
# argv[3] = person_name

def printHelp():
    print """
    Usage: python main.py <remixsid_cookie> <dialog_id> <name_of_folder>
    <dialog_id> is a string parameter "sel" in address line which you see when open a dialog
    """

try:
    sys.argv[1]
except IndexError:
    printHelp()
    exit()

if( sys.argv[1] == '--help' ):
    printHelp()
    exit()
else:
    if( len(sys.argv) < 4 ):
        print """
        Invalid number of arguments. Use parameter --help to know more
        """
        exit()

remixsid_cookie = sys.argv[1]

RequestData = {
    "act": "show",
    "al": 1,
    "loc":"im",
    "w": "history" + sys.argv[2] + "_photo",
    "offset" : 0,
    "part" : 1
}

request_href = "http://vk.com/wkview.php"
bound = {"count" : 10000, "offset" : 0}

try:
    if not os.path.exists("drop_" + sys.argv[3]):
        os.mkdir("drop_" + sys.argv[3])
except OSError:
    print "There are some problems with creating folder 'drop_" + sys.argv[3] + "'"
if( os.path.exists("drop_" + sys.argv[3]) ):
    os.chdir("drop_" + sys.argv[3])
else:
    print "Failed to create folder\n"
    exit()

test = open("links", "w+")
while( bound['offset'] < bound['count'] ):
    RequestData['offset'] = bound['offset']
    content = requests.post(request_href, cookies={"remixsid": remixsid_cookie}, params=RequestData).text
    json_data_offset = re.compile('\{"count":.+?,"offset":.+?\}').search(content)
    bound = json.loads(content[json_data_offset.span()[0]:json_data_offset.span()[1]])
    bound['count'] = int(bound['count'])
    bound['offset'] = int(bound['offset'])

    photos = re.compile('photo_row_[^>]*>').findall(content)

    for photo in photos:
        photo_row = re.compile('photo_row_[\d_]+').search(photo).group(0).replace("photo_row_", "")
        #photo_fpart = re.compile('cs\d+').search(photo).group(0).replace("cs", "c")
        #test.write(photo_row + ' ' + photo_fpart + '\n')
        test.write(photo_row + '\n')

test.close()

test = open("links", "r")
photos_url = []
file_num = 0
for line in test:
    href = re.compile('[\d_]+').search(line).group(0)
    data = {
        "act": "show",
        "al": 1,
        "al_ad":"0",
        "gid":"0",
        "list":"mail386227",
        "module":"im",
        "photo": href
    }
    request_href = "https://vk.com/al_photos.php"
    content = requests.post(request_href, cookies={"remixsid": remixsid_cookie}, params=data).text.encode('utf-8')
    info = re.compile('w_src[\w\\\/\.\"\:]+\.jpg').search(content)
    if info is not None:
        info = info.group(0)
        print info + "\n\n"
        url = info.replace("w_src\":\"", "").replace("\\", "")
        photos_url.append(url)
        print url;
	
test.close()

test = open("urls", "w+")
for url in photos_url:
    test.write(url + "\n")
	
test.close()

#url_file = open("urls", "r")
#file_num = 0
#for href in url_file:
#    urllib.urlretrieve(href, str(file_num) + ".jpg")
#    file_num += 1
#    print "Downloaded " + str(file_num) + " files\n"
#	
#url_file.close()