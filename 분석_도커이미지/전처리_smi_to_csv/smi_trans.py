import re # smi 파일에서 텍스트 뽑아내는 모듈
import pandas as pd
import nltk
nltk.download('punkt')
from nltk import sent_tokenize

import boto3
from io import StringIO


def upload_to_s3(df, sentences, bucket_name, key_prefix):
    # Convert DataFrame to CSV string
    df_csv_buffer = StringIO()
    df.to_csv(df_csv_buffer, index=False)
    df_csv_content = df_csv_buffer.getvalue()

    # Upload DataFrame to S3
    df_key = f'{key_prefix}/dataframe.csv'
    s3.put_object(Body=df_csv_content, Bucket=bucket_name, Key=df_key)
    print(f'DataFrame이 S3에 업로드되었습니다: s3://{bucket_name}/{df_key}')

    # Convert list of sentences to DataFrame and then to CSV string
    sentences_df = pd.DataFrame(sentences, columns=['Sentence'])
    sentences_csv_buffer = StringIO()
    sentences_df.to_csv(sentences_csv_buffer, index=False)
    sentences_csv_content = sentences_csv_buffer.getvalue()

    # Upload sentences to S3
    sentences_key = f'{key_prefix}/nltk_dataframe.csv'
    s3.put_object(Body=sentences_csv_content, Bucket=bucket_name, Key=sentences_key)
    print(f'문장 리스트가 S3에 업로드되었습니다: s3://{bucket_name}/{sentences_key}')
import os
def s3_connection():
    try:
        aws_access_key_id = os.environ.get("AWS_ACCESS_KEY_ID")
        aws_secret_access_key = os.environ.get("AWS_SECRET_ACCESS_KEY")
        
        s3 = boto3.client(
            service_name="s3",
            region_name="ap-northeast-2", # 자신이 설정한 bucket region
            aws_access_key_id=aws_access_key_id,
            aws_secret_access_key=aws_secret_access_key,
        )
    except Exception as e:
        print(e)
    else:
        print("s3 bucket connected!")
        return s3

def download_s3_jeoncheori(file_path):
        
    obj = s3.get_object(Bucket = 's3-ncho', Key = file_path)
    content = obj['Body'].read().decode('cp949')
    wholefile = content.lower()
    pattern = re.compile(r'<sync start=(\d+)><p class=krcc>\r\n(.*?)\n', re.DOTALL)
    matches = pattern.findall(''.join(wholefile))
    matches = [(str(time_stamp), text) for time_stamp, text in matches]
    df = pd.DataFrame(matches, columns=['Time_Stamp(s)', 'Text'])
    df['Time_Stamp(s)'] = df['Time_Stamp(s)'].apply(lambda x: float(x)/1000)
    text = ''.join(df['Text'].tolist())
    sentences = sent_tokenize(''.join(text))
    return df, sentences


s3 = s3_connection()

def main():

    df, sentences = download_s3_jeoncheori('ori_file/user_upload.smi')
    upload_to_s3(df, sentences, 's3-ncho', 'jeoncheori')

if __name__ == "__main__":
    main()

