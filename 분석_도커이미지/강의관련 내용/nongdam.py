import pandas as pd
from konlpy.tag import Komoran
from collections import Counter
import boto3
import os
from datetime import datetime
from io import BytesIO
from io import StringIO

## 용어사전 정의
# 불용어
with open('./word_dic/stopword.txt', 'r', encoding='utf-8') as stopwords_file:
    # 파일 내용을 줄 단위로 읽어와 리스트로 저장
    stopwords = stopwords_file.read().splitlines()

# 두 파일의 내용을 읽어와서 합치기 (수업과 관련된 단어, 관련없는 단어) ## 애매한 단어 추가 예정
with open('./word_dic/user_dic.txt', 'r', encoding='utf-8') as file1, open('./word_dic/user_dic_moo.txt', 'r', encoding='utf-8') as file2,open('./word_dic/user_dic_uncertain.txt', 'r', encoding='utf-8') as file3:
    file1_line = file1.readlines()
    file2_line = file2.readlines()
    file3_line = file3.readlines()

def s3_connection():
    try:

        aws_access_key_id = os.environ.get("AWS_ACCESS_KEY_ID")
        aws_secret_access_key = os.environ.get("AWS_SECRET_ACCESS_KEY")

        
        s3 = boto3.client(
            service_name="s3",
            region_name="ap-northeast-2", # 자신이 설정한 bucket region
            aws_access_key_id= aws_access_key_id,
            aws_secret_access_key= aws_secret_access_key,
        )
    except Exception as e:
        print(e)
    else:
        print("s3 bucket connected!")
        return s3

## s3 에서 파일 가져오기
def download_s3(file_path):
    s3 = s3_connection()
    obj = s3.get_object(Bucket='s3-ncho', Key=file_path)
    content = obj['Body'].read()
    df = pd.read_csv(BytesIO(content))
    return df

def nongdam(file_path):

    df = download_s3(file_path)
    # 특수기호 제거, 한글 숫자만
    df['Text_kor'] = df['Text'].str.replace("[.,]"," ")

    # 문장 길이 기준으로 일정 길이 이상인 행만 선택
    min_sentence_length = 10
    df = df[df['Text'].apply(len) >= min_sentence_length]
    
    # 결측치 제거
    rows_to_remove = df[(df['Text_kor'] == ' ')].index
    df = df.drop(rows_to_remove)
    df.dropna(inplace=True)

    ## 문장 토큰화
    komoran = Komoran()
    # 사용자 용어사전 등록
    komoran = Komoran(userdic='./word_dic/combined_user_dic.txt')

    tokenized_words, sentence_nouns_total = [], []

    for sentence in df['Text_kor']:
        # 토큰화 및 정규화
        tokenized_word = komoran.morphs(sentence)
        
        # 불용어 제거
        stopwords_removed_sentence = [word for word in tokenized_word if not word in stopwords]
        tokenized_words.append(stopwords_removed_sentence)

        # 명사만 추출
        nouns = komoran.nouns(sentence)
        
        # 불용어가 제거된 명사만 저장
        nouns_removed_stopwords = [noun for noun in nouns if not noun in stopwords]
        nouns_filtered = [noun for noun in nouns_removed_stopwords if len(noun) >= 2]
        sentence_nouns_total.append(nouns_filtered)
    
    df['tokenized_words'] = tokenized_words
    # 리스트로 되어 있는것을 단어로 구분
    df['tokenized_words'] = df['tokenized_words'].apply(lambda noun_list: ' '.join(map(str, noun_list)))

    list1 = []
    all_reviews = [item for sublist in sentence_nouns_total for item in sublist]

    word_freq = Counter(all_reviews)
    top_words = word_freq.most_common()

    for word, freq in top_words:
        if freq >= 10:
            list1.append(word)
    
    # 강의 단어 리스트 작성
    ## 강의 관련 없는 단어
    unrelated_list = [line.split('\t')[0] for line in file2_line]
    ## 구분 애매한 단어
    ambiguous_list = [line.split('\t')[0] for line in file3_line]
    ## 강의 연관 단어
    list4 = [line.split('\t')[0] for line in file1_line]
    relation_total = list1 + list4
    relation_total = [word for word in relation_total if word not in (unrelated_list + ambiguous_list)]

    df['강의관련'] = df['tokenized_words'].apply(lambda text: sum(word.lower() in relation_total for word in text.split()))
    df['강의상관없는 단어'] = df['tokenized_words'].apply(lambda text: sum(word.lower() in unrelated_list for word in text.split()))
    df['애매한 단어'] = df['tokenized_words'].apply(lambda text: sum(word.lower() in ambiguous_list for word in text.split()))

    df['환산 점수'] = df['강의관련'] * 3 + df['강의상관없는 단어'] * -3 + df['애매한 단어']

    return df, len(df), len(df[df['환산 점수']<=2])

def upload_speed_s3(total, target):
    s3 = s3_connection()
    df = pd.DataFrame([[total, target, round((target/total)*100, 3)]], columns=['total_len', 'target_len', 'rate'])
    datetime_upload = str(datetime.today())
    df['datetime_upload'] = datetime_upload
    df['subject'] = ''
    df['minor_subject'] = ''
    df['teacher'] = 'NEW'
    df['class_name'] = ''
    df['lecture_name'] = ''
    column_order = ['datetime_upload', 'subject', 'minor_subject' ,'teacher', 'class_name' , 'lecture_name', 'total_len', 'target_len', 'rate' ]
    data = df[column_order]
    csv_buffer = StringIO()
    data.to_csv(csv_buffer, index=False)
    bucket_name = 's3-ncho'
    csv_file_key = 'user_result/nongdam_new.csv'
    s3.put_object(Body=csv_buffer.getvalue(), Bucket=bucket_name, Key=csv_file_key)


s3 = s3_connection()

def main() : 
    
    df, total, target = nongdam('jeoncheori/dataframe.csv')
    upload_speed_s3(total, target)

if __name__ == "__main__":
    main()