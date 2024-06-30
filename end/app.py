# import caching as caching
from flask import Flask, jsonify, request
from sqlalchemy import text
from flask import send_file
from config import BaseConfig
from flask_sqlalchemy import SQLAlchemy
import auth
# from aliyunsms.sms_send import send_sms
import json
import random
import datetime
from redis import StrictRedis
import threading
import smtplib
from email.mime.text import MIMEText
from email.utils import formataddr
from email.header import Header
import schedule
import pymysql
import time
import os
import smtplib
from email.mime.text import MIMEText
from email.utils import formataddr
from email.header import Header
import schedule
import pymysql
import time
import io
# 创建redis对象
redis_store = StrictRedis(host=BaseConfig.REDIS_HOST, port=BaseConfig.REDIS_PORT, decode_responses=True)

# 跨域
from flask_cors import CORS
from flask_cors import cross_origin

app = Flask(__name__)

# 添加配置数据库
app.config.from_object(BaseConfig)
# 初始化拓展,app到数据库的ORM映射
db = SQLAlchemy(app)

# 检查数据库连接是否成功
with app.app_context():
    with db.engine.connect() as conn:
        rs = conn.execute(text("select 1"))
        print(rs.fetchone())


def fetch_and_send_emails():
    """Fetch data from the database and send emails."""
    with app.app_context():  # 推送应用程序上下文
        # 邮件配置信息
        smtp_server = 'smtp.qq.com'  # 邮箱服务器
        smtp_port = 465  # 邮箱端口
        smtp_ssl = True  # 启用ssl
        smtp_user = '1053095096@qq.com'
        smtp_password = 'rbsvplymgcvzbgaf'  # 邮箱授权码
        sender_email = '1053095096@qq.com'  # 发送者邮箱
        sender_name = 'Policy Manager'  # 发件人名字

        # 连接邮件服务器
        smtp_obj = smtplib.SMTP_SSL(smtp_server, smtp_port)
        smtp_obj.login(smtp_user, smtp_password)

        # 使用 SQLAlchemy 连接数据库并发送邮件
        try:
            results = db.session.execute(text(
                "SELECT PolicyID, Name, ProductName, NextPaymentdata, PaymentAmount, EmailAddress FROM PaymentDetails")).fetchall()
            for row in results:
                receivers = [row[5]]  # 接收者邮箱列表，使用索引访问 EmailAddress
                mail_content = f"Dear {row[1]}, your policyID: {row[0]} policy {row[2]} is about to be paid, the next payment date is at {row[3]}, and you need to pay ${row[4]}, please remember to pay on time."
                message = MIMEText(mail_content, 'plain', 'utf-8')
                message['From'] = formataddr((sender_name, sender_email))
                message['To'] = ', '.join(receivers)
                message['Subject'] = Header("Payment Reminder", 'utf-8')

                # 发送邮件
                try:
                    smtp_obj.sendmail(sender_email, receivers, message.as_string())
                    print(f"邮件发送成功至 {receivers}")
                except smtplib.SMTPException as e:
                    print(f"Error: 邮件发送失败至 {receivers}: {e}")
        finally:
            smtp_obj.quit()


def start_sending_emails():
    """Start the scheduled email sending."""
    # 定时任务，设定在每天09:15发送邮件
    schedule.every().day.at("19:54").do(fetch_and_send_emails)
    while True:
        schedule.run_pending()
        time.sleep(1)


def rem():
    """Main function to start the email sending process."""
    start_sending_emails()

# 用户登录
@app.route("/api/user/login", methods=["POST"])
@cross_origin()
def user_login():
    print(request.json)
    userortel = request.json.get("userortel").strip()
    password = request.json.get("password").strip()
    sql = ('select * ' \
           + 'from user ' \
           + 'where telephone = "{0}" and password = "{1}"').format(userortel, password)
    data = db.session.execute(text(sql)).first()
    print(data)
    if data != None:
        user = {'id': data[0], 'username': data[1], 'password': data[2], 'telephone': data[3]}
        # 生成token
        token = auth.encode_func(user)
        print(token)
        return jsonify({"code": 200, "msg": "登录成功", "token": token, "role": data[4]})
    else:
        return jsonify({"code": 1000, "msg": "用户名或密码错误"})


