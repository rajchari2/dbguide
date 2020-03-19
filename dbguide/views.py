from time import strftime
from django.shortcuts import render
from django.http import HttpResponse
from wsgiref.util import FileWrapper
from django.contrib import messages
from django.template import RequestContext
import random
from collections import defaultdict
import string
import os.path
import os
import subprocess


def home(request):
	return render(request, 'dbguide.html', {})

def main(request):
	return render(request, 'dbguide.html', {})


# def submitV1(request):
# 	if request.method == "POST":
# 		# first check they have everything
# 		if request.POST['Name']=='' or '@' in request.POST['Name'] or '#' in request.POST['Name'] or '*' in request.POST['Name'] or '&' in request.POST['Name']:
# 			return render(request, 'sgRNAScorerV1.html', {'error': 'Error: missing or invalid characters in name'})
# 		elif request.POST['Email']=='' or '@' not in request.POST['Email'] or ' ' in request.POST['Email'] or '#' in request.POST['Email'] or '*' in request.POST['Email'] or '&' in request.POST['Email']:
# 			return render(request, 'sgRNAScorerV1.html', {'error': 'Error: Please fill in a valid email address'})
# 		elif request.POST['inputType']=='pasteSequence' and (request.POST['sequence']=='' or request.POST['sequence'].startswith('>')==False):
# 			return render(request, 'sgRNAScorerV1.html', {'error': 'Error: Please input valid FASTA formatted sequences'})
# 		else:
# 			# first get the current time
# 			currTime = strftime("%Y.%m.%d.%H.%M.%S") + '.' + str(random.randint(1,1000))
# 			# get name
# 			name = request.POST['Name']
# 			# if you see slashes, get rid of it
