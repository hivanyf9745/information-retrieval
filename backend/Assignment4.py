import subprocess
import sys
import os
import pandas as pd
import json
import nltk
from nltk.corpus import stopwords
import re
from nltk.stem import PorterStemmer
from nltk.stem.snowball import FrenchStemmer
import unidecode
from deep_translator import GoogleTranslator


# nltk.download('stopwords')
ps = PorterStemmer()
fs = FrenchStemmer()

doDebug = True
index_count = 0

import pyterrier as pt
pt.init()

inputQuery = '{"query": "la dépression", "type": "FR"}'

def prepare_index_path(indexName):
  global index_count
  index_count = index_count + 1
  index_path = indexName + str(index_count)
  
  if os.path.exists(index_path) & os.path.isdir(index_path):
    # print('Deleting index directory' + index_path)
    files = os.listdir(index_path)
    for f in files:
      fname =index_path + '/' + f
      os.remove(fname)
    os.rmdir(index_path)
    # print("Successfully deleted index directory " + index_path)
  elif os.path.exists(index_path) & (not os.path.isdir(index_path)):
    os.rmove(index_path)
    # print("Index path was actually a file, so removed it " + index_path)
  # else:
  #   print("Index path doesn't exist, so no need to clear it: " + index_path)
  
  return index_path

def stem_sentences_PS(sentence):
  tokens = sentence.split()
  stemmed_tokens = [ps.stem(token) for token in tokens]
  return ' '.join(stemmed_tokens)

def stem_sentences_FS(sentence):
    tokens = sentence.split()
    stemmed_tokens = [fs.stem(token) for token in tokens]
    return ' '.join(stemmed_tokens)

def load_dataframe(dataFrame, abs_column):
  loaded_documents = pd.DataFrame(columns = ['docno', 'text'])
  count = 0
  for abstract in dataFrame[abs_column]:
    abstractAsSingleString = "".join(abstract)
    loaded_documents = loaded_documents.append({'docno': str(count), 'text': abstractAsSingleString}, ignore_index=True)
    count += 1
  return loaded_documents

def build_myindex(loaded_documents):
  index_path_to_use = prepare_index_path("MINE")
  indexer = pt.DFIndexer('./' + index_path_to_use, overwrite=True)
  indexer.setProperty('termpipelines', 'NoOp')
  index_created = indexer.index(loaded_documents["text"], loaded_documents["docno"])
  return index_created

def porterInputStemmed(argText):
  stemmed_text_lst = argText.lower().split()
  
  query_eng_PS = ''

  for i in range(len(stemmed_text_lst)):
    stemmed_text_lst[i] = ps.stem(stemmed_text_lst[i])
    if i != 0:
      if stemmed_text_lst[i] == 'and':
        query_eng_PS += ' and '
      elif stemmed_text_lst[i] == 'or':
        query_eng_PS += ' or '
      else:
        if stemmed_text_lst[i-1] == 'and' or stemmed_text_lst[i-1] == 'or':
          query_eng_PS += stemmed_text_lst[i]
        else:
          query_eng_PS += ' and ' + stemmed_text_lst[i]
    else:
      query_eng_PS += stemmed_text_lst[i]


  return query_eng_PS

def frenchInputStemmed(argText):
  stemmed_text_lst = argText.lower().split()
  
  query_fc_FS = ''

  for i in range(len(stemmed_text_lst)):
    stemmed_text_lst[i] = fs.stem(stemmed_text_lst[i])
    if i != 0:
      if stemmed_text_lst[i] == 'and':
        query_fc_FS += ' and '
      elif stemmed_text_lst[i] == 'or':
        query_fc_FS += ' or '
      else:
        if stemmed_text_lst[i-1] == 'and' or stemmed_text_lst[i-1] == 'or':
          query_fc_FS += stemmed_text_lst[i]
        else:
          query_fc_FS += ' and ' + stemmed_text_lst[i]
    else:
      query_fc_FS += stemmed_text_lst[i]


  return query_fc_FS

