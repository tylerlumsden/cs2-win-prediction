from awpy import Demo
import time
import marshal as json
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split, cross_val_score
import numpy as np
import tensorflow as tf
import tensorflow.keras as keras
from tensorflow.keras.utils import to_categorical
import os
import json

def parse_formatted(demoName):
    print("Parsing Demo")

    start = time.time()

    dem = Demo(demoName)

    dem.ticks.to_csv("test.csv")

    end = time.time()

    print("Time elapsed: ", (end - start), "seconds")

    round_winner = dem.rounds[["winner", "round"]]

    ct_pos = dem.ticks.copy()[["team_name", "X", "Y","tick"]]
    ct_pos = ct_pos[ct_pos.team_name == "CT"]
    ct_pos = ct_pos.groupby(ct_pos['tick']).agg({'team_name':'first','X':list,'Y':list})
    ct_pos = ct_pos.join(pd.DataFrame(ct_pos.pop('X').tolist()).rename(columns=lambda x:f"X{x+1}_ct"))
    ct_pos = ct_pos.join(pd.DataFrame(ct_pos.pop('Y').tolist()).rename(columns=lambda x:f"Y{x+1}_ct"))

    t_pos = dem.ticks.copy()[["team_name", "X", "Y", "tick"]]
    t_pos = t_pos[t_pos.team_name == "TERRORIST"]
    t_pos = t_pos.groupby(t_pos['tick']).agg({'team_name':'first','X':list,'Y':list})
    t_pos = t_pos.join(pd.DataFrame(t_pos.pop('X').tolist()).rename(columns=lambda x:f"X{x+1}_t"))
    t_pos = t_pos.join(pd.DataFrame(t_pos.pop('Y').tolist()).rename(columns=lambda x:f"Y{x+1}_t"))


    final = dem.ticks.copy()[["round", "tick"]]
    final = pd.merge(final, round_winner, on='round', how='outer')

    final = pd.merge(final, ct_pos, on='tick', how='outer')
    final = pd.merge(final, t_pos, on='tick', how='outer')
    final = final.drop(columns=['team_name_x', 'team_name_y'])

    final = final[np.arange(len(final))%128==0]

    return final

count = 0
final = pd.DataFrame.empty
test = pd.DataFrame.empty
for filename in os.listdir("parse/csv"):
    f = os.path.join("parse/csv", filename)

    if os.path.isfile(f):     
        if final is pd.DataFrame.empty:
            final = pd.read_csv(f)
            final = final.iloc[::1000]
        else:
            data = pd.read_csv(f)
            data = data.iloc[::1000]
            final = pd.concat([final, data], axis=0)
        count = count + 1


print(count, "CSV files loaded")

#final = final.dropna()
final = final.drop_duplicates()
final.to_csv("test.csv")

x, y = final.drop(columns=['Winner', 'Round', 'Tick']), final[["Winner"]]

final = final.dropna()

#print(x.count())

#x_train, y_train = x,y

#test = test[test.reset_index().index % 1000 == 0] 
#x_test, y_test = test.drop(columns=['Winner', 'Round', 'Tick']), test["Winner"]

x_train, x_test, y_train, y_test = train_test_split(x, y, test_size=0.2)

#print(x)

#x_train, x_test, y_train, y_test = train_test_split(x, y, test_size=0.2)

print(x.info())
print(y.info())

forest = RandomForestClassifier(n_jobs=4, n_estimators=400)
forest.fit(x_train, y_train)

#forest classifier returning perfect score??? is this expected??
#print("test")
print(forest.score(x_test, y_test))

#test.to_csv("testing.csv")

#predict = forest.predict_proba(x_test)

#with open("output.txt", "w") as txt_file:
    #for line in predict:
        #txt_file.write("".join(str(line)) + "\n") # works with any number of elements in a line
        
#predict_row = x.iloc[1:3]

#predict_row.loc[predict_row['health_y'] > 1.0, 'health_y'] = 0.0

#print(predict_row)

#print(forest.predict(predict_row))


#model = tf.keras.models.Sequential()

