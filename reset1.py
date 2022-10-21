from fastapi import FastAPI,HTTPException
import psycopg2
from psycopg2.extras import RealDictCursor
import json
import smtplib
import random,string


app = FastAPI()

while True:
    try:
        conn = psycopg2.connect(host = 'localhost',database = 'fastapi',user='postgres',password='Ajay@99044', cursor_factory= RealDictCursor)
        cursor = conn.cursor()
        print("database connection is successful")
        break
    except Exception as error:
        print("Connection to database Failed")
        print("error: ", error)

def random_no():
    x = "".join(random.choices(string.ascii_letters+string.digits,k=16))
    print(x)
    return x

def find_exist_user(email):
    cursor.execute(f"""SELECT email FROM  public."user" WHERE email = '{email}'""")
    posts = cursor.fetchall()
    posts_json = json.dumps(posts)
    print("---------------------------------------******",posts_json)
    return(posts_json)

def register_user(email,password,rand_no):
    cursor.execute(f"""INSERT INTO public."user" (email,password,random_no) VALUES ('{email}','{password}','{rand_no}');""")
    conn.commit()
    cursor.execute(f"""SELECT * FROM  public.user WHERE email = '{email}'""")
    posts = cursor.fetchone() 
    posts_json = json.dumps(posts)
    print("--------------------------------------------",posts_json)
    return posts_json


def user_login(email,password):
    cursor.execute(f"""SELECT * FROM  public."user" WHERE email = '{email}' AND password LIKE '{password}'""")
    posts = cursor.fetchall()
    if len(posts) == 0:
        return email_reset_link(email)
    else: 
        posts_json = json.dumps(posts)
        return(posts_json)



def find_email(email):
    cursor.execute(f"""SELECT * FROM  public.user WHERE email = '{email}' """)
    posts = cursor.fetchall()
    for p in posts:
        if p['email']==email:
            print("--------------",p['email'])
            return p['email']
        else:
            return 0

def update_pass(new_password,email):
    print("New and Email--------",new_password,email)
    update_qry = f" UPDATE public.user SET password = '{new_password}' WHERE email = '{email}' "
    cursor.execute(update_qry)
    conn.commit()
    cursor.execute(f"""SELECT * FROM  public.user WHERE email = '{email}'""")
    posts = cursor.fetchone()
    posts_json = json.dumps(posts)
    print("Updated Posts-------",posts_json)
    return(posts_json)


def reset_pass(email,random_no,new_password,confirm_password):
    cursor.execute(f"""SELECT random_no FROM  public.user WHERE email = '{email}'""")
    posts = cursor.fetchone()
    print("-----------------------po",posts['random_no'])
    if random_no == posts['random_no']:
        e_mail = find_email(email)
        print("-------------------",e_mail)
        if new_password==confirm_password:
            return update_pass(new_password,e_mail)
        else: 
            ("password does not match")
    else:
        return ("invalid user")



def email_reset_link(email):
    global g_email
    g_email = email
    
    cursor.execute(f"""SELECT random_no FROM  public."user" WHERE email = '{email}'""")
    posts = cursor.fetchone()
    print("-----------------------po",posts['random_no'])
    global ran_no
    ran_no = posts['random_no']
    url = r"http://127.0.0.1:8000/docs#/default/resetpassword_resetpassword_post/"
    
    TO = email
    SUBJECT = 'Your Link for Reset password'
    TEXT = 'Hello Subscriber, here is your link for reset password :'+url+email+'-'+posts['random_no'] 

    gmail_sender = 'ajay.p@rupiya.app'
    gmail_passwd = 'Ajay@99044'
    
    server = smtplib.SMTP('smtp.gmail.com', 587)
    server.ehlo()
    server.starttls()
    server.login(gmail_sender, gmail_passwd)

    BODY = '\r\n'.join(['To: %s' % TO,
                        'From: %s' % gmail_sender,
                        'Subject: %s' % SUBJECT,
                        '', TEXT])

    try:
        server.sendmail(gmail_sender, [TO], BODY)
        print('email sent')
    except:
        print('error sending mail')

    server.quit()
    return("Reset link has been sent successfully")

# --------------------------------------------------------------------------------------------------------------

@app.post("/register")
async def register(email,password):
    rand_no = random_no()
    result = find_email(email)
    print("Regi - User--------",result)
    if result == None:
        print("-------------------------------RESULT",result)
        return register_user(email,password,rand_no)
    else:
        raise HTTPException(status_code=404,detail="user already registered")

@app.post('/login')
def login(email,password):
    return user_login(email,password)

@app.post('/resetpassword')
def resetpassword(new_password,confirm_password):
    print("Globals-----------",g_email,ran_no)
    email = g_email
    random_no = ran_no
    return reset_pass(email,random_no,new_password,confirm_password)
