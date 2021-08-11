import datetime
import time
import json
import os
from collections import Counter

import requests
from bs4 import BeautifulSoup
from django.conf import settings
from django.contrib import messages
from django.db.models import F
from django.http import Http404, JsonResponse
from django.shortcuts import render
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from django.views.generic import FormView, TemplateView, DetailView
import urllib.parse as urlparse
from urllib.parse import parse_qs
from django.views.generic.base import ContextMixin, View

from django_powercms.cms.email import sendmail
from django_powercms.utils.models import LogObject


