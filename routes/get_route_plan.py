from pathlib import Path
import pandas as pd
import requests
import json
import copy
from pulp import *
import math

# -----------------Variable Declarations------------------------------------------------
DATA_DIR=Path("./data/gtfscecil")
number_of_stops=0
number_of_routes=0
number_of_trips=0
AdjMatrix=[]
timeMatrix=[]
stop_key_to_val={}
stop_val_to_key={}
trip_to_route={}
route_key_to_val={}
route_val_to_key={}
stop_lon={}
stop_lat={}
stop_names={}
stop= int(sys.argv[1])
MaxTime=240


# -----------------Function  Definitons------------------------------------------------
def isNaN(num):
    return num!= num

def time_to_sec(t):
    h, m, s = map(int, t.split(':'))
    return h * 3600 + m * 60 + s

def hashStops():
    stop_file=pd.read_csv(DATA_DIR/"stops.txt")
    stop_key_to_val={i:0 for i in stop_file.stop_id}
    stop_val_to_key={i:0 for i in range(len(stop_file))}
    count=0
    for i in stop_file.stop_id:
        stop_key_to_val[i]=count
        stop_val_to_key[count]=i
        count=count+1
    Stop_x = {stop_key_to_val[i]:0 for i in stop_file.stop_id}
    Stop_y = {stop_key_to_val[i]:0 for i in stop_file.stop_id}
    stop_name = {stop_key_to_val[i]:0 for i in stop_file.stop_id}
    for i in range(len(stop_file)):
        stop_name[stop_key_to_val[stop_file.loc[i].stop_id]]=stop_file.loc[i].stop_name
    for i in range(len(stop_file)):
        Stop_x[stop_key_to_val[stop_file.loc[i].stop_id]]=stop_file.loc[i].stop_lon
        Stop_y[stop_key_to_val[stop_file.loc[i].stop_id]]=stop_file.loc[i].stop_lat
    return stop_key_to_val,stop_val_to_key,count,Stop_x,Stop_y,stop_name

def hashRoutes():
    route_df=pd.read_csv(DATA_DIR/"routes.txt")
    route_key_to_val={ i:0 for i in route_df.route_id}
    route_val_to_key={i:0 for i in range(len(route_df))}
    count=0
    for i in route_df.route_id:
        route_key_to_val[i]=count
        route_val_to_key[count]=i
        count=count+1
    number_of_routes=count
    trip_df=pd.read_csv(DATA_DIR/"trips.txt")
    number_of_trips=len(trip_df)
    trip_to_route={i:0 for i in trip_df.trip_id}
    j=0
    for i in trip_df.trip_id:
        trip_to_route[i]=route_key_to_val[trip_df.loc[j].route_id]
        j+=1
    return number_of_routes,route_key_to_val,route_val_to_key,number_of_trips,trip_to_route
    
def buildGraph():
    table=pd.read_csv(DATA_DIR/"stop_times.txt")
    df=pd.DataFrame(table)
    graph_dict = {new_list: [] for new_list in table.trip_id}
    for j in range(len(df)):
        graph_dict[df.loc[j].trip_id].append([df.loc[j].stop_id,df.loc[j].arrival_time])
    timeMatrix=[[[100000 for col in range(number_of_routes)] for col in range(number_of_stops)] for row in range(number_of_stops)]
    AdjMatrix=[[[0 for col in range(number_of_routes)] for col in range(number_of_stops)] for row in range(number_of_stops)]
    for i in graph_dict:
        for j in range(len(graph_dict[i])-1):
            k=trip_to_route[i]
            u=stop_key_to_val[graph_dict[i][j][0]]
            v=stop_key_to_val[graph_dict[i][j+1][0]]
            time1=graph_dict[i][j][1]
            time2=graph_dict[i][j+1][1]
            if(isNaN(time1) or isNaN(time2)):
                time_diff=10
                timeMatrix[u][v][k]=time_diff
                AdjMatrix[u][v][k]=1
            else:
                time_diff=(time_to_sec(time2)-time_to_sec(time1))/60
                timeMatrix[u][v][k]=time_diff
                AdjMatrix[u][v][k]=1
    return AdjMatrix,timeMatrix

def get_plan(r0,stop):
    r=copy.copy(r0)
    route = []
    index=-1
    for i in range(len(r)):
        if r[i][0]==stop:
            index=i
    while len(r) != 0:
        plan = [r[index]]
        del (r[index])
        l = 0
        while len(plan) > l:
            l = len(plan)
            for i, j in enumerate(r):
                if plan[-1][1] == j[0]:
                    plan.append(j)
                    del (r[i])
    return(plan)

