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

# nltk.download('stopwords')
ps = PorterStemmer()
fs = FrenchStemmer()

doDebug = True
index_count = 0

import pyterrier as pt
pt.init()

inputQuery = 'test'

def prepare_index_path(indexName):
  global index_count
  index_count = index_count + 1
  index_path = indexName + str(index_count)
  
  if os.path.exists(index_path) & os.path.isdir(index_path):
    print('Deleting index directory' + index_path)
    files = os.listdir(index_path)
    for f in files:
      fname =index_path + '/' + f
      os.remove(fname)
    os.rmdir(index_path)
    print("Successfully deleted index directory " + index_path)
  elif os.path.exists(index_path) & (not os.path.isdir(index_path)):
    os.rmove(index_path)
    print("Index path was actually a file, so removed it " + index_path)
  else:
    print("Index path doesn't exist, so no need to clear it: " + index_path)
  
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
  print(index_path_to_use)
  indexer = pt.DFIndexer('./' + index_path_to_use, overwrite=True)
  indexer.setProperty('termpipelines', 'NoOp')
  index_created = indexer.index(loaded_documents["text"], loaded_documents["docno"])
  print(index_created)
  return index_created

def printOutcome(inputQuery):

  eng_data = pd.read_csv('eng.csv')
  french_data = pd.read_csv('french.csv')
  eng_data['Abstract_processed'] = [re.sub('[^\w\s]+', '', s) for s in eng_data['Abstract'].tolist()]
  french_data['Abstract_processed']=[re.sub('[^\w\s]+', '', s) for s in french_data['Abstract'].tolist()]
  eng_data['Abstract_processed'] = eng_data['Abstract'].str.lower()
  french_data['Abstract_processed'] = french_data['Abstract'].str.lower()

  stop_eng = stopwords.words('english')
  eng_data['Abstract_processed'] = eng_data['Abstract_processed'].apply(lambda x: ' '.join([word for word in x.split() if word not in (stop_eng)]))

  stop_fr = stopwords.words('french')
  french_data['Abstract_processed'] = french_data['Abstract_processed'].apply(lambda x: ' '.join([word for word in x.split() if word not in (stop_fr)]))

  eng_data['Abstract_PS'] = eng_data['Abstract_processed'].apply(stem_sentences_PS)
  french_data['Abstract_FS'] = french_data['Abstract_processed'].apply(stem_sentences_FS)
  french_data['simplified'] = french_data.apply(lambda row: unidecode.unidecode(row.Abstract_FS), axis=1)

  loaded_df_PS = load_dataframe(eng_data, 'Abstract_PS')
  indexref_PS = build_myindex(loaded_df_PS)

  loaded_df_FS = load_dataframe(french_data, 'simplified')
  indexref_FS = build_myindex(loaded_df_FS)

  query = inputQuery
  print(pt.BatchRetrieve(indexref_PS, wmodel='BM25').search(query))
  # print(pt.BatchRetrieve(indexref_FS, wmodel='BM25').search(query))
  sys.stdout.flush()


printOutcome(inputQuery)
