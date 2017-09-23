# encoding=utf8 

import sys
import os
import requests
import json
import re
import urllib

# argv[1] = remixsid_cookie
# argv[2] = dialog_id
# argv[3] = folder_name

reload(sys)  
sys.setdefaultencoding('utf8')

try:
    sys.argv[1]
except IndexError:
    printHelp()
    exit()

if( sys.argv[1] == '--help' ):
    printHelp()
    exit()
else:
    if( len(sys.argv) < 3 ):
        print """
        Should be 3 params
        """
        exit()

remixsid_cookie = sys.argv[1]

print "vkview.php POST ..."
request_url = "http://vk.com/wkview.php"
request_data = {
    "act": "show",
    "al": 1,
    "loc":"im",
    "w": "history" + sys.argv[2] + "_photo",
    "offset" : 0,
    "part" : 1
}
bound = {"count" : 10000, "offset" : 0}

try:
    dir_name = "photos"
    if not len(sys.argv) > 2:
        dir_name = sys.argv[3]
    if not os.path.exists("drop_" + dir_name):
        os.mkdir("drop_" + dir_name)
except OSError:
    print "There are some problems with creating folder 'drop_" + dir_name + "'"
if( os.path.exists("drop_" + dir_name) ):
    os.chdir("drop_" + dir_name)
else:
    print "Failed to create folder\n"
    exit()

print "vkview.php responsed"
print "Parsing vkview.php response ..."
photos_row = []
while( bound['offset'] < bound['count'] ):
    request_data['offset'] = bound['offset']
    content = requests.post(request_url, cookies={"remixsid": remixsid_cookie}, params=request_data).text
    json_data_offset = re.compile('\{"count":.+?,"offset":.+?\}').search(content)
    bound = json.loads(content[json_data_offset.span()[0]:json_data_offset.span()[1]])
    bound['count'] = int(bound['count'])
    bound['offset'] = int(bound['offset'])

    photos = re.compile('showPhoto[^\{]*\{').findall(content)

    for photo in photos:
        if photo is not None:
            photo_album_id = re.compile('mail[\d]+').search(photo)
            photo_album_id = photo_album_id.group(0)
            photo_row = re.compile('showPhoto\(\'-?[\d_]+').search(photo)
            photo_row = photo_row.group(0).replace("showPhoto('", "")
            photos_row.append(photo_row + ' ' + photo_album_id)
					
print "vkview.php response parsed. Total count: " + str(len(photos_row))
print "al_photos.php POST ..."

links_file = open("links", "w")
photos_url = []
block_count = 0;
for line in photos_row:
    url = re.compile('[\d_]+').search(line).group(0)
    args = line.split(' ')
    request_url = "https://vk.com/al_photos.php"
    request_data = {
        "act": "show",
        "al": 1,
        "al_ad":"0",
        "gid":"0",
        "list":args[1],
        "module":"im",
        "photo": args[0]
    }
    content = requests.post(request_url, cookies={"remixsid": remixsid_cookie}, params=request_data).text
    blocks = re.compile('\"desc\"\:[\S]+}').findall(content)
    for block in blocks:	
        info = re.compile('w_src[\w\\\/\.\"\:\-]+\.jpg').search(block)
        if info is None:
            info = re.compile('z_src[\w\\\/\.\"\:\-]+\.jpg').search(block)
        if info is None:
            info = re.compile('y_src[\w\\\/\.\"\:\-]+\.jpg').search(block)
        if info is None:
            info = re.compile('r_src[\w\\\/\.\"\:\-]+\.jpg').search(block)
        if info is None:
            info = re.compile('q_src[\w\\\/\.\"\:\-]+\.jpg').search(block)
        if info is None:
            info = re.compile('p_src[\w\\\/\.\"\:\-]+\.jpg').search(block)
        if info is None:
            info = re.compile('o_src[\w\\\/\.\"\:\-]+\.jpg').search(block)
        if info is not None:
            info = info.group(0)
            fpart = re.compile('\"\:\[\"c[\d]+').search(block).group(0)
            fpart = re.sub("[^0-9]", "", fpart)
            url = info.replace("w_src\":\"", "").replace("y_src\":\"", "").replace("z_src\":\"", "")
            url = url.replace("r_src\":\"", "").replace("q_src\":\"", "").replace("p_src\":\"", "").replace("o_src\":\"", "")
            url = url.replace("\\", "")
            #url = info.replace("w_src\":\"", "w " + fpart + " ").replace("y_src\":\"", "y " + fpart + " ").replace("z_src\":\"", "z " + fpart + " ").replace("\\", "")
            photos_url.append(url)
            
    block_count = block_count + 1
    print block_count

links_file.close()
print "al_photos.php responsed"

urls_file = open("urls", "w+")
photos_set = set(photos_url)
for url in photos_set:
    urls_file.write(url + "\n")
	
urls_file.close()

url_file = open("urls", "r")
file_num = 0
for href in url_file:
    urllib.urlretrieve(href, str(file_num) + ".jpg")
    file_num += 1
    print str(file_num) + " photos loaded\n"
	
url_file.close()

print "Done!"

def printHelp():
    print """
    Help: python take_photos.py <remixsid_cookie> <dialog_id> [<folder_name>]
    """