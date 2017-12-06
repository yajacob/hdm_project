import csv

from django.contrib.auth.decorators import login_required
from django.db import connection
from django.http import HttpResponse
from django.shortcuts import render, redirect

from hdm.modules.hdm_db_proc import *
from hdm.modules.hdm_result_calc import HdmResultCalc
import numpy as np
import pandas as pd
import json

@login_required(login_url="/accounts/login/")
def hdm_result_csv_download(request, hdm_id, exp_id):
    cursor = connection.cursor()
    
    # Individual Result
    query = """SELECT a.*, '-' chart_cr, '-' chart_al FROM hdm_evaluation a JOIN 
                (SELECT max(id) as max_id FROM hdm_evaluation GROUP BY hdm_id, expert_email) b
            ON a.id = b.max_id
            WHERE a.hdm_id = '%s'
              AND a.expert_no = '%s'
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
        #eval_cr = eval_cr.to_html()
        
        eval_fa = pd.read_json(ev['eval_fa'])
        eval_fa.index = np.arange(1, len(eval_fa) + 1)
        main_df_fa = pd.concat([main_df_fa, eval_fa])
        #eval_fa = eval_fa.to_html()
        
        eval_al = pd.read_json(ev['eval_al'])
        eval_al.index = np.arange(1, len(eval_al) + 1)
        main_df_al = pd.concat([main_df_al, eval_al])
        #eval_al = eval_al[['Criteria', 'Factors', 'Alternatives', 'Value']].to_html()

    # change order of the dataframe
    main_df_al = main_df_al[['Criteria', 'Factors', 'Alternatives', 'Value']]
    
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="hdm_evaluation.csv"'

    temp_key1 = []
    temp_key2 = []
    temp_key3 = []
    temp_val = []
    write_list = []
    writer = csv.writer(response)
    writer.writerow(['1. Evaluation for Criteria'])
    for idx, alist in enumerate(main_df_cr.values.tolist()):
        temp_key1.append(alist[0])
        temp_val.append(alist[1])
        
        if idx%2 == 1:
            write_list += temp_key1
            write_list += temp_val
            writer.writerow(write_list)
            temp_key1 = []
            temp_val = []
            write_list = []
    
    writer.writerow([''])
    writer.writerow(['2. Evaluation for Factors'])
    for idx, alist in enumerate(main_df_fa.values.tolist()):
        if idx%2 == 0:
            temp_key1.append(alist[0])
        temp_key2.append(alist[1])
        temp_val.append(alist[2])
        
        if idx%2 == 1:
            write_list += temp_key1
            write_list += temp_key2
            write_list += temp_val
            writer.writerow(write_list)
            temp_key1 = []
            temp_key2 = []
            temp_val = []
            write_list = []
    
    writer.writerow([''])
    writer.writerow(['3. Evaluation for Alternatives'])
    for idx, alist in enumerate(main_df_al.values.tolist()):
        if idx%2 == 0:
            temp_key1.append(alist[0])
            temp_key2.append(alist[1])
        temp_key3.append(alist[2])
        temp_val.append(alist[3])
        
        if idx%2 == 1:
            write_list += temp_key1
            write_list += temp_key2
            write_list += temp_key3
            write_list += temp_val
            writer.writerow(write_list)
            temp_key1 = []
            temp_key2 = []
            temp_key3 = []
            temp_val = []
            write_list = []
    
    return response

@login_required(login_url="/accounts/login/")
def hdm_result_json_download(request, hdm_id, exp_id):
    cursor = connection.cursor()
    
    # Individual Result
    query = """SELECT a.*, '-' chart_cr, '-' chart_al FROM hdm_evaluation a JOIN 
                (SELECT max(id) as max_id FROM hdm_evaluation GROUP BY hdm_id, expert_email) b
            ON a.id = b.max_id
            WHERE a.hdm_id = '%s'
              AND a.expert_no = '%s'
            ORDER BY a.id DESC""" % (hdm_id, exp_id)
    cursor.execute(query)
    columns = [col[0] for col in cursor.description]
    eval_list = [dict(zip(columns, row)) for row in cursor.fetchall()]
    cursor.close()
    
    for ev in eval_list:
        json_cr_data = ev['eval_cr']
        json_fa_data = ev['eval_fa'] 
        json_al_data = ev['eval_al']
    
    json_data = "[\n" + json_cr_data + ",\n" + json_fa_data + ",\n" + json_al_data + "]"
    
    response = HttpResponse(json_data, content_type='application/json')
    response['Content-Disposition'] = 'attachment; filename=export.json'

    return response

# CR00,0|CR10,0.0181|CR11,0|CR12,0|CR13,0|CR20,0|CR21,0|CR22,0
def make_incon_dic(incon_data):
    temp_list = incon_data.split("|")
    incon_dic = {}
    
    if incon_data == "":
        return incon_dic
    
    for tl in temp_list:
        sub_list = tl.split(",")
        incon_dic[sub_list[0]] = sub_list[1]
    return incon_dic

# CR00,0|CR10,0.0181|CR11,0|CR12,0|CR13,0|CR20,0|CR21,0|CR22,0
def make_incon_list(incon_data):
    temp_list = incon_data.split("|")
    incon_list = []
    
    if incon_data == "":
        return incon_list
    
    for tl in temp_list:
        sub_list = tl.split(",")
        incon_list.append(float(sub_list[1]))
    return incon_list

@login_required(login_url="/accounts/login/")
def hdm_model_result(request, hdm_id, exp_id):
    # pandas setting for float number
    pd.options.display.float_format = '{:.4f}'.format

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
    cursor.close()
    
    eval_len = len(eval_list)

    main_df_cr = pd.DataFrame()
    main_df_fa = pd.DataFrame()
    main_df_al = pd.DataFrame()
    total_df_al= pd.DataFrame()
    total_df_al_chart = pd.DataFrame()
    df_all_eval_incon = pd.DataFrame()
    
    list_col_keys = []
    incon_dic = {}

    for ev in eval_list:
        exp_no = ev['expert_no']

        # 1. evaluation data
        eval_cr = pd.read_json(ev['eval_cr'])
        eval_cr.index = np.arange(1, len(eval_cr) + 1)
        main_df_cr = pd.concat([main_df_cr, eval_cr])
        eval_cr_html = eval_cr.to_html()
        
        eval_fa = pd.read_json(ev['eval_fa'])
        eval_fa.index = np.arange(1, len(eval_fa) + 1)
        main_df_fa = pd.concat([main_df_fa, eval_fa])
        eval_fa_html = eval_fa.to_html()
        
        eval_al = pd.read_json(ev['eval_al'])
        eval_al.index = np.arange(1, len(eval_al) + 1)
        main_df_al = pd.concat([main_df_al, eval_al])
        eval_al_html = eval_al[['Criteria', 'Factors', 'Alternatives', 'Value']].to_html()

        df_eval_incon = pd.read_json(ev['inconsistency'])
        df_all_eval_incon = pd.concat([df_all_eval_incon, df_eval_incon])

        ev['eval_cr'] = eval_cr_html.replace("dataframe", "dataframe data_eval eval_cr") 
        ev['eval_fa'] = eval_fa_html.replace("dataframe", "dataframe data_eval eval_fa")
        ev['eval_al'] = eval_al_html.replace("dataframe", "dataframe data_eval eval_al")

        # 2. chart data
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
        
        # 3.0. incon. for object
        ev['incon_cr00'] = round(df_eval_incon.to_dict()['incon'][0], 4)

        # 3.1. left join with result_cr and eval_incon  
        df_result_cr = pd.read_json(ev['result_cr'])
        df_result_cr_incon = pd.merge(df_result_cr,
                      df_eval_incon,
                      on='ecode', how='left')
        df_result_cr_incon.drop(['ecode'],inplace=True,axis=1)
        
        # 3.2. left join with result_cr and eval_incon  
        df_result_fa = pd.read_json(ev['result_fa'])
        df_result_fa_incon = pd.merge(df_result_fa,
                      df_eval_incon,
                      on='ecode', how='left')
        df_result_fa_incon.drop(['ecode'],inplace=True,axis=1)
        # change index name
        #df_result_fa_incon= df_result_fa_incon.set_index(df_result_fa_incon['ename'])

        # 3.3. data for result_al
        df_result_al = pd.read_json(ev['result_al'])
        df_result_al['SUM'] = df_result_al.sum(axis=1)        
        
        # 3.4. 
        ev['result_cr'] = df_result_cr_incon.to_html()
        ev['result_fa'] = df_result_fa_incon.to_html()
        ev['result_al'] = df_result_al.to_html()
        
        ev['result_cr'] = ev['result_cr'].replace("dataframe", "dataframe data_result result_cr") 
        ev['result_fa'] = ev['result_fa'].replace("dataframe", "dataframe data_result result_fa")
        ev['result_al'] = ev['result_al'].replace("dataframe", "dataframe data_result result_al")

        
        # Calculating for Main Alternative
        al_cal = HdmResultCalc(hdm_id)
        al_result_dic = al_cal.proc_total_result_al(hdm_id, exp_no)
        
        # for chart data
        temp_df_al_chart = pd.DataFrame([al_result_dic], columns=al_result_dic.keys())
        total_df_al_chart = pd.concat([total_df_al_chart, temp_df_al_chart])
        
        temp_df = pd.DataFrame([al_result_dic], columns=al_result_dic.keys())

        for key in list(temp_df.columns.values):
            temp_df[key] = temp_df[key].astype(float).fillna(0.0)
            temp_df[key] =  temp_df[key] / 100
            list_col_keys.append(al_result_dic.keys())

        # Add expert column
        temp_df['Experts'] = ev['expert_fname'] + ' ' + ev['expert_lname']
        incon_max = round(list(df_eval_incon.max())[1], 4)
        incon_mean = round(list(df_eval_incon.mean())[0], 4)
        
        inconsistency = ""
        inconsistency += "Max: " + str(incon_max)
        inconsistency += ", Mean: " + str(incon_mean)
        temp_df['Inconsistency'] = inconsistency
        
        total_df_al = pd.concat([total_df_al, temp_df])

    #main_total_chart_cr
    main_chart_cr = ''
    
    #main_total_chart_al
    for key in list(total_df_al_chart.columns.values):
        total_df_al_chart[key] = total_df_al_chart[key].astype(float).fillna(0.0)
    
    total_df_al_mean_dict = total_df_al_chart.mean().to_dict()        
    temp = ""
    for key, val in total_df_al_mean_dict.items():
        temp += "['%s', %.2f]," % (key, val)
    main_chart_al = "[%s]" % temp
    
    # Set Index as Expert's name
    total_df_al.set_index('Experts', inplace=True, drop=True)

    # for inconsistency - calculation of mean, min, max, std. dev.
    inc_mean = list(df_all_eval_incon.mean())[0]
    inc_min  = list(df_all_eval_incon.min())[1]
    inc_max  = list(df_all_eval_incon.max())[1]
    inc_std  = list(df_all_eval_incon.std())[0]

    # calculate mean, min, max, std. dev.
    total_df_al.loc['Mean'] = total_df_al.mean()
    total_df_al.loc['Min']  = total_df_al.min()
    total_df_al.loc['Max']  = total_df_al.max()
    total_df_al.loc['Std. Deviation'] = total_df_al.std()
    
    result_cal = HdmResultCalc(hdm_id)
    main_result_cr = result_cal.proc_result_main_cr(main_df_cr)
    main_result_fa = result_cal.proc_result_main_fa(main_df_fa)
    main_result_al = result_cal.proc_result_main_al(main_df_al)

    # multiindex to single index
    total_df_al = total_df_al.reset_index()
    
    # set data for inconsistency
    total_df_al.at[eval_len + 0, 'Inconsistency'] = inc_mean
    total_df_al.at[eval_len + 1, 'Inconsistency'] = inc_min
    total_df_al.at[eval_len + 2, 'Inconsistency'] = inc_max
    total_df_al.at[eval_len + 3, 'Inconsistency'] = inc_std

    # char data for main
    main_result_cr_html = main_result_cr.to_html()
    main_result_fa_html = main_result_fa.to_html()
    main_result_al_html = main_result_al.to_html()
    
    #print("*"*80)
    #print("total_df_al:\n", total_df_al)
    
    total_df_al_html    = total_df_al.to_html()

    main_result_cr_html = main_result_cr_html.replace("dataframe", "dataframe data_eval eval_cr") 
    main_result_fa_html = main_result_fa_html.replace("dataframe", "dataframe data_eval eval_fa")
    main_result_al_html = main_result_al_html.replace("dataframe", "dataframe data_eval eval_al")
    total_df_al_html    = total_df_al_html.replace("dataframe", "dataframe data_main main_al")
    
    return render(request, 'hdm/model_result.html', {'eval_all_list': eval_all_list, 'eval_list': eval_list, 'hdm_id':hdm_id, 
                   'main_result_cr':main_result_cr_html, 'main_result_fa':main_result_fa_html, 'main_result_al':main_result_al_html,
                   'total_df_al':total_df_al_html, 'main_chart_cr':main_chart_cr, 'main_chart_al':main_chart_al})


@login_required(login_url="/accounts/login/")
def hdm_expert_delete(request, hdm_id, exp_id):
    cursor = connection.cursor()

    query = "DELETE FROM hdm_evaluation WHERE hdm_id = '%s' AND expert_no in (%s)" % (hdm_id, exp_id)
    cursor.execute(query)

    return redirect('/result/' + hdm_id)

