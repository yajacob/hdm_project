from django.db import connection
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
import pandas as pd
import numpy as np
from ..modules.hdm_eval_calc import HdmEvalCalc
from django.views.generic import View

class ViewResult(View):
    @login_required(login_url="/accounts/login/")
    #def hdm_model_result(self, request, hdm_id, exp_id):
    def hdm_model_result(self, request, *args, **kwargs):
        hdm_id = ""
        exp_id = ""
        print(args)
        print(kwargs)

        cursor = connection.cursor()
    
        query = """SELECT a.*, '-' chart_cr, '-' chart_al FROM hdm_evaluation a JOIN 
                    (SELECT max(id) as max_id FROM hdm_evaluation GROUP BY hdm_id, expert_email) b
                ON a.id = b.max_id
                WHERE a.hdm_id = '%s'
                ORDER BY a.id DESC""" % (hdm_id)
        cursor.execute(query)
        columns = [col[0] for col in cursor.description]
        eval_all_list = [dict(zip(columns, row)) for row in cursor.fetchall()]
        
        # For Checked Experts
        if exp_id != "":
            exp_id = "AND a.expert_no in (" + exp_id + ")"
    
        # Individual Result
        query = """SELECT a.*, '-' chart_cr, '-' chart_al FROM hdm_evaluation a JOIN 
                    (SELECT max(id) as max_id FROM hdm_evaluation GROUP BY hdm_id, expert_email) b
                ON a.id = b.max_id
                WHERE a.hdm_id = '%s'
                %s
                ORDER BY a.id DESC""" % (hdm_id, exp_id)
        cursor.execute(query)
        columns = [col[0] for col in cursor.description]
        eval_list = [dict(zip(columns, row)) for row in cursor.fetchall()]
        
        main_df_cr = pd.DataFrame()
        main_df_fa = pd.DataFrame()
        main_df_al = pd.DataFrame()
    
        for ev in eval_list:
            eval_cr = pd.read_json(ev['eval_cr'])
            eval_cr.index = np.arange(1, len(eval_cr) + 1)
            main_df_cr = pd.concat([main_df_cr, eval_cr])
            eval_cr = eval_cr.to_html()
            eval_fa = pd.read_json(ev['eval_fa'])
            eval_fa.index = np.arange(1, len(eval_fa) + 1)
            main_df_fa = pd.concat([main_df_fa, eval_fa])
            eval_fa = eval_fa.to_html()
            eval_al = pd.read_json(ev['eval_al'])
            eval_al.index = np.arange(1, len(eval_al) + 1)
            main_df_al = pd.concat([main_df_al, eval_al])
            eval_al = eval_al[['Criteria', 'Factors', 'Alternatives', 'Value']].to_html()
            
            ev['eval_cr'] = eval_cr.replace("dataframe", "dataframe data_eval eval_cr") 
            ev['eval_fa'] = eval_fa.replace("dataframe", "dataframe data_eval eval_fa")
            ev['eval_al'] = eval_al.replace("dataframe", "dataframe data_eval eval_al")
            
            # char data
            temp = ""
            dic_chart_cr = pd.read_json(ev['result_cr']).to_dict()
            for key, val in dic_chart_cr["eval"].items():
                temp += "['%s', %s]," % (key, val)
            ev['chart_cr'] = "[%s]" % temp
            dic_sum = pd.read_json(ev['result_al']).sum(axis=1)
            temp = ""
            for key, val in dic_sum.items():
                temp += "['%s', %.2f]," % (key, val)
            ev['chart_al'] = "[%s]" % temp
            
            ev['result_cr'] = pd.read_json(ev['result_cr']).to_html()
            ev['result_fa'] = pd.read_json(ev['result_fa']).to_html().replace("0.000", "-").replace("0.00", "-").replace("0.0", "-")
            ev['result_al'] = pd.read_json(ev['result_al'])
            ev['result_al']['SUM'] = ev['result_al'].sum(axis=1)
            ev['result_al'] = ev['result_al'].to_html()
        
        cal = HdmEvalCalc(hdm_id)
        main_result_cr = cal.proc_result_main_cr(main_df_cr)
        main_result_fa = cal.proc_result_main_fa(main_df_fa)
        main_result_al = cal.proc_result_main_al(main_df_al)
        
        # char data for main
        main_result_cr = main_result_cr.to_html()
        main_result_fa = main_result_fa.to_html()
        main_result_al = main_result_al.to_html()
    
        main_result_cr = main_result_cr.replace("dataframe", "dataframe data_eval eval_cr") 
        main_result_fa = main_result_fa.replace("dataframe", "dataframe data_eval eval_fa")
        main_result_al = main_result_al.replace("dataframe", "dataframe data_eval eval_al")
        
        return render(request, 'hdm/model_result.html', {'eval_all_list': eval_all_list, 'eval_list': eval_list, 'hdm_id':hdm_id, 
                       'main_result_cr':main_result_cr, 'main_result_fa':main_result_fa, 'main_result_al':main_result_al})
    
