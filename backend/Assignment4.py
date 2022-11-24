import subprocess
import sys
import os
import pandas as pd
import json
import nltk
from nltk.corpus import wordnet as wn
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords
import re
from nltk.stem import PorterStemmer
from nltk.stem.snowball import FrenchStemmer
import unidecode
from deep_translator import GoogleTranslator


# nltk.download('stopwords')
# nltk.download('punkt')
# nltk.download('wordnet')
# nltk.download('averaged_perceptron_tagger')
# nltk.download('omw-1.4')
ps = PorterStemmer()
fs = FrenchStemmer()

doDebug = True
index_count = 0

import pyterrier as pt
pt.init()

pos_tag_map = {
  'NN': [ wn.NOUN ],
  'JJ': [ wn.ADJ, wn.ADJ_SAT ],
  'RB': [ wn.ADV ],
  'VB': [ wn.VERB ]
}

inputQuery = sys.argv[1]
# '{"query": "emotion", "type": "EN", "userFeedback": ["4, english", "5, french"]}'
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

# def pos_tag_converter(nltk_pos_tag):
#   root_tag = nltk_pos_tag[0:2]
#   try:
#     pos_tag_map[root_tag]
#     return pos_tag_map[root_tag]
#   except KeyError:
#     return ''

# def get_synsets(tokens):
#   synsets = []
#   for token in tokens:
#     wn_pos_tag = pos_tag_converter(token[1])
#     if wn_pos_tag == '':
#       continue
#     else:
#       synsets.append(wn.synsets(token[0], wn_pos_tag))
#   return synsets

# def get_tokens_from_synsets(synsets):
#   tokens = {}
#   for synset in synsets:
#     for s in synset:
#       if s.name() in tokens:
#         tokens[s.name().split('.')[0]] += 1
#       else:
#         tokens[s.name().split('.')[0]] = 1
#   return tokens

# def get_hypernyms(synsets):
#   hypernyms = []
#   for synset in synsets:
#     for s in synset:
#       hypernyms.append(s.hypernyms())
            
#   return hypernyms

# def get_tokens_from_hypernyms(synsets):
#   tokens = {}
#   for synset in synsets:
#     for s in synsets:
#       for ss in s:
#         if ss.name().split('.')[0] in tokens:
#           tokens[(ss.name().split('.')[0])] += 1
#         else:
#           tokens[(ss.name().split('.')[0])] = 1
#   return tokens

# def underscore_replacer(tokens):
#   new_tokens = {}
#   for key in tokens.keys():
#     mod_key = re.sub(r'_', ' ', key)
#     new_tokens[mod_key] = tokens[key]
#   return new_tokens

# def generate_tokens_eng(sentence):
#   tokens = tokenizer(sentence)
#   tokens = pos_tagger(tokens)
#   tokens = stopword_treatment_eng(tokens)
#   return tokens

# def generate_tokens_fr(sentence):
#   tokens = tokenizer(sentence)
#   tokens = pos_tagger(tokens)
#   tokens = stopword_treatment_fr(tokens)
#   return tokens

# def tokenizer(sentence):
#   return word_tokenize(sentence)

# def pos_tagger(tokens):
#   return nltk.pos_tag(tokens)

# def stopword_treatment_eng(tokens):
#   stopword = stopwords.words('english')
#   result = []
#   for token in tokens:
#     if token[0].lower() not in stopword:
#       result.append(tuple([token[0].lower(), token[1]]))
  
#   return result

# def stopword_treatment_fr(tokens):
#   stopword = stopwords.words('french')
#   result = []
#   for token in tokens:
#     if token[0].lower() not in stopword:
#       result.append(tuple([token[0].lower(), token[1]]))
  
#   return result

