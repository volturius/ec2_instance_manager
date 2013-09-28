#!/usr/bin/python

# I wrote this to make it easy to do simple things from the command
# line I need to do.  Things include listing and finding instances
# across multiple availability zones, starting and stopping existing
# instances, and easily hooking up dns entires in route53.

# usage:
# ec2admin.py list
# ec2admin.py list --regions us-west-2
# ec2admin.py start us-west-2 i-517d9566
# ec2admin.py stop  us-west-2 i-517d9566
# ec2admin.py console us-west-2 i-517d9566
# ec2admin tag mytag myvalue  i-d863dcb3
# ec2admin setdns us-west-2 i-517d9566

# TODO:
#   * instnance tagging
#   * route53 hooks

import os
import sys
import boto.ec2
import argparse

AWS_ACCESS_KEY_ID     = ''
AWS_SECRET_ACCESS_KEY = ''

class ec2admin(object):

    def __init__(self, region):
        """
        Create an ec2admin object.

        Expects AWS_ACCESS_KEY_ID and AWS_SECRET_ACCESS_KEY from the 
        environment.
        """

        self.region      = region
        self.ec2_conn    = boto.ec2.connect_to_region(self.region)
        self.r53_conn    = boto.connect_route53()
        self.ec2_regions = [r.name for r in boto.ec2.regions()]

        if not self.region in self.ec2_regions:
            print "ERROR: bad region specified %s" % self.region
            sys.exit(1)

        self.instances = self._compile_cache()


    def _compile_cache(self):

        instances = {}

        reservations = self.ec2_conn.get_all_instances()

        for reservation in reservations:
            for instance in reservation.instances:
                instances[instance.id] = instance

        return instances

    def add_tag(self, name, instance):
        instance.add_tag("Name","{{INSERT NAME}}")

    def get_instance_info(self, filter, state):

        response = ''
        for inst in self.instances.values():

            # filter for names
            if filter == None:
                pass

            elif not 'Name' in inst.tags:
                continue # there _is_ a filtername, and can't match here

            elif filter in inst.tags['Name']:
                pass

            else:
                continue

            # filter for instance state
            if state == None:
                pass

            elif inst.state == state:
                pass

            else:
                continue

            response += str(inst) + " "
            if 'Name' in inst.tags:
                response += "'%s'\n" % inst.tags['Name']
            response += "\t%s\n" % inst.id
            response += "\t%s\n" % inst.image_id
            response += "\t%s\n" % inst.state
            response += "\t%s\n" % inst.instance_type
            response += "\t%s\n" % inst.placement
            response += "\t%s\n" % inst.key_name
            response += "\t%s\n" % inst.dns_name
            response += "\t%s\n" % inst.private_ip_address
            response += "\t%s\n" % inst.public_dns_name
            response += "\t%s\n" % inst.ip_address

        return response

    def start_instance(self, id):

        print "starting %s in region %s" % (id, self.region)
        self.ec2_conn.start_instances(instance_ids=[id], dry_run=False)
            
    
    def stop_instance(self, id):

        print "stopping %s in region %s" % (id, self.region)
        self.ec2_conn.stop_instances(instance_ids=[id])
    
    def get_console_text(self, id):

        output = self.instances[id].get_console_output().output

        if type(output) == str:
            output = output.replace("\r", "")

        return output
    def set_instance_dns(self, id, name, domain):

        ip = self.instances[id].ip_address
        ttl = 30
        results = self.r53_conn.get_all_hosted_zones()
        zone_id = None
        fqdn = name + '.' + domain
        delete_rset = None

        for zone in results['ListHostedZonesResponse']['HostedZones']:
            zid = zone['Id'].replace('/hostedzone/', '')
#            print zone['Name']
#            print "\t%s" % zid
            if zone['Name'].strip('.') == domain:
                zone_id = zid
                continue

        if zone_id == None:
            print "ERROR: Couldn't find zone id for '%s'" % domain
            return

        print "zone id: '%s'" % zone_id

        sets = self.r53_conn.get_all_rrsets(zone_id, name=fqdn, maxitems=1)
#        print "SET CHECK %s" % sets
        for rset in sets:

#            print "***SET***"
#            print dir(rset)
#            print "rset '%s'" % rset
#            print rset.to_print()
#            print rset.to_xml()
#            print "\t'%s': '%s' '%s' @ '%s'" % (rset.name, rset.type, rset.resource_records, rset.ttl)

            if rset.name.strip('.') == fqdn:
                print "WARNING: Deleting FQDN that already exists '%s' '%s'" % (rset.name, rset.resource_records)
                delete_rset = rset
                break

        changes = boto.route53.record.ResourceRecordSets(self.r53_conn, zone_id)

        if delete_rset:
            print "Deleting exising A record for '%s' '%s'" % (fqdn, delete_rset.resource_records)
            change_delete = changes.add_change("DELETE", fqdn, 'A')

            change_delete.ttl = delete_rset.ttl
            for old_value in delete_rset.resource_records:
                change_delete.add_value(old_value)

        print "Creating A record for '%s' '%s'" % (fqdn, ip)
        change_create = changes.add_change("CREATE", fqdn, "A")
        change_create.add_value(ip)
        change_create.ttl = ttl

        result = changes.commit()
        print result


## Main program here
def main(argv=None):

    # create the top-level parser
    parser = argparse.ArgumentParser()

    # main arguments
    parser.add_argument('--domain', metavar='ROUTE53_DOMAIN_NAME', nargs=1, help='set route53 domain name')
    parser.add_argument('--version', action='store_true')

    subparsers = parser.add_subparsers(dest='command')

    # create the parser for the "list" command
    parser_list = subparsers.add_parser('list', help='start specified instance')
    parser_list.add_argument('--regions', default='ALL', nargs='*', help='region names')
    parser_list.add_argument('--match', help='limit listing to instance names (or subsstring')
    parser_list.add_argument('--id', dest='list_ids', nargs='*', help='instance id')
    parser_list.add_argument('--state', help='only list instances in this state')

    # create the parser for the "start" command
    parser_start = subparsers.add_parser('start', help='start specified instance')
    parser_start.add_argument('region', help='instance region')
    parser_start.add_argument('id', help='instance id')

    # create the parser for the "stop" command
    parser_stop = subparsers.add_parser('stop', help='stop specified instance')
    parser_stop.add_argument('region', help='instance region')
    parser_stop.add_argument('id', help='instance id')

    # create the parser for the "console" command
    parser_console = subparsers.add_parser('console', help='get console text for specified instance')
    parser_console.add_argument('region', help='instance region')
    parser_console.add_argument('id', help='instance id')

    # create the parser for the "dns" command
    parser_dns = subparsers.add_parser('dns', help='update dns name in route53')
    parser_dns.add_argument('host', default=None, help='host name \'mybox\'')
    parser_dns.add_argument('domain', default=None, help='domain name \'example.com\'')
    parser_dns.add_argument('region', help='instance region')
    parser_dns.add_argument('id', help='instance id')

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

    if args.command == 'list':

        name_match = args.match
        state = args.state
        regions = args.regions

        if (regions == 'ALL'):
            regions = [r.name for r in boto.ec2.regions()]

        print "listing region %s" % regions

        for region in regions:

            print "listing instances in region '%s'" % region

            try:
                ec2a = ec2admin(region)
            except boto.exception.EC2ResponseError:
                print "Skipping. Insufficient permissions for region %s" % region
                continue

            print ec2a.get_instance_info(name_match, state)
    else:
        try:
            ec2a = ec2admin(args.region)
        except boto.exception.EC2ResponseError:
            print "Skipping. Insufficient permissions for region %s" % args.region
            return 1

    if args.command == 'start':
        print "starting instance '%s' in region '%s'" % (args.id, args.region)
        try:
            ec2a.start_instance(args.id)
        except boto.exception.EC2ResponseError:
            print "Skipping. Can't start id '%s'" % args.id
            return 1

    if args.command == 'stop':
        print "stopping instance '%s' in region '%s'" % (args.id, args.region)
        ec2a.stop_instance(args.id)

    if args.command == 'console':
        print "getting console text for instance '%s' in region '%s'" % (args.id, args.region)
        print ec2a.get_console_text(args.id)

    if args.command == 'tag':
        print "updating tag for instance %s" % args.domain

    if args.command == 'dns':
        print "updating dns for domain %s" % args.domain
        ec2a.set_instance_dns(args.id, args.host, args.domain)

if __name__ == "__main__":
    sys.exit(main())
