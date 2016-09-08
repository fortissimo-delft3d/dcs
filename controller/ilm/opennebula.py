import base64
import json
import logging
from logging.config import dictConfig
import uuid
import oca
from settings import Settings
from template_builder import build_template

# currently only 1 machine per reservation

with open('logging.json') as jl:
    dictConfig(json.load(jl))

settings = Settings()

def get_client():
    one_endpoint = "http://localhost:2633/RPC2"
    client =  oca.Client(settings.one_user + ':' +
                         settings.one_password, one_endpoint)
    return client

def start_machine(ami, instance):
    client = get_client()

    if not client:
        logging.error('Cannot connect to OpenNebula')
        return None, None

    worker_id = 'jm-%s' % uuid.uuid4()
    logging.info('Request workerID = %s' % worker_id)

    template_xml = build_template(worker_id)

    vm_id = oca.VirtualMachine.allocate(client, template_xml)

    logging.info('Allocate vm with worker_id %s, vm_id %s' % (worker_id,
        vm_id))

    return worker_id, vm_id


def terminate_machine(instance_id):

    client = get_client()

    if not client:
        logging.error('Cannot connect to OpenNebula RPC endpoint')
        return None, None

    vm = oca.VirtualMachine.new_with_id(instance_id)
    
    try:
        vm.shutdown_hard()
        return True
    except Exception, e:
        logging.exception('Cannot terminate instance %s (%s)' % (instance_id, e))
        return None

# returns the instance_id and the ip-address for a given reservation_id
def my_booted_machine(reservation_id):
    
    client = get_client()

    if not client:
        logging.error('Cannot connect to OpenNebula RPC endpoint')
        return None, None

    vm = oca.VirtualMachine.new_with_id(instance_id)
    vm.info()

    if vm.state == 3:
        ip_address = vm["TEMPLATE"].find("NIC").find("IP").text
        return reservation_id, ip_address

    else:
        logging.exception('Could not get reservations for %s (%s)' % (reservation_id, e))
        return None, None

def get_status(instance_id):
    ec2 = boto.ec2.connect_to_region(settings.aws_region,
                                     aws_access_key_id=settings.aws_access,
                                     aws_secret_access_key=settings.aws_secret)

    if not ec2:
        logging.error('Cannot connect to region %s' % settings.aws_region)
        return None
    try:
        statuses = ec2.get_all_instance_status(instance_ids=[instance_id])
        if len(statuses) == 1:
            logging.info('current %s status: %s' % (instance_id, statuses[0].system_status))
            return statuses[0].system_status
        return None
    except Exception, e:
        logging.exception('Could not get status for %s (%s)' % (instance_id, e))
        return None
    finally:
        if ec2:
            ec2.close()


def get_max_instances():
    ec2 = boto.ec2.connect_to_region(settings.aws_region,
                                     aws_access_key_id=settings.aws_access,
                                     aws_secret_access_key=settings.aws_secret)

    if not ec2:
        logging.error('Cannot connect to region %s' % settings.aws_region)
        return None
    try:
        attributes = ec2.describe_account_attributes()
        for attribute in attributes:
            if attribute.attribute_name and 'max-instances' in attribute.attribute_name.lower():
                return int(attribute.attribute_values[0])
        return 0
    except Exception, e:
        logging.exception('Could not get attributes (%s)' % e)
        return None
    finally:
        if ec2:
            ec2.close()


def active_instance_count():
    client = get_client()

    if not client:
        logging.error('Cannot connect to OpenNebula RPC endpoint')
        return None, None

    vmpool = oca.VirtualMachinePool(client)
    vmpool.info()

    n_active_instances = 0
    for vm in vmpool:
        vm.info()
        if vm.state == 3:
            n_active_instances += 1
    
    return n_active_instances


def get_storage_usage(instances):

    # not implemented yet
    return 0
