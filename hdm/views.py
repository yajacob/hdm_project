import pandas as pd
import numpy as np
import csv
import uuid
import json
from django.contrib import messages
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required
from django.http import Http404
from django.http import JsonResponse
from django.contrib.auth import login, authenticate
from django.contrib.auth import update_session_auth_hash
from django.contrib.auth.forms import PasswordChangeForm
from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.utils import timezone
from django.db import connection
from .models import HDM
from .forms.signup_forms import HDMUserCreationForm
from .forms.hdm_forms import HDMForm
from .modules.create_design_diagram_script import DiagramScript
from .modules.create_expert_diagram_script import ExpertDiagramScript
from .modules.hdm_db_proc import *
from .modules.hdm_eval_calc import HdmEvalCalc
from .modules.hdm_result_calc import HdmResultCalc

def make_list(temp):
    temp_list = temp.split("|")
    rs_list = []
    for tl in temp_list:
        rs_list.append(tl.split(","))
    return rs_list

def signup(request):
    if request.method == 'POST':
        #form = UserCreationForm(request.POST)
        form = HDMUserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            username = form.cleaned_data.get('username')
            raw_password = form.cleaned_data.get('password1')
            user = authenticate(username=username, password=raw_password)
            login(request, user)
            return redirect('/')
    else:
        #form = UserCreationForm()
        form = HDMUserCreationForm()
    return render(request, 'accounts/signup.html', {'form': form})

# Signup from Home
def signupHome(request):
    if request.method == 'POST':
        #form = UserCreationForm(request.POST)
        form = HDMUserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            username = form.cleaned_data.get('username')
            raw_password = form.cleaned_data.get('password1')
            user = authenticate(username=username, password=raw_password)
            login(request, user)
            return redirect('/accounts/login/')
    else:
        #form = UserCreationForm()
        form = HDMUserCreationForm()
    return render(request, 'hdm/home.html', {'form': form})

def change_password(request):
    if request.method == 'POST':
        form = PasswordChangeForm(request.user, request.POST)
        if form.is_valid():
            user = form.save()
            update_session_auth_hash(request, user)  # Important!
            messages.success(request, 'Your password was successfully updated!')
            return redirect('/')
        else:
            messages.error(request, 'Please correct the error below.')
    else:
        form = PasswordChangeForm(request.user)
    return render(request, 'accounts/change_password.html', {
        'form': form
    })

def hdm_home(request):
    if request.method == 'POST':
        #form = UserCreationForm(request.POST)
        form = HDMUserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            username = form.cleaned_data.get('username')
            raw_password = form.cleaned_data.get('password1')
            user = authenticate(username=username, password=raw_password)
            login(request, user)
            return redirect('/accounts/login/')
    else:
        cursor = connection.cursor()
        if request.user.is_staff == True:
            query = """SELECT a.*, strftime('%m/%d/%Y', a.created_date) cre_date,
                             (SELECT count(DISTINCT expert_email) FROM hdm_evaluation WHERE hdm_id=a.id) eval_cnt,
                             (SELECT username FROM auth_user WHERE id=a.registrant_id) user_id
                       FROM hdm_hdm a
                       ORDER BY a.created_date desc LIMIT 5"""
            query_user = "SELECT * FROM auth_user ORDER BY date_joined LIMIT 5"
        else:
            query = """SELECT a.*, strftime('%%m/%%d/%%Y', a.created_date) cre_date,
                             (SELECT count(distinct expert_email) FROM hdm_evaluation WHERE hdm_id=a.id) eval_cnt
                       FROM hdm_hdm a
                       WHERE registrant_id = '%s'
                       ORDER BY a.created_date desc
                       LIMIT 5 """ % (request.user.id)
        
        cursor.execute(query)
        columns = [col[0] for col in cursor.description]
        hdm_list = [dict(zip(columns, row)) for row in cursor.fetchall()]

        user_list = None
        if request.user.is_staff == True:
            cursor.execute(query_user)
            columns = [col[0] for col in cursor.description]
            user_list = [dict(zip(columns, row)) for row in cursor.fetchall()]
        
        return render(request, 'hdm/home.html', {'hdm_list': hdm_list, 'user_list':user_list})

