#!/usr/bin/python
import boto
import commands
import sys
import re
from boto.ec2.connection import EC2Connection



def usage():
  print "%s <regex> (user)" % sys.argv[0]


def fill_dict():
  host_dict = {}
  rr=[boto.ec2.get_region('eu-west-1')]
  for reg in rr:
    conn=reg.connect()
    reservations = conn.get_all_instances()
    for r in reservations:
      for i in r.instances:
        if 'Name' in i.tags:
          n = i.tags['Name']
        else:
          n = '???'
        host_dict[n] = i.ip_address
  return host_dict


def main():
  if len(sys.argv) < 2:
    usage()
    sys.exit(-1)
  else:
    regex = sys.argv[1]
    creg = re.compile(regex)
  host_list = ''
  host_dict = fill_dict()
  hosts = host_dict.keys()
  for host in hosts:
    if creg.search(host):
      host_list += host_dict[host] + ' '
      #host_list += host + '.popmog.com '
  print len(sys.argv)
  if len(sys.argv) == 3:
    out = commands.getoutput('cssh -l %s %s' % (sys.argv[2],host_list))
  else:
    out = commands.getoutput('cssh %s' % host_list)
  print out


if __name__ == "__main__":
  main()

