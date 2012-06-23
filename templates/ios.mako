hostname ${node}
!
boot-start-marker
boot-end-marker
!
!
no aaa new-model
!
!
ip cef
! 
!      
% for interface in node.interfaces:  
interface ${interface.id}
	description ${interface.description}
	ip address ${interface.ip_address} ${interface.subnet.netmask}   
	% if interface.cost:
	ip ospf cost ${interface.cost}
	% endif
	no shutdown
   	duplex auto
	speed auto
!
% endfor 
!               
% if node.ospf: 
router ospf ${node.ospf.process_id} 
% for ospf_link in node.ospf.ospf_links:
	network ${ospf_link.network.network} ${ospf_link.network.hostmask} area ${ospf_link.area} 
% endfor    
% endif           
% if node.isis: 
router isis ${node.isis.process_id}       
% endif  
% if node.eigrp: 
router eigrp ${node.eigrp.process_id}       
% endif   
!
!  
% if node.bgp: 
router bgp ${node.asn}   
	no synchronization
% for subnet in node.bgp.advertise_subnets:
	network ${subnet.network} mask ${subnet.netmask}                                                          
% endfor 
! ibgp
% for client in node.bgp.ibgp_rr_clients:       
	! ${client.neighbor}
	neighbor remote-as ${client.neighbor.asn}
	neighbor ${client.loopback} update-source ${client.update_source} 
	neighbor ${client.loopback} route-reflector-client                                                   
	neighbor send-community      
% endfor    
% for neigh in node.bgp.ibgp_neighbors:       
	! ${neigh.neighbor}
	neighbor remote-as ${neigh.neighbor.asn}
	neighbor ${neigh.loopback} update-source ${neigh.update_source}                                                     
	neighbor send-community      
% endfor
! ebgp
% for neigh in node.bgp.ebgp_neighbors:      
	! ${neigh.neighbor} 
	neighbor remote-as ${neigh.neighbor.asn}
	neighbor ${neigh.loopback} update-source ${neigh.update_source}                                                     
	neighbor send-community
% endfor    
% endif   
!
!
ip forward-protocol nd
!
no ip http server
!