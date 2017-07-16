%%%%%%%%%%%%%%%%%%%%%%%%%% BASE
#program base.


dir(0,1).
dir(1,0).
dir(0,-1).
dir(-1,0).

lowestT(T)                                      :-  #min{Tl : order(R, product(I), pickingStation(P),amount(A1)),
                                                    ison(product(I),shelf(S),amount(A2)), A1<=A2, at(shelf(S),X,Y,0),
                                                    at(pickingStation(P),X2,Y2),Xp = |X-X2|, Yp = |Y-Y2|, Tl=Xp+Yp+1 }=T.
                                                    %minimal benötigte Zeit um Order zu lösen

grid(X,Y)                                       :-  init(object(node,_),value(at,(X,Y))).
highway(X,Y)                                    :-  init(object(highway,_),value(at,(X,Y))).
x(X);y(Y)                                       :-  grid(X,Y).

at(pickingStation(P),X,Y)                       :-  init(object(pickingStation,P),value(at,(X,Y))).
at(robot(R),X,Y,0)                              :-  init(object(robot,R),value(at,(X,Y))).
at(shelf(S),X,Y,0)                              :-  init(object(shelf,S),value(at,(X,Y))).
ison(product(P), shelf(S),amount(A))            :-  init(object(product,P),value(on,(S,A))).
order(R, product(P), pickingStation(S),amount(A))          :-  init(object(order,R),value(line,(P,A))),
                                                               init(object(order,R),value(pickingStation,S)).

robot(R)                                        :-  at(robot(R),X,Y,0).
shelf(S)                                        :-  at(shelf(S),X,Y,0).
pickingStation(P)                               :-  at(pickingStation(P),X,Y).
product(P)                                      :-  ison(product(P),shelf(S),amount(A)).
order(R)                                        :-  order(R, product(P), pickingStation(S), amount(A)).

%%%%%%%%%%%%%%%%%%%%%%%%%% END BASE 



%%%%%%%%%%%%%%%%%%%%%%%%%% STEP
#program step(k).

%%% POSITIONING
%Robot
at(robot(R),X1,Y,k)             :-  do(robot(R),move(Xd,0),k), at(robot(R),X,Y,k-1), X1=X+Xd, x(X1).	                %Roboter bewegt sich in X
at(robot(R),X,Y1,k)             :-  do(robot(R),move(0,Yd),k), at(robot(R),X,Y,k-1), Y1=Y+Yd, y(Y1).	                %Roboter bewegt sich in Y
at(robot(R),X,Y,k)              :-  not do(robot(R),move(_,_),k), at(robot(R),X,Y,k-1).                                 %Roboter bewegt sich nicht

lifted(robot(R),shelf(S),k)     :-  do(robot(R),lift,k), at(shelf(S),X,Y,k-1), at(robot(R),X,Y,k-1).	                %shelf wird gelifted
lifted(robot(R),shelf(S),k)     :-  not do(robot(R),place,k), lifted(robot(R),shelf(S),k-1).		                    %shelf bleibt gelifted, wenn nicht geplaced wird

%Shelfs
at(shelf(S),X,Y,k)              :-  at(shelf(S),X,Y,k-1), lifted(robot(R),shelf(S),k), not do(robot(R),move(_,_),k).    %Shelf gelifted, roboter bewegt sich nicht
at(shelf(S),X,Y,k)              :-  at(shelf(S),X,Y,k-1), not lifted(robot(_),shelf(S),k).				                %Shelf ist nicht gelifted

at(shelf(S),X1,Y,k)             :-  do(robot(R),move(Xd,0),k), lifted(robot(R),shelf(S),k), at(shelf(S),X,Y,k-1), X1=X+Xd, x(X1).		%shelf geliftet, Roboter bewegt sich in X
at(shelf(S),X,Y1,k)             :-  do(robot(R),move(0,Yd),k), lifted(robot(R),shelf(S),k), at(shelf(S),X,Y,k-1), Y1=Y+Yd, y(Y1).		%shelf geliftet, Roboter bewegt sich in Y


%%% ACTIONS
{do(robot(R),place,k); do(robot(R),lift,k); do(robot(R),move(X,Y),k) : dir(X,Y)} 1          :-  at(robot(R),_,_,k).

:- do(robot(R),lift,k), at(robot(R),X,Y,k-1), not lifted(robot(R),_,k).
:- do(robot(R),place,k), at(robot(R),X,Y,k-1), not lifted(robot(R),_,k-1).
:- do(robot(R),move(Dx,Dy),k), dir(Dx,Dy), not grid(X+Dx, Y+Dy), at(robot(R),X,Y,k-1).

:- do(robot(R),lift,k), lifted(robot(R),_,k-1).
	

%collision constraints
:- at(robot(R),X,Y,k), at(robot(R2D2),X,Y,k), R<R2D2.					                                                %keine 2 Roboter auf gleicher Position.
:- at(shelf(S),X,Y,k), at(shelf(S2),X,Y,k), S<S2.						                                                %keine 2 Shelfs auf gleicher Position.
:- at(robot(R),X,Y,k-1), at(robot(R2D2),X2,Y2,k-1), at(robot(R),X2,Y2,k), at(robot(R2D2),X,Y,k), R<R2D2, dir(X-X2,Y-Y2). 	%Roboter dürfen Positionen nicht swapen

%state constraints
:- not 1{at(robot(R),_,_,k)} 1 , robot(R).
:- not {lifted(robot(R),_,k)} 1 , robot(R).
:- not 1{at(shelf(S),_,_,k) } 1 , shelf(S).


%Order Solved
solved(R, I, P, k)              :-  at(pickingStation(P),X,Y), at(shelf(S),X,Y,k), order(R, product(I), pickingStation(P),amount(A1)), ison(product(I),shelf(S),amount(A2)), A1<=A2.
solved(R, I, P, k)              :-  solved(R, I, P, k-1).


%Do
do(k) :- do(_,_,k).
:- do(k), not do(k-1), k > 1.

#minimize{1,T:do(T)}.
#minimize{1,T:do(robot(R),_,T)}.
#minimize{1,T:solved(R,I,P,T)}.

%cast internal to visualizer format
%%cast internal plan format to output plan format
occurs(object(robot, RID), action(move, (DX,DY)), k)    :- do(robot(RID),move(DX,DY),k).
occurs(object(robot, RID), action(pickup, ()), k)       :- do(robot(RID),lift,k).
occurs(object(robot, RID), action(putdown, ()), k)      :- do(robot(RID),place,k).
occurs(object(robot, RID), action(deliver, (RQID, PRID, RQAMT)), t) :- solved(RQID,PRID,P,t), order(RQID,product(PRID),P,amount(RQAMT)), lifted(robot(RID),shelf(S),k),  at(pickingStation(P),X,Y), at(shelf(S),X,Y,k).


%%%%%%%%%%%%%%%%%%%%%%%%%% END STEP



%%%%%%%%%%%%%%%%%%%%%%%%%% CHECK
#program check(k).

:- lowestT(T), k < T, query(k).
:- order(R, product(I), pickingStation(P),_), not solved(R,I,P,k), query(k).

#external query(k).
%%%%%%%%%%%%%%%%%%%%%%%%%% END CHECK
