correct_poscat(1553,500,ap).
correct_poscat(70701,19,ne).
correct_poscat(75988,2,vvfin).
correct_poscat(157256,14,appo).
correct_poscat(157256,503,np).
correct_poscat(279835,515,np).
correct_poscat(365471,6,art).
correct_poscat(715878,509,np). % dirty hack but works
correct_poscat(864736,508,np).
correct_poscat(918488,508,np).
correct_poscat(918488,507,np).
correct_poscat(918488,510,cnp).

correct_edge_label(1553,1,mo).
correct_edge_label(75988,1,sb).
correct_edge_label(75988,2,hd).
correct_edge_label(95884,13,mo).
correct_edge_label(243518,6,nmc).
correct_edge_label(243518,7,nmc).
correct_edge_label(528050,15,ph).
correct_edge_label(621038,508,op).
correct_edge_label(742690,38,pd).
correct_edge_label(742690,505,mo).
correct_edge_label(742690,37,hd).
correct_edge_label(864736,508,cc).
correct_edge_label(918488,510,nk).
correct_edge_label(934849,4,--).

correct_edge_label(8723,3,--).
correct_edge_label(134875,3,--).
correct_edge_label(159170,32,--).
correct_edge_label(247105,6,--).
correct_edge_label(583286,4,--).
correct_edge_label(581628,3,--).
correct_edge_label(580264,27,--).

additional_node(node(243518,512,501,'$phrase','$phrase',hd,nm,[])).
additional_node(node(918488,517,512,'$phrase','$phrase',op,pp,[])).

correct_attachment(75988,1,514).
correct_attachment(75988,2,514).
correct_attachment(95884,13,505).
correct_attachment(243518,6,512).
correct_attachment(243518,7,512).
correct_attachment(365471,7,507).
correct_attachment(365471,8,507).
correct_attachment(583286,10,503).
correct_attachment(583286,11,503).
correct_attachment(621038,505,508).
correct_attachment(621038,508,510).
correct_attachment(742690,38,508).
correct_attachment(918488,4,517).
correct_attachment(918488,510,517).

unnecessary_node(75988,500).
unnecessary_node(365471,501).
unnecessary_node(583286,501).
unnecessary_node(621038,509).

