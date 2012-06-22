router ${node}    


dsfsdfdf


%if node.ip:  
--IP--                    
% for allocation in node.ip.allocations:
IP ${allocation}
% endfor     
% endif

% if node.igp:
---IGP---
${node.igp}

% endif

%if node.bgp:
--BGP--       
IP blocks: ${node.bgp.asn_sn_blocks}              
% for session in node.bgp.session:           
session ${session.peer} type ${session.type}   id ${session.peer_ip}
% endfor     
% endif
                     

