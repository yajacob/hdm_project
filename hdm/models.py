from django.db import models
from django.utils import timezone
from bokeh.themes import default

class Hdm(models.Model):
    registrant = models.ForeignKey('auth.User')
    hdm_objective = models.CharField(max_length=200, default="")
    hdm_criteria = models.CharField(max_length=400, default="")
    hdm_factors = models.CharField(max_length=1000, default="")
    hdm_alternatives = models.CharField(max_length=400, default="")
    hdm_uuid = models.CharField(max_length=50, default="")
    hdm_text = models.TextField(default="")
    created_date = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return self.hdm_objective

class Evaluation(models.Model):
    hdm = models.ForeignKey('hdm.HDM', on_delete=models.CASCADE)
    expert_no = models.IntegerField(default=1)
    expert_fname = models.CharField(max_length=30, default="")
    expert_lname = models.CharField(max_length=30, default="")
    expert_email = models.EmailField()
    # get evaluation of criteria
    get_eval_cr = models.TextField(default="")
    # get evaluation of factors
    get_eval_fa = models.TextField(default="")
    # get evaluation of alternatives
    get_eval_al = models.TextField(default="")
    # for evaluation of criteria
    eval_cr = models.TextField(default="")
    # for evaluation of factors
    eval_fa = models.TextField(default="")
    # for evaluation of alternatives
    eval_al = models.TextField(default="")
    # calculated result for criteria
    result_cr = models.TextField(default="")
    # calculated result for factors
    result_fa = models.TextField(default="")
    # calculated result for alternatives
    result_al = models.TextField(default="")
    eval_date = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return self.eval_no
