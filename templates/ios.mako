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
% for interface in node.interfaces:   
${interface}

% endfor

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