def model_str_clean(stype, mstr):
    result = ""
    if stype == "fa":
        # Pink, Blue, Yellow|16GB, 32GB, 64GB, 128GB|USPS, UPS, FedEx|
        for idx, grp in enumerate(mstr.split("|")):
            if len(grp) < 1:
                continue
            if idx > 0:
                result += "|"
            for idx2, item in enumerate(grp.split(",")):
                if idx2 > 0:
                    result += ","
                result += item.strip()
    # "cr" or "al"
    else:
        #Color, Memory, Delivery
        for idx, item in enumerate(mstr.split(",")):
            if len(item) < 1:
                continue
            if idx > 0:
                result += ","
            result += item.strip()
    return result
         

@login_required(login_url="/accounts/login/")
def hdm_model_create(request):
    if request.method == "POST":
        form = HDMForm(request.POST)
        if form.is_valid():
            hdm = form.save(commit=False)
            hdm.hdm_uuid = uuid.uuid4().hex 
            hdm.registrant = request.user

            # clean data
            hdm.hdm_criteria = model_str_clean("cr", request.POST.get('hdm_criteria'))
            hdm.hdm_factors = model_str_clean("fa",request.POST.get('hdm_factors'))
            hdm.hdm_alternatives = model_str_clean("al",request.POST.get('hdm_alternatives'))

            hdm.created_date = timezone.now()
            hdm.save()
            return redirect('/hdm/model_manage/')
        else:
            return redirect('/hdm/model_manage/')
    else:
        range12 = list(range(1, 13))
        return render(request, 'hdm/model_create.html', {'range12': range12})

@login_required(login_url="/accounts/login/")
def hdm_model_update(request, hdm_id):
    # Update Process
    if request.method == "POST":
        hdm_objective = request.POST.get('hdm_objective')

        # clean data
        hdm_criteria = model_str_clean("cr", request.POST.get('hdm_criteria'))
        hdm_factors = model_str_clean("fa",request.POST.get('hdm_factors'))
        hdm_alternatives = model_str_clean("al",request.POST.get('hdm_alternatives'))
    
        cursor = connection.cursor()
        query = "UPDATE hdm_hdm SET hdm_objective=%s, hdm_criteria=%s, hdm_factors=%s, hdm_alternatives=%s WHERE id=%s"
        cursor.execute(query, (hdm_objective, hdm_criteria, hdm_factors, hdm_alternatives, hdm_id))
        return redirect('/hdm/model_view/' + hdm_id + '/')

    # Update Form
    else:
        try:
            hdm = HDM.objects.get(id__iexact=hdm_id)
            hdm_dict = {"hdm_objective":hdm.hdm_objective, "hdm_criteria":hdm.hdm_criteria, "hdm_factors":hdm.hdm_factors}
            ds = DiagramScript(hdm_dict)
            hdm_fa = hdm.hdm_factors.split("|")
            hdm_fa = list(map(lambda hdm_fa: hdm_fa.strip(), hdm_fa))

        except HDM.DoesNotExist:
            raise Http404
    
        range12 = list(range(1, 13))
        return render(request, 'hdm/model_update.html', {'range12': range12, 'hdm': hdm, 'ds':ds, 'hdm_fa':hdm_fa, 'hdm_id':hdm_id})

@login_required(login_url="/accounts/login/")
def hdm_model_manage(request):
    if request.user.is_staff == True:
        query = """SELECT a.*, strftime('%m/%d/%Y %H:%M', a.created_date) cre_date,
                         (SELECT count(distinct expert_email) FROM hdm_evaluation WHERE hdm_id=a.id) eval_cnt,
                         (SELECT username FROM auth_user WHERE id=a.registrant_id) user_id
                   FROM hdm_hdm a
                   ORDER BY a.created_date desc"""
    else:
        query = """SELECT a.*, strftime('%%m/%%d/%%Y %%H:%%M', a.created_date) cre_date,
                         (SELECT count(distinct expert_email) FROM hdm_evaluation WHERE hdm_id=a.id) eval_cnt
                   FROM hdm_hdm a
                   WHERE registrant_id = '%s'
                   ORDER BY a.created_date desc
                   LIMIT 10 """ % (request.user.id)

    cursor = connection.cursor()
    cursor.execute(query)
    columns = [col[0] for col in cursor.description]
    hdm_list = [dict(zip(columns, row)) for row in cursor.fetchall()]
    
    hdm_domain = "http://" + request.get_host()
    return render(request, 'hdm/model_manage.html', {'hdm_list': hdm_list}, {'hdm_domain':hdm_domain})

