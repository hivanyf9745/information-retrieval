# If you haven't installed all the python libraries listed below, please run the pip3 install <libraryName> in your terminal
# Import all the essential libraries
import subprocess
import sys
import os
import pandas as pd
import json
import nltk
import numpy as np
from nltk.corpus import wordnet as wn
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords
import re
from nltk.stem import PorterStemmer
from nltk.stem.snowball import FrenchStemmer
import unidecode
from deep_translator import GoogleTranslator

# If you haven't installed all the following nltk packages to your local environment, please uncomment to make sure the first time the code run, it will work
# nltk.download('stopwords')
# nltk.download('punkt')
# nltk.download('wordnet')
# nltk.download('averaged_perceptron_tagger')
# nltk.download('omw-1.4')
ps = PorterStemmer()
fs = FrenchStemmer()

doDebug = True
index_count = 0

#Start the pyterrier 
import pyterrier as pt
pt.init()

#preprocessing for query expansion
pos_tag_map = {
  'NN': [ wn.NOUN ],
  'JJ': [ wn.ADJ, wn.ADJ_SAT ],
  'RB': [ wn.ADV ],
  'VB': [ wn.VERB ]
}

#This line is crucial so that the frontend will send the query to nodejs, which invoke the python function with inputQuery's value as the parameter
# So the input value should look like this'{"query": "emotion", "type": "EN", "userFeedback": ["4, english", "5, french"]}'
inputQuery = sys.argv[1]
def prepare_index_path(indexName):
  global index_count
  index_count = index_count + 1
  index_path = indexName + str(index_count)
  
  if os.path.exists(index_path) & os.path.isdir(index_path):
    files = os.listdir(index_path)
    for f in files:
      fname =index_path + '/' + f
      os.remove(fname)
    os.rmdir(index_path)
  elif os.path.exists(index_path) & (not os.path.isdir(index_path)):
    os.rmove(index_path)

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

def addRelevantDocs(docssofar, newdocstoadd, qid, query):
  for doctoadd in newdocstoadd:
    docssofar.append({"qid":str(qid), "query":query, "docno":doctoadd})
  return docssofar

def normalizeDataFrames(df, colname):
  colNeedNormaltoList = df[colname].to_list()

  maxColValue = max(colNeedNormaltoList)

  for idx, row in df.iterrows():
    df.loc[idx, colname] = (df.loc[idx, colname] - 1) / maxColValue
  
  return df
#################################################


