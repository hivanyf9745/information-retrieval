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

#This line is crucial so that the frontend will send the query to nodejs, which invoke the python function with inputQuery's value as the parameter
# So the input value should look like this'{"query": "emotion", "type": "EN"}'
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

def engInputProcessed(argText):
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

def frenchInputProcessed(argText):
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
  minColValue = min(colNeedNormaltoList)

  for idx, row in df.iterrows():
    df.loc[idx, colname] = (df.loc[idx, colname] - minColValue) / maxColValue
  
  return df
#################################################


#################################################
#################################################
def printOutcome(inputQuery):
  try:  # read the csv data from both file sources
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

    # Set up the peudoRelevance pipeline??
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
      finalQuery_origin = engInputProcessed(original_query)
      finalQuery_translated = frenchInputProcessed(translated_result_simple)

      # Now that we've done with the preprocessing, let's dump the query into the batch retrieval index
      initial_results_eng = rankedRetrieval_eng.search(finalQuery_origin)
      initial_results_fr = rankedRetrieval_fr.search(finalQuery_translated)

      bo1_eng_transformed = bo1_eng.transform(initial_results_eng)
      bo1_fr_transformed = bo1_fr.transform(initial_results_fr)

      tokenized_bo1_eng_transformed = bo1_eng_transformed.loc[0, 'query'].split(' ')
      tokenized_bo1_fr_transformed = bo1_fr_transformed.loc[0, 'query'].split(' ')

      englishTerms = tokenized_bo1_eng_transformed
      frenchTerms = tokenized_bo1_fr_transformed
      for item in tokenized_bo1_eng_transformed:
        if (item != 'applypipeline:off'):
          item_lst = item.split('^')
          try:
            translated_expandQuery = GoogleTranslator(source='english', target='french').translate(item_lst[0])
            # I want to stem the query
            translated_expandQuery_stemmed = fs.stem(translated_expandQuery)
            # and then remove the accents in french
            translated_expandQuery_final = unidecode.unidecode(translated_expandQuery_stemmed)
            # now the newTermEntry should be good to go
            newTermEntry = [translated_expandQuery_final, item_lst[1]]
            # insert into list at right location
            for i in range(len(frenchTerms)):
              if (i != 0):
                currTerms = frenchTerms[i].split('^')
                if (float(currTerms[1]) < float(item_lst[1])):
                  frenchTerms.insert(i, ''+newTermEntry[0]+'^'+newTermEntry[1])
                  break
                # we are assuming index 0 is always 1
          except:
            continue

      for item in tokenized_bo1_fr_transformed:
        if (item != 'applypipeline:off'):
          item_lst = item.split('^')
          try:
            translated_expandQuery = GoogleTranslator(source='french', target='english').translate(item_lst[0])
            # first you need to stem the translated expand queries
            translated_expandQuery_final = ps.stem(translated_expandQuery)
            # now put that in the newTermEntry
            newTermEntry = [translated_expandQuery_final, item_lst[1]]
            # insert into list at right location
            for i in range(len(englishTerms)):
              if (i != 0):
                currTerms = englishTerms[i].split('^')
                if (float(currTerms[1]) < float(item_lst[1])):
                  englishTerms.insert(i, ''+newTermEntry[0]+'^'+newTermEntry[1])
                  break
          except:
            continue
      
      expandedEngQueries = []
      for i in range(len(englishTerms)):
        if (i == 0):
          continue
        else:
          english_item_lst = englishTerms[i].split('^')
          expandedEngQueries.append(english_item_lst[0])
      expandedEngQueries = list(dict.fromkeys(expandedEngQueries))

      frenchTermstoString = ' '.join(frenchTerms)
      englishTermstoString = ' '.join(englishTerms)

      allqid_eng = bo1_eng_transformed['qid'].tolist()
      allqid_fr = bo1_fr_transformed['qid'].tolist()

      newQuerydf_eng = pd.DataFrame({'qid': allqid_eng, 'query': [englishTermstoString]})
      newQuerydf_fr = pd.DataFrame({'qid': allqid_fr, 'query': [frenchTermstoString]})

      results_eng = rankedRetrieval_eng.transform(newQuerydf_eng)
      results_fr = rankedRetrieval_eng.transform(newQuerydf_fr)

      results_eng['language'] = ['english'] * len(results_eng['rank'])
      results_fr['language'] = ['french'] * len(results_fr['rank'])

      results_eng = normalizeDataFrames(results_eng, 'score')
      results_fr = normalizeDataFrames(results_fr, 'score')

      results_frames = [results_eng, results_fr]
      combined_results = pd.concat(results_frames)

      combined_results['ranking-score'] = combined_results['score'].rank(ascending = 0)
      combined_results = combined_results.set_index('ranking-score')
      combined_results = combined_results.sort_index()

      initial_results_eng['language'] = ['english'] * len(initial_results_eng['rank'])
      initial_results_fr['language'] = ['french'] * len(initial_results_fr['rank'])

      initial_results_eng = normalizeDataFrames(initial_results_eng, 'score')
      initial_results_fr = normalizeDataFrames(initial_results_fr, 'score')

      initial_results_frames = [initial_results_eng, initial_results_fr]
      initial_combined_results = pd.concat(initial_results_frames)

      initial_combined_results['ranking-score'] = initial_combined_results['score'].rank(ascending = 0)
      initial_combined_results = initial_combined_results.set_index('ranking-score')
      initial_combined_results = initial_combined_results.sort_index()

      initial_docno = []
      combined_pseudo_docno = []
      returned_data = {
        "translatedResult": translated_result,
        "queryLanguage": "english",
        "expandedQueries": expandedEngQueries,
        "initialDocs":[],
        "expandedDocs": []
      }

      for row in initial_combined_results.itertuples():
        if row.language == 'french':
          initial_docno.append({"docno": int(row.docno), "language": "french", "score": float(row.score)})
        elif row.language == 'english':
          initial_docno.append({"docno": int(row.docno), "language": "english", "score": float(row.score)})

      for item in initial_docno:
        for row in combined_data.itertuples():
          if int(row.Sno) == (int(item["docno"]) + 1) and row.Language == item["language"]:
            tokenized_abstract = row.Abstract.split(' ')
            abstract_lst = tokenized_abstract[0:30]
            abstract_snippet = ' '.join(abstract_lst)
            abstract_snippet = abstract_snippet + '...'
            returned_data['initialDocs'].append({
              "docid": row.Sno,
              "score": item['score'],
              "docLanguage": row.Language,
              "title": row.Title,
              "keywords": row.Keywords.split('; '),
              "authors": row.Authors,
              "releaseDate": row.ReleaseDate,
              "subjectHeadings": row.SubjectHeading.split(', '),
              "abstract": row.Abstract,
              "snippet": abstract_snippet
            })

      for row in combined_results.itertuples():
        if row.language == 'french':
          combined_pseudo_docno.append({"docno": int(row.docno), "language": "french", "score": float(row.score)})
        elif row.language == 'english':
          combined_pseudo_docno.append({"docno": int(row.docno), "language": "english", "score": float(row.score)})

      for item in combined_pseudo_docno:
        for row in combined_data.itertuples():
          if int(row.Sno) == (int(item["docno"]) + 1) and row.Language == item["language"]:
            tokenized_abstract = row.Abstract.split(' ')
            abstract_lst = tokenized_abstract[0:30]
            abstract_snippet = ' '.join(abstract_lst)
            abstract_snippet = abstract_snippet + '...'
            returned_data['expandedDocs'].append({
              "docid": row.Sno,
              "score": item['score'],
              "docLanguage": row.Language,
              "title": row.Title,
              "keywords": row.Keywords.split('; '),
              "authors": row.Authors,
              "releaseDate": row.ReleaseDate,
              "subjectHeadings": row.SubjectHeading.split(', '),
              "abstract": row.Abstract,
              "snippet": abstract_snippet
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

      finalQuery_origin = frenchInputProcessed(original_query_simple)
      finalQuery_translated = engInputProcessed(translated_result_final)

      initial_results_eng = rankedRetrieval_eng.search(finalQuery_translated)
      initial_results_fr = rankedRetrieval_fr.search(finalQuery_origin)

      bo1_eng_transformed = bo1_eng.transform(initial_results_eng)
      bo1_fr_transformed = bo1_fr.transform(initial_results_fr)

      tokenized_bo1_eng_transformed = bo1_eng_transformed.loc[0, 'query'].split(' ')
      tokenized_bo1_fr_transformed = bo1_fr_transformed.loc[0, 'query'].split(' ')

      englishTerms = tokenized_bo1_eng_transformed
      frenchTerms = tokenized_bo1_fr_transformed
      for item in tokenized_bo1_eng_transformed:
        if (item != 'applypipeline:off'):
          item_lst = item.split('^')
          try:
            translated_expandQuery = GoogleTranslator(source='english', target='french').translate(item_lst[0])
            # I want to stem the query
            translated_expandQuery_stemmed = fs.stem(translated_expandQuery)
            # and then remove the accents in french
            translated_expandQuery_final = unidecode.unidecode(translated_expandQuery_stemmed)
            # now the newTermEntry should be good to go
            newTermEntry = [translated_expandQuery_final, item_lst[1]]
            # insert into list at right location
            for i in range(len(frenchTerms)):
              if (i != 0):
                currTerms = frenchTerms[i].split('^')
                if (float(currTerms[1]) < float(item_lst[1])):
                  frenchTerms.insert(i, ''+newTermEntry[0]+'^'+newTermEntry[1])
                  break
                # we are assuming index 0 is always 1
          except:
            continue

      for item in tokenized_bo1_fr_transformed:
        if (item != 'applypipeline:off'):
          item_lst = item.split('^')
          try:
            translated_expandQuery = GoogleTranslator(source='french', target='english').translate(item_lst[0])
            # first you need to stem the translated expand queries
            translated_expandQuery_final = ps.stem(translated_expandQuery)
            # now put that in the newTermEntry
            newTermEntry = [translated_expandQuery_final, item_lst[1]]
            # insert into list at right location
            for i in range(len(englishTerms)):
              if (i != 0):
                currTerms = englishTerms[i].split('^')
                if (float(currTerms[1]) < float(item_lst[1])):
                  englishTerms.insert(i, ''+newTermEntry[0]+'^'+newTermEntry[1])
                  break
          except:
            continue

      expandedEngQueries = []
      for i in range(len(englishTerms)):
        if (i == 0):
          continue
        else:
          english_item_lst = englishTerms[i].split('^')
          expandedEngQueries.append(english_item_lst[0])
      expandedEngQueries = list(dict.fromkeys(expandedEngQueries))

      frenchTermstoString = ' '.join(frenchTerms)
      englishTermstoString = ' '.join(englishTerms)

      allqid_eng = bo1_eng_transformed['qid'].tolist()
      allqid_fr = bo1_fr_transformed['qid'].tolist()

      newQuerydf_eng = pd.DataFrame({'qid': allqid_eng, 'query': [englishTermstoString]})
      newQuerydf_fr = pd.DataFrame({'qid': allqid_fr, 'query': [frenchTermstoString]})

      results_eng = rankedRetrieval_eng.transform(newQuerydf_eng)
      results_fr = rankedRetrieval_eng.transform(newQuerydf_fr)

      results_eng['language'] = ['english'] * len(results_eng['rank'])
      results_fr['language'] = ['french'] * len(results_fr['rank'])

      results_eng = normalizeDataFrames(results_eng, 'score')
      results_fr = normalizeDataFrames(results_fr, 'score')

      results_frames = [results_eng, results_fr]
      combined_results = pd.concat(results_frames)

      combined_results['ranking-score'] = combined_results['score'].rank(ascending = 0)
      combined_results = combined_results.set_index('ranking-score')
      combined_results = combined_results.sort_index()

      initial_results_eng['language'] = ['english'] * len(initial_results_eng['rank'])
      initial_results_fr['language'] = ['french'] * len(initial_results_fr['rank'])

      initial_results_eng = normalizeDataFrames(initial_results_eng, 'score')
      initial_results_fr = normalizeDataFrames(initial_results_fr, 'score')

      initial_results_frames = [initial_results_eng, initial_results_fr]
      initial_combined_results = pd.concat(initial_results_frames)

      initial_combined_results['ranking-score'] = initial_combined_results['score'].rank(ascending = 0)
      initial_combined_results = initial_combined_results.set_index('ranking-score')
      initial_combined_results = initial_combined_results.sort_index()

      initial_docno = []
      combined_pseudo_docno = []
      returned_data = {
        "translatedResult": translated_result,
        "queryLanguage": "english",
        "expandedQueries": expandedEngQueries,
        "initialDocs":[],
        "expandedDocs": []
      }

      for row in initial_combined_results.itertuples():
        if row.language == 'french':
          initial_docno.append({"docno": int(row.docno), "language": "french", "score": float(row.score)})
        elif row.language == 'english':
          initial_docno.append({"docno": int(row.docno), "language": "english", "score": float(row.score)})

      for item in initial_docno:
        for row in combined_data.itertuples():
          if int(row.Sno) == (int(item["docno"]) + 1) and row.Language == item["language"]:
            tokenized_abstract = row.Abstract.split(' ')
            abstract_lst = tokenized_abstract[0:30]
            abstract_snippet = ' '.join(abstract_lst)
            abstract_snippet = abstract_snippet + '...'
            returned_data['initialDocs'].append({
              "docid": row.Sno,
              "score": item['score'],
              "docLanguage": row.Language,
              "title": row.Title,
              "keywords": row.Keywords.split('; '),
              "authors": row.Authors,
              "releaseDate": row.ReleaseDate,
              "subjectHeadings": row.SubjectHeading.split(', '),
              "abstract": row.Abstract,
              "snippet": abstract_snippet
            })

      for row in combined_results.itertuples():
        if row.language == 'french':
          combined_pseudo_docno.append({"docno": int(row.docno), "language": "french", "score": float(row.score)})
        elif row.language == 'english':
          combined_pseudo_docno.append({"docno": int(row.docno), "language": "english", "score": float(row.score)})

      for item in combined_pseudo_docno:
        for row in combined_data.itertuples():
          if int(row.Sno) == (int(item["docno"]) + 1) and row.Language == item["language"]:
            tokenized_abstract = row.Abstract.split(' ')
            abstract_lst = tokenized_abstract[0:30]
            abstract_snippet = ' '.join(abstract_lst)
            abstract_snippet = abstract_snippet + '...'
            returned_data['expandedDocs'].append({
              "docid": row.Sno,
              "score": item['score'],
              "docLanguage": row.Language,
              "title": row.Title,
              "keywords": row.Keywords.split('; '),
              "authors": row.Authors,
              "releaseDate": row.ReleaseDate,
              "subjectHeadings": row.SubjectHeading.split(', '),
              "abstract": row.Abstract,
              "snippet": abstract_snippet
            })

      print(json.dumps(returned_data))
  except:
    print('Some error occured ????. There is no valid answer ??????? ????')
  sys.stdout.flush()


printOutcome(inputQuery)
