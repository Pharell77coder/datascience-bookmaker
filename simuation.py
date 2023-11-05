import matplotlib.pyplot as pl
import pandas as pa

T = pa.read_csv('season-1819.csv')

col = ['Date', 'HomeTeam', 'AwayTeam', 'FTHG', 'FTAG']
T = T[col]

T.rename(columns = {'HomeTeam' : 'DOM', 'AwayTeam' : 'EXT', 'FTHG' : 'BDOM', 'FTAG' : 'BEXT'}, inplace = True )

T.head()

len(T)

M = T['BDOM'].value_counts().sort_index()
M

M.plot.bar(color = 'black')
pl.xlabel('Buts par match')
pl.xticks(range(10), rotation = 0)

m = T.mean()
m

m['BDOM']

m['BEXT']

from scipy.stats import binom

X = binom(45, m['BDOM']/45)
E = [380 * X.pmf(k) for k in range(7)]
E

M.plot.bar(color = 'black')
pl.bar(range(7), E, color = 'red', alpha = 0.5, label = 'Théorie')
pl.xlabel('Buts par match')
pl.xticks(range(10), rotation = 0)
pl.legend(labels = ['Saison 2018/2019', 'Théorie'])

TD = T.query('DOM == "Marseille"').mean()
TD

TD['BDOM'] / m['BDOM']

TD['BEXT'] / m['BEXT']

TE = T.query('EXT == "Toulouse"').mean()
TE

TE['BDOM'] / m['BDOM']

TE['BEXT'] / m['BEXT']

(TD['BDOM'] / m['BDOM']) * (TE['BDOM'] / m['BDOM']) * m['BDOM']

(TD['BEXT'] / m['BEXT']) * (TE['BEXT'] / m['BEXT']) * m['BEXT']

def Esp(e1, e2):
    TD = T.query('DOM == @e1').mean()
    TE = T.query('EXT == @e2').mean()
    EX = TD['BDOM'] * TE['BDOM'] / m['BDOM']
    EY = TD['BEXT'] * TE['BEXT'] / m['BEXT']
    
    return EX, EY

m1, m2 = Esp('Marseille', 'Toulouse')
m1, m2

X = binom(45, m1 / 45)
Y = binom(45, m2 / 45)
s = 0
for i in range(7):
    s = s + X.pmf(i) * Y.pmf(i)
s

for match in range(380):
    e1 = T.loc[match, 'DOM']
    e2 = T.loc[match, 'EXT']
    T.loc[match, 'EX'], T.loc[match, 'EY'] = Esp(e1, e2)
T.head()

P_Off = {equipe : 0 for equipe in set(T['DOM'])}
P_Off

for e1, e2, x, y in zip(T['DOM'], T['EXT'], T['BDOM'], T['BEXT']):
    if x > y:
        P_Off[e1] = P_Off[e1] + 3
    elif x == y:
        P_Off[e1] = P_Off[e1] + 1
        P_Off[e2] = P_Off[e2] + 1
    else: 
        P_Off[e2] = P_Off[e2] + 3
P_Off

from random import *
from math import floor

def nb_buts(EX):
    X = 0
    for k in range(45):
        X = X + floor(random() + EX/45)
    return X

def simulation(n):
    P = {team : 0 for team in set(T['DOM'])}
    for k in range(n):
        for e1, e2, EX, EY in zip(T['DOM'], T['EXT'], T['EX'], T['EY']):
            x = nb_buts(EX)
            y = nb_buts(EY)
            if x > y :
                P[e1] = P[e1] + 3
            elif x == y:
                P[e1] = P[e1] + 1
                P[e2] = P[e2] + 1
            else :
                P[e2] = P[e2] + 3       
    return {equipe : P[equipe]/n for equipe in P }

P_Sim = simulation(1)
print(P_Sim)

M = pa.DataFrame()
M['Equipe'] = list(set(T['DOM']))
for k in range(20):
    equipe = M.loc[k, 'Equipe']
    M.loc[k, 'Points_Off'] = P_Off[equipe]
    M.loc[k, 'Points_Sim'] = P_Sim[equipe]

# création de ka colonne des rangs officiels   
M['Rangs_Off'] = M['Points_Off'].rank(ascending = False)
M['Rangs_Off'] = M['Rangs_Off'].astype(int)

# création de ka colonne des rangs simulés
M['Rangs_Sim'] = M['Points_Sim'].rank(ascending = False)
M['Rangs_Sim'] = M['Rangs_Sim'].astype(int)

#Affichage de T trié selon Points_Off
M.sort_values(by = 'Points_Off', ascending = False)