# 获取理赔记录
@app.route("/api/claimsrecord", methods=["GET"])
@cross_origin()
def get_claimsrecord():
    query = '''
    SELECT
        claimsrecord.ClaimNumber, 
        claimsrecord.PolicyID, 
        claimsrecord.ClaimAmount, 
        claimsrecord.ClaimTime, 
        claimsrecord.Reason
    FROM
        claimsrecord
    ORDER BY
        claimsrecord.ClaimTime DESC;
    '''
    data = db.session.execute(text(query)).fetchall()

    claimsrecord_data = []
    for row in data:
        claim_time_str = row[3].strftime('%Y-%m-%d %H:%M:%S') if row[3] else None
        claimsrecord = {
            'ClaimNumber': row[0],
            'PolicyID': row[1],
            'ClaimAmount': row[2],
            'ClaimTime': claim_time_str,
            'Reason': row[4]
        }
        claimsrecord_data.append(claimsrecord)

    return jsonify(status=200, tabledata=claimsrecord_data)

# 添加理赔记录
@app.route("/api/addclaim", methods=["POST"])
@cross_origin()
def user_addclaim():
    rq = request.json
    # 获取各个参数
    claim_number = rq.get("ClaimNumber")
    policy_id = rq.get("PolicyID")
    claim_amount = rq.get("ClaimAmount")
    claim_time = rq.get("ClaimTime")
    reason = rq.get("Reason")

    try:
        db.session.execute(text('''
            INSERT INTO claimsrecord (ClaimNumber, PolicyID, ClaimAmount, ClaimTime, Reason) 
            VALUES (:claim_number, :policy_id, :claim_amount, :claim_time, :reason)
        '''), {
            'claim_number': claim_number,
            'policy_id': policy_id,
            'claim_amount': claim_amount,
            'claim_time': claim_time,
            'reason': reason
        })
        db.session.commit()
        return jsonify(status=200, msg="成功添加")
    except Exception as e:
        db.session.rollback()
        print(f"Error: {e}")
        return jsonify(status=500, msg="添加失败")


# 删除理赔记录
@app.route("/api/claimsrecord", methods=["DELETE"])
@cross_origin()
def delete_claimsrecord():
    rq = request.json
    delete_id = rq.get('delete_id')

    try:
        db.session.execute(text('''
            DELETE FROM claimsrecord 
            WHERE ClaimNumber = :delete_id
        '''), {'delete_id': delete_id})
        db.session.commit()
        return jsonify(status=200, msg="成功删除")

    except Exception as e:
        db.session.rollback()
        print(f"Error: {e}")
        return jsonify(status=500, msg="删除失败")


# 获取家庭成员信息
@app.route("/api/family", methods=["GET"])
@cross_origin()
def get_familymember():
    query = '''
    SELECT
        familymember.IDNumber, 
        familymember.Name, 
        familymember.EmailAddress
    FROM
        familymember
    '''
    data = db.session.execute(text(query)).fetchall()

    familymember_data = []
    for row in data:
        familymember = {
            'IDNumber': row[0],
            'Name': row[1],
            'EmailAddress': row[2]
        }
        familymember_data.append(familymember)

    return jsonify(status=200, tabledata=familymember_data)

# 添加家庭成员信息
@app.route("/api/addfamilymember", methods=["POST"])
@cross_origin()
def add_familymember():
    rq = request.json
    # 获取各个参数
    id_number = rq.get("IDNumber")
    name = rq.get("Name")
    email_address = rq.get("EmailAddress")

    try:
        db.session.execute(text('''
            INSERT INTO familymember (IDNumber, Name, EmailAddress) 
            VALUES (:id_number, :name, :email_address)
        '''), {
            'id_number': id_number,
            'name': name,
            'email_address': email_address
        })
        db.session.commit()
        return jsonify(status=200, msg="成功添加")
    except Exception as e:
        db.session.rollback()
        print(f"Error: {e}")
        return jsonify(status=500, msg="添加失败")

