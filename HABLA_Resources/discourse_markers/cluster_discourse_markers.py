# -*- coding:utf-8-*-
__author__ = 'Lianet'

import argparse
import re
import numpy as np
import itertools
from sklearn.cluster import AffinityPropagation
from math import log
import json
from utils import utilHABLA

'''
This script builts automatically a resources with discourse marker in Spanish (SP) and Portuguese (PT)
A list of discourse markers in SP is translated to the PT using Moses

Inputs:
(1) moses translations; (2) list of Spanish markers and (3) list of portuguese markers
Output:
Discourse markers in Spanish and Portuguese translated following the similarities among the translations

The moses translations are selected as a candidate translation of discourse markers if it belongs the list of markers (SP or PT) passed as a parameter 

As traduções obtidas com o Moses são selecionadas como traduções candidatas sempre que elas perteçam a lista
de marcadores discursivos gerada no Dizer e na Teses

How to run the script
python3 discourse_markers/createAgrupamente_Marcadores.py -e input/spanishDiscourseMarkers_HABLA.txt -d input/portugueseDM_HABLA 
-m input/out_SeveralTranslationsDiscouseMarkers > ver
'''

def scriptParameters():
    parser = argparse.ArgumentParser(description='Cluster SP and PT discourse markers')
    parser.add_argument('-e', '--listMarcadoresEspanhol', help='list of SP markers', required=True)
    parser.add_argument('-d', '--listMarcadoresPT' ,help='list of portuguese markers',  required=True)
    parser.add_argument('-m', '--traducaoMoses', help='file with SP and PT transtalations (Moses)', required=True)
    args = parser.parse_args()
    return args

def create_Reference_DM_PT(portuguese_DiscourseMarkers):
    '''
        Build a list of PT discourse markers (reference)
        :param portuguese_DiscourseMarkers: list of portuguese markers
        :return: dictionary with PT discourse markers
    '''
    dic_Ref_PT_DM = {}
    for i in portuguese_DiscourseMarkers:
        i = i.strip('\n')
        if i in dic_Ref_PT_DM:
            dic_Ref_PT_DM[i] = dic_Ref_PT_DM[i] + 1
        else:
            dic_Ref_PT_DM[i] = 1
    return dic_Ref_PT_DM

def createDicTraducoes_PT(list_translations):
    '''

    :param list_translations: list of PT translation
    :return: dictionary of PT which the number of times each marker appear in each translation. This dictionary is useful
    to identified if many markers in Spanish have the same PT translation
    '''
    dic_Traducao_Marcadores = {}
    for i in list_translations:
        arrayWord = i.split('\t')
        for eachWord in arrayWord:
            if eachWord != ' ':
                if eachWord not in dic_Traducao_Marcadores:
                    dic_Traducao_Marcadores[eachWord] = 1
                else:
                    dic_Traducao_Marcadores[eachWord] = dic_Traducao_Marcadores[eachWord] + 1
    return dic_Traducao_Marcadores

def agrupamentoMarcadores(list_spanishMarkers, list_translations, dic_Traducao_Marcadores):
    '''
    Cluster DMs in SP and PT base on the translations
    :param list_spanishMarkers: list of SP markers
    :param list_translations: list of translations
    :param dic_Traducao_Marcadores: dictionary with PT markers and its occurence in SP translation
    :return:
    '''
    stringMarkers = np.array(list(dic_Traducao_Marcadores.keys()))
    print('Calculating distances')
    (dim,) = stringMarkers.shape
    print(totalMarcadores)
    # Using Dice coeficient
    #f = lambda x: calculaDice(x, dic_Traducao_Marcadores, totalMarcadores, list_translations)
    # Using likelihood
    f = lambda x: calcula_LogLikelihood(x, dic_Traducao_Marcadores, totalMarcadores, list_translations)
    # Using Point Wise Mutual information
    #f = lambda x: calculaPointWiseMutual_Information(x, dic_Traducao_Marcadores, totalMarcadores, list_translations)
    res = np.fromiter(map(f, [(x, y) for x, y in itertools.product(stringMarkers, stringMarkers)]), dtype=np.float)
    A = np.reshape(res,(dim,dim))

    #af = AffinityPropagation(affinity='precomputed').fit(A) #Using precompute ==> Worse cluster was obtained
    af = AffinityPropagation().fit(A) # Using Euclidian similarity measure ==> Best cluster was obtained
    cluster_centers_indices = af.cluster_centers_indices_
    labels = af.labels_
    return stringMarkers, labels

