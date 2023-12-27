import pandas as pd
import nltk
nltk.download('punkt')
from nltk import sent_tokenize
import os
import boto3
from io import StringIO
from transformers import AutoTokenizer, AutoModelForSequenceClassification, pipeline
from datetime import datetime
# import mysql.connector
from transformers import RobertaTokenizerFast, RobertaForSequenceClassification, TextClassificationPipeline


def s3_connection():
    try:
        aws_access_key_id = os.environ.get("AWS_ACCESS_KEY_ID")
        aws_secret_access_key = os.environ.get("AWS_SECRET_ACCESS_KEY")
        s3 = boto3.client(
            service_name="s3",
            region_name="ap-northeast-2",
            aws_access_key_id=aws_access_key_id,
            aws_secret_access_key=aws_secret_access_key,
        )
    except Exception as e:
        print(e)
    else:
        print("s3 bucket connected!")
        return s3
def s3_download_context(key):
    s3 = s3_connection()
    bucket_name = 's3-ncho'
    response = s3.get_object(Bucket=bucket_name, Key=key)
    csv_content = response['Body'].read().decode('utf-8')
    csv_file = StringIO(csv_content)
    df = pd.read_csv(csv_file)
    csv_data_flat_list = df.values.flatten().tolist()
    return df, csv_data_flat_list
def jondatmal_susahak():
    nltk_df, sentences = s3_download_context('jeoncheori/nltk_dataframe.csv')
    fragment, statement, question, command, rhetorical_question, rhetorical_command, intonation_dependent_utterance = 0, 0, 0, 0, 0, 0, 0
    sentences_list = formal_classifier(sentences)
    formal_df = pd.DataFrame(sentences_list)
    # LABEL_0을 반말, LABEL_1을 존댓말로 바꾸기
    formal_df['label'] = formal_df['label'].replace('LABEL_0', '반말')
    formal_df['label'] = formal_df['label'].replace('LABEL_1', '존댓말')
    for i in range(len(sentences)):
        preds_list = text_classifier(sentences[i])
        best_pred = preds_list[0]
        nltk_df.loc[i, '의도'] = max(preds_list[0], key=lambda x: x['score'])['label']
        nltk_df.loc[i, '의도_점수'] = max(preds_list[0], key=lambda x: x['score'])['score']
        if nltk_df.loc[i, '의도'] == 'fragment':
            fragment += 1
        elif nltk_df.loc[i, '의도'] == 'statement':
            statement += 1
        elif nltk_df.loc[i, '의도'] == 'question':
            question += 1
        elif nltk_df.loc[i, '의도'] == 'command':
            command += 1
        elif nltk_df.loc[i, '의도'] == 'rhetorical_question':
            rhetorical_question += 1
        elif nltk_df.loc[i, '의도'] == 'rhetorical_command':
            rhetorical_command += 1
        elif nltk_df.loc[i, '의도'] == 'intonation_dependent_utterance':
            intonation_dependent_utterance += 1
    df_concat = pd.concat([nltk_df,formal_df], axis=1)
    df_concat.columns=['문장', '의도','의도_점수', 'label', 'score']
    df_result = df_concat.groupby(['의도','label'])['score'].count().unstack(fill_value=0).stack()
    df_result = pd.DataFrame(df_result).reset_index()
    df_rds = df_result.copy()
    new_column = df_result['의도'] + '_' + df_result['label']
    df_rds.insert(loc=2, column='reset', value=new_column)
    df_rds = df_rds.drop(['의도','label'], axis=1)
    # re를 행렬 변환
    df_rds = df_rds.T
    # column 행을 행이름으로 지정
    df_rds.columns = df_rds.iloc[0]
    df_rds.drop(df_rds.index[0], inplace=True)
    df_rds = df_rds.rename_axis(columns=None).reset_index(drop=True)
    return df_rds

# 반말 존댓말 분류 모델
model = AutoModelForSequenceClassification.from_pretrained("j5ng/kcbert-formal-classifier")
tokenizer = AutoTokenizer.from_pretrained('j5ng/kcbert-formal-classifier')
formal_classifier = pipeline(task="text-classification", model=model, tokenizer=tokenizer)
# 의도 파악 모델
# Load fine-tuned model by HuggingFace Model Hub
HUGGINGFACE_MODEL_PATH = "bespin-global/klue-roberta-small-3i4k-intent-classification"
loaded_tokenizer = RobertaTokenizerFast.from_pretrained(HUGGINGFACE_MODEL_PATH )
loaded_model = RobertaForSequenceClassification.from_pretrained(HUGGINGFACE_MODEL_PATH )
# using Pipeline
text_classifier = TextClassificationPipeline(
    tokenizer=loaded_tokenizer,
    model=loaded_model,
    return_all_scores=True
)
def upload_s3(df_rds):
    s3 = s3_connection()
    datetime_upload = str(datetime.today())
    subject = ''
    minor_subject = ''
    teacher = 'NEW'
    class_name = ''
    lecture_name = ''
    command_il = df_rds['command_반말'][0]
    command_fl = df_rds['command_존댓말'][0]
    fragment_il = df_rds['fragment_반말'][0]
    fragment_fl = df_rds['fragment_존댓말'][0]
    idu_il = df_rds['intonation-dependent utterance_반말'][0]
    idu_fl = df_rds['intonation-dependent utterance_존댓말'][0]
    question_il = df_rds['question_반말'][0]
    question_fl = df_rds['question_존댓말'][0]
    rc_il = df_rds['rhetorical command_반말'][0]
    rc_fl = df_rds['rhetorical command_존댓말'][0]
    rq_il = df_rds['rhetorical question_반말'][0]
    rq_fl = df_rds['rhetorical question_존댓말'][0]
    statement_il = df_rds['statement_반말'][0]
    statement_fl = df_rds['statement_존댓말'][0]
    data = pd.DataFrame({'datetime_upload' : [datetime_upload], 'subject' : [''], 'minor_subject' : [''], 'teacher' : [''],
                         'class_name' : [''], 'lecture_name' : [''],
                         'command_il': [command_il], 'command_fl': [command_fl],
                         'fragment_il': [fragment_il], 'fragment_fl': [fragment_fl],
                         'idu_il': [idu_il], 'idu_fl': [idu_fl],
                         'question_il': [question_il], 'question_fl': [question_fl],
                         'rc_il': [rc_il], 'rc_fl': [rc_fl],
                         'rq_il': [rq_il], 'rq_fl': [rq_fl],
                         'statement_il': [statement_il], 'statement_fl': [statement_fl]
                         })
    csv_buffer = StringIO()
    data.to_csv(csv_buffer, index=False)
    bucket_name = 's3-ncho'
    csv_file_key = 'user_result/context_new.csv'
    s3.put_object(Body=csv_buffer.getvalue(), Bucket=bucket_name, Key=csv_file_key)
def main():
    df_rds = jondatmal_susahak()
    upload_s3(df_rds)
if __name__ == "__main__":
    main()