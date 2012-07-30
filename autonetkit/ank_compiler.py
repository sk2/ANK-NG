import ank
import itertools
import netaddr
import os

#TODO: for any property not in nidb, try and pass through to obtain from respective overlay, eg ospf tries from G_ospf.node(node) etc


#TODO: rename compiler to build

#TODO: tidy up the dict to list, and sorting formats

def dict_to_sorted_list(data, sort_key):
    """Returns values in dict, sorted by sort_key"""
    return sorted(data.values(), key = lambda x: x[sort_key])

class RouterCompiler(object):
    def __init__(self, nidb, anm):
        self.nidb = nidb
        self.anm = anm

    def compile(self, node):
        ip_node = self.anm.overlay.ip.node(node)
        node.loopback = ip_node.loopback
        node.interfaces = dict_to_sorted_list(self.interfaces(node), 'id')
        if node in self.anm.overlay.ospf:
            node.ospf.ospf_links = dict_to_sorted_list(self.ospf(node), 'network')

        #print "|", type(node.ospf.ospf_links), "|"
        #for val in node.ospf.ospf_links:
            #print val, type(val)
        
        if node in self.anm.overlay.bgp:
            bgp_data = self.bgp(node)
#TODO: could do this as a sorted dict, but then have problem of clashing keys: keep as list for simplicity
# TODO: talk about edge id and uniqueness in thesis
#TODO: keep as a list, but use edge_id property when iterating.... so can avoid this passing around dict stuff
#and can then just sort as a normal list
            node.bgp.ibgp_rr_clients = dict_to_sorted_list(bgp_data['ibgp_rr_clients'], 'neighbor')
            node.bgp.ibgp_rr_parents = dict_to_sorted_list(bgp_data['ibgp_rr_parents'], 'neighbor')
            node.bgp.ibgp_neighbors = dict_to_sorted_list(bgp_data['ibgp_neighbors'], 'neighbor')
            node.bgp.ebgp_neighbors = dict_to_sorted_list(bgp_data['ebgp_neighbors'], 'neighbor')

    def interfaces(self, node):
        phy_node = self.anm.overlay.phy.node(node)
        G_ip = self.anm.overlay.ip
        interfaces = {}
        for link in phy_node.edges():
            ip_link = G_ip.edge(link)
            nidb_edge = self.nidb.edge(link)
            #TODO: what if multiple ospf costs for this link
            subnet =  ip_link.dst.subnet # netmask comes from collision domain on the link
            interfaces[link] = {
                    'id': nidb_edge.id,
                    'description': "%s to %s" % (link.src, link.dst),
                    'ip_address': link.overlay.ip.ip_address,
                    'subnet': subnet,
                    }

        return interfaces

    def ospf(self, node):
        """Returns OSPF links
        Also sets process_id
        """
        G_ospf = self.anm.overlay.ospf
        phy_node = self.anm.overlay.phy.node(node)
        node.ospf.process_id = 1
        node.ospf.lo_interface = "Loopback0"
        ospf_links = {}
        for link in G_ospf.edges(phy_node):
            ospf_links[link] = {
                'network': link.overlay.ip.dst.subnet,
                'area': link.area,
                }
        return ospf_links

    def bgp(self, node):
        phy_node = self.anm.overlay.phy.node(node)
        G_bgp = self.anm.overlay.bgp
        G_ip = self.anm.overlay.ip
        asn = phy_node.asn # easy reference for cleaner code
        node.asn = asn
        node.bgp.advertise_subnets = G_ip.data.asn_blocks[asn]
        
        ibgp_neighbors = {}
        ibgp_rr_clients = {}
        ibgp_rr_parents = {}
        ebgp_neighbors = {}

        for session in G_bgp.edges(phy_node):
            neigh = session.dst
            key = str(neigh) # used to index dict for sorting
            neigh_ip = G_ip.node(neigh)
            if session.type == "ibgp":
                #print session.direction
                data = {
                    'neighbor': neigh,
                    'loopback': neigh_ip.loopback,
                    'update_source': "loopback 0",
                    }
                if session.direction == 'down':
                    ibgp_rr_clients[key] = data
                elif session.direction == 'up':
                    ibgp_rr_parents[key] = data
                else:
                    ibgp_neighbors[key] = data
            else:
                ebgp_neighbors[key] = {
                    'neighbor': neigh,
                    'loopback': neigh_ip.loopback,
                    'update_source': "loopback 0",
                }

        return {
                'ibgp_rr_clients':  ibgp_rr_clients,
                'ibgp_rr_parents': ibgp_rr_parents,
                'ibgp_neighbors': ibgp_neighbors,
                'ebgp_neighbors': ebgp_neighbors,
                }


class QuaggaCompiler(RouterCompiler):
    def interfaces(self, node):
        ip_node = self.anm.overlay.ip.node(node)
        loopback_subnet = netaddr.IPNetwork("0.0.0.0/32")

        interfaces = super(QuaggaCompiler, self).interfaces(node)
        # OSPF cost
        for link in interfaces:
            interfaces[link]['ospf_cost'] = link['ospf'].cost

        return interfaces