def calculaDice(tuple_markers, dic_Traducao_Marcadores, totalMarcadores, list_translations):
    '''
    Estimate the similarity between DMs using Dice coeficient
    ::param tuple_markers: Dm tuple
    :param dic_Traducao_Marcadores: dictionary with PT markers
    :param totalMarcadores: total of DM
    :param list_translations: total of translations
    :return: similarity value between DM following Dice coefficient
    '''

    i, j = tuple_markers
    valueDice = 0
    count_i_j = 0
    if dic_Traducao_Marcadores.has_key(i) and dic_Traducao_Marcadores.has_key(j):
        pb_i = (float(dic_Traducao_Marcadores[i])/totalMarcadores)
        pb_j = (float(dic_Traducao_Marcadores[j])/totalMarcadores)
        for traducao in list_translations:
            arrayTraducao = traducao.split('\t')
            if i in arrayTraducao: #Se aparece a palavra i na traducao candidata verifica se aparece
                if j in arrayTraducao:
                    count_i_j = count_i_j + 1
        count_i_j = float(count_i_j)/totalMarcadores
        valueDice = (2 * count_i_j)/(pb_i+pb_j)
    return valueDice

def calculaPointWiseMutual_Information(tuple_markers, dic_Traducao_Marcadores, totalMarcadores, list_translations):
    '''
    pmi = log2(p(x|y)/p(x)*p(y))
    Estimate the similarity between DMs using Point Wise Mutual Information
        ::param tuple_markers: Dm tuple
        :param dic_Traducao_Marcadores: dictionary with PT markers
        :param totalMarcadores: total of DM
        :param list_translations: total of translations
        :return: similarity value between DM following Point Wise Mutual Information
    '''
    valuePointWise = 0
    count_i_j = 0
    i, j = tuple_markers
    if dic_Traducao_Marcadores.has_key(i) and dic_Traducao_Marcadores.has_key(j):
        pb_i = (float(dic_Traducao_Marcadores[i])/totalMarcadores)
        pb_j = (float(dic_Traducao_Marcadores[j])/totalMarcadores)
        for traducao in list_translations:
            arrayTraducao = traducao.split('\t')
            if i in arrayTraducao: #Se aparece a palavra i na traducao candidata verifica se aparece
            #a tradução j
                if j in arrayTraducao:
                    count_i_j = count_i_j + 1#Quantidades de vezes que acontecem conjuntamente os dois marcadores
        count_i_j = float(count_i_j)/totalMarcadores#Probabilidade Conjunta
        value = ((count_i_j)/(pb_i*pb_j))
        if value!=0:
            valuePointWise = log(value,2)
        else:
            valuePointWise = 0
    return valuePointWise

