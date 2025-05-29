import os
import json
import requests
import numpy as np
import boto3
import logging

from botocore.exceptions import ClientError
from datetime import date

API_BASE_URL = os.getenv("API_BASE_URL")
logger = logging.getLogger()
logger.setLevel(logging.INFO)

def get_secret_parameter(name: str, with_decryption=True) -> str:
    ssm = boto3.client('ssm')
    try:
        response = ssm.get_parameter(
            Name=name,
            WithDecryption=with_decryption
        )
        return response['Parameter']['Value']
    except ClientError as e:
        logger.error(f"Error getting parameter {name}: {e}")
        raise e

def is_past_3_business_days(from_date: date) -> bool:
    today = date.today()
    return np.busday_count(from_date.isoformat(), today.isoformat()) >= 3

def lambda_login():
    # LambdaログインAPI用認証キー取得
    LAMBDA_API_KEY = get_secret_parameter('/hsano/notify_missing_schedule/lambda_api_key')

    url = f"{API_BASE_URL}/api/auth/login/lambda"

    response = requests.post(
        url,
        headers={"x-api-key": LAMBDA_API_KEY},
        data={
            "username": get_secret_parameter('/hsano/notify_missing_schedule/lambda_login_username'),
            "password": get_secret_parameter('/hsano/notify_missing_schedule/lambda_login_password')
        },
        verify="selfsigned.pem"
    )
    response.raise_for_status()
    data = response.json()
    # 返却されたアクセストークンを取り出す
    access_token = data.get("access_token")
    if not access_token:
        raise Exception("Failed to get access_token from login response")
    return access_token

def lambda_handler(event, context):
    today = date.today()
    first_day = date(today.year, today.month, 1)

    if not is_past_3_business_days(first_day):
        return {
            "statusCode": 200,
            "body": json.dumps({"message": "まだ3営業日経過していません"})
        }

    try:
        # 1. Lambda専用ログインしてトークン取得
        access_token = lambda_login()

        # 2. トークンを使って未登録ユーザ取得API呼び出し
        url = f"{API_BASE_URL}/api/users/missing-schedule"
        headers = {
            "Authorization": f"Bearer {access_token}"
        }
        params = {
            "year": today.year,
            "month": today.month
        }

        response = requests.get(
            url,
            headers=headers,
            params=params,
            verify="selfsigned.pem"
        )
        response.raise_for_status()
        users = response.json()

        # 3. 未登録ユーザへメール送信
        sent_count = 0
        for user in users:
            email = user.get("email")
            if email:
                send_email(
                    to=email,
                    subject="作業場所スケジュールが未登録です",
                    body=f"{today.month}月の作業場所スケジュールが登録されていません。至急ご対応ください。"
                )
                sent_count += 1

        return {
            "statusCode": 200,
            "body": json.dumps({"message": f"{sent_count}人にメールを送信しました"})
        }

    except requests.HTTPError as e:
        status_code = e.response.status_code if e.response else 500
        return {
            "statusCode": status_code,
            "body": json.dumps({"error": f"API呼び出し失敗: {str(e)}"})
        }
    except Exception as e:
        return {
            "statusCode": 500,
            "body": json.dumps({"error": f"予期しないエラー: {str(e)}"})
        }

def send_email(to: str, subject: str, body: str):
    ses = boto3.client("ses", region_name="us-east-1")
    try:
        response = ses.send_email(
            Source=os.getenv("SES_FROM_EMAIL"),
            Destination={"ToAddresses": [to]},
            Message={
                "Subject": {"Data": subject, "Charset": "UTF-8"},
                "Body": {"Text": {"Data": body, "Charset": "UTF-8"}}
            }
        )
        logger.info(f"Email sent to {to}: MessageId={response.get('MessageId')}")
    except ClientError as e:
        error_msg = e.response['Error']['Message']
        logger.warning(f"Email to {to} failed: {error_msg}")
    except Exception as e:
        logger.error(f"Unexpected error sending email to {to}: {e}")
