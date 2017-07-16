%%%%%%%%%%%%%%%%%%%%%%%%%% BASE
%#program base.


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

#const max_step=40.

%%%%%%%%%%%%%%%%%%%%%%%%%% STEP
%#program step(k).

%%% POSITIONING
%Robot
at(robot(R),X1,Y,T)             :-  do(robot(R),move(Xd,0),T), at(robot(R),X,Y,T-1), X1=X+Xd, x(X1), T=1..max_step.	                %Roboter bewegt sich in X
at(robot(R),X,Y1,T)             :-  do(robot(R),move(0,Yd),T), at(robot(R),X,Y,T-1), Y1=Y+Yd, y(Y1), T=1..max_step.	                %Roboter bewegt sich in Y
at(robot(R),X,Y,T)              :-  not do(robot(R),move(_,_),T), at(robot(R),X,Y,T-1), T=1..max_step.                                 %Roboter bewegt sich nicht

lifted(robot(R),shelf(S),T)     :-  do(robot(R),lift,T), at(shelf(S),X,Y,T-1), at(robot(R),X,Y,T-1), T=1..max_step.	                %shelf wird gelifted
lifted(robot(R),shelf(S),T)     :-  not do(robot(R),place,T), lifted(robot(R),shelf(S),T-1), T=1..max_step.		                    %shelf bleibt gelifted, wenn nicht geplaced wird

%Shelfs
at(shelf(S),X,Y,T)              :-  at(shelf(S),X,Y,T-1), lifted(robot(R),shelf(S),T), not do(robot(R),move(_,_),T), T=1..max_step.    %Shelf gelifted, roboter bewegt sich nicht
at(shelf(S),X,Y,T)              :-  at(shelf(S),X,Y,T-1), not lifted(robot(_),shelf(S),T), T=1..max_step.			                %Shelf ist nicht gelifted

at(shelf(S),X1,Y,T)             :-  do(robot(R),move(Xd,0),T), lifted(robot(R),shelf(S),T), at(shelf(S),X,Y,T-1), X1=X+Xd, x(X1), T=1..max_step.		%shelf geliftet, Roboter bewegt sich in X
at(shelf(S),X,Y1,T)             :-  do(robot(R),move(0,Yd),T), lifted(robot(R),shelf(S),T), at(shelf(S),X,Y,T-1), Y1=Y+Yd, y(Y1), T=1..max_step.		%shelf geliftet, Roboter bewegt sich in Y


%%% ACTIONS
{do(robot(R),place,T+1); do(robot(R),lift,T+1); do(robot(R),move(X,Y),T+1) : dir(X,Y)} 1          :-  at(robot(R),_,_,T).

:- do(robot(R),lift,T), at(robot(R),X,Y,T-1), not lifted(robot(R),_,T).
:- do(robot(R),place,T), at(robot(R),X,Y,T-1), not lifted(robot(R),_,T-1).
:- do(robot(R),move(Dx,Dy),T), dir(Dx,Dy), not grid(X+Dx, Y+Dy), at(robot(R),X,Y,T-1).

:- do(robot(R),lift,T), lifted(robot(R),_,T-1).
	

%collision constraints
:- at(robot(R),X,Y,T), at(robot(R2D2),X,Y,T), R<R2D2.		                                         %keine 2 Roboter auf gleicher Position.
:- at(shelf(S),X,Y,T), at(shelf(S2),X,Y,T), S<S2.						                                                %keine 2 Shelfs auf gleicher Position.
:- at(robot(R),X,Y,T-1), at(robot(R2D2),X2,Y2,T-1), at(robot(R),X2,Y2,T), at(robot(R2D2),X,Y,T), R<R2D2, dir(X-X2,Y-Y2). 	%Roboter dürfen Positionen nicht swapen

%state constraints
:- not 1{at(robot(R),_,_,T)} 1 , robot(R), T=1..max_step.
:- not {lifted(robot(R),_,T)} 1 , robot(R), T=1..max_step.
:- not 1{at(shelf(S),_,_,T)} 1 , shelf(S), T=1..max_step.



%Order Solved
solved(R, I, P, T)              :-  at(pickingStation(P),X,Y), at(shelf(S),X,Y,T), order(R, product(I), pickingStation(P),amount(A1)), ison(product(I),shelf(S),amount(A2)), A1<=A2.
solved(R, I, P, T+1)            :-  solved(R, I, P, T), T=1..max_step.


%Do
do(T) :- do(_,_,T).
:- do(T), not do(T-1), T-1 = 1..max_step.

#minimize{1,T:do(T)}.
#minimize{1,T:do(robot(R),_,T)}.
#minimize{1,T:solved(R,I,P,T)}.


%%%%%%%%%%%%%%%%%%%%%%%%%% END STEP

#show do/3.
#show do/1.
#show solved/4.
#show ison/3.

%%%%%%%%%%%%%%%%%%%%%%%%%% CHECK
%#program check(k).

:- lowestT(T), max_step < T.
:- order(R, product(I), pickingStation(P),_), not solved(R,I,P,_).

%#external query(k).
%%%%%%%%%%%%%%%%%%%%%%%%%% END CHECK
