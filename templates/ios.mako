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

% endif   
!
!


<%doc>
interface ${i['id']}
 description ${i['description']}
 ip address ${i['ip']} ${i['netmask']} 
 % if igp_protocol == 'isis' and len(igp_interfaces) > 0:
 ip router isis
   % if 'weight' in i:
 isis metric ${i['weight']}
   % endif
 % elif 'weight' in i and len(igp_interfaces) > 0:
 ip ospf cost ${i['weight']}
 % endif
 no shutdown
 duplex auto
 speed auto
!                
</%doc>
