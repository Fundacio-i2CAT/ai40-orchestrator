from openstack import connection
import signal
from contextlib import contextmanager

from openstack.exceptions import HttpException


class TimeoutException(Exception): pass


def create_connection(data):
    return connection.Connection(auth_url=data['auth_url'], username=data['username'], password=data['password'],
                                 project_id=data['project_id'], user_domain_name=data['user_domain_name'])


def create_instance(conn, data):
    flavor = conn.compute.find_flavor(data['flavor'])
    image = conn.compute.find_image(data['image'])
    network = conn.network.find_network(data['network'])

    return conn.compute.create_server(name=data['name_instance'], image_id=image.id, flavor_id=flavor.id,
                                      networks=[{"uuid": network.id}])


@contextmanager
def time_limit(seconds):
    def signal_handler(signum, frame):
        raise TimeoutException

    signal.signal(signal.SIGALRM, signal_handler)
    signal.alarm(seconds)
    try:
        yield
    finally:
        signal.alarm(0)


def assign_float_ip(conn, instance, ip_float):
    is_assigned = False
    try:
        with time_limit(5):
            while not is_assigned:
                is_assigned = assign_float_ip2(conn, instance, ip_float)
        return 1
    except TimeoutException:
        return -1


def assign_float_ip2(conn, instance, ip_float):
    try:
        instance.action(conn.session, {'addFloatingIp': {'server_id': instance.id, 'address': ip_float}})
        return True
    except HttpException:
        return False


def get_instance(conn, id_instance):
    return conn.compute.find_server(id_instance, True)
