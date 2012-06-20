router ${node}   

%if node.ip:  
--IP--                    
% for allocation in node.ip.allocations:
IP ${allocation}
% endfor     
% endif

%if node.bgp:
--BGP--                      
% for session in node.bgp.session:
session ${session['peer']} type ${session['type']}
% endfor     
% endif
                     