# 删除家庭成员信息
@app.route("/api/family", methods=["DELETE"])
@cross_origin()
def delete_familymember():
    rq = request.json
    delete_id = rq.get('delete_id')

    try:
        db.session.execute(text('''
            DELETE FROM familymember 
            WHERE IDNumber = :delete_id
        '''), {'delete_id': delete_id})
        db.session.commit()
        return jsonify(status=200, msg="成功删除家庭成员信息")

    except Exception as e:
        db.session.rollback()
        print(f"Error: {e}")
        return jsonify(status=500, msg="删除家庭成员信息时发生错误")

# 获取家庭成员的保险统计信息
@app.route("/api/statistics", methods=["GET"])
@cross_origin()
def get_familymember_statistics():
    query_familymember = '''
    SELECT
        Name, 
        IDNumber, 
        TotalCost,
        TotalCoverage,
        PolicyCount
    FROM
        statistics    
    '''

    query_total = '''
    SELECT
        TotalCost,
        TotalCoverage,
        PolicyCount
    FROM
        total_statistics
    '''

    data_familymember = db.session.execute(text(query_familymember)).fetchall()
    data_total = db.session.execute(text(query_total)).fetchone()

    statistics_data = []
    for row in data_familymember:
        statistics = {
            'Name': row[0],
            'IDNumber': row[1],
            'TotalCost': row[2],
            'TotalCoverage': row[3],
            'PolicyCount': row[4]
        }
        statistics_data.append(statistics)

    # 添加总统计数据
    total_statistics = {
        'Name': '总计',
        'TotalCost': data_total[0],
        'TotalCoverage': data_total[1],
        'PolicyCount': data_total[2]
    }
    statistics_data.append(total_statistics)

    return jsonify(status=200, tabledata=statistics_data)


# 获取家庭成员的保险统计信息
@app.route("/api/draw", methods=["GET"])
@cross_origin()
def get_draw():
    query_familymember = '''
    SELECT
        Name, 
        IDNumber, 
        TotalCost,
        TotalCoverage,
        PolicyCount
    FROM
        statistics  
    '''

    query_total = '''
    SELECT
        TotalCost,
        TotalCoverage,
        PolicyCount
    FROM
        total_statistics
    '''

    data_familymember = db.session.execute(text(query_familymember)).fetchall()
    data_total = db.session.execute(text(query_total)).fetchone()

    statistics_data = []
    for row in data_familymember:
        statistics = {
            'Name': row[0],
            'IDNumber': row[1],
            'TotalCost': row[2],
            'TotalCoverage': row[3],
            'PolicyCount': row[4]
        }
        statistics_data.append(statistics)

    return jsonify(status=200, tabledata=statistics_data)


# 获取保单视图记录
@app.route("/api/insurance", methods=["GET"])
@cross_origin()
def get_policyview():
    query = '''
    SELECT
        PolicyID,
        Name,
        Insurer,
        Type,
        CoverageAmount,
        ProductName,
        NextPaymentData,
        PaymentAmount,
        status
    FROM
        policyview
    '''
    data = db.session.execute(text(query)).fetchall()

    policyview_data = []
    for row in data:
        next_payment_data_str = row[6].strftime('%Y-%m-%d %H:%M:%S') if row[6] else None
        policy = {
            'PolicyID': row[0],
            'Name': row[1],
            'Insurer': row[2],
            'Type': row[3],
            'CoverageAmount': row[4],
            'ProductName': row[5],
            'NextPaymentData': next_payment_data_str,
            'PaymentAmount': row[7],
            'status': row[8]
        }
        policyview_data.append(policy)

    return jsonify(status=200, tabledata=policyview_data)


