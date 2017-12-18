# -*- coding: utf-8 -*-

from rest_framework.decorators import api_view
from rest_framework.response import Response
from hdm.modules.calc_inconsistency import HdmInconsistency

@api_view(('GET','POST',))
def get_inconsistency(request):
    if request.method == 'GET':
        eval_data = request.GET.get('eval_data')
        if eval_data != "":
            try:
                hi = HdmInconsistency()
                inconsistency = hi.main_process(eval_data)
            except:
                inconsistency = -1.0
        return Response({"inconsistency": inconsistency})
    
    return Response({"inconsistency": "*"})
