#!/usr/bin/python

## usage: ec2admin start awsbox
## usage: ec2admin tag awsbox 'domain=volturius.com'
# ec2admin list --regions us-east-1 us-west-1 --matchname php --idZZ

# TODO:
#   * implement substring match on instance name listing
#   * start/stop logic
#   * route53 hooks

import sys
import boto.ec2
import argparse

class ec2admin(object):

    def __init__(self, region):
        self.region = region

    def add_tag(self, name, instance):
        instance.add_tag("Name","{{INSERT NAME}}")

    def get_instance_names(self, instance_list, state):

        conn = boto.ec2.connect_to_region(self.region)

        reservations = conn.get_all_instances()

        for reservation in reservations:
            
#            print reservation
            instances = reservation.instances

#            print instances

            # instance attributes
            #   ['__class__', '__delattr__', '__dict__', '__doc__', '__format__', '__getattribute__', '__hash__', '__init__', '__module__', '__new__', '__reduce__', '__reduce_ex__', '__repr__', '__setattr__', '__sizeof__', '__str__', '__subclasshook__', '__weakref__', '_in_monitoring_element', '_placement', '_previous_state', '_state', '_update', 'add_tag', 'ami_launch_index', 'architecture', 'block_device_mapping', 'client_token', 'confirm_product', 'connection', 'create_image', 'dns_name', 'ebs_optimized', 'endElement', 'eventsSet', 'get_attribute', 'get_console_output', 'group_name', 'groups', 'hypervisor', 'id', 'image_id', 'instance_profile', 'instance_type', 'interfaces', 'ip_address', 'item', 'kernel', 'key_name', 'launch_time', 'modify_attribute', 'monitor', 'monitored', 'monitoring', 'monitoring_state', 'persistent', 'placement', 'placement_group', 'placement_tenancy', 'platform', 'previous_state', 'previous_state_code', 'private_dns_name', 'private_ip_address', 'product_codes', 'public_dns_name', 'ramdisk', 'reason', 'reboot', 'region', 'remove_tag', 'requester_id', 'reset_attribute', 'root_device_name', 'root_device_type', 'spot_instance_request_id', 'start', 'startElement', 'state', 'state_code', 'state_reason', 'stop', 'subnet_id', 'tags', 'terminate', 'unmonitor', 'update', 'use_ip', 'virtualization_type', 'vpc_id']

            for inst in instances:

#               if ((instance_list == None) or (inst.tags['Name'] in instance_list)):
#                print instance_list
#                print inst.tags['Name']
#                if ((instance_list == None) or any(inst.tags['Name'] in s for s in instance_list)):
#
                if ((instance_list == None) or any(s in inst.tags['Name'] for s in instance_list)):

                    if (state == None or inst.state == state):

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

    # create the top-level parser
    parser = argparse.ArgumentParser()

    #parser.add_argument('command', metavar='COMMAND', nargs=None, help='ec2 command')
    parser.add_argument('--domain', metavar='ROUTE53_DOMAIN_NAME', nargs=1, help='set route53 domain name')
    parser.add_argument('--version', action='store_true')

    subparsers = parser.add_subparsers()

    # create the parser for the "list" command
    parser_start = subparsers.add_parser('list', help='start specified instance')
    parser_start.add_argument('--regions', default='ALL', nargs='*', help='region names')
    parser_start.add_argument('--instances', nargs='*', help='instance names (or subsstring')
    parser_start.add_argument('--state', help='only list instances in this state')

    # create the parser for the "start" command
    parser_start = subparsers.add_parser('start', help='start specified instance')
    parser_start.add_argument('start_instance', default=None, metavar='ID', help='instance help')

    # create the parser for the "stop" command
    parser_stop = subparsers.add_parser('stop', help='stop specified instance')
    parser_stop.add_argument('stop_instance', default=None, help='instance help')

    # create the parser for the "dns" command
    parser_stop = subparsers.add_parser('dns', help='update dns name in route53')
    parser_stop.add_argument('domain_name', default=None, help='domain help')

    args = parser.parse_args()

    if hasattr(args, 'regions'):

        ec2_regions = [region.name for region in boto.ec2.regions()]

        instances = args.instances
        state = args.state
        regions = args.regions

        if (regions == 'ALL'):
            regions = ec2_regions

        print "listing region %s" % regions

        for region in regions:

            if region not in ec2_regions:
                print "WARNING: bad region specified '%s'" % region
                continue

            print "getting region '%s'" % region

            ec2a = ec2admin(region)

            ec2a.get_instance_names(instances, state)
            print

    if hasattr(args, 'stop_instance'):
        print "stopping instance %s" % args.stop_instance

    if hasattr(args, 'start_instance'):
        print "starting instance %s" % args.start_instance

    if hasattr(args, 'domain_name'):
        print "updating dns for domain %s" % args.domain_name


if __name__ == "__main__":
    sys.exit(main())

