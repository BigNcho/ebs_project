import numpy as np
from datetime import datetime
import pandas as pd
import boto3
from io import StringIO
import os
import mysql.connector

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
    
def s3_download_context(key):
    s3 = s3_connection()
    response = s3.get_object(Bucket='s3-ncho', Key=key)
    csv_content = response['Body'].read().decode('utf-8')
    csv_file = StringIO(csv_content)
    df = pd.read_csv(csv_file)
    csv_data_flat_list = df.values.flatten().tolist()
    return df, csv_data_flat_list

def convert_to_percentage(df):
    start_timestamp = df['Time_Stamp(s)'].min()
    end_timestamp = df['Time_Stamp(s)'].max()
    df['Scaled_Percent'] = (df['Time_Stamp(s)'] - start_timestamp) / (end_timestamp - start_timestamp) * 100
    return df

def calculate_speed(df):
    df['Time_difference'] = df['Time_Stamp(s)'].shift(-1) - df['Time_Stamp(s)']
    df['Time_difference'].fillna(0, inplace=True)
    df['words'] = df['Text'].apply(lambda x: len(x))
    df = df[(df['Time_difference'] < 20) & (df['Time_difference'] > 1) & (df['words'] > 10)]
    df['speed'] = df['Time_difference'] / df['words']
    return df

def get_average_speed_by_percent(df):
    avg_speed_by_percent = df.groupby('Scaled_Percent')['speed'].mean().reset_index()
    return avg_speed_by_percent

def calculate_interval_speed(df, interval):
    interval_speeds = []
    for i in range(0, 100, interval):
        subset_df = df[(df['Scaled_Percent'] >= i) & (df['Scaled_Percent'] < i + interval)]
        median_speed = np.nanmedian(subset_df['speed'])  # 중앙값으로 변경
        interval_speeds.append(median_speed)
    return interval_speeds

def upload_speed_s3(df):
    s3 = s3_connection()
    datetime_upload = str(datetime.today())
    df['datetime_upload'] = datetime_upload
    df['subject'] = ''
    df['minor_subject'] = ''
    df['teacher'] = 'NEW'
    df['class_name'] = ''
    df['lecture_name'] = ''
    column_order = ['datetime_upload', 'subject', 'minor_subject' ,'teacher', 'class_name' , 'lecture_name', 'time_percentage', 'speed' ]
    data = df[column_order]
    csv_buffer = StringIO()
    data.to_csv(csv_buffer, index=False)
    bucket_name = 's3-ncho'
    csv_file_key = 'user_result/speed_new.csv'
    s3.put_object(Body=csv_buffer.getvalue(), Bucket=bucket_name, Key=csv_file_key)

def rds_upload(df):

    user_host = os.environ.get("RDS_HOST")
    user_id = os.environ.get("RDS_ID")
    user_password = os.environ.get("RDS_PASSWORD")
    user_db = os.environ.get("RDS_DB")

    conn = mysql.connector.connect(
        host = user_host,
        user= user_id,
        password= user_password,
        db= user_db
        )
    cursor = conn.cursor()
    datetime_upload = ''
    subject = ''
    minor_subject = ''
    teacher = 'NEW'
    class_name = ''
    lecture_name = ''
    time_percentage = ''
    speed = ''
    # SQL 쿼리 수정
    sql = """
    INSERT INTO speed (datetime_upload, subject, minor_subject , teacher , class_name ,lecture_name , time_percentage, speed ) 
    VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
    """
    cursor.execute(sql, (datetime_upload, subject, minor_subject , teacher , class_name ,lecture_name ,time_percentage, speed))
    conn.commit()
    conn.close()
    print('rds 적재 완료')

def main():
    interval = 1  # 1% 간격으로 계산
    interval_speeds_list = []
    df,_ = s3_download_context('jeoncheori/dataframe.csv')
    df = convert_to_percentage(df)
    df = calculate_speed(df)
    avg_speed_by_percent = get_average_speed_by_percent(df)
    interval_speeds = calculate_interval_speed(avg_speed_by_percent, interval)
    interval_speeds_list.append(interval_speeds)
    combined_interval_speed_df = pd.DataFrame(interval_speeds_list).transpose()
    combined_interval_speed_df.index = range(1, 101)
    combined_interval_speed_df = combined_interval_speed_df.mean(axis=1)
    combined_interval_speed_df = pd.DataFrame({'time_percentage': combined_interval_speed_df.index, 'speed': combined_interval_speed_df.values})
    return combined_interval_speed_df  # 변수 반환