@login_required(login_url="/accounts/login/")
def hdm_model_view(request, hdm_id):
    try:
        hdm_dict = getHDMById(request, hdm_id)

        ds = DiagramScript(hdm_dict)
        hdm_al = hdm_dict['hdm_alternatives'].split(",")

        if hdm_id == "":
            hdm_id = hdm_dict['hdm_id']
        eval_cnt = getEvalCount(hdm_id)
        
    except:
        raise Http404

    return render(request, 'hdm/model_view.html', {'ds':ds, 'hdm_al':hdm_al, 'hdm':hdm_dict, 'eval_cnt':eval_cnt})

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
    print(query)
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

    main_df_cr = pd.DataFrame()
    main_df_fa = pd.DataFrame()
    main_df_al = pd.DataFrame()
    total_df_al= pd.DataFrame()
    total_df_al_chart = pd.DataFrame()
    
    list_col_keys = []

    for ev in eval_list:
        exp_no = ev['expert_no']
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
        
        ev['eval_cr'] = eval_cr_html.replace("dataframe", "dataframe data_eval eval_cr") 
        ev['eval_fa'] = eval_fa_html.replace("dataframe", "dataframe data_eval eval_fa")
        ev['eval_al'] = eval_al_html.replace("dataframe", "dataframe data_eval eval_al")

        # chart data
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
        ev['result_fa'] = pd.read_json(ev['result_fa']).to_html() #.replace("0.000", "-").replace("0.00", "-").replace("0.0", "-")
        ev['result_al'] = pd.read_json(ev['result_al'])
        ev['result_al']['SUM'] = ev['result_al'].sum(axis=1)
        ev['result_al'] = ev['result_al'].to_html()
        
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
        temp_df['Experts'] = ev['expert_lname'] + ', ' + ev['expert_fname']
        inconsistency = 0.0000
        #al_result_dic.update({'_Inconsistency':inconsistency})
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

    # char data for main
    main_result_cr_html = main_result_cr.to_html()
    main_result_fa_html = main_result_fa.to_html()
    main_result_al_html = main_result_al.to_html()
    total_df_al_html    = total_df_al.to_html()

    main_result_cr_html = main_result_cr_html.replace("dataframe", "dataframe data_eval eval_cr") 
    main_result_fa_html = main_result_fa_html.replace("dataframe", "dataframe data_eval eval_fa")
    main_result_al_html = main_result_al_html.replace("dataframe", "dataframe data_eval eval_al")
    total_df_al_html    = total_df_al_html.replace("dataframe", "dataframe data_main main_al")
    
    return render(request, 'hdm/model_result.html', {'eval_all_list': eval_all_list, 'eval_list': eval_list, 'hdm_id':hdm_id, 
                   'main_result_cr':main_result_cr_html, 'main_result_fa':main_result_fa_html, 'main_result_al':main_result_al_html,
                   'total_df_al':total_df_al_html, 'main_chart_cr':main_chart_cr, 'main_chart_al':main_chart_al})

@csrf_exempt
def uploadCSVfile(request):
    response = {}
    print("#################")
    print(request.FILES)
    print("#################")
    if request.method == 'POST' and request.FILES['upload_file']:
        file = request.FILES['upload_file']
        print('test1')
        try:
            data = [row for row in csv.reader(file.read().splitlines())]
            print('test2')
            print(data)
        except:
            print("Error")
        #data = [row for row in csv.reader(f.read().splitlines())] # csv file parsing
        #df = pd.read_csv(f)
        #print(df)
        response = {'success': True}
    else:
        response = {'success': False}
    return HttpResponse(json.dumps(response))

# login for expert
def hdm_expert_login(request, uuid):
    # proc login - sending to evaluation
    message = ""
    if request.method == "POST":
        exp_email = request.POST.get('exp_email')
        if isExpertParticipated(uuid, exp_email):
            message = "ALREADY"

        try:
            hdm = HDM.objects.get(hdm_uuid__iexact=uuid)
            ds = ExpertDiagramScript(hdm)
            
        except HDM.DoesNotExist:
            raise Http404
    
        hdm_al = hdm.hdm_alternatives.split(",")
        range28 = list(range(1, 29))
        return render(request, 'hdm/expert_evaluate.html', {'message':message, 'req_post':request.POST, 'uuid':uuid, 'hdm':hdm, 'ds':ds, 'hdm_al':hdm_al, 'range28':range28})
    # login form
    else:
        try:
            HDM.objects.get(hdm_uuid__iexact=uuid)
        except HDM.DoesNotExist:
            raise Http404

        return render(request, 'hdm/expert_login.html', {'uuid': uuid })
        
