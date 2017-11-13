from django.conf import settings
from django.db import connection
import pandas as pd
import numpy as np

class HdmResultCalc:

    def __init__(self, hdm_id=None, eval_dic=None):
        # Model Design
        self.hdm_dic = dict()
        # Evaluation
        self.eval_dic = eval_dic
        # Set hdm_dic
        self.getDesign(hdm_id)

    def getDesign(self, hdm_id):
        cursor = connection.cursor()
        query = "SELECT hdm_criteria, hdm_factors, hdm_alternatives FROM hdm_hdm WHERE id='%s'" % hdm_id
        cursor.execute(query)
        hdm = cursor.fetchone()
        self.hdm_dic['cr'] = hdm[0]
        self.hdm_dic['fa'] = hdm[1]
        self.hdm_dic['al'] = hdm[2]
        self.hdm_dic['len_cr'] = len(hdm[0].split(","))
        self.hdm_dic['len_fa'] = []
        self.hdm_dic['len_al'] = len(hdm[2].split(","))
        for hm in hdm[1].split("|"):
            self.hdm_dic['len_fa'].append(len(hm.split(",")))

    def make_list(self, temp):
        temp_list = temp.split("|")
        rs_list = []
        for tl in temp_list:
            rs_list.append(tl.split(","))
        return rs_list


    def proc_total_result_al(self, hdm_id, exp_no):
        cursor = connection.cursor()
        query = "SELECT get_eval_cr, get_eval_fa, get_eval_al FROM hdm_evaluation WHERE hdm_id='%s' AND expert_no=%s" % (hdm_id, exp_no)
        cursor.execute(query)
        exp = cursor.fetchone()

        #ev_list = self.make_list(self.eval_dic['ob']+"|"+self.eval_dic['cr']+"|"+self.eval_dic['fa'])
        ev_list = self.make_list(exp[0]+"|"+exp[1]+"|"+exp[2])
        
        df = pd.DataFrame(ev_list)
        df.columns = ['ecode', 'ename', 'eval']

        # substring - remove "CR" in ecode 
        df['ecode'] = df['ecode'].str[2:]
        df['ecode'] = df['ecode'].astype(int)
        df['eval']  = df['eval'].astype(int)

        # group by - sum eval
        df = df.groupby(['ecode', 'ename'], as_index=False).sum()

        # dataframe for each data
        cr = df[df['ecode']%10 == 0]
        fa = df[(df['ecode'] < 100) & (df['ecode']%10 > 0)]
        al = df[(df['ecode'] > 100)]

        # dictionary for each data
        dic_cr = df[df['ecode']%10 == 0].set_index('ecode')['eval'].to_dict()
        dic_fa = df[(df['ecode'] < 100) & (df['ecode']%10 > 0)].set_index('ecode')['eval'].to_dict()
        dic_al = df[(df['ecode'] > 100)].set_index('ecode')['eval'].to_dict()
        
        #al_temp_result = [0] * self.len_al
        #al_result = [0] * self.len_al
        al_temp_result = [0] * self.hdm_dic['len_al']
        al_result = [0] * self.hdm_dic['len_al']

        # calculation for alternatives
        for cr_key, cr_value in dic_cr.items():
            for fa_key, fa_value in dic_fa.items():
                for al_key, al_value in dic_al.items():
                    idx = al_key % 10 - 1
                    al_val_mul = round((al_value * cr_value * fa_value)/100)
                    al_temp_result[idx] += al_val_mul 

        for idx, al in enumerate(al_temp_result):
            temp = al/sum(al_temp_result)*100
            al_result[idx] = round(temp, 2)
            #print("al: %f, temp: %f, result:%f" % (al, temp, al_result[idx]))

        al_list_key = list(self.hdm_dic['al'].split(","))
        al_result_dic = {}

        for idx, key in enumerate(al_list_key):
            temp = "%2.2f" % al_result[idx]
            al_result_dic[key] = temp
        
        #return {"cr":dic_cr, "fa":dic_fa, "al":dic_al, "al_dat":al_dat}
        return al_result_dic


    def proc_result_main_cr(self, df_cr):
        #str_cr = 'CR10,Color,24|CR20,Memory,76|CR10,Color,72|CR30,Delivery,28|CR20,Memory,37|CR30,Delivery,63'
        df_cr = df_cr.groupby(['Criteria'], as_index=False).sum()
        sum_cr = df_cr['Value'].sum()
        df_cr['Value'] = round(df_cr['Value']/sum_cr, 3)
        
        return df_cr

    def proc_result_main_fa(self, df_fa):
        df_fa = df_fa.groupby(['Criteria', 'Factors'], as_index=False).sum()
        sum_fa = df_fa['Value'].sum()
        df_fa['Value'] = round(df_fa['Value']/sum_fa, 3)
        
        return df_fa

    def proc_result_main_al(self, df_al):
        print(df_al)
        df_al = df_al.groupby(['Criteria', 'Factors', 'Alternatives'], as_index=False).sum()
        sum_al = df_al['Value'].sum()
        df_al['Value'] = round(df_al['Value']/sum_al, 3)

        return df_al

