JUNOS

router ${node}    

                 
% for interface in node.interfaces:  
interface ${interface.id}
	description ${interface.description}
	ip address ${interface.ip_address} ${interface.subnet.netmask}   
	% if interface.ospf_cost:
	ip ospf cost ${interface.ospf_cost}
	% endif
	no shutdown
   	duplex auto
	speed auto
!
% endfor