# evaluation for expert submit
@csrf_exempt
def hdm_expert_evaluate(request):
    if request.method == 'POST':
        result = "SUCCESS"

        uuid = request.POST.get('uuid')
        exp_fname = request.POST.get('exp_fname')
        exp_lname = request.POST.get('exp_lname')
        exp_email = request.POST.get('exp_email')
        
        hdm_dict = getHDMbyUUID(uuid)

        if hdm_dict is None:
            raise Http404("Wrong URL for the Evaluation!")

        hdm_id = hdm_dict['hdm_id']
        registrant_id = hdm_dict['registrant_id']

        designer_dict = getUserInfoBy(registrant_id)

        # Insert Evaluating Data 
        get_eval_cr = request.POST.get('eval_cr')
        get_eval_fa = request.POST.get('eval_fa')
        get_eval_al = request.POST.get('eval_al')
        
        eval_dic = {"cr":get_eval_cr, "fa":get_eval_fa, "al":get_eval_al }
        
        # calculation of evaluation 
        eval_calc = HdmEvalCalc(hdm_id, eval_dic)
        eval_cr = eval_calc.proc_eval_cr()
        eval_fa = eval_calc.proc_eval_fa()
        eval_al = eval_calc.proc_eval_al()
        
        # calculation of result
        rs_cr = eval_calc.proc_result_cr()
        rs_fa = eval_calc.proc_result_fa()
        rs_al = eval_calc.proc_result_al()

        # DB Insert
        cursor = connection.cursor()
        query = '''INSERT INTO hdm_evaluation (expert_no, expert_fname, expert_lname, expert_email,
                        hdm_id, get_eval_cr, get_eval_fa, get_eval_al, eval_cr, eval_fa, eval_al,
                        result_cr, result_fa, result_al, eval_date)
                    VALUES ((select ifnull(max(expert_no), 0) + 1 FROM hdm_evaluation where hdm_id = %s), %s, %s, %s,
                        %s, %s, %s, %s, %s, %s, %s,
                        %s, %s, %s, DATETIME('now'))
                '''
        cursor.execute(query, (hdm_id, exp_fname, exp_lname, exp_email, hdm_id, get_eval_cr, get_eval_fa, get_eval_al, eval_cr, eval_fa, eval_al, rs_cr, rs_fa, rs_al))
        
        return render(request, 'hdm/expert_success.html', {'result':result, 'designer':designer_dict})
    else:
        raise Http404

@login_required(login_url="/accounts/login/")
def hdm_expert_delete(request, hdm_id, exp_id):
    cursor = connection.cursor()

    query = "DELETE FROM hdm_evaluation WHERE hdm_id = '%s' AND expert_no in (%s)" % (hdm_id, exp_id)
    cursor.execute(query)

    return redirect('/hdm/model_view/' + hdm_id)    

@login_required(login_url="/accounts/login/")
def hdm_model_diagram(request, hdm_id):
    hdm = HDM.objects.get(id__iexact=hdm_id)
    ds = ExpertDiagramScript(hdm)

    hdm_al = hdm.hdm_alternatives.split(",")
    return render(request, 'hdm/model_diagram.html', {'ds':ds, 'hdm_al':hdm_al})
        
@login_required(login_url="/accounts/login/")
def hdm_model_delete(request, hdm_uuid):
    hdm_id = getIDbyUUID(hdm_uuid)
    if hdm_id is None:
        raise Http404
    
    cursor = connection.cursor()
    if request.user.is_staff == True:
        query = "DELETE FROM hdm_evaluation WHERE hdm_id='%s'" % (hdm_id)
        cursor.execute(query)
        query = "DELETE FROM hdm_hdm WHERE id='%s'" % (hdm_id)
        cursor.execute(query)
    else:
        query = """
            DELETE FROM hdm_evaluation
            WHERE hdm_id in (SELECT id FROM hdm_hdm WHERE id='%s' and registrant_id = '%s')
            """ % (hdm_id, request.user.id)
        cursor.execute(query)
        query = "DELETE FROM hdm_hdm WHERE id='%s' and registrant_id='%s'" % (hdm_id, request.user.id)
        cursor.execute(query)
        
    return redirect('/hdm/model_manage/')
        
def help_manual(request):
    return render(request, 'help/manual.html', {})