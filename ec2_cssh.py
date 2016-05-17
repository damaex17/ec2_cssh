#!/usr/bin/env python
import boto
import boto.ec2
import commands
import sys
import re
import threading
import Queue
import time

class MyThread(threading.Thread):
  def __init__(self,region,regex,queue):
    self.region = region
    self.regex = regex
    self.queue = queue
    threading.Thread.__init__(self)

  def run(self):
    self.instances = []
    self.conn = self.region.connect()
    self.reservations = self.conn.get_all_instances()
    self.addresses = self.conn.get_all_addresses()
    for self.r in self.reservations:
      for self.i in self.r.instances:
        if 'Name' in self.i.tags and self.i.state == 'running':
          if self.regex.search(self.i.tags['Name']):
            self.instances.append(self.i.ip_address)
    self.queue.put(self.instances)
    print '%s done' % self.region

def usage():
  print "%s <regex> (user)" % sys.argv[0]

def get_region():
  return boto.ec2.regions()

def main():
  if len(sys.argv) < 2:
    usage()
    sys.exit(-1)
  else:
    regex = re.compile(sys.argv[1])
  q = Queue.Queue()
  regions = get_region()
  host_list = []
  ips = []
  counter = 0
  for reg in regions:
    if reg.name not in ['us-gov-west-1','cn-north-1']:
      counter += 1
      MyThread(reg,regex,q).start()
  while counter != 0: 
    host_list.append(q.get())
    counter -= 1
  for h in host_list:
    if len(h) > 0:
      for host in h:
        ips.append(host)
  if len(sys.argv) == 3:
    out = commands.getoutput('cssh -l %s %s' % (sys.argv[2],' '.join(ips)))
  else:
    out = commands.getoutput('cssh %s' % ' '.join(ips))
  print out


if __name__ == "__main__":
  main()

