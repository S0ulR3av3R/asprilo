%%%%%%%%%%%%%%%%%%%%%%%%%% INIT

%init
%#external init(robot(R), X, Y) : robot(R), grid(X,Y).
%#external init(shelf(S), X, Y) : shelf(S), grid(X,Y).
#external ison(product(P),shelf(S)) : product(P), shelf(S).
#external init(lifted(R,S)) : robot(R), shelf(S).

%requests
#external order(O, product(P), pickingStation(S)) : product(P), pickingStation(S), order(O).

%%%%%%%%%%%%%%%%%%%%%%%%%% END INIT