def generate_route():
    route =[(i,j,k) for i in range(number_of_stops) for j in range(number_of_stops)for k in range(number_of_routes) if x[i][j][k].value()==1]
    route_plan = get_plan(route,stop)
    times=[]
    currTime=0
    for t in range(len(route_plan)):
        elapsed_time=int(timeMatrix[route_plan[t][0]][route_plan[t][1]][route_plan[t][2]])
        if(elapsed_time==0):
            elapsed_time=2
        if (t==0):
            times.append(currTime+elapsed_time)
            currTime=elapsed_time
        elif(route_plan[t-1][2]!=route_plan[t][2]):
            times.append(currTime+elapsed_time+5)
            currTime=currTime+elapsed_time+5
        else:
            times.append(currTime+elapsed_time+2)
            currTime=currTime+elapsed_time+2
    path = []
    count=0
    for s in route_plan:
        t_0=0
        if(count!=0):
            t_0=times[count-1]
        t_1=times[count]
        path.append([s[0], stop_names[s[0]],stop_lon[s[0]],stop_lat[s[0]],t_0,s[1], stop_names[s[1]],stop_lon[s[1]],stop_lat[s[1]],t_1,s[2]])
        count+=1
    columns = ["stop_a_id", "stop_a_name", "stop_a_lat", "stop_a_lng", "stop_a_time","stop_b_id",
                "stop_b_name", "stop_b_lat", "stop_b_lng", "stop_b_time","route"]
    solution = pd.DataFrame(path,columns=columns)
    print(solution.to_json(orient="index"))


stop_key_to_val,stop_val_to_key,number_of_stops,stop_lon,stop_lat,stop_names=hashStops()
number_of_routes,route_key_to_val,route_val_to_key,number_of_trips,trip_to_route=hashRoutes()
AdjMatrix,timeMatrix=buildGraph()


# -----------------Solving Optimization  Problem using pulp------------------------------------------------

#Problem Definition
lp = LpProblem("TicketInspector",LpMaximize)

# -----------------Problem Variable Declaration Section------------------------------------------------
#x[i][j][k]=1 inspector visits stop j from stop i, going through route k
x=LpVariable.dicts("x",(range(number_of_stops),range(number_of_stops),range(number_of_routes)),0,1,LpBinary)

#y[k] =1, route k was visited (atleast 2 stops)
y=LpVariable.dicts("y",(range(number_of_routes)),0,1,LpBinary)

#t[i] defines order in which stop i is visited
t = pulp.LpVariable.dicts("t", (i for i in range(number_of_stops)),lowBound=1,upBound= number_of_stops, cat='Continuous')


# -----------------Problem Objective Declaration Section------------------------------------------------
#objective refers to quantity that is to be optimized
objective = lpSum(y[j] for j in range(number_of_routes))
lp += objective, "Objective Function"


# -----------------Constraints------------------------------------------------
#making sure that i,j,k are chosen such as they always exist in our adjacency matrix
for i in range(number_of_stops):
    for j in range (number_of_stops):
        for k in range(number_of_routes):
            lp+=x[i][j][k]<=AdjMatrix[i][j][k]

#To ensure y is chosen only if atleast two stops are visited in the route k
for k in range(number_of_routes):
    sumlanes=0
    for i in range(number_of_stops):
        for j in range(number_of_stops):
            sumlanes+=x[i][j][k]
    lp+=y[k]<=sumlanes/2

#stop i, stop j can have a single predecessor
for i in range(number_of_stops):
    single=0
    for j in range (number_of_stops):
        for k in range(number_of_routes):
            single+=x[i][j][k]
    lp+=single<=1
#stop i, stop j can have a single successor            
for i in range(number_of_stops):
    single=0
    for j in range (number_of_stops):
        for k in range(number_of_routes):
            single+=x[j][i][k]
    lp+=single<=1

#cycle has to start at the defined stop
start=0
for j in range (number_of_stops):
    for k in range(number_of_routes):
        start+=x[stop][j][k]
lp+=start==1

 #cycle has to end at the defined stop
end=0
for j in range (number_of_stops):
    for k in range(number_of_routes):
        end+=x[j][stop][k]
lp+=end==1

#flow conservation
for i in range(number_of_stops):
    sum1=0
    sum2=0
    ind=0
    for k in range(number_of_routes):
        for j in range(number_of_stops):
            sum1+=x[i][j][k]
            sum2+=x[j][i][k]

    lp+=sum1==sum2

#MTZ constraints for subtour elimination 
for i in range(number_of_stops):
    for j in range(number_of_stops):
        tripSum=lpSum(x[i][j][k] for k in range(number_of_routes))
        if i!=j and (i!=stop and j!=stop):
            lp+=t[j]>=t[i]+1 - (2*number_of_stops)*(1-tripSum)

#making sure only those edges are chosen that strictly comply to Ticket Inspector's time Window
tsum=0
for k in range(number_of_routes):
    for i in range(number_of_stops):
        for j in range(number_of_stops):
            tsum+=x[i][j][k]*(timeMatrix[i][j][k]+5)
lp+=tsum<=MaxTime 


lp.solve(PULP_CBC_CMD(msg=0))
status = str(LpStatus[lp.status])
generate_route()


