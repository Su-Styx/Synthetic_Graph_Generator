import pandas as pd 


csvpath='/home/styx/Dissertation/Synthetic_Graph_Generator/modules/ER_model/15_runs_per_size2.csv'
df =pd.read_csv(csvpath)

groups = df.groupby(df.index // 15)
df_list = [group for _, group in groups]

n_100 = df_list[0]

n_1000 = df_list[1]

n_5000 =df_list[2]

print(n_100['n_edges'])
# print(n_1000['n_edges'])
# print(n_5000)




# temp=0
# for i in n_100['n_edges']: temp+=i
# print('n-100: '+str(temp/15))
# temp=0
# for i in n_1000['n_edges']: temp+=i
# print('n-1000: '+str(temp/15))
# temp=0
# for i in n_5000['n_edges']: temp+=i
# print('n-5000:' +str(temp/15))
# temp=0