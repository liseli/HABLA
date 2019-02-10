# -*- coding:utf-8-*-

__author__ = 'lianet'

import codecs
import nltk
from nltk.tokenize.regexp import regexp_tokenize
train = nltk.data.load('tokenizers/punkt/portuguese.pickle')
import re

#Funcao que receve o endereco do corpus e devolve a lista com todos os textos do corpus. O corpus pode ter varios textos o um unico texto
def carrega_corpus(dir_corpus,typeFile):
    '''
    Given the address of a corpus return a list of all the text
    :param dir_corpus:
    :param typeFile:
    :return:
    '''
    my_corpus=nltk.corpus.PlaintextCorpusReader(dir_corpus,typeFile)#Objeto que representa o corpus
    list_files = my_corpus.fileids()#Devolve a lista com os nomes do arquivos de texto
    return list_files

def carrega_texto_Linhas(pathTextos):
    '''
    Given the text's address return a list with all the line of the text.
    :param pathTextos: text address
    :return: list of lines
    '''
    file = open(pathTextos, 'r')#Arquivo
    ler_linhas = file.readlines()#Retorna uma lista com todas as linhas do arquivo
    return ler_linhas

def indexaUnigramText(pathText):

    '''
    Create a dictionary of unigrams
    :param pathText:
    :return:
    '''
    pattern = r'[\w]*\-[\w]*\-[\w]*|[\w]*\-[\w]*|[\-]?[0-9]+\,[0-9]+|[\-]?[0-9]+\.[0-9]+|\w+|[^\w\s\d]'
    paternNumberSymbol = r'\d+|[\\\.\^\$\?\+\*\{\}\[\]\(\)\|\:\;\"\`\!\#\,\<\>\=\_\%\&]'
    dicUnigram = {}
    #Carrega o texto
    text=codecs.open(pathText, 'r', 'utf-8-sig')
    #Tokeniza o texto
    for sent in train.tokenize(text.read()):
        #Funcao que devolve uma lista com as palavras de cada sentenca
        list_wordXSentenca=regexp_tokenize(sent, pattern, gaps=False, discard_empty=True,flags=re.UNICODE | re.MULTILINE | re.DOTALL)
        #print sent.encode('utf-8')
        for word in list_wordXSentenca:
            word = word.encode("utf-8")
            #print word
            list_word = regexp_tokenize(word,paternNumberSymbol,gaps=False,discard_empty=True,flags=re.UNICODE | re.MULTILINE | re.DOTALL)
            if list_word!=[]:
                pass
            else:
                if word in dicUnigram:
                    dicUnigram[word] = dicUnigram[word] + 1
                else:
                    dicUnigram[word] = 1
    return dicUnigram

def indexaBigramText(pathText):
    '''
    Create a dictionary of brigrams
    :param pathText: text's address
    :return:
    '''
    pattern = r'[\w]*\-[\w]*\-[\w]*|[\w]*\-[\w]*|[\-]?[0-9]+\,[0-9]+|[\-]?[0-9]+\.[0-9]+|\w+|[^\w\s\d]'
    paternNumberSymbol = r'\d+\s\d+|[\\\.\^\$\?\+\*\{\}\[\]\(\)\|\:\;\"\`\!\#\,\-\<\>\=\_\%\&]+\s[\\\.\^\$\?\+\*\{\}\[\]\(\)\|\:\;\"\`\!\#\,\-\<\>\=\_\%\&]+|\d+\s[\\\.\^\$\?\+\*\{\}\[\]\(\)\|\:\;\"\`\!\#\,\-\<\>\=\_\%\&]+|[\\\.\^\$\?\+\*\{\}\[\]\(\)\|\:\;\"\`\!\#\,\-\<\>\=\_\%\&]+\s\d+'
    dicBrigram = {}
    #Carrega o texto
    text = codecs.open(pathText, 'r', 'utf-8-sig')
    #Tokeniza o texto
    for sent in train.tokenize(text.read()):
        listBiGram = []
        #Funcao que devolve uma lista com as palavras de cada sentenca
        list_wordXSentenca=regexp_tokenize(sent, pattern, gaps=False, discard_empty=True,flags=re.UNICODE | re.MULTILINE | re.DOTALL)
        listBiGram = nltk.bigrams(list_wordXSentenca)#Cria uma lista de tuplas com os bigramas de cada sentença. Receve uma lista de palavras
        for eachTupla_Bi in listBiGram:
            atualBigram = eachTupla_Bi[0] + ' ' + eachTupla_Bi[1]
            atualBigram = atualBigram.encode("utf-8")
            list_word=regexp_tokenize(atualBigram.decode('utf-8'),paternNumberSymbol,gaps=False,discard_empty=True,flags=re.UNICODE | re.MULTILINE | re.DOTALL)
            if list_word!=[]:#len(list_word)==int(tamanhoNGram):
                pass
            else:
                if atualBigram in dicBrigram:
                    dicBrigram[atualBigram] = dicBrigram[atualBigram] + 1
                else:
                    dicBrigram[atualBigram] = 1
    return dicBrigram

def obtainBigramByWord(word,pathText):
    '''
    Select the bigrams that constin specific word
    :param word: word to search
    :param pathText: text's address
    :return:
    '''
    pattern = r'[\w]*\-[\w]*\-[\w]*|[\w]*\-[\w]*|[\-]?[0-9]+\,[0-9]+|[\-]?[0-9]+\.[0-9]+|\w+|[^\w\s\d]'
    errorsBiGram = []
    word = word.decode( 'utf-8' )
    #Carrega o texto
    text=codecs.open(pathText, 'r', 'utf-8-sig')
    #Tokeniza o texto
    for sent in train.tokenize(text.read()):
        #Funcao que devolve uma lista com as palavras de cada sentenca
        list_wordXSentenca=regexp_tokenize(sent, pattern, gaps=False, discard_empty=True,flags=re.UNICODE | re.MULTILINE | re.DOTALL)
        if word in list_wordXSentenca:
            listBiGram = nltk.bigrams(list_wordXSentenca)#Cria uma lista de tuplas com os bigramas de cada sentença. Receve uma lista de palavras
            #Seleciona as superCadeias que contem word
            for biGram in listBiGram:
                if word in biGram:
                    if biGram not in errorsBiGram:
                        errorsBiGram.append(biGram)
                    else:
                        pass
    return errorsBiGram

