from time import strftime
from django.shortcuts import render
from django.http import HttpResponse
from wsgiref.util import FileWrapper
from django.contrib import messages
from django.template import RequestContext
from django.views.generic.base import TemplateView
import random
from collections import defaultdict
import string
import os.path
import os
import subprocess
import pymysql.cursors
from django.db import connection


def home(request):
	return render(request, 'dbguide.html', {})

def publications(request):
	return render(request, 'publications.html', {})

def plasmidsandprotocols(request):
	return render(request, 'plasmidsAndProtocols.html', {})

def template(request):
	# myFileName = '/var/www/html/download/dbGuide-data-upload-template-200601.xlsx'
	# wrapper = FileWrapper(open(myFileName),'rb')
	# response = HttpResponse(wrapper)
	return response 

def main(request):
	return render(request, 'dbguide.html', {})

def submit(request):
	if request.method == "POST":
		# grab the search term
		query = request.POST['search']
		# grab the dropdown value
		genome = request.POST['genome']
		# initiate connection
		#conn = pymysql.connect(user="dbguide_user",password="User_2020",host="fr-s-mysql-4.ncifcrf.gov",port=3306)
		# place the cursor
		cur = connection.cursor()
		# pick right tables based on genome
		alias_table = ''
		gencode_table = ''
		guide_info_table = ''
		exon_info_table = ''
		# variables to store coordinates
		chrom_q = ''
		start_q = ''
		end_q = ''
		gene_symbol = 'n/a'
		ens_gene_id = 'n/a'
		ens_transcript_id = 'n/a' 
		if genome=='Hg':
			alias_table = 'hg_alias'
			gencode_table = 'hg_gencode'
			guide_info_table = 'hg_guide_info'
			exon_info_table = 'hg_exon_info'
		else:
			alias_table = 'mm_alias'
			gencode_table = 'mm_gencode'
			guide_info_table = 'mm_guide_info'
			exon_info_table = 'mm_exon_info'
		# check if the input is valid
		input_type = map_search_type(query)
		if input_type=='gene':
			# statement
			get_coords = "SELECT " + gencode_table + ".transcript_id, " + gencode_table + ".ens_gene_id, " + gencode_table + ".chrom, " + gencode_table + ".tx_start, " + gencode_table + ".tx_end FROM guidedb." + gencode_table + " INNER JOIN guidedb." + alias_table + " ON " + alias_table + ".transcript_id=" + gencode_table + ".transcript_id WHERE " + alias_table + ".alias=\'" + query + "\' AND " + gencode_table + ".ens_gene_id != \'n/a\'"

			cur.execute(get_coords)
			for (ens_t, ens_g, chrom, start, end) in cur:
				ens_transcript_id = ens_t
				ens_gene_id = ens_g
				chrom_q = chrom
				start_q = str(start)
				end_q = str(end)

			gene_symbol = query

		elif input_type=='coordinate':
			query_parts = query.split(':')
			chrom_q = query_parts[0]
			start_q, end_q = query_parts[1].split('-')

		elif input_type=='ensembl-transcript':
			# check if it has version #
			cluster_id = ''
			if '.' in query:
				tid,version = query.split('.')
				query = tid

			get_coords = "SELECT " + gencode_table + ".transcript_id, " + gencode_table + ".cluster_id, " + gencode_table + ".gene_symbol, " + gencode_table + ".chrom, " + gencode_table + ".cds_start, " + gencode_table + ".cds_end FROM guidedb." + gencode_table + " WHERE " + gencode_table + ".transcript_id=\'" + query + "\'"
			cur.execute(get_coords)		
			for (ens_t, cluster, gs, chrom, start, end) in cur:
				cluster_id = cluster
				ens_transcript_id = ens_t
				chrom_q = chrom
				start_q = str(start)
				end_q = str(end)
				gene_symbol = gs

			# get the ens_gene_id
			get_gene_id = "SELECT " + gencode_table + ".ens_gene_id FROM guidedb." + gencode_table + " WHERE " + gencode_table + ".cluster_id=" + str(cluster_id) + " AND " + gencode_table + ".ens_gene_id !=\'n/a\'"
			cur.execute(get_gene_id)
			for (gene_id) in cur:
				ens_gene_id = gene_id[0]

		elif input_type=='ensembl-gene':
			if '.' in query:
				gid,version = query.split('.')
				query = gid		
			get_coords = "SELECT " + gencode_table + ".transcript_id, " + gencode_table + ".ens_gene_id, " + gencode_table + ".gene_symbol, " + gencode_table + ".chrom, " + gencode_table + ".cds_start, " + gencode_table + ".cds_end FROM guidedb." + gencode_table + " WHERE " + gencode_table + ".ens_gene_id=\'" + query + "\'"
			cur.execute(get_coords)		
			for (ens_t, ens_g, gs, chrom, start, end) in cur:
				ens_transcript_id = ens_t
				ens_gene_id = ens_g
				chrom_q = chrom
				start_q = str(start)
				end_q = str(end)
				gene_symbol = gs

		# get guides
		statement = "SELECT " + guide_info_table + ".guide_rna, " + guide_info_table + ".crispr_system," + guide_info_table + ".sgrnascorer," + guide_info_table + ".guide_scan_off," + guide_info_table + ".chrom," + guide_info_table + ".start," + guide_info_table + ".end," + guide_info_table + ".in_protein_coding_exon, guide_data.mutated_read_count, guide_data.total_read_count" + ", COUNT(publications.PMID) as num_publications, COUNT(screen_validated.pmid) as num_screens FROM (guidedb." + guide_info_table + " LEFT JOIN guidedb.guide_data ON guide_data.guide_rna=" + guide_info_table + ".guide_rna) LEFT JOIN guidedb.publications ON publications.guide_rna=" + guide_info_table + ".guide_rna LEFT JOIN guidedb.screen_validated ON screen_validated.guide_rna=" + guide_info_table + ".guide_rna WHERE " + guide_info_table + ".chrom=" + "\'" + chrom_q + "\' AND " + guide_info_table + ".start >= " + start_q + " AND " + guide_info_table + ".end <=" + end_q + " GROUP BY " + guide_info_table + ".guide_rna ORDER BY num_publications DESC" 
		# statement = "SELECT " + guide_info_table + ".*, guide_data.mutated_read_count, guide_data.total_read_count" + ", COUNT(publications.PMID) as num_publications, COUNT(screen_validated.pmid) as num_screens FROM (guidedb." + guide_info_table + " LEFT JOIN guidedb.guide_data ON guide_data.guide_rna=" + guide_info_table + ".guide_rna) LEFT JOIN guidedb.publications ON publications.guide_rna=" + guide_info_table + ".guide_rna LEFT JOIN guidedb.screen_validated ON screen_validated.guide_rna=" + guide_info_table + ".guide_rna WHERE " + guide_info_table + ".chrom=" + "\'" + chrom_q + "\' AND " + guide_info_table + ".start >= " + start_q + " AND " + guide_info_table + ".end <=" + end_q + " GROUP BY " + guide_info_table + ".guide_rna ORDER BY num_publications DESC" 

		# run query
		cur.execute(statement)

		# header
		col_names = []
		col_names.append('Gene-Symbol')
		for col in cur.description:
			col_names.append(col[0])

		# get the results
		results = cur.fetchall()

		x = cur.description
		resultsList = []   
		for r in results:
			i = 0
			d = {}
			while i < len(x):
				d[x[i][0]] = r[i]
				i = i+1
			resultsList.append(d)

		return render(request, 'results.html', context={'header': col_names, 'rows': resultsList, 'gene_symbol': gene_symbol, 'ens_trans_id': ens_transcript_id, 'ens_gene_id': ens_gene_id})

def map_search_type(search_term):
	search_type = ''
	invalid_chars = string.punctuation
	if ' ' in search_term:
		return render(request, 'dbguide.html', {'error': 'Error: no spaces in search term'})
	elif any(char in invalid_chars for char in search_term):
		return render(request, 'dbguide.html', {'error': 'Special characters ' + invalid_chars + ' not permitted'})
	elif search_term.startswith('ENST')==True:
		search_type = 'ensembl-transcript'
	elif search_term.startswith('ENSG')==True:
		search_type = 'ensembl-gene'
	elif search_term.startswith('chr') and ':' in search_term and '-' in search_term:
		search_type = 'coordinate'
	else:
		search_type = 'gene'
	return search_type
