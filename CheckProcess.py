import os

scriptname = 'RaspPyNet'

tmp = os.popen("ps -A | grep RaspPyNet").read()
counter = tmp.count(scriptname)

if counter > 0:
    print(counter, "processes running of ", scriptname)

else:
print ("Script is not running - needs to be started!")