def printOutcome(inputQuery):

  # read the csv data from both file sources
  eng_data = pd.read_csv('eng.csv')
  french_data = pd.read_csv('french.csv')

  # puctuation removal and lowercase the entire text
  eng_data['Abstract_processed'] = [re.sub('[^\w\s]+', '', s) for s in eng_data['Abstract'].tolist()]
  french_data['Abstract_processed']=[re.sub('[^\w\s]+', '', s) for s in french_data['Abstract'].tolist()]
  eng_data['Abstract_processed'] = eng_data['Abstract'].str.lower()
  french_data['Abstract_processed'] = french_data['Abstract'].str.lower()

  # stopwords removal
  stop_eng = stopwords.words('english')
  eng_data['Abstract_processed'] = eng_data['Abstract_processed'].apply(lambda x: ' '.join([word for word in x.split() if word not in (stop_eng)]))

  stop_fr = stopwords.words('french')
  french_data['Abstract_processed'] = french_data['Abstract_processed'].apply(lambda x: ' '.join([word for word in x.split() if word not in (stop_fr)]))

  # apply porter stemming and snowball stemming on both english and french corpus
  eng_data['Abstract_PS'] = eng_data['Abstract_processed'].apply(stem_sentences_PS)
  french_data['Abstract_FS'] = french_data['Abstract_processed'].apply(stem_sentences_FS)
  # remove the french tones
  french_data['simplified'] = french_data.apply(lambda row: unidecode.unidecode(row.Abstract_FS), axis=1)

  loaded_df_PS = load_dataframe(eng_data, 'Abstract_PS')
  indexref_PS = build_myindex(loaded_df_PS)

  loaded_df_FS = load_dataframe(french_data, 'simplified')
  indexref_FS = build_myindex(loaded_df_FS)

  query = inputQuery

  processed_query = json.loads(query)
  
  original_query = processed_query['query']
  translated_result = ''
  finalQuery_origin = ''
  finalQuery_translated = ''

  rankedRetrieval_eng = pt.BatchRetrieve(indexref_PS, wmodel='BM25')
  rankedRetrieval_fr = pt.BatchRetrieve(indexref_FS, wmodel='BM25')

  bo1_eng = pt.rewrite.Bo1QueryExpansion(indexref_PS, fb_terms=8, fb_docs=2)
  bo1_fr = pt.rewrite.Bo1QueryExpansion(indexref_FS, fb_terms=8, fb_docs=2)

  if processed_query['type'] == 'EN':
    translated_result = GoogleTranslator(source='english', target='french').translate(processed_query['query'])
    translated_result_punct = re.sub('[^\w\s]+', '', translated_result)
    translated_result_lower = translated_result_punct.lower()
    translated_result_split = translated_result_lower.split()
    translated_result_stop = [word for word in translated_result_split if word not in (stop_fr)]
    translated_result_final = ' '.join(translated_result_stop)
    translated_result_simple = unidecode.unidecode(translated_result_final)

    finalQuery_origin = porterInputStemmed(original_query)
    finalQuery_translated = frenchInputStemmed(translated_result_simple)

    initial_results_eng = rankedRetrieval_eng.search(finalQuery_origin)
    initial_results_fr = rankedRetrieval_fr.search(finalQuery_translated)

    piplineQE_eng = rankedRetrieval_eng >> bo1_eng >> rankedRetrieval_eng
    piplineQE_fr = rankedRetrieval_fr >> bo1_fr >> rankedRetrieval_fr

    resultsAfterPseudoRelevance_eng = piplineQE_eng.search(finalQuery_origin)
    resultsAfterPseudoRelevance_fr = piplineQE_fr.search(finalQuery_translated)

    print('initial eng results: ---->', initial_results_eng)
    print('initial french results: ---->', initial_results_fr)
    print('expanded eng results: ---->', resultsAfterPseudoRelevance_eng)
    print('expanded french results: ---->', resultsAfterPseudoRelevance_fr)
    # print(translated_result)
  elif processed_query['type'] == 'FR':
    translated_result = GoogleTranslator(source='french', target='english').translate(processed_query['query'])
    translated_result_punct = re.sub('[^\w\s]+', '', translated_result)
    translated_result_lower = translated_result_punct.lower()
    translated_result_split = translated_result_lower.split()
    translated_result_stop = [word for word in translated_result_split if word not in (stop_eng)]
    translated_result_final = ' '.join(translated_result_stop)

    original_query_punct = re.sub('[^\w\s]+', '', original_query)
    original_query_lower = original_query_punct.lower()
    original_query_split = original_query_lower.split()
    original_query_stop = [word for word in original_query_split if word not in (stop_fr)]
    original_query_final = ' '.join(original_query_stop)
    original_query_simple = unidecode.unidecode(original_query_final)

    finalQuery_origin = frenchInputStemmed(original_query_simple)
    finalQuery_translated = porterInputStemmed(translated_result_final)

    initial_results_eng = rankedRetrieval_eng.search(finalQuery_translated)
    initial_results_fr = rankedRetrieval_fr.search(finalQuery_origin)

    piplineQE_eng = rankedRetrieval_eng >> bo1_eng >> rankedRetrieval_eng
    piplineQE_fr = rankedRetrieval_fr >> bo1_fr >> rankedRetrieval_fr

    resultsAfterPseudoRelevance_eng = piplineQE_eng.search(finalQuery_translated)
    resultsAfterPseudoRelevance_fr = piplineQE_fr.search(finalQuery_origin)

    print('initial eng results: ---->', initial_results_eng)
    print('initial french results: ---->', initial_results_fr)
    print('expanded eng results: ---->', resultsAfterPseudoRelevance_eng)
    print('expanded french results: ---->', resultsAfterPseudoRelevance_fr)
    # print(translated_result)

  sys.stdout.flush()


printOutcome(inputQuery)
