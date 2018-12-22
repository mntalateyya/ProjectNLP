# Natural Language Processing Project - 11-411 CMU
A question generation and answering system from article documents. The system generates questions and answers by searching for certain patterns in the dependency trees of sentences or using maximum lexical overlap.

We implemented these two functions that takes a document and would either return questions or answers if asked, by coreference resolution, patterns question/answer generating, rankings, maximum overlap.

Results:

Question Generation:
    We ran our implementation on one of the documents (Wikipedia/Chinese Language), and achieved 70% accuracy. Examples: 
        
        System's Question: Who estimated that there are hundreds of mutually unintelligible varieties of Chinese?
        
        System's Question: When did the National Language Unification Commission settle on the Beijing dialect ?



Question Answering:
    We ran our implementation on one of the documents (Wikipedia/Cancer (Constellation)), and achieved 83% accuracy. Examples: 
        
        Question: When is Cancer best visible ?
        System's Answer: It can be seen at latitudes between +90 ° and -60 ° and is best visible at 9 p.m. during the month of March
        
        Question: What is the dimmest of zodiacal constellations ?
        System's Answer: Cancer
        
        System's Question: In Chinese astronomy, what does the stars of Cancer lie within ?
        System's Answer: In Chinese astronomy, the stars of Cancer lie within the The Vermillion Bird of the South -LRB- 南方朱雀 , Nán Fāng Zhū Què-RRB
