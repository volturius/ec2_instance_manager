#!/usr/bin/python

# usage:
# ec2admin list --regions us-east-1 us-west-1 --match php --id i-d863dcb3
# ec2admin start instance-id [instance-id ...]
# ec2admin stop instance-id [instance-id ...]
# ec2admin tag mytag myvalue --id i-d863dcb3
# ec2admin dns 

# TODO:
#   * implement substring match on instance name listing
#   * start/stop logic
#   * route53 hooks

import os
import sys
import boto.ec2
import argparse

AWS_ACCESS_KEY_ID     = ''
AWS_SECRET_ACCESS_KEY = ''

class ec2admin(object):

    def __init__(self, region):

        self.region    = region
        self.conn      = boto.ec2.connect_to_region(self.region)
        self.ec2_regions = [r.name for r in boto.ec2.regions()]

        if not self.region in self.ec2_regions:
            print "ERROR: bad region specified %s" % self.region
            sys.exit(1)

        self.instances = self._compile_cache()


    def _compile_cache(self):

        print self.conn

        reservations = self.conn.get_all_instances()
        instances = {}

        for reservation in reservations:
            for instance in reservation.instances:
                instances[instance.image_id] = instance

        return instances


    def add_tag(self, name, instance):
        instance.add_tag("Name","{{INSERT NAME}}")

    def get_instance_names(self, filter_names, state):

        for inst in self.instances.values():

            if ((filter_names == None) or any(s in inst.tags['Name'] for s in filter_names)):

                if (state == None or inst.state == state):

                    print str(inst) + " ",
                    if 'Name' in inst.tags:
                        print "'%s'" % inst.tags['Name']
                    print "\t%s" % inst.id
                    print "\t%s" % inst.image_id
                    print "\t%s" % inst.state
                    print "\t%s" % inst.instance_type
                    print "\t%s" % inst.placement
                    print "\t%s" % inst.key_name
                    print "\t%s" % inst.dns_name
                    print "\t%s" % inst.private_ip_address
                    print "\t%s" % inst.public_dns_name
                    print "\t%s" % inst.ip_address

    def start_instance(self, id):

        print "starting %s in region %s" % (id, self.region)
        self.conn.run_instances(id)
    
    def stop_instance(self, region, id):

        print "stopping %s in region %s" % (id, self.region)
        self.conn.stop_instances(id)
    
    def get_console_text(self, id):

        print "\t%s" % self.instances[id].get_console_output().output


## Main program here
def main(argv=None):

    # create the top-level parser
    parser = argparse.ArgumentParser()

    #parser.add_argument('command', metavar='COMMAND', nargs=None, help='ec2 command')
    parser.add_argument('--domain', metavar='ROUTE53_DOMAIN_NAME', nargs=1, help='set route53 domain name')
    parser.add_argument('--version', action='store_true')

    subparsers = parser.add_subparsers(dest='command')

    # create the parser for the "list" command
    parser_list = subparsers.add_parser('list', help='start specified instance')
    parser_list.add_argument('--regions', default='ALL', nargs='*', help='region names')
    parser_list.add_argument('--match', nargs='*', help='limit listing to instance names (or subsstring')
    parser_list.add_argument('--id', dest='list_ids', nargs='*', help='instance id')
    parser_list.add_argument('--state', help='only list instances in this state')

    # create the parser for the "start" command
    parser_start = subparsers.add_parser('start', help='start specified instance')
    parser_start.add_argument('region', help='instance region')
    parser_start.add_argument('id', help='instance ids')

    # create the parser for the "stop" command
    parser_stop = subparsers.add_parser('stop', help='stop specified instance')
    parser_stop.add_argument('stop_instance', default=None, help='instance help')
    parser_stop.add_argument('--stopregion', nargs='*', help='instance names (or subsstring')
    parser_stop.add_argument('--stopid', nargs='*', help='instance names (or subsstring')

    # create the parser for the "dns" command
    parser_dns = subparsers.add_parser('dns', help='update dns name in route53')
    parser_dns.add_argument('domain_name', default=None, help='domain help')

    # create the parser for the "tag" command
    parser_tag = subparsers.add_parser('tag', help='update instance tag')
    parser_tag.add_argument('name', default=None, help='domain help')
    parser_tag.add_argument('value', default=None, help='domain help')
    parser_tag.add_argument('--id', nargs='*', help='instance id')

    args = parser.parse_args()

    # Put AWS keys into environment valiables
    if (not AWS_SECRET_ACCESS_KEY == '' or not AWS_ACCESS_KEY_ID == ''):

        os.environ['AWS_SECRET_ACCESS_KEY'] = AWS_SECRET_ACCESS_KEY
        os.environ['AWS_ACCESS_KEY_ID']     = AWS_ACCESS_KEY_ID
    try:
        os.environ['AWS_SECRET_ACCESS_KEY']
        os.environ['AWS_ACCESS_KEY_ID']
    except KeyError:
        print "ERROR: No AWS Keys found"
        print "       Try setting AWS_SECRET_ACCESS_KEY and AWS_ACCESS_KEY_ID in environment"
        exit(1)

#    print args
#    sys.exit(99)


    if args.command == 'list':

        name_match = args.match
        state = args.state
        regions = args.regions

        if (regions == 'ALL'):
            regions = [r.name for r in boto.ec2.regions()]

        print "listing region %s" % regions

        for region in regions:

#            print "getting region '%s'" % region

            ec2a = ec2admin(region)

            ec2a.get_instance_names(name_match, state)
            print

    if args.command == 'start':
        print "starting instance '%s' in region '%s'" % (args.id, args.region)

        ec2a = ec2admin(args.region)
        ec2a.start_instance(args.id)

    if args.command == 'stop':
        print "stopping instance %s" % args.sto

        ec2a = ec2admin(stopregion)
        ec2a.stop_instance(id)

    if args.command == 'tag':
        print "updating tag for instance %s" % args.domain_name

    if args.command == 'dns':
        print "updating dns for domain %s" % args.domain_name


if __name__ == "__main__":
    sys.exit(main())

