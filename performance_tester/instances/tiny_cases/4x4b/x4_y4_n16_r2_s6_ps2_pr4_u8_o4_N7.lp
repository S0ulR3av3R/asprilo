%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
% Grid Size X:                      4
% Grid Size Y:                      4
% Number of Nodes:                  16
% Number of Robots:                 2
% Number of Shelves:                6
% Number of picking stations:       2
% Number of products:               4
% Number of product units in total: 8
% Number of orders:                 4
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
#program base.

% init
init(object(node,1),value(at,(1,1))).
init(object(node,2),value(at,(2,1))).
init(object(node,3),value(at,(3,1))).
init(object(node,4),value(at,(4,1))).
init(object(node,5),value(at,(1,2))).
init(object(node,6),value(at,(2,2))).
init(object(node,7),value(at,(3,2))).
init(object(node,8),value(at,(4,2))).
init(object(node,9),value(at,(1,3))).
init(object(node,10),value(at,(2,3))).
init(object(node,11),value(at,(3,3))).
init(object(node,12),value(at,(4,3))).
init(object(node,13),value(at,(1,4))).
init(object(node,14),value(at,(2,4))).
init(object(node,15),value(at,(3,4))).
init(object(node,16),value(at,(4,4))).
init(object(order,1),value(line,(1,1))).
init(object(order,1),value(pickingStation,1)).
init(object(order,2),value(line,(4,1))).
init(object(order,2),value(pickingStation,1)).
init(object(order,3),value(line,(3,4))).
init(object(order,3),value(pickingStation,1)).
init(object(order,4),value(line,(2,1))).
init(object(order,4),value(pickingStation,2)).
init(object(pickingStation,1),value(at,(4,3))).
init(object(pickingStation,2),value(at,(1,1))).
init(object(product,1),value(on,(6,1))).
init(object(product,2),value(on,(2,2))).
init(object(product,3),value(on,(5,4))).
init(object(product,4),value(on,(3,1))).
init(object(robot,1),value(at,(4,4))).
init(object(robot,2),value(at,(2,3))).
init(object(shelf,1),value(at,(4,4))).
init(object(shelf,2),value(at,(3,3))).
init(object(shelf,3),value(at,(2,3))).
init(object(shelf,4),value(at,(2,2))).
init(object(shelf,5),value(at,(3,4))).
init(object(shelf,6),value(at,(4,1))).
