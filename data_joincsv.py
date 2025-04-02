import pandas as pd
import glob 

folder = glob.glob("joinfiles/*.csv")
df_final = pd.concat([pd.read_csv(arquivo,sep=';', encoding="latin1") for arquivo in folder], ignore_index=True)
df_final.to_csv("dislit_final.csv",   index=False, encoding="latin1")