#################################################
#// printOPutcome function will blah vblah blah.  It is run when blahahblah
#Coded by Jay
#################################################
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

  ##Test trial to concat both dataframes together
  frames = [eng_data, french_data]
  combined_data = pd.concat(frames)

  # You will load the dataframes and come up with the stemmed index.
  # Noticed that for the french one we eliminate the tones for words
  loaded_df_PS = load_dataframe(eng_data, 'Abstract_PS')
  indexref_PS = build_myindex(loaded_df_PS)

  loaded_df_FS = load_dataframe(french_data, 'simplified')
  indexref_FS = build_myindex(loaded_df_FS)

  # This line might be redundant but let's go with the flow
  query = inputQuery

  # inputQuery is returned in a string format, the following code should change the inputQuery to json (python dictionary)
  processed_query = json.loads(query)

  # There are three keys in the processed_query: 
  # "query" as in the original query (put in either french or english)
  # "type" as in the query language type, so it's either EN or FR in this context
  # "userfeedback" as in the userbased feendback after the first BM25 results are presented and people filter out the relevant ones

  # Here we need to pre-set the variable for translating the query: eng --> french, or french --> eng
  original_query = processed_query['query']
  translated_result = ''
  finalQuery_origin = ''
  finalQuery_translated = ''

  # This is to pre-set for the all the BatchRetrieve process for specific query search
  rankedRetrieval_eng = pt.BatchRetrieve(indexref_PS, wmodel='BM25')
  rankedRetrieval_fr = pt.BatchRetrieve(indexref_FS, wmodel='BM25')

  # Set up the peudoRelevance pipeline·
  bo1_eng = pt.rewrite.Bo1QueryExpansion(indexref_PS, fb_terms=8, fb_docs=2)
  bo1_fr = pt.rewrite.Bo1QueryExpansion(indexref_FS, fb_terms=8, fb_docs=2)

  # We separate the scenario into two groups: when the input query is in English || when the input query is in French


  if processed_query['type'] == 'EN':

    # We are using the Google Translator python package to translate english to french
    translated_result = GoogleTranslator(source='english', target='french').translate(processed_query['query'])

    # punctuation removal is always expected. Following that are lowercase, and split the string into list so we can remove the tones and stopwords if the translated target is french
    translated_result_punct = re.sub('[^\w\s]+', '', translated_result)
    translated_result_lower = translated_result_punct.lower()
    translated_result_split = translated_result_lower.split()
    translated_result_stop = [word for word in translated_result_split if word not in (stop_fr)]
    translated_result_final = ' '.join(translated_result_stop)
    translated_result_simple = unidecode.unidecode(translated_result_final)

    # After the procecssing for stopwords, punctuation, and tone removal (if applicable), we now want to stem the query since the index are for stemmed results as well

    #### The method for English stemmer is Porter, and French stemmer is Snowball
    finalQuery_origin = porterInputStemmed(original_query)
    finalQuery_translated = frenchInputStemmed(translated_result_simple)

    # Now that we've done with the preprocessing, let's dump the query into the batch retrieval index
    initial_results_eng = rankedRetrieval_eng.search(finalQuery_origin)
    initial_results_fr = rankedRetrieval_fr.search(finalQuery_translated)

    # However, since we need to merge the English and French results together and see if the ranking works, first we need to add a new column specifying the returned docs language type
    initial_results_eng['language'] = ['english'] * len(initial_results_eng['rank'])
    initial_results_fr['language'] = ['french'] * len(initial_results_fr['rank'])

    # Normalized the initial dataframe's score
    initial_results_eng = normalizeDataFrames(initial_results_eng, 'score')
    initial_results_fr = normalizeDataFrames(initial_results_fr, 'score')


    #################################3
    # This is just repeating the process of specifying doc's language and normalize their score, but for the PseudoRelevance one
    piplineQE_eng = rankedRetrieval_eng >> bo1_eng >> rankedRetrieval_eng
    piplineQE_fr = rankedRetrieval_fr >> bo1_fr >> rankedRetrieval_fr

    # So this is the results returned after the PseudoRelevance processing
    resultsAfterPseudoRelevance_eng = piplineQE_eng.search(finalQuery_origin)
    resultsAfterPseudoRelevance_fr = piplineQE_fr.search(finalQuery_translated)

    resultsAfterPseudoRelevance_eng['language'] = ['english'] * len(resultsAfterPseudoRelevance_eng['rank'])
    resultsAfterPseudoRelevance_fr['language'] = ['french'] * len(resultsAfterPseudoRelevance_fr['rank'])

    # print('BEFORE EN: ---->', resultsAfterPseudoRelevance_eng)
    # print('BEFORE FR: ---->', resultsAfterPseudoRelevance_fr)

    # Normalized the pseudo dataframe
    resultsAfterPseudoRelevance_eng = normalizeDataFrames(resultsAfterPseudoRelevance_eng, 'score')
    resultsAfterPseudoRelevance_fr = normalizeDataFrames(resultsAfterPseudoRelevance_fr, 'score')

    # print('AFTER EN: ---->', resultsAfterPseudoRelevance_eng)
    # print('AFTER FR: ---->', resultsAfterPseudoRelevance_fr)

    # Now we need to combine these two dataframes to start ranking their normalized scores
    ## This is for both initial results (representing BM25), and pseudo relevance feedback
    initial_frames = [initial_results_eng, initial_results_fr]
    combined_initial_results = pd.concat(initial_frames)

    combined_initial_results['ranking-score'] = combined_initial_results['score'].rank(ascending = 0)
    combined_initial_results = combined_initial_results.set_index('ranking-score')
    combined_initial_results = combined_initial_results.sort_index()

    combined_pseudo_frames = [resultsAfterPseudoRelevance_eng, resultsAfterPseudoRelevance_fr]
    combined_pseudo_results = pd.concat(combined_pseudo_frames)

    combined_pseudo_results['ranking-score'] = combined_pseudo_results['score'].rank(ascending = 0)
    combined_pseudo_results = combined_pseudo_results.set_index('ranking-score')
    combined_pseudo_results = combined_pseudo_results.sort_index()

    #### So we have the pseudoRelevance, we have the initial results, we are depending on the initial results to start user based one
    ### Therefore, we need to start preparing the data we want to return to the frontend
    ### The final returned data should look like 
    #######
    # '{"trasnlatedResult": "emotion", "queryLanguage": "english", "returnedDocs": [resultsreturned by initial results], "expandedDocs": [results coming from pseudoRelevance], "userbasedDocs": [results representing userfeedback]}'
    ###
    initial_docno = []
    combined_pseudo_docno = []
    combined_userbased_docno = []
    returned_data = {
      "translatedResult": translated_result,
      "queryLanguage": "english",
      "returnedDocs": [],
      "expandedDocs": [],
    }

    for row in combined_initial_results.itertuples():
      if row.language == 'french':
        initial_docno.append({"docno": int(row.docno), "language": "french"})
      elif row.language == 'english':
        initial_docno.append({"docno": int(row.docno), "language": "english"})

    for row in combined_pseudo_results.itertuples():
      if row.language == 'french':
        combined_pseudo_docno.append({"docno": int(row.docno), "language": "french"})
      elif row.language == 'english':
        combined_pseudo_docno.append({"docno": int(row.docno), "language": "english"})


    for item in initial_docno:
      for row in combined_data.itertuples():
        if (int(item["docno"]) + 1) == int(row.Sno) and item["language"] == row.Language:
          returned_data['returnedDocs'].append({
            "docid": row.Sno,
            "docLanguage": row.Language,
            "title": row.Title,
            "keywords": row.Keywords.split('; '),
            "authors": row.Authors,
            "releaseDate": row.ReleaseDate,
            "subjectHeadings": row.SubjectHeading.split(', '),
            "abstract": row.Abstract
          })
          
    for item in combined_pseudo_docno:
      for row in combined_data.itertuples():
        if int(row.Sno) == (int(item["docno"]) + 1) and row.Language == item["language"]:
          returned_data['expandedDocs'].append({
            "docid": row.Sno,
            "docLanguage": row.Language,
            "title": row.Title,
            "keywords": row.Keywords.split('; '),
            "authors": row.Authors,
            "releaseDate": row.ReleaseDate,
            "subjectHeadings": row.SubjectHeading.split(', '),
            "abstract": row.Abstract
          })

    print(json.dumps(returned_data))