class IosCompiler(RouterCompiler):

    def interfaces(self, node):
        ip_node = self.anm.overlay.ip.node(node)
        loopback_subnet = netaddr.IPNetwork("0.0.0.0/32")

        interfaces = super(IosCompiler, self).interfaces(node)
        # OSPF cost
        for link in interfaces:
            interfaces[link]['ospf_cost'] = link.overlay.ospf.cost

        interfaces['lo0'] = {
            'id': 'lo0',
            'description': "Loopback",
            'ip_address': ip_node.loopback,
            'subnet': loopback_subnet,
            }

        return interfaces

class Ios2Compiler(RouterCompiler):

    def compile(self, node):
        ip_node = self.anm.overlay.ip.node(node)
        node.loopback = ip_node.loopback
        node.interfaces = dict_to_sorted_list(self.interfaces(node), 'id')
        if node in self.anm.overlay.ospf:
            node.ospf.ospf_links = dict_to_sorted_list(self.ospf(node), 'interface')
        
        if node in self.anm.overlay.bgp:
            bgp_data = self.bgp(node)
            node.bgp.ibgp_rr_clients = dict_to_sorted_list(bgp_data['ibgp_rr_clients'], 'neighbor')
            node.bgp.ibgp_rr_parents = dict_to_sorted_list(bgp_data['ibgp_rr_parents'], 'neighbor')
            node.bgp.ibgp_neighbors = dict_to_sorted_list(bgp_data['ibgp_neighbors'], 'neighbor')
            node.bgp.ebgp_neighbors = dict_to_sorted_list(bgp_data['ebgp_neighbors'], 'neighbor')

    def interfaces(self, node):
        ip_node = self.anm.overlay.ip.node(node)
        loopback_subnet = netaddr.IPNetwork("0.0.0.0/32")

        interfaces = super(Ios2Compiler, self).interfaces(node)

        interfaces['lo0'] = {
            'id': 'Loopback0',
            'description': "Loopback",
            'ip_address': ip_node.loopback,
            'subnet': loopback_subnet,
            }

        return interfaces

    def ospf(self, node):
        """Returns OSPF links
        Also sets process_id
        """
        ip_node = self.anm.overlay.ip.node(node)
        node.ospf.router_id = ip_node.loopback
        node.ospf.area = 0 #TODO: build area dict from node/links

        node.ospf.lo_interface = "Loopback0"
        
        G_ospf = self.anm.overlay.ospf
        phy_node = self.anm.overlay.phy.node(node)
        node.ospf.process_id = 1
        ospf_links = {}
       
        for link in G_ospf.edges(phy_node):
            nidb_edge = self.nidb.edge(link)
            ospf_links[link] = {
                'network': link.overlay.ip.dst.subnet,
                'interface': nidb_edge.id,
                'cost': link.cost,
                }

        return ospf_links

class JunosCompiler(RouterCompiler):

    def compile(self, node):
        node.interfaces = dict_to_sorted_list(self.interfaces(node), 'id')
        if node in self.anm.overlay.ospf:
            node.ospf.ospf_links = dict_to_sorted_list(self.ospf(node), 'network')
            
        if node in self.anm.overlay.bgp:
            bgp_data = self.bgp(node)
            node.bgp.ebgp_neighbors = dict_to_sorted_list(bgp_data['ebgp_neighbors'], 'neighbor')

    def interfaces(self, node):
        ip_node = self.anm.overlay.ip.node(node)
        loopback_subnet = netaddr.IPNetwork("0.0.0.0/32")

        interfaces = super(JunosCompiler, self).interfaces(node)
        for link in interfaces:
            nidb_link =  self.nidb.edge(link)
            interfaces[link]['unit'] = nidb_link.unit

        interfaces['lo0'] = {
            'id': 'lo0',
            'description': "Loopback",
            'ip_address': ip_node.loopback,
            'subnet': loopback_subnet,
            }

        return interfaces

# Platform compilers
class PlatformCompiler(object):
# and set properties in nidb._graph.graph
    def __init__(self, nidb, anm, host):
        self.nidb = nidb
        self.anm = anm
        self.host = host

    @property
    def timestamp(self):
        return self.nidb.timestamp

    def compile(self):
        #TODO: make this abstract
        pass

class JunosphereCompiler(PlatformCompiler):
    def interface_ids(self):
        invalid = set([2])
        valid_ids = (x for x in itertools.count(0) if x not in invalid)
        for x in valid_ids:
            yield "ge-0/0/%s" % x

    def compile(self):
        print "Compiling Junosphere for", self.host
        G_phy = self.anm.overlay.phy
        junos_compiler = JunosCompiler(self.nidb, self.anm)
        for phy_node in G_phy.nodes('is_router', host = self.host, syntax='junos'):
            nidb_node = self.nidb.node(phy_node)
            nidb_node.render.template = "templates/junos.mako"
            nidb_node.render.dst_folder = "rendered/%s/%s" % (self.host, "junosphere")
            nidb_node.render.dst_file = "%s.conf" % ank.name_folder_safe(phy_node.label)

            int_ids = self.interface_ids()
            for edge in self.nidb.edges(nidb_node):
                edge.unit = 0
                edge.id = int_ids.next()

            junos_compiler.compile(nidb_node)