# 添加保单
@app.route("/api/addpolicy", methods=["POST"])
@cross_origin()
def add_policy():
    rq = request.json
    # 获取用户输入的各个参数
    id_number = rq.get("IDNumber")
    insurer = rq.get("Insurer")
    product_name = rq.get("ProductName")
    policy_id = rq.get("PolicyID")
    effective_date = rq.get("EffectiveDate")
    first_payment_date = rq.get("FirstPaymentDate")
    card_last_digits = rq.get("CardLastDigits")
    policyholder = rq.get("Policyholder")

    try:
        # 查询familymember表获取家庭成员信息
        family_member = db.session.execute(text('''
            SELECT Name FROM familymember WHERE IDNumber = :id_number
        '''), {'id_number': id_number}).fetchone()

        if not family_member:
            return jsonify(status=404, msg="家庭成员未找到")

        # 查询insuranceproduct表获取保险产品信息
        insurance_product = db.session.execute(text('''
            SELECT PaymentAmount, CoverageAmount, NumberOfPayments FROM insuranceproduct
            WHERE Insurer = :insurer AND ProductName = :product_name
        '''), {'insurer': insurer, 'product_name': product_name}).fetchone()

        if not insurance_product:
            return jsonify(status=404, msg="保险产品未找到")

        # 向insurancepolicy表格插入数据
        db.session.execute(text('''
            INSERT INTO insurancepolicy (PolicyID, FamilyMemberID, Insurer, ProductName, EffectiveDate, FirstPaymentdata, BankAccountLastDigits, Policyholder)
            VALUES (:policy_id, :id_number, :insurer, :product_name, :effective_date, :first_payment_date, :card_last_digits, :policyholder)
        '''), {
            'policy_id': policy_id,
            'id_number': id_number,
            'insurer': insurer,
            'product_name': product_name,
            'effective_date': effective_date,
            'first_payment_date': first_payment_date,
            'card_last_digits': card_last_digits,
            'policyholder': policyholder
        })
        db.session.commit()
        return jsonify(status=200, msg="成功添加保单")

    except Exception as e:
        db.session.rollback()
        print(f"Error: {e}")
        return jsonify(status=500, msg="添加保单时发生错误")


# 删除保单
@app.route("/api/insurance", methods=["DELETE"])
@cross_origin()
def delete_policy():
    rq = request.json
    policy_id = rq.get("delete_id")
    try:
        # 删除insurance表格中的数据
        db.session.execute(text('''
            DELETE FROM insurancepolicy WHERE PolicyID = :policy_id
        '''), {'policy_id': policy_id})
        db.session.commit()
        return jsonify(status=200, msg="成功删除保单")

    except Exception as e:
        db.session.rollback()
        print(f"Error: {e}")
        return jsonify(status=500, msg="删除保单时发生错误")




# 获取保单详情及理赔记录
@app.route("/api/overview", methods=["GET"])
@cross_origin()
def get_completeinsuranceoverview():
    policy_id = request.args.get('policy_id')

    if not policy_id:
        return jsonify(status=400, msg="缺少保单号参数")

    # 查询保单基本信息（新增Policyholder）
    policy_query = '''
    SELECT
        Insurer,
        ProductName,
        Type,
        Name,
        IDNumber,
        BankAccountLastDigits,
        PolicyID,
        EffectiveDate,
        status,
        PaymentAmount,
        PaymentFrequency,
        Totalpaymenttime,
        Term,
        CoverageAmount,
        Policyholder
    FROM
        completeinsuranceoverview
    WHERE
        PolicyID = :policy_id
    '''
    policy_data = db.session.execute(text(policy_query), {'policy_id': policy_id}).fetchone()

    if not policy_data:
        return jsonify(status=404, msg="保单未找到")

    policy_detail = {
        'Insurer': policy_data[0],
        'ProductName': policy_data[1],
        'Type': policy_data[2],
        'Name': policy_data[3],
        'IDNumber': policy_data[4],
        'BankAccountLastDigits': policy_data[5],
        'PolicyID': policy_data[6],
        'EffectiveDate': policy_data[7].strftime('%Y-%m-%d') if policy_data[7] else None,
        'status': policy_data[8],
        'PaymentAmount': policy_data[9],
        'PaymentFrequency': policy_data[10],
        'Totalpaymenttime': policy_data[11],
        'Term': policy_data[12],
        'CoverageAmount': policy_data[13],
        'Policyholder': policy_data[14]
    }

    # 查询理赔记录
    claims_query = '''
    SELECT
        ClaimNumber,
        ClaimAmount,
        ClaimTime,
        Reason
    FROM
        completeinsuranceoverview
    WHERE
        PolicyID = :policy_id
    '''
    claims_data = db.session.execute(text(claims_query), {'policy_id': policy_id}).fetchall()

    claims_records = []
    for row in claims_data:
        claim_time_str = row[2].strftime('%Y-%m-%d %H:%M:%S') if row[2] else None
        claim = {
            'ClaimNumber': row[0],
            'ClaimAmount': row[1],
            'ClaimTime': claim_time_str,
            'Reason': row[3]
        }
        claims_records.append(claim)
    return jsonify(status=200, policyDetail=policy_detail, claimsRecords=claims_records)


