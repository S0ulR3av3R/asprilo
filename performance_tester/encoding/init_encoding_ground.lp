%%%%%%%%%%%%%%%%%%%%%%%%%% INIT

#program initRobot(id,x,y).
init(object(robot,id),value(at,(x,y))).

#program initShelf(id,x,y).
init(object(shelf,id),value(at,(x,y))).

#program initProduct(i,a,s).
init(object(product,i),value(on,(s,a))).

#program initOrder(i,p,s).
order(i,product(p),pickingStation(s)).

#program initLifted(r,s).
init(lifted(r,s)).

%%%%%%%%%%%%%%%%%%%%%%%%%% END INIT
