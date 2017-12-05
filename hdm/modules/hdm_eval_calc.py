from django.conf import settings
from django.db import connection
import pandas as pd
import numpy as np

class HdmEvalCalc:
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

    # Experts' Criteria evaluation to JSON
    def proc_eval_cr(self):
        eval_cr = pd.DataFrame(self.make_list(self.eval_dic['cr']))
        eval_cr.drop(0, inplace=True, axis=1)
        eval_cr.columns = ['Criteria', 'Value']
        eval_cr.sort(['Criteria', 'Value'])
        return eval_cr.to_json()

    # Experts' Factors evaluation to JSON
    def proc_eval_fa(self):
        #str_fa = 'CR11,Pink,27|CR12,Blue,73|CR11,Pink,71|CR13,Yellow,29|CR12,Blue,30|CR13,Yellow,70|CR21,16GB,32|CR22,32GB,68|CR21,16GB,31|CR23,64GB,69|CR21,16GB,62|CR24,128GB,38|CR22,32GB,56|CR23,64GB,44|CR22,32GB,50|CR24,128GB,50|CR23,64GB,57|CR24,128GB,43|CR31,USPS,27|CR32,UPS,73|CR31,USPS,67|CR33,FedEx,33|CR32,UPS,30|CR33,FedEx,70'
        df_cr = pd.DataFrame(self.make_list(self.eval_dic['cr']))
        df_cr.columns = ['ecode', 'ename', 'eval']
        df_cr['cr'] = df_cr['ecode'].str[2]
        df_cr.drop(['ecode','eval'], inplace=True, axis=1)
        df_cr = df_cr.drop_duplicates(subset=['ename', 'cr'])

        df_fa = pd.DataFrame(self.make_list(self.eval_dic['fa']))
        df_fa.columns = ['ecode', 'ename', 'eval']
        df_fa['cr'] = df_fa['ecode'].str[-2]
        df_fa['fa'] = df_fa['ecode'].str[-1]
        df_fa['eval'] = df_fa['eval'].astype(int)
        df_fa = pd.merge(df_fa, df_cr, how="inner", left_on="cr", right_on="cr")
        df_fa = df_fa[['ename_y', 'ename_x', 'eval']]
        df_fa.rename(columns={"ename_y":"Criteria", "ename_x":"Factors", "eval":"Value"}, inplace = True)

        return df_fa.to_json()

    # Experts' Alternatives evaluation to JSON
    def proc_eval_al(self):
        #str_al = 'CR111,Samsung,32|CR112,LG,68|CR111,Samsung,58|CR113,Sony,42|CR111,Samsung,21|CR114,Apple,79|CR112,LG,62|CR113,Sony,38|CR112,LG,57|CR114,Apple,43|CR113,Sony,69|CR114,Apple,31|CR121,Samsung,25|CR122,LG,75|CR121,Samsung,36|CR123,Sony,64|CR121,Samsung,59|CR124,Apple,41|CR122,LG,58|CR123,Sony,42|CR122,LG,48|CR124,Apple,52|CR123,Sony,60|CR124,Apple,40|CR131,Samsung,36|CR132,LG,64|CR131,Samsung,56|CR133,Sony,44|CR131,Samsung,57|CR134,Apple,43|CR132,LG,56|CR133,Sony,44|CR132,LG,32|CR134,Apple,68|CR133,Sony,42|CR134,Apple,58|CR211,Samsung,31|CR212,LG,69|CR211,Samsung,67|CR213,Sony,33|CR211,Samsung,64|CR214,Apple,36|CR212,LG,58|CR213,Sony,42|CR212,LG,56|CR214,Apple,44|CR213,Sony,64|CR214,Apple,36|CR221,Samsung,25|CR222,LG,75|CR221,Samsung,60|CR223,Sony,40|CR221,Samsung,22|CR224,Apple,78|CR222,LG,55|CR223,Sony,45|CR222,LG,33|CR224,Apple,67|CR223,Sony,60|CR224,Apple,40|CR311,Samsung,36|CR312,LG,64|CR311,Samsung,50|CR313,Sony,50|CR311,Samsung,32|CR314,Apple,68|CR312,LG,50|CR313,Sony,50|CR312,LG,56|CR314,Apple,44|CR313,Sony,37|CR314,Apple,63|CR321,Samsung,23|CR322,LG,77|CR321,Samsung,57|CR323,Sony,43|CR321,Samsung,58|CR324,Apple,42|CR322,LG,50|CR323,Sony,50|CR322,LG,32|CR324,Apple,68|CR323,Sony,62|CR324,Apple,38|CR231,Samsung,27|CR232,LG,73|CR231,Samsung,64|CR233,Sony,36|CR231,Samsung,31|CR234,Apple,69|CR232,LG,34|CR233,Sony,66|CR232,LG,60|CR234,Apple,40|CR233,Sony,70|CR234,Apple,30|CR241,Samsung,30|CR242,LG,70|CR241,Samsung,66|CR243,Sony,34|CR241,Samsung,27|CR244,Apple,73|CR242,LG,75|CR243,Sony,25|CR242,LG,16|CR244,Apple,84|CR243,Sony,75|CR244,Apple,25|CR331,Samsung,23|CR332,LG,77|CR331,Samsung,50|CR333,Sony,50|CR331,Samsung,36|CR334,Apple,64|CR332,LG,71|CR333,Sony,29|CR332,LG,36|CR334,Apple,64|CR333,Sony,53|CR334,Apple,47'
        
        df_cr = pd.DataFrame(self.make_list(self.eval_dic['cr']))
        df_fa = pd.DataFrame(self.make_list(self.eval_dic['fa']))
        df_al = pd.DataFrame(self.make_list(self.eval_dic['al']))
        
        df_cr.columns = ['ecode', 'ename', 'eval']
        df_fa.columns = ['ecode', 'ename', 'eval']
        df_al.columns = ['ecode', 'ename', 'eval']
        
        df_cr['cr'] = df_cr['ecode'].str[2]
        df_fa['cr'] = df_fa['ecode'].str[2]
        df_fa['fa'] = df_fa['ecode'].str[2:4]
        df_al['cr'] = df_al['ecode'].str[2]
        df_al['fa'] = df_al['ecode'].str[2:4]
        df_al['al'] = df_al['ecode'].str[4]
        
        df_cr.drop(['ecode','eval'], inplace=True, axis=1)
        df_cr= df_cr.drop_duplicates(subset=['ename', 'cr'])
        df_fa.drop(['ecode','eval'], inplace=True, axis=1)
        df_fa = df_fa[['fa', 'ename']]
        df_fa = df_fa.drop_duplicates(subset=['fa', 'ename'])
        df_al = pd.merge(df_al, df_cr, how="inner", left_on="cr", right_on="cr")
        df_al = pd.merge(df_al, df_fa, how="inner", left_on="fa", right_on="fa")
        df_al = df_al[['ename_y', 'ename', 'ename_x', 'eval']]
        df_al.rename(columns={"ename_y":"Criteria", "ename":"Factors", "ename_x":"Alternatives", "eval":"Value"}, inplace = True)
        
        return df_al.to_json()
    
    # to insert data - hdm_evaluation / result_cr
    def proc_result_cr_bak(self):
        #str_cr = 'CR10,Color,24|CR20,Memory,76|CR10,Color,72|CR30,Delivery,28|CR20,Memory,37|CR30,Delivery,63'
        cr_list = self.make_list(self.eval_dic['cr'])
        df_cr = pd.DataFrame(cr_list)
        df_cr.columns = ['ecode', 'ename', 'eval']
        df_cr['eval'] = df_cr['eval'].astype(int)

        df_cr = df_cr.groupby(['ecode', 'ename'], as_index=False).sum()
        df_cr.drop(['ecode'],inplace=True,axis=1)
        df_cr = df_cr.set_index('ename')
        sum_cr = df_cr['eval'].sum()
        df_cr['eval'] = round(df_cr['eval']/sum_cr, 3)
        
        return df_cr.to_json()

    # to insert data - hdm_evaluation / result_cr
    def proc_result_cr(self):
        #str_cr = 'CR10,Color,24|CR20,Memory,76|CR10,Color,72|CR30,Delivery,28|CR20,Memory,37|CR30,Delivery,63'
        cr_list = self.make_list(self.eval_dic['cr'])
        df_cr = pd.DataFrame(cr_list)
        df_cr.columns = ['ecode', 'ename', 'eval']
        df_cr['eval'] = df_cr['eval'].astype(int)

        df_cr = df_cr.groupby(['ecode', 'ename'], as_index=False).sum()
        #df_cr['ev_index'] = df_cr['ecode'] +','+ df_cr['ename']
        #df_cr.drop(['ecode'],inplace=True,axis=1)
        #df_cr.drop(['ename'],inplace=True,axis=1)
        #df_cr = df_cr.set_index('ev_index')
        sum_cr = df_cr['eval'].sum()
        df_cr['eval'] = round(df_cr['eval']/sum_cr, 3)
        
        return df_cr.to_json()

    # to insert data - hdm_evaluation / result_fa
    def proc_result_fa(self):
        hdm_str_cr = self.hdm_dic['cr']
        fa_list = self.make_list(self.eval_dic['fa'])
        df_fa = pd.DataFrame(fa_list)
        df_fa.columns = ['ecode', 'ename', 'eval']
        df_fa['ename'] = df_fa['ecode'] + df_fa['ename']
        #df_fa = df_fa.sort_values(by=['ecode'])
        df_fa['cr'] = df_fa['ecode'].str[-2]
        df_fa['fa'] = df_fa['ecode'].str[-1]
        df_fa['eval'] = df_fa['eval'].astype(int)

        pdf_fa = pd.pivot_table(df_fa, index=['ename'], columns=['cr'], values='eval', aggfunc=np.sum).fillna(0)
        sum_fa = pdf_fa.sum()

        for idx, col in pdf_fa.iteritems():
            pdf_fa[idx] = round(col/sum_fa[int(idx)-1], 3)
            
        fa_list = []
        for i in hdm_str_cr.split(','):
            fa_list.append(i)

        pdf_fa.columns = fa_list
        
        pdf_fa['ecode'] = pdf_fa.index.values
        pdf_fa['ecode'] = pdf_fa['ecode'].str[:4]
        pdf_fa['ename'] = pdf_fa.index.str[4:]
        print("*"*80)
        print("pdf_fa:", pdf_fa)

        return pdf_fa.to_json()

    # to insert data - hdm_evaluation / result_fa
    def proc_result_fa_bak(self):
        hdm_str_cr = self.hdm_dic['cr']
        fa_list = self.make_list(self.eval_dic['fa'])
        df_fa = pd.DataFrame(fa_list)
        df_fa.columns = ['ecode', 'ename', 'eval']
        df_fa['ename'] = df_fa['ecode'] + df_fa['ename']
        #df_fa = df_fa.sort_values(by=['ecode'])
        df_fa['cr'] = df_fa['ecode'].str[-2]
        df_fa['fa'] = df_fa['ecode'].str[-1]
        df_fa['eval'] = df_fa['eval'].astype(int)

        pdf_fa = pd.pivot_table(df_fa, index=['ename'], columns=['cr'], values='eval', aggfunc=np.sum).fillna(0)
        sum_fa = pdf_fa.sum()

        for idx, col in pdf_fa.iteritems():
            pdf_fa[idx] = round(col/sum_fa[int(idx)-1], 3)
            
        # change index name
        pdf_fa= pdf_fa.set_index(pdf_fa.index.str[4:])
                
        fa_list = []
        for i in hdm_str_cr.split(','):
            fa_list.append(i)

        pdf_fa.columns = fa_list
        return pdf_fa.to_json()

    # to insert data - hdm_evaluation / result_al
    def proc_result_al(self):
        #str_al = 'CR111,Samsung,32|CR112,LG,68|CR111,Samsung,58|CR113,Sony,42|CR111,Samsung,21|CR114,Apple,79|CR112,LG,62|CR113,Sony,38|CR112,LG,57|CR114,Apple,43|CR113,Sony,69|CR114,Apple,31|CR121,Samsung,25|CR122,LG,75|CR121,Samsung,36|CR123,Sony,64|CR121,Samsung,59|CR124,Apple,41|CR122,LG,58|CR123,Sony,42|CR122,LG,48|CR124,Apple,52|CR123,Sony,60|CR124,Apple,40|CR131,Samsung,36|CR132,LG,64|CR131,Samsung,56|CR133,Sony,44|CR131,Samsung,57|CR134,Apple,43|CR132,LG,56|CR133,Sony,44|CR132,LG,32|CR134,Apple,68|CR133,Sony,42|CR134,Apple,58|CR211,Samsung,31|CR212,LG,69|CR211,Samsung,67|CR213,Sony,33|CR211,Samsung,64|CR214,Apple,36|CR212,LG,58|CR213,Sony,42|CR212,LG,56|CR214,Apple,44|CR213,Sony,64|CR214,Apple,36|CR221,Samsung,25|CR222,LG,75|CR221,Samsung,60|CR223,Sony,40|CR221,Samsung,22|CR224,Apple,78|CR222,LG,55|CR223,Sony,45|CR222,LG,33|CR224,Apple,67|CR223,Sony,60|CR224,Apple,40|CR311,Samsung,36|CR312,LG,64|CR311,Samsung,50|CR313,Sony,50|CR311,Samsung,32|CR314,Apple,68|CR312,LG,50|CR313,Sony,50|CR312,LG,56|CR314,Apple,44|CR313,Sony,37|CR314,Apple,63|CR321,Samsung,23|CR322,LG,77|CR321,Samsung,57|CR323,Sony,43|CR321,Samsung,58|CR324,Apple,42|CR322,LG,50|CR323,Sony,50|CR322,LG,32|CR324,Apple,68|CR323,Sony,62|CR324,Apple,38|CR231,Samsung,27|CR232,LG,73|CR231,Samsung,64|CR233,Sony,36|CR231,Samsung,31|CR234,Apple,69|CR232,LG,34|CR233,Sony,66|CR232,LG,60|CR234,Apple,40|CR233,Sony,70|CR234,Apple,30|CR241,Samsung,30|CR242,LG,70|CR241,Samsung,66|CR243,Sony,34|CR241,Samsung,27|CR244,Apple,73|CR242,LG,75|CR243,Sony,25|CR242,LG,16|CR244,Apple,84|CR243,Sony,75|CR244,Apple,25|CR331,Samsung,23|CR332,LG,77|CR331,Samsung,50|CR333,Sony,50|CR331,Samsung,36|CR334,Apple,64|CR332,LG,71|CR333,Sony,29|CR332,LG,36|CR334,Apple,64|CR333,Sony,53|CR334,Apple,47'
        hdm_str_fa = self.hdm_dic['fa']
        al_list = self.make_list(self.eval_dic['al'])
        df_al = pd.DataFrame(al_list)
        df_al.columns = ['ecode', 'ename', 'eval']
        df_al['cr'] = df_al['ecode'].str[-3]
        df_al['fa'] = df_al['ecode'].str[-3:-1]
        df_al['al'] = df_al['ecode'].str[-1]
        df_al['eval'] = df_al['eval'].astype(int)

        pdf_al = pd.pivot_table(df_al, index=['ename'], columns=['fa'], values='eval', aggfunc=np.sum)
        sum_al = pdf_al.sum()[0]

        for col in pdf_al:
            pdf_al[col] = round(pdf_al[col]/sum_al, 3)
            
        fa_list = []
        for i in hdm_str_fa.split('|'):
            for j in i.split(','):
                fa_list.append(j)

        pdf_al.columns = fa_list
        return pdf_al.to_json()

    def proc_incon_json(self):
        inc_str = self.eval_dic['inc']
        inc_list = self.make_list(inc_str)
        print("inc_list:",inc_list)
        df_incon = pd.DataFrame(inc_list)
        print("df_incon:",df_incon)
        df_incon.columns = ['ecode', 'incon']
        df_incon['incon'] = df_incon['incon'].astype(float)
        return df_incon.to_json()
        