# 获取最近保单
@app.route("/api/recentpolicy", methods=["GET"])
@cross_origin()
def get_recentpolicy():
    query = '''
    SELECT
        PolicyID,
        Name,
        Insurer,
        Type,
        CoverageAmount,
        ProductName,
        NextPaymentData,
        PaymentAmount,
        status
    FROM
        recentpolicy
    '''
    data = db.session.execute(text(query)).fetchall()

    recentpolicy_data = []
    for row in data:
        next_payment_data_str = row[6].strftime('%Y-%m-%d') if row[6] else None
        policy = {
            'PolicyID': row[0],
            'Name': row[1],
            'Insurer': row[2],
            'Type': row[3],
            'CoverageAmount': row[4],
            'ProductName': row[5],
            'NextPaymentData': next_payment_data_str,
            'PaymentAmount': row[7],
            'status': row[8]
        }
        recentpolicy_data.append(policy)

    return jsonify(status=200, tabledata=recentpolicy_data)

# 获取保单信息
@app.route("/api/getpolicy", methods=["GET"])
@cross_origin()
def get_policy():
    policy_id = request.args.get('policy_id')
    try:
        # 查询insurancepolicy表获取保单信息
        policy_data = db.session.execute(text('''
            SELECT FamilyMemberID, Insurer, ProductName, PolicyID, EffectiveDate, FirstPaymentdata, BankAccountLastDigits, Policyholder
            FROM insurancepolicy WHERE PolicyID = :policy_id
        '''), {'policy_id': policy_id}).fetchone()

        if not policy_data:
            return jsonify(status=404, msg="保单未找到")

        policy_detail = {
            'IDNumber': policy_data[0],
            'Insurer': policy_data[1],
            'ProductName': policy_data[2],
            'PolicyID': policy_data[3],
            'EffectiveDate': policy_data[4].strftime('%Y-%m-%d') if policy_data[4] else None,
            'FirstPaymentdata': policy_data[5].strftime('%Y-%m-%d') if policy_data[5] else None,
            'BankAccountLastDigits': policy_data[6],
            'Policyholder': policy_data[7]
        }

        return jsonify(status=200, tabledata=policy_detail)

    except Exception as e:
        print(f"Error: {e}")
        return jsonify(status=500, msg="获取保单信息时发生错误")

# 修改保单
@app.route("/api/updatepolicy", methods=["POST"])
@cross_origin()
def update_policy():
    rq = request.json
    # 获取用户输入的各个参数
    id_number = rq.get("IDNumber")
    insurer = rq.get("Insurer")
    product_name = rq.get("ProductName")
    policy_id = rq.get("PolicyID")
    effective_date = rq.get("EffectiveDate")
    first_payment_date = rq.get("FirstPaymentDate")
    card_last_digits = rq.get("CardLastDigits")
    policyholder = rq.get("Policyholder")
    old = rq.get("old")

    try:
        # 查询familymember表获取家庭成员信息
        family_member = db.session.execute(text('''
            SELECT Name FROM familymember WHERE IDNumber = :id_number
        '''), {'id_number': id_number}).fetchone()

        if not family_member:
            return jsonify(status=404, msg="家庭成员未找到")

        # 查询insuranceproduct表获取保险产品信息
        insurance_product = db.session.execute(text('''
            SELECT PaymentAmount, CoverageAmount, NumberOfPayments FROM insuranceproduct
            WHERE Insurer = :insurer AND ProductName = :product_name
        '''), {'insurer': insurer, 'product_name': product_name}).fetchone()

        if not insurance_product:
            return jsonify(status=404, msg="保险产品未找到")

        # 更新insurancepolicy表格中的数据
        db.session.execute(text('''
            UPDATE insurancepolicy
            SET PolicyID = :policy_id, FamilyMemberID = :id_number, Insurer = :insurer, ProductName = :product_name,
                EffectiveDate = :effective_date, FirstPaymentdata = :first_payment_date, BankAccountLastDigits = :card_last_digits,
                Policyholder = :policyholder
            WHERE PolicyID = :old
        '''), {
            'id_number': id_number,
            'insurer': insurer,
            'product_name': product_name,
            'effective_date': effective_date,
            'first_payment_date': first_payment_date,
            'card_last_digits': card_last_digits,
            'policyholder': policyholder,
            'policy_id': policy_id,
            'old': old
        })
        db.session.commit()
        return jsonify(status=200, msg="成功更新保单")

    except Exception as e:
        db.session.rollback()
        print(f"Error: {e}")
        return jsonify(status=500, msg="更新保单时发生错误")

