from flask import Flask, render_template
import subprocess, json,os
from threading import Thread

IP_PREFIX = '172.16.64.' #Prefix used in for ip range

class PingQuick(Thread):
  """ Ping theaded class 

  This class requires mac/linux for the ping command - untested on win
  """

  def __init__(self,ip):
    Thread.__init__(self)
    self.ip_address = ip
    self.status = -1

  def run(self):
    try:
      ### Ping command
      ret = str(subprocess.Popen(['ping', '-c','1', self.ip_address], stdout=subprocess.PIPE).communicate()[0])
      ### TODO: Improve test
      if 'round-trip' in ret:
        self.status = 'Passed'
      else:
        self.status = 'Failed'
    except(subprocess.CalledProcessError):
      self.status = 'Exception'

app = Flask(__name__)

@app.route('/')
def index():
  """ Index rendering for main page - see the templates folder """

  return render_template('index.html')

@app.route('/cronrun')
def cronrun():
  """Used to generate the ip list.

  This is a basic example using the range operator
  creates JSON file for consumption
  """

  ips = [IP_PREFIX+str(x) for x in range(0,256)]
  ips.append('google.com');
  ips.append('yahoo.com');

  process_list = []
  data_dict = {}
  ### this section is the worker in creating the thread structure and joining them
  for ip_item in ips:
    current = PingQuick(ip_item)
    process_list.append(current)
    current.start()

  for process_q in process_list:
    process_q.join()

    ### Right now just get the IP and Status (see above) TODO: add more data here
    data_dict[process_q.ip_address] = process_q.status

    ### Write out the json file
    with open(os.path.dirname(os.path.abspath(__file__))+"/static/results.json",'w') as outfile:
      outfile.write(json.dumps(data_dict,sort_keys=True))
      dump = json.dumps(data_dict, sort_keys=True,indent=2)

  return render_template('cronrun.html',res='run completed', dump=dump)

### Main function
if __name__ == "__main__":
  app.run(debug=True)
