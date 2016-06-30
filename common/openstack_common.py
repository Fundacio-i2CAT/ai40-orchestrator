from openstack import connection


def create_connection(data):
    return connection.Connection(auth_url=data['auth_url'], username=data['username'], password=data['password'],
                                 project_id=data['project_id'], user_domain_name=data['user_domain_name'])


def create_instance(conn, data):
    flavor = conn.compute.find_flavor(data['flavor'])
    image = conn.compute.find_image(data['image'])
    network = conn.network.find_network(data['network'])

    return conn.compute.create_server(name=data['name_instance'], image_id=image.id, flavor_id=flavor.id,
                                      networks=[{"uuid": network.id}])


def get_instance(conn, id_instance):
    return conn.compute.find_server(id_instance, True)