# 上传 PDF 文件并存储在数据库中
@app.route("/api/pdf", methods=["POST"])
@cross_origin()
def upload_pdf():
    rq = request.json
    pdf_path = rq.get("path")
    policy_id = rq.get("policy_id")

    if not pdf_path or not policy_id:
        return jsonify(status=400, msg="缺少路径或保单号参数")

    try:
        # 检查文件是否存在
        if not os.path.exists(pdf_path):
            return jsonify(status=404, msg="PDF文件未找到")

        # 读取 PDF 文件的二进制内容
        with open(pdf_path, "rb") as pdf_file:
            pdf_content = pdf_file.read()

        # 输出 PDF 文件的二进制内容的前100字节用于调试
        print(f"PDF content (first 100 bytes): {pdf_content[:100]}")

        # 将 PDF 文件的二进制内容存储在数据库中
        db.session.execute(text('''
            UPDATE insurancepolicy
            SET PDFContent = :pdf_content
            WHERE PolicyID = :policy_id
        '''), {
            'pdf_content': pdf_content,
            'policy_id': policy_id
        })
        db.session.commit()
        return jsonify(status=200, msg="成功上传PDF文件")

    except Exception as e:
        db.session.rollback()
        print(f"Error: {e}")
        return jsonify(status=500, msg="上传 PDF 文件时发生错误")

# 下载 PDF 文件
@app.route("/api/downloadpdf", methods=["GET"])
@cross_origin()
def download_pdf():
    policy_id = request.args.get('policy_id')
    print(f"Received policy_id: {policy_id}")  # 打印接收到的参数

    if not policy_id:
        return jsonify(status=400, msg="缺少保单号参数")

    try:
        file_data = db.session.execute(text('''
            SELECT PDFContent FROM insurancepolicy WHERE PolicyID = :policy_id
        '''), {'policy_id': policy_id}).fetchone()

        if not file_data:
            return jsonify(status=404, msg="保单未找到")

        pdf_content = file_data[0]

        if pdf_content is None:
            return jsonify(status=404, msg="未上传PDF文件")

        return send_file(
            io.BytesIO(pdf_content),
            download_name=f'{policy_id}.pdf',
            as_attachment=True,
            mimetype='application/pdf'
        )

    except Exception as e:
        print(f"Error: {e}")
        return jsonify(status=500, msg="下载 PDF 文件时发生错误")

# 推荐
@app.route("/api/recommended", methods=["GET"])
@cross_origin()
def get_recommended_insurance():
    query = '''
    SELECT
        Name,
        Insurer,
        ProductName,
        Type,
        Term
    FROM
        recommendedinterface
    '''
    data = db.session.execute(text(query)).fetchall()
    recommended_data = []
    for row in data:
        recommended_policy = {
            'Name': row[0],
            'Insurer': row[1],
            'ProductName': row[2],
            'Type': row[3],
            'Term': row[4]
        }
        recommended_data.append(recommended_policy)

    return jsonify(status=200, tabledata=recommended_data)


if __name__ == '__main__':
    rem_thread = threading.Thread(target=rem)
    rem_thread.start()
    app.run(debug=True, host='127.0.0.1', port=5000)
    # 开启了debug模式