################ Now you just have to perform the same process as query is in French!!!!
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

    initial_results_eng['language'] = ['english'] * len(initial_results_eng['rank'])
    initial_results_fr['language'] = ['french'] * len(initial_results_fr['rank'])

    piplineQE_eng = rankedRetrieval_eng >> bo1_eng >> rankedRetrieval_eng
    piplineQE_fr = rankedRetrieval_fr >> bo1_fr >> rankedRetrieval_fr

    resultsAfterPseudoRelevance_eng = piplineQE_eng.search(finalQuery_translated)
    resultsAfterPseudoRelevance_fr = piplineQE_fr.search(finalQuery_origin)

    resultsAfterPseudoRelevance_eng['language'] = ['english'] * len(resultsAfterPseudoRelevance_eng['rank'])
    resultsAfterPseudoRelevance_fr['language'] = ['french'] * len(resultsAfterPseudoRelevance_fr['rank'])

    initial_frames = [initial_results_eng, initial_results_fr]
    combined_initial_results = pd.concat(initial_frames)

    combined_initial_results['ranking-score'] = combined_initial_results['score'].rank(ascending = 0)
    combined_initial_results = combined_initial_results.set_index('ranking-score')
    combined_initial_results = combined_initial_results.sort_index()

    combined_pseudo_frames = [resultsAfterPseudoRelevance_eng, resultsAfterPseudoRelevance_fr]
    combined_pseudo_results = pd.concat(combined_pseudo_frames)

    combined_pseudo_results['ranking-score'] = combined_pseudo_results['score'].rank(ascending = 0)
    combined_pseudo_results = combined_pseudo_results.set_index('ranking-score')
    combined_pseudo_results = combined_pseudo_results.sort_index()

    initial_docno = []
    combined_userbased_docno = []
    combined_pseudo_docno = []
    returned_data = {
      "translatedResult": translated_result,
      "queryLanguage": "french",
      "returnedDocs": [],
      "expandedDocs": [],
      "userbasedDocs": []
    }

    for row in combined_initial_results.itertuples():
      if row.language == 'french':
        initial_docno.append({"docno": int(row.docno), "language": "french"})
      elif row.language == 'english':
        initial_docno.append({"docno": int(row.docno), "language": "english"})

    for row in combined_pseudo_results.itertuples():
      if row.language == 'french':
        combined_pseudo_docno.append({"docno": int(row.docno), "language": "french"})
      elif row.language == 'english':
        combined_pseudo_docno.append({"docno": int(row.docno), "language": "english"})

    for item in initial_docno:
      for row in combined_data.itertuples():
        if (int(item["docno"]) + 1) == int(row.Sno) and item["language"] == row.Language:
          returned_data['returnedDocs'].append({
            "docid": row.Sno,
            "docLanguage": row.Language,
            "title": row.Title,
            "keywords": row.Keywords.split('; '),
            "authors": row.Authors,
            "releaseDate": row.ReleaseDate,
            "subjectHeadings": row.SubjectHeading.split(', '),
            "abstract": row.Abstract
          })
          
    for item in combined_pseudo_docno:
      for row in combined_data.itertuples():
        if int(row.Sno) == (int(item["docno"]) + 1) and row.Language == item["language"]:
          returned_data['expandedDocs'].append({
            "docid": row.Sno,
            "docLanguage": row.Language,
            "title": row.Title,
            "keywords": row.Keywords.split('; '),
            "authors": row.Authors,
            "releaseDate": row.ReleaseDate,
            "subjectHeadings": row.SubjectHeading.split(', '),
            "abstract": row.Abstract
          })

    print(json.dumps(returned_data))

  sys.stdout.flush()


printOutcome(inputQuery)