# def generate_synonymsandhypernyms(tokens):
#   # tokens = tokenizer(sentence)
#   # tokens = pos_tagger(tokens)
#   # tokens = stopword_treatment(tokens)
#   # print(tokens)
#   synsets = get_synsets(tokens)
#   synonyms = get_tokens_from_synsets(synsets)
#   synonyms = underscore_replacer(synonyms)
#   hypernyms = get_hypernyms(synsets)
#   hypernyms = get_tokens_from_hypernyms(hypernyms)
#   hypernyms = underscore_replacer(hypernyms)
#   results = {**synonyms, **hypernyms}
#   return results




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

  frames = [eng_data, french_data]
  combined_data = pd.concat(frames)

  loaded_df_PS = load_dataframe(eng_data, 'Abstract_PS')
  indexref_PS = build_myindex(loaded_df_PS)

  loaded_df_FS = load_dataframe(french_data, 'simplified')
  indexref_FS = build_myindex(loaded_df_FS)

  query = inputQuery
  # print('inputQuery: ---->', inputQuery)

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

    initial_results_eng['language'] = ['english'] * len(initial_results_eng['rank'])
    initial_results_fr['language'] = ['french'] * len(initial_results_fr['rank'])

    # Normalized the initial dataframe
    initial_results_eng = normalizeDataFrames(initial_results_eng, 'score')
    initial_results_fr = normalizeDataFrames(initial_results_fr, 'score')

    piplineQE_eng = rankedRetrieval_eng >> bo1_eng >> rankedRetrieval_eng
    piplineQE_fr = rankedRetrieval_fr >> bo1_fr >> rankedRetrieval_fr

    resultsAfterPseudoRelevance_eng = piplineQE_eng.search(finalQuery_origin)
    resultsAfterPseudoRelevance_fr = piplineQE_fr.search(finalQuery_translated)

    resultsAfterPseudoRelevance_eng['language'] = ['english'] * len(resultsAfterPseudoRelevance_eng['rank'])
    resultsAfterPseudoRelevance_fr['language'] = ['french'] * len(resultsAfterPseudoRelevance_fr['rank'])

    # Normalized the pseudo dataframe
    resultsAfterPseudoRelevance_eng = normalizeDataFrames(resultsAfterPseudoRelevance_eng, 'score')
    resultsAfterPseudoRelevance_fr = normalizeDataFrames(resultsAfterPseudoRelevance_fr, 'score')

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
    combined_pseudo_docno = []
    combined_userbased_docno = []
    returned_data = {
      "translatedResult": translated_result,
      "queryLanguage": "english",
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

    relevantDocsFlaggedByUser_eng = []
    relevantDocsFlaggedByUser_fr = []
    if processed_query['userFeedback'] == []:
      print(json.dumps(returned_data))
    else: 
      for feedback in processed_query['userFeedback']:
        feedbacklst = feedback.split(', ')
        if feedbacklst[1] == 'english':
          relevantDocsFlaggedByUser_eng.append(feedbacklst[0])
        elif feedbacklst[1] == 'french':
          relevantDocsFlaggedByUser_fr.append(feedbacklst[0])
      
      allRelevantDocsByQuery_eng=[]
      qid_eng = initial_results_eng.iloc[0]['qid']
      query_eng = initial_results_eng.iloc[0]['query']
      
      allRelevantDocsByQuery_eng = addRelevantDocs(allRelevantDocsByQuery_eng, relevantDocsFlaggedByUser_eng, qid_eng, query_eng)
      relevantDF_eng = pd.DataFrame(allRelevantDocsByQuery_eng)

      bo1User_eng = pt.rewrite.Bo1QueryExpansion(indexref_PS, fb_terms=10, fb_docs=len(relevantDocsFlaggedByUser_eng))
      pipeUser_eng = bo1User_eng >> rankedRetrieval_eng
      newresults_eng = pipeUser_eng.transform(relevantDF_eng)

      allRelevantDocsByQuery_fr = []
      qid_fr = initial_results_fr.iloc[0]['qid']
      query_fr = initial_results_fr.iloc[0]['query']
      allRelevantDocsByQuery_fr = addRelevantDocs(allRelevantDocsByQuery_fr, relevantDocsFlaggedByUser_fr, qid_fr, query_fr)
      relevantDF_fr = pd.DataFrame(allRelevantDocsByQuery_fr)
      
      bo1User_fr = pt.rewrite.Bo1QueryExpansion(indexref_FS, fb_terms=8, fb_docs=len(relevantDocsFlaggedByUser_fr))
      pipe_fr = bo1User_fr >> rankedRetrieval_fr
      newresults_fr = pipe_fr.transform(relevantDF_fr)

      newresults_eng['language'] = ['english'] * len(newresults_eng['rank'])
      newresults_fr['language'] = ['french'] * len(newresults_fr['rank'])

      newresults_eng = normalizeDataFrames(newresults_eng, 'score')
      newresults_fr = normalizeDataFrames(newresults_fr, 'score')

      userbased_frames = [newresults_eng, newresults_fr]
      combined_userbased_results = pd.concat(userbased_frames)

      combined_userbased_results['ranking-score'] = combined_userbased_results['score'].rank(ascending = 0)
      combined_userbased_results = combined_userbased_results.set_index('ranking-score')
      combined_userbased_results = combined_userbased_results.sort_index()

      for row in combined_userbased_results.itertuples():
        if row.language == 'french':
          combined_userbased_docno.append({"docno": int(row.docno), "language": "french"})
        elif row.language == 'english':
          combined_userbased_docno.append({"docno": int(row.docno), "language": "english"})

      for item in combined_userbased_docno:
        for row in combined_data.itertuples():
          if int(row.Sno) == (int(item["docno"]) + 1) and row.Language == item["language"]:
            returned_data['userbasedDocs'].append({
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

    relevantDocsFlaggedByUser_eng = []
    relevantDocsFlaggedByUser_fr = []
    if processed_query['userFeedback'] == []:
      print(json.dumps(returned_data))
    else: 
      for feedback in processed_query['userFeedback']:
        feedbacklst = feedback.split(', ')
        if feedbacklst[1] == 'english':
          relevantDocsFlaggedByUser_eng.append(feedbacklst[0])
        elif feedbacklst[1] == 'french':
          relevantDocsFlaggedByUser_fr.append(feedbacklst[0])
      
      allRelevantDocsByQuery_eng=[]
      qid_eng = initial_results_eng.iloc[0]['qid']
      query_eng = initial_results_eng.iloc[0]['query']
      
      allRelevantDocsByQuery_eng = addRelevantDocs(allRelevantDocsByQuery_eng, relevantDocsFlaggedByUser_eng, qid_eng, query_eng)
      relevantDF_eng = pd.DataFrame(allRelevantDocsByQuery_eng)

      bo1User_eng = pt.rewrite.Bo1QueryExpansion(indexref_PS, fb_terms=10, fb_docs=len(relevantDocsFlaggedByUser_eng))
      pipeUser_eng = bo1User_eng >> rankedRetrieval_eng
      newresults_eng = pipeUser_eng.transform(relevantDF_eng)

      allRelevantDocsByQuery_fr = []
      qid_fr = initial_results_fr.iloc[0]['qid']
      query_fr = initial_results_fr.iloc[0]['query']
      allRelevantDocsByQuery_fr = addRelevantDocs(allRelevantDocsByQuery_fr, relevantDocsFlaggedByUser_fr, qid_fr, query_fr)
      relevantDF_fr = pd.DataFrame(allRelevantDocsByQuery_fr)

      bo1User_fr = pt.rewrite.Bo1QueryExpansion(indexref_FS, fb_terms=8, fb_docs=len(relevantDocsFlaggedByUser_fr))
      pipe_fr = bo1User_fr >> rankedRetrieval_fr
      newresults_fr = pipe_fr.transform(relevantDF_fr)

      newresults_eng['language'] = ['english'] * len(newresults_eng['rank'])
      newresults_fr['language'] = ['french'] * len(newresults_fr['rank'])

      newresults_eng = normalizeDataFrames(newresults_eng, 'score')
      newresults_fr = normalizeDataFrames(newresults_fr, 'score')

      userbased_frames = [newresults_eng, newresults_fr]
      combined_userbased_results = pd.concat(userbased_frames)

      combined_userbased_results['ranking-score'] = combined_userbased_results['score'].rank(ascending = 0)
      combined_userbased_results = combined_userbased_results.set_index('ranking-score')
      combined_userbased_results = combined_userbased_results.sort_index()

      for row in combined_userbased_results.itertuples():
        if row.language == 'french':
          combined_userbased_docno.append({"docno": int(row.docno), "language": "french"})
        elif row.language == 'english':
          combined_userbased_docno.append({"docno": int(row.docno), "language": "english"})

      for item in combined_userbased_docno:
        for row in combined_data.itertuples():
          if int(row.Sno) == (int(item["docno"]) + 1) and row.Language == item["language"]:
            returned_data['userbasedDocs'].append({
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