if __name__ == "__main__":
    df = main()  # 함수 실행 결과를 변수에 저장
    upload_speed_s3(df)
    print(df)
    rds_upload(df)



# import numpy as np
# from datetime import datetime
# import pandas as pd
# import boto3
# from io import StringIO
# import os
# def s3_connection():
#     try:
#         aws_access_key_id = os.environ.get("AWS_ACCESS_KEY_ID")
#         aws_secret_access_key = os.environ.get("AWS_SECRET_ACCESS_KEY")

#         s3 = boto3.client(
#             service_name="s3",
#             region_name="ap-northeast-2", # 자신이 설정한 bucket region
#             aws_access_key_id=aws_access_key_id,
#             aws_secret_access_key=aws_secret_access_key,
#         )
#     except Exception as e:
#         print(e)
#     else:
#         print("s3 bucket connected!")
#         return s3
    
    
# def s3_download_context(key):
#     s3 = s3_connection()
#     response = s3.get_object(Bucket='s3-ncho', Key=key)
#     csv_content = response['Body'].read().decode('utf-8')
#     csv_file = StringIO(csv_content)
#     df = pd.read_csv(csv_file)
#     csv_data_flat_list = df.values.flatten().tolist()
#     return df, csv_data_flat_list


# def convert_to_percentage(df):
#     start_timestamp = df['Time_Stamp(s)'].min()
#     end_timestamp = df['Time_Stamp(s)'].max()
#     df['Scaled_Percent'] = (df['Time_Stamp(s)'] - start_timestamp) / (end_timestamp - start_timestamp) * 100
#     return df

# def calculate_speed(df):
#     df['Time_difference'] = df['Time_Stamp(s)'].shift(-1) - df['Time_Stamp(s)']
#     df['Time_difference'].fillna(0, inplace=True)
#     df['words'] = df['Text'].apply(lambda x: len(x))
#     df = df[(df['Time_difference'] < 20) & (df['Time_difference'] > 1) & (df['words'] > 10)]
#     df['speed'] = df['Time_difference'] / df['words']
#     return df

# def get_average_speed_by_percent(df):
#     avg_speed_by_percent = df.groupby('Scaled_Percent')['speed'].mean().reset_index()
#     return avg_speed_by_percent
# def calculate_interval_speed(df, interval):
#     interval_speeds = []
#     for i in range(0, 100, interval):
#         subset_df = df[(df['Scaled_Percent'] >= i) & (df['Scaled_Percent'] < i + interval)]
#         median_speed = np.nanmedian(subset_df['speed'])  # 중앙값으로 변경
#         interval_speeds.append(median_speed)
#     return interval_speeds
# def upload_speed_s3(df):
#     s3 = s3_connection()
#     datetime_upload = str(datetime.today())
#     df['datetime_upload'] = datetime_upload
#     df['subject'] = ''
#     df['minor_subject'] = ''
#     df['teacher'] = 'NEW'
#     df['class_name'] = ''
#     df['lecture_name'] = ''
#     column_order = ['datetime_upload', 'subject', 'minor_subject' ,'teacher', 'class_name' , 'lecture_name', 'time_percentage', 'speed' ]
#     data = df[column_order]
#     csv_buffer = StringIO()
#     data.to_csv(csv_buffer, index=False)
#     bucket_name = 's3-ncho'
#     csv_file_key = 'user_result/speed_new.csv'
#     s3.put_object(Body=csv_buffer.getvalue(), Bucket=bucket_name, Key=csv_file_key)
# def main():
#     interval = 1  # 1% 간격으로 계산
#     interval_speeds_list = []
#     df,_ = s3_download_context('jeoncheori/dataframe.csv')
#     df = convert_to_percentage(df)
#     df = calculate_speed(df)
#     avg_speed_by_percent = get_average_speed_by_percent(df)
#     interval_speeds = calculate_interval_speed(avg_speed_by_percent, interval)
#     interval_speeds_list.append(interval_speeds)
#     combined_interval_speed_df = pd.DataFrame(interval_speeds_list).transpose()
#     combined_interval_speed_df.index = range(1, 101)
#     combined_interval_speed_df = combined_interval_speed_df.mean(axis=1)
#     combined_interval_speed_df = pd.DataFrame({'time_percentage': combined_interval_speed_df.index, 'speed': combined_interval_speed_df.values})
#     return combined_interval_speed_df  # 변수 반환
# if __name__ == "__main__":
#     df = main()  # 함수 실행 결과를 변수에 저장
#     upload_speed_s3(df)