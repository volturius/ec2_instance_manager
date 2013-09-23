#!/usr/bin/python

## usage: ec2admin start awsbox
## usage: ec2admin tag awsbox 'domain=volturius.com'

import sys
import boto.ec2
import argparse

class ec2admin(object):

    def __init__(self, region):
        self.region = region

    def add_tag(self, name, instance):
        instance.add_tag("Name","{{INSERT NAME}}")

    def get_instance_names(self):

        conn = boto.ec2.connect_to_region(self.region.name)

        reservations = conn.get_all_instances()

        for reservation in reservations:
            print reservation
            instances = reservation.instances

            print instances

            # instance attributes
            #   ['__class__', '__delattr__', '__dict__', '__doc__', '__format__', '__getattribute__', '__hash__', '__init__', '__module__', '__new__', '__reduce__', '__reduce_ex__', '__repr__', '__setattr__', '__sizeof__', '__str__', '__subclasshook__', '__weakref__', '_in_monitoring_element', '_placement', '_previous_state', '_state', '_update', 'add_tag', 'ami_launch_index', 'architecture', 'block_device_mapping', 'client_token', 'confirm_product', 'connection', 'create_image', 'dns_name', 'ebs_optimized', 'endElement', 'eventsSet', 'get_attribute', 'get_console_output', 'group_name', 'groups', 'hypervisor', 'id', 'image_id', 'instance_profile', 'instance_type', 'interfaces', 'ip_address', 'item', 'kernel', 'key_name', 'launch_time', 'modify_attribute', 'monitor', 'monitored', 'monitoring', 'monitoring_state', 'persistent', 'placement', 'placement_group', 'placement_tenancy', 'platform', 'previous_state', 'previous_state_code', 'private_dns_name', 'private_ip_address', 'product_codes', 'public_dns_name', 'ramdisk', 'reason', 'reboot', 'region', 'remove_tag', 'requester_id', 'reset_attribute', 'root_device_name', 'root_device_type', 'spot_instance_request_id', 'start', 'startElement', 'state', 'state_code', 'state_reason', 'stop', 'subnet_id', 'tags', 'terminate', 'unmonitor', 'update', 'use_ip', 'virtualization_type', 'vpc_id']

            for inst in instances:
                print str(inst) + " ",
                print "'%s'" % inst.tags['Name']
                print "\t%s" % inst.state
                print "\t%s" % inst.instance_type
                print "\t%s" % inst.placement
                print "\t%s" % inst.key_name
                print "\t%s" % inst.dns_name
                print "\t%s" % inst.private_ip_address
                print "\t%s" % inst.public_dns_name
                print "\t%s" % inst.ip_address
#            print "\t%s" % inst.get_console_output().output



## Main program here

def main(argv=None):

    parser = argparse.ArgumentParser(description='Manage EC2 Instances')
    parser.add_argument('command',  metavar='COMMAND', nargs=1, type=str, help="command 'admin' or 'tag'")

    parser.add_argument('--version', action='version', version='%(prog)s 2.0')

    subparsers = parser.add_subparsers()
    subparsers.add_parser('instance', metavar='INSTANCE', nargs=1, type=str, help='instance name or id')

    args = parser.parse_args()
    print args

    regions = boto.ec2.regions()
    for region in regions:
        print "getting region '%s'" % region

        ec2a = ec2admin(region)

        ec2a.get_instance_names()
        print


if __name__ == "__main__":
    sys.exit(main())
