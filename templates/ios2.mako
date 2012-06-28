hostname ${node}
! 
!      
% for interface in node.interfaces:  
interface ${interface.id}
	description ${interface.description}
	ipv4 address ${interface.ip_address} ${interface.subnet.netmask}   
!
% endfor 
!               
% if node.ospf: 
router ospf ${node.ospf.process_id}  
	router-id ${node.ospf.router_id}         
	address-family ipv4
	area ${node.ospf.area}
		% for ospf_link in node.ospf.ospf_links:
		interface ${ospf_link.interface}
			cost ${ospf_link.cost}
		!
		% endfor    
% endif             
!
! 
ip forward-protocol nd
!
no ip http server
!