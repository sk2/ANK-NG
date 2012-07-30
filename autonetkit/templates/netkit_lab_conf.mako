LAB_DESCRIPTION="${topology.description}"
LAB_VERSION="${ank_version}"
LAB_AUTHOR="${topology.author}"  
LAB_EMAIL="${topology.email}"
LAB_WEB="${topology.web}"    

${topology}

% for config_item in topology.config_items:
${config_item}
%endfor
