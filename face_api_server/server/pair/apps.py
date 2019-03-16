# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.apps import AppConfig

import sys, os
sys.path.append(os.path.abspath(os.path.join('../..', 'demo')))
sys.path.append(os.path.abspath(os.path.join('../..', 'api')))
sys.path.append(os.path.abspath(os.path.join('../../caffe', 'python')))

from face_veri_pose_cd import model_init

import models

class PairConfig(AppConfig):
    name = 'pair'

    def ready(self):
        models.det, models.pose, models.landmark_p, models.recog, models.align = model_init()
        #print models.det