def main():
    eval_dic = dict()
    eval_dic['hdm_id'] = 19
    eval_dic['ob'] = 'CR10,Color,32|CR20,Memory,68|CR10,Color,64|CR30,Delivery,36|CR20,Memory,70|CR30,Delivery,30'
    eval_dic['cr'] = 'CR21,16GB,24|CR22,32GB,76|CR21,16GB,22|CR23,64GB,78|CR21,16GB,63|CR24,128GB,37|CR22,32GB,75|CR23,64GB,25|CR22,32GB,80|CR24,128GB,20|CR23,64GB,72|CR24,128GB,28|CR11,Pink,67|CR12,Blue,33|CR11,Pink,77|CR13,Yellow,23|CR12,Blue,64|CR13,Yellow,36|CR31,USPS,15|CR32,UPS,85|CR31,USPS,72|CR33,FedEx,28|CR32,UPS,26|CR33,FedEx,74'
    eval_dic['fa'] = 'CR111,Samsung,26|CR112,LG,74|CR111,Samsung,63|CR113,Sony,37|CR111,Samsung,27|CR114,Apple,73|CR112,LG,27|CR113,Sony,73|CR112,LG,64|CR114,Apple,36|CR113,Sony,76|CR114,Apple,24|CR121,Samsung,8|CR122,LG,92|CR121,Samsung,56|CR123,Sony,44|CR121,Samsung,50|CR124,Apple,50|CR122,LG,63|CR123,Sony,37|CR122,LG,66|CR124,Apple,34|CR123,Sony,72|CR124,Apple,28|CR131,Samsung,26|CR132,LG,74|CR131,Samsung,25|CR133,Sony,75|CR131,Samsung,63|CR134,Apple,37|CR132,LG,65|CR133,Sony,35|CR132,LG,61|CR134,Apple,39|CR133,Sony,68|CR134,Apple,32|CR211,Samsung,50|CR212,LG,50|CR211,Samsung,72|CR213,Sony,28|CR211,Samsung,27|CR214,Apple,73|CR212,LG,68|CR213,Sony,32|CR212,LG,32|CR214,Apple,68|CR213,Sony,50|CR214,Apple,50|CR221,Samsung,50|CR222,LG,50|CR221,Samsung,50|CR223,Sony,50|CR221,Samsung,24|CR224,Apple,76|CR222,LG,71|CR223,Sony,29|CR222,LG,46|CR224,Apple,54|CR223,Sony,61|CR224,Apple,39|CR231,Samsung,23|CR232,LG,77|CR231,Samsung,57|CR233,Sony,43|CR231,Samsung,25|CR234,Apple,75|CR232,LG,60|CR233,Sony,40|CR232,LG,24|CR234,Apple,76|CR233,Sony,50|CR234,Apple,50|CR311,Samsung,26|CR312,LG,74|CR311,Samsung,50|CR313,Sony,50|CR311,Samsung,28|CR314,Apple,72|CR312,LG,61|CR313,Sony,39|CR312,LG,27|CR314,Apple,73|CR313,Sony,74|CR314,Apple,26|CR241,Samsung,25|CR242,LG,75|CR241,Samsung,62|CR243,Sony,38|CR241,Samsung,50|CR244,Apple,50|CR242,LG,59|CR243,Sony,41|CR242,LG,26|CR244,Apple,74|CR243,Sony,66|CR244,Apple,34|CR321,Samsung,33|CR322,LG,67|CR321,Samsung,54|CR323,Sony,46|CR321,Samsung,30|CR324,Apple,70|CR322,LG,68|CR323,Sony,32|CR322,LG,14|CR324,Apple,86|CR323,Sony,79|CR324,Apple,21|CR331,Samsung,24|CR332,LG,76|CR331,Samsung,65|CR333,Sony,35|CR331,Samsung,25|CR334,Apple,75|CR332,LG,69|CR333,Sony,31|CR332,LG,77|CR334,Apple,23|CR333,Sony,73|CR334,Apple,27'

    hrc = HdmResultCalc(eval_dic)
    hrc.getDesign(eval_dic['hdm_id'])
    hrc.proc_total_result_al()

if __name__ == "__main__":
    main()