def calcula_LogLikelihood(tuple_markers, dic_Traducao_Marcadores,
                          totalMarcadores, list_translations):
    '''
        Estimate the similarity between DMs using log-likelihood (ll)
        :param tuple_markers: Dm tuple
        :param dic_Traducao_Marcadores: dictionary with PT markers
        :param totalMarcadores: total of DM
        :param list_translations: total of translations
        :return: similarity value between DM following log-likelihood (ll)
    '''

    i, j = tuple_markers
    valuell = 0
    count_i_j = 0 #Acontecem os dois
    count_Ni_j = 0 #Nao Acontecem i, mas acontece j
    count_i_Nj = 0 #Acontecem i, mas Nao acontece j
    count_Ni_Nj = 0 #Nao Acontece nem i e nem j
    if i in dic_Traducao_Marcadores and j in dic_Traducao_Marcadores:
        pb_i = (float(dic_Traducao_Marcadores[i])/totalMarcadores)
        pb_j = (float(dic_Traducao_Marcadores[j])/totalMarcadores)
        for traducao in list_translations:
            arrayTraducao = traducao.split('\t')
            #Calcula se acontecem os dois
            if i in arrayTraducao: #Se aparece a palavra i na traducao candidata verifica se aparece
            #a tradução j
                if j in arrayTraducao:
                    count_i_j = count_i_j + 1#Quantidades de vezes que acontecem conjuntamente os dois marcadores
            #Acontece i e nao acontece j
            if i in arrayTraducao: #Se aparece a palavra i na traducao candidata verifica se aparece
            #a tradução j
                if j not in arrayTraducao:#j nao aparece
                    count_i_Nj = count_i_Nj + 1#
            #Acontece j e nao acontece i
            if i not in arrayTraducao: #i nao acontece
            #a tradução j
                if j in arrayTraducao:#j acontece
                    count_Ni_j = count_Ni_j + 1#
            #Nao acontece nem i e nem j
            if i not in arrayTraducao: #i nao acontece
            #a tradução j
                if j not in arrayTraducao:#j acontece
                    count_Ni_Nj = count_Ni_Nj + 1#

        if count_i_j!=0:#Acontecem os dois
            a=log(count_i_j,2)
        else: a = log(0.0000000000000000000000000000000000001,2)
        if count_i_Nj!=0:#Acontece i e nao acontece j
            b = log(count_i_Nj,2)
        else: b= log(0.0000000000000000000000000000000000001,2)
        if count_Ni_j!=0:#Nao Acontece i e acontece j
            c = log(count_Ni_j,2)
        else: c= log(0.0000000000000000000000000000000000001,2)
        if count_Ni_Nj!=0: #Nao acontece nem i e nem j
            d = log(count_Ni_Nj,2)
        else: d= log(0.0000000000000000000000000000000000001,2)
        somaABCD = a+b+c+d
        if somaABCD>0:
            somaABCDLog = log(somaABCD,2)
        else:somaABCDLog = log(0.0000000000000000000000000000000000001,2)
        value_1=(count_i_j*a)+(count_i_Nj*b)+(count_Ni_j*c)+(count_Ni_Nj*d)+(somaABCD*somaABCDLog)
        if (count_i_j+count_i_Nj)!=0:
            logAB = log(count_i_j+count_i_Nj,2)
        else: logAB= log(0.0000000000000000000000000000000000001,2)
        if (count_i_j+count_Ni_j)!=0:
            logAC = log(count_i_j+count_Ni_j,2)
        else: logAC= log(0.0000000000000000000000000000000000001,2)
        if (count_i_Nj+count_Ni_Nj)!=0:
            logBD = log(count_i_Nj+count_Ni_Nj,2)
        else: logBD= log(0.0000000000000000000000000000000000001,2)
        if (count_Ni_j+count_Ni_Nj)!=0:
            logCD = log(count_Ni_j+count_Ni_Nj,2)
        else:
            logCD= log(0.0000000000000000000000000000000000001,2)
        value_2 = ((count_i_j+count_i_Nj)*logAB)-((count_i_j+count_Ni_j)*logAC)-((count_i_Nj+count_Ni_Nj)*logBD)-((count_Ni_j+count_Ni_Nj)*logCD)
        valuell = value_1 - value_2
        valuePointWise = 0
    return valuell

