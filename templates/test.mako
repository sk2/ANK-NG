router ${node}

%if node.bgp:                      
% for session in node.bgp.session:
session ${session['peer']} type ${session['type']}
% endfor     

% endif
