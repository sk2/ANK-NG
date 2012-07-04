hostname ${node}
! 
!      
service timestamps log datetime msec
service timestamps debug datetime msec
telnet vrf default ipv4 server max-servers 10
domain lookup disable
line template vty
timestamp
exec-timeout 720 0
!
line console
exec-timeout 0 0
!
line default
exec-timeout 720 0
!
vty-pool default 0 50
control-plane
 management-plane
  inband
   interface all
    allow all
   !
  !
 !
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
   interface ${node.ospf.lo_interface}
    passive enable
   !
   % for ospf_link in node.ospf.ospf_links:
   interface ${ospf_link.interface}
    cost ${ospf_link.cost}
   !
   % endfor    
 % endif             
 !
!
end