class NetkitCompiler(PlatformCompiler):
    def interface_ids(self):
        for x in itertools.count(0):
            yield "eth%s" % x

    def compile(self):
        print "Compiling Netkit for", self.host
        print [(node, node.platform) for node in self.nidb.nodes()]
        G_phy = self.anm.overlay.phy
        quagga_compiler = QuaggaCompiler(self.nidb, self.anm)
        for phy_node in G_phy.nodes('is_router', host = self.host, syntax='quagga'):
            nidb_node = self.nidb.node(phy_node)
            nidb_node.render.base = "templates/quagga"
            nidb_node.render.template = "templates/netkit_startup.mako"
            nidb_node.render.dst_folder = "rendered/%s/%s" % (self.host, "netkit")
            nidb_node.render.base_dst_folder = "rendered/%s/%s/%s" % (self.host, "netkit", phy_node)
            nidb_node.render.dst_file = "%s.startup" % ank.name_folder_safe(phy_node.label)

# allocate zebra information
            nidb_node.zebra.password = "1234"
            
            # Allocate edges
            # assign interfaces
            # Note this could take external data
            int_ids = self.interface_ids()
            for edge in self.nidb.edges(nidb_node):
                edge.id = int_ids.next()

            quagga_compiler.compile(nidb_node)

        # and lab.conf
        host_nodes = self.nidb.nodes(host = self.host)
#TODO: replace name/label and use attribute from subgraph
        lab_topology = self.nidb.topology.add(self.host)
        lab_topology.render_base = "templates/quagga"
        lab_topology.render_template = "templates/netkit_startup.mako"
        lab_topology.render_dst_folder = "rendered/%s/%s" % (self.host, "netkit")
        lab_topology.render_base_dst_folder = "rendered/%s/%s/%s" % (self.host, "netkit", phy_node)
        lab_topology.render_dst_file = "%s.startup" % ank.name_folder_safe(phy_node.label)
        subgraph = self.nidb.subgraph(host_nodes, self.host)


class CiscoCompiler(PlatformCompiler):
    def interface_ids_ios(self):
        id_pairs = ( (slot, port) for (slot, port) in itertools.product(range(17), range(5))) 
        for (slot, port) in id_pairs:
            yield "Ethernet%s/%s" % (slot, port)

    def interface_ids_ios2(self):
        for x in itertools.count(0):
            yield "GigabitEthernet0/0/0/%s" % x

    def compile(self):
        print "Compiling Cisco for", self.host
        G_phy = self.anm.overlay.phy
        ios_compiler = IosCompiler(self.nidb, self.anm)
        ios2_compiler = Ios2Compiler(self.nidb, self.anm)
        for phy_node in G_phy.nodes('is_router', host = self.host, syntax='ios'):
            nidb_node = self.nidb.node(phy_node)
            nidb_node.render.template = "templates/ios.mako"
            nidb_node.render.dst_folder = os.path.join(self.host, self.timestamp)
            nidb_node.render.dst_file = "%s.conf" % ank.name_folder_safe(phy_node.label)

            # Assign interfaces
            int_ids = self.interface_ids_ios()
            for edge in self.nidb.edges(nidb_node):
                edge.id = int_ids.next()

            ios_compiler.compile(nidb_node)

        for phy_node in G_phy.nodes('is_router', host = self.host, syntax='ios2'):
            nidb_node = self.nidb.node(phy_node)
            nidb_node.render.base = "templates/ios2"
            nidb_node.render.dst_folder = os.path.join(self.host, self.timestamp)
            nidb_node.render.base_dst_folder = os.path.join(self.host, self.timestamp, str(phy_node))

            # Assign interfaces
            int_ids = self.interface_ids_ios2()
            for edge in self.nidb.edges(nidb_node):
                edge.id = int_ids.next()

            ios2_compiler.compile(nidb_node)

class DynagenCompiler(PlatformCompiler):
    def interface_ids(self):
        for x in itertools.count(0):
            yield "gigabitethernet0/0/0/%s" % x

    def compile(self):
        print "Compiling Dynagen for", self.host
        G_phy = self.anm.overlay.phy
        ios_compiler = IosCompiler(self.nidb, self.anm)
        for phy_node in G_phy.nodes('is_router', host = self.host, syntax='ios'):
            nidb_node = self.nidb.node(phy_node)
            nidb_node.render.template = "templates/ios.mako"
            nidb_node.render.dst_folder = "rendered/%s/%s" % (self.host, "dynagen")
            nidb_node.render.dst_file = "%s.conf" % ank.name_folder_safe(phy_node.label)

            # Allocate edges
            # assign interfaces
            # Note this could take external data
            int_ids = self.interface_ids()
            for edge in self.nidb.edges(nidb_node):
                edge.id = int_ids.next()

            ios_compiler.compile(nidb_node)