def obtain_Translation(list_spanishMarkers, dic_Ref_PT_DM, file_traducaoMoses):

    '''

    :param list_spanishMarkers: list of SP DMs
    :param dic_Ref_PT_DM: dictionary with PT DMs
    :param file_traducaoMoses: Moses file with SP and PT translations
    :return: dictionary key = SP values = list of PT that is a translation of SP
    '''

    dic_Espanhol_Translations = {}
    list_translateMoses = utilHABLA.carrega_texto_Linhas(file_traducaoMoses)
    pattern = r'[\w+]*|[\w+\s\w+]*'
    pos_FileTranslate = 0
    for pos in range(0, len(list_spanishMarkers)-1):
        dicTranslations = {}
        infoLine = list_translateMoses[pos_FileTranslate]
        posAtual = (infoLine.split(' ||| ')[0]).strip('\n')
        while int(pos) == int(posAtual):
            #Check if translation is a marker
            atualTranslate = (infoLine.split(' ||| ')[1]).strip('') #Current translation
            m = re.compile(pattern, flags=re.UNICODE)
            atual = ''
            for s in m.findall(atualTranslate):
                if s != '':
                    atual = atual + ' ' + s
            atualTranslate = atual.strip(' ')
            if atualTranslate in dic_Ref_PT_DM:
                if atualTranslate in dicTranslations:
                    dicTranslations[str(atualTranslate)] = dicTranslations[str(atualTranslate)] + 1
                else:
                    dicTranslations[str(atualTranslate)] = 1
            pos_FileTranslate = pos_FileTranslate + 1
            infoLine = list_translateMoses[pos_FileTranslate]
            posAtual = (infoLine.split(' ||| ')[0]).strip('\n')
        dic_Espanhol_Translations[list_spanishMarkers[pos]] = dicTranslations

    return dic_Espanhol_Translations

if __name__ == '__main__':
    args = scriptParameters()

    list_SemTraducao = []
    listSpanish = []
    list_translations = []
    portuguese_DiscourseMarkers = utilHABLA.carrega_texto_Linhas(args.listMarcadoresPT)
    dic_Ref_PT_DM = create_Reference_DM_PT(portuguese_DiscourseMarkers)

    list_spanishMarkers = utilHABLA.carrega_texto_Linhas(args.listMarcadoresEspanhol)
    dic_Espanhol_Translations = obtain_Translation(list_spanishMarkers, dic_Ref_PT_DM, args.traducaoMoses)

    # Check each marker to create a list of PT DMs that are translation of SP
    es_pt_pairs = {}
    for key, values in dic_Espanhol_Translations.items():
        translations = []
        if values:
            for item, value in values.items():
                translations.append(item)
        es_pt_pairs[key.strip('\n')] = translations

    for i in dic_Espanhol_Translations:
        translations = ' '
        if dic_Espanhol_Translations[i]!={}:
            for each_Translate in dic_Espanhol_Translations[i]:
                translations = translations + '\t' +each_Translate
            listSpanish.append(i.strip('\n'))
            list_translations.append(translations)
        else:
            list_SemTraducao.append(i)

    # Following similarity among markers are calculate to DM considering its occurence in different translation
    dic_Traducao_Marcadores = createDicTraducoes_PT(list_translations)

    totalMarcadores = len(dic_Traducao_Marcadores)
    print(totalMarcadores)
    #Clustering DM
    #Input --> (i) spanish DM and its translations; (ii) dictionary with PT DM and how many times occured in each spanish translation
    #Output --> Gruops (list with the groups) Each group is a list of elements [pos0=spanish_markers, pos1=portuguese_translations]
    stringMarkers, labels = agrupamentoMarcadores(list_spanishMarkers, list_translations, dic_Traducao_Marcadores)
    unique_labels = set(labels)

    # Print cluster in a json file
    # Dictionary key = cluster ID and values = list of PT DM
    pt_group = {}
    for i in unique_labels:
        if i in pt_group:
            pt_group[i].append(stringMarkers[labels == i][0])
        else:
            pt_group[i] = [stringMarkers[labels == i][0]]

    pt_es_align = {}
    # Align ES an PT per cluster ID
    for i in range(0, 33):
        es_cand = []
        for marker in np.nditer(pt_group[i]):
            for es, pt_cand in es_pt_pairs.items():
                if marker in pt_cand:
                    es_cand.append(es)
        pt_es_align[i] = {'pt': pt_group[i], 'es': es_cand}

    with open('exemple1.json', 'w', encoding='utf-8') as fp:
        json.dump(pt_es_align, fp, ensure_ascii=False)