
%correct_poscat(471,8,piat).

%correct_edge_label(53,5,hd).

%correct_attachment(85,12,504).

%unnecessary_node(143,506).

%additional_node(node(445,510,504,'$phrase','$phrase',oc,vp,[])).

%correct_surf(401,13,'...').

correct_poscat(25,1,appr).
correct_poscat(91,504,vp).
correct_poscat(91,508,cvp).
correct_poscat(165,21,nn).
correct_poscat(191,501,mpn).
correct_poscat(288,14,vainf).
correct_poscat(420,30,vafin).
correct_poscat(478,3,appr).

correct_edge_label(50,509,cc).
correct_edge_label(91,506,cj).
correct_edge_label(91,508,oc).
correct_edge_label(191,13,pnc).
correct_edge_label(191,14,pnc).
correct_edge_label(191,510,cc).
correct_edge_label(165,21,hd).
correct_edge_label(192,503,oa).
correct_edge_label(526,510,oa).

correct_attachment(50,20,509).
correct_attachment(50,503,509).
correct_attachment(68,20,513).
correct_attachment(68,506,513).
correct_attachment(91,506,508).
correct_attachment(91,508,507).
correct_attachment(191,502,510).
correct_attachment(191,503,510).
% correct_attachment(275,1,505). % this should come out correctly in the dependency conversion anyway
correct_attachment(288,13,510).
correct_attachment(288,14,510).

additional_node(node(68,513,507,'$phrase','$phrase',oc,vp,[])).
additional_node(node(288,510,504,'$phrase','$phrase',oc,vp,[])).

unnecessary_node(50,506).
unnecessary_node(191,507).

new_root(91,507).