#model.add(tf.keras.layers.Dense(10, activation=tf.nn.relu))
#model.add(tf.keras.layers.Dense(10, activation=tf.nn.relu))
#model.add(tf.keras.layers.Dense(2, activation=tf.nn.sigmoid))

#model.compile(optimizer='adam',
              #loss='binary_crossentropy',
              #metrics=['accuracy'])

#y_test = to_categorical(y_test, num_classes=2)
#y_train = to_categorical(y_train, num_classes=2)           

#model.fit(x_train, y_train, epochs=10)

#val_loss, val_acc = model.evaluate(x_test, y_test)  # evaluate the out of sample data with model
#print(val_loss)  # model's loss (error)
#print(val_acc)  # model's accuracy

#predict = model.predict(x_test)
predict = forest.predict_proba(x_test)

#print(cross_val_score(forest, x_test, y_test, cv=8))

samplepredict = x_test.head(10)

samplepredict = samplepredict.assign(CT_X1 = -800.0)
samplepredict = samplepredict.assign(CT_X2 = -800.0)
samplepredict = samplepredict.assign(CT_X3 = 1000.0)
samplepredict = samplepredict.assign(CT_X4 = 1000.0)
samplepredict = samplepredict.assign(CT_X5 = 1000.0)
samplepredict = samplepredict.assign(CT_Y1 = 800.0)
samplepredict = samplepredict.assign(CT_Y2 = 800.0)
samplepredict = samplepredict.assign(CT_Y3 = 1700.0)
samplepredict = samplepredict.assign(CT_Y4 = 1700.0)
samplepredict = samplepredict.assign(CT_Y5 = 1700.0)

samplepredict = samplepredict.assign(T_X1 = -1000.0)
samplepredict = samplepredict.assign(T_X2 = -1000.0)
samplepredict = samplepredict.assign(T_X3 = -1000.0)
samplepredict = samplepredict.assign(T_X4 = -200.0)
samplepredict = samplepredict.assign(T_X5 = -200.0)
samplepredict = samplepredict.assign(T_Y1 = -300.0)
samplepredict = samplepredict.assign(T_Y2 = -300.0)
samplepredict = samplepredict.assign(T_Y3 = -300.0)
samplepredict = samplepredict.assign(T_Y4 = 200.0)
samplepredict = samplepredict.assign(T_Y5 = 200.0)

samplepredict = samplepredict.assign(AliveCT_1 = True)
samplepredict = samplepredict.assign(AliveCT_2 = True)
samplepredict = samplepredict.assign(AliveCT_3 = True)
samplepredict = samplepredict.assign(AliveCT_4 = True)
samplepredict = samplepredict.assign(AliveCT_5 = True)

samplepredict = samplepredict.assign(AliveT_1 = True)
samplepredict = samplepredict.assign(AliveT_2 = True)
samplepredict = samplepredict.assign(AliveT_3 = True)
samplepredict = samplepredict.assign(AliveT_4 = True)
samplepredict = samplepredict.assign(AliveT_5 = True)
samplepredict = samplepredict.assign(TimeLeft = 90.0)

print(samplepredict)
#print(model.predict(samplepredict))
print(forest.predict_proba(samplepredict))

samplepredict = samplepredict.assign(AliveT_1 = False)
#print(model.predict(samplepredict))
print(forest.predict_proba(samplepredict))

samplepredict = samplepredict.assign(AliveT_2 = False)
#print(model.predict(samplepredict))
print(forest.predict_proba(samplepredict))

samplepredict = samplepredict.assign(AliveT_3 = False)
#print(model.predict(samplepredict))
print(forest.predict_proba(samplepredict))

samplepredict = samplepredict.assign(AliveT_4 = False)
#print(model.predict(samplepredict))
print(forest.predict_proba(samplepredict))

samplepredict = samplepredict.assign(AliveT_5 = False)
#print(model.predict(samplepredict))
print(forest.predict_proba(samplepredict))


with open("outputNN.txt", "w") as txt_file:
    for line in predict:
        txt_file.write("".join(str(line)) + "\n") # works with any number of elements in a lineu