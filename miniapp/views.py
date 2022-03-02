from django.shortcuts import render,redirect
from django.contrib.auth.models import User
from django.contrib.auth import login,logout,authenticate
from random import randrange
from miniproject.settings import EMAIL_HOST_USER
from django.core.mail import send_mail
from .models import FeedModel,Doctor
import pdfkit
import requests


global doc_name,doc_qual,doc_reg,doc_hname,pat_name,pat_age,pat_gender,prescription_number
doc_name,doc_qual,doc_reg,doc_hname,pat_name,pat_age,pat_gender,prescription_number = " "," "," "," "," "," "," "," "
global prescription, doc_info,pat_info
prescription , doc_info , pat_info = [],[],[]
global pred_dict
pred_dict=[]
global doc_sign
doc_sign = " "

def usignup(request):
	if request.method=="POST":
		un=request.POST.get("un")
		em=request.POST.get("em")
		try:
			usr=User.objects.get(username=un)
			return render(request,'usignup.html',{'msg':'username already taken'})
		except User.DoesNotExist:
			try:
				usr=User.objects.get(email=em)
				return render(request,'usignup.html',{'msg':'email already registered'})
			except User.DoesNotExist:
				text="1234567890abcdefghojglmnopqrstuvwxyz"
				pw=""
				for i in range(6):
					pw= pw + text[randrange(len(text))]
				
				send_mail("Welcome to Prescribe.ME","Your Password Is "+ pw,EMAIL_HOST_USER,[em])
				usr=User.objects.create_user(username=un,password=pw,email=em)
				usr.save()
				Doctor.objects.create(
				user=usr,
				fname=usr.username,
				lname=" ",
				hname=" ",
				reg=" ",
				qualification=" "
				)
				return redirect('ulogin')
	else:
		return render(request,'usignup.html')

def ulogin(request):
	if request.method=="POST":
		un=request.POST.get('un')
		pw=request.POST.get("pw")
		usr=authenticate(username=un,password=pw)
		if usr is None:
			return render(request,'ulogin.html',{'msg':'Invalid Credentials'})
		else:
			login(request,usr)
			return redirect('home')
	else:
		return render(request,'ulogin.html')

def ulogout(request):
	logout(request)
	return redirect('ulogin')

def uresetpassword(request):
	if request.method=="POST":
		un=request.POST.get("un")
		em=request.POST.get("em")
		try:
			usr=User.objects.get(username=un) and User.objects.get(email=em)
			text="1234567890abcdefghojglmnopqrstuvwxyz"
			pw=""
			for i in range(6):
				pw= pw + text[randrange(len(text))]
			send_mail("Welcome to Prescribe.ME","Your Password Is "+ pw,EMAIL_HOST_USER,[em])
			usr.set_password(pw)
			usr.save()
			return redirect('ulogin')
		except User.DoesNotExist:
			return render(request,'uresetpassword.html',{'msg':'Invalid Credentials'})

	else:
		return render(request,'uresetpassword.html')

def feedback(request):
	if request.method=="POST":
		e="asgroup693@gmail.com"
		n=request.POST.get("name")
		em=request.POST.get("email")
		feed=request.POST.get("message")
		ff=FeedModel.objects.create(name=n,em=em,message=feed)
		ff.save()
		send_mail("FeedBack From Your User","Name:"+n+"\nEmail:"+em+"\nFeedBack:"+feed,EMAIL_HOST_USER,[e])
		return render(request,'feedback.html',{'msg':'Thankyou For Your Feedback'})
	else:
		return render(request,'feedback.html')

def home(request):
	if request.user.is_authenticated:
		return render(request,'home.html')
	else:
		return redirect('ulogin')


def patient(request):
	if request.user.is_authenticated:
		user = request.user
		d = Doctor.objects.get(user=user)
		try:
			doc_name = d.fname + "  " + d.lname
			doc_qual = d.qualification
			doc_reg = d.reg
			doc_hname = d.hname
			doc_sign = d.sign.url
		except:
			return render(request,'home.html',{'msg':'Please Update your profile first'})
		if request.method == "POST":
			pfname = request.POST.get("pfname")
			plname = request.POST.get("plname")
			pat_name = pfname +" " + plname
			pat_gender = request.POST.get("gen")
			pat_age = request.POST.get("age")
			doc_info.clear()
			pat_info.clear()
			prescription.clear()
			doc_info.append(doc_name)
			doc_info.append(doc_qual)
			doc_info.append(doc_reg)
			doc_info.append(doc_hname)
			doc_info.append(doc_sign)
			pat_info.append(pat_name)
			pat_info.append(str(pat_age)+" "+pat_gender)
			print(doc_info[4])
			global date
			from datetime import datetime
			current = datetime.now()
			date = current.strftime('%d %m %Y')
			return render(request,'prescribe.html')
		else:
			return render(request,'patient.html')
	else:
		return redirect('ulogin')

def profile(request):
	if request.user.is_authenticated:
		user = request.user
		if request.method =="POST":
			fname=request.POST.get("fname")
			lname=request.POST.get("lname")
			qualification=request.POST.get("qualificaiton")
			reg = request.POST.get("regno")
			hname=request.POST.get("hname")
			sign=request.FILES.get("sign")
			d = Doctor.objects.get(user=user)
			d.fname=fname
			d.lname=lname
			d.sign=sign
			d.hname=hname
			d.qualification=qualification
			d.reg=reg
			d.save(update_fields=['fname','lname','sign','reg','hname','qualification'])
			return render(request,'profile.html',{'msg':'Profile Updated'})
		else:
			return render(request,'profile.html')

def prescribe(request):
	data = request.POST.get('prescribe')
	import speech_recognition as sr
	r = sr.Recognizer()
	with sr.Microphone() as source:
		audio = r.listen(source)
	try:
		output = " " + r.recognize_google(audio)
	except sr.UnknownValueError:
		output = "Could not Understand audio"
	except sr.RequestError as e:
		output = "Could not request results; {0}".format(e)
	print(output)
	generate_prescription(output)
	return render(request,'prescribe.html')
	
def generate_prescription(sent):
	data = sent
	wa="https://prescribe-me.herokuapp.com/web_predict/" + str(sent)
	res=requests.post(wa)
	print(res)
	data=res.json()
	slots = data["response"]

	if slots != 'non-prescriptive' :
		global Drug, INN, Freq, CMA, Dur, Gap, Qty, ROA, Cond, Fast,inn, rhy, freq, dur_val, dos_val, cond,drug,dur, qty, gap, max,cma, fasting, roa
		Drug, INN, Freq, CMA, Dur, Gap, Qty, ROA, Cond, Fast='','','','','','','','','',''
		inn, rhy, freq, dur_val, dos_val, cond=[], [], [], [], [], []
		drug=['','','','']
		dur, qty, gap, max=['',''], ['',''], ['',''], ['','']
		cma, fasting, roa='', '', ''
		for token in slots:
			slot=token['slot']
			value=token['value']
			if slot == 'INN':
				inn.append(value.strip())
			elif slot == 'Drug':
				drug[1]=value.strip()
			elif slot == 'd-dos-form':
				drug[0]=value.strip()
			elif slot == 'd-dos-val':
				drug[2]=value.strip()
			elif slot == 'd-dos-UP':
				drug[3]=value.strip()
			elif slot == 'rhythm-TDTE':
				rhy.append(value.strip())
			elif slot == 'rhythm-hour':
				rhy.append('at '+value.strip())
			elif slot == 'rhythm-perday':
				rhy.append(value.strip()+' daily')
			elif slot == 'rhythm-rec-val':
				rhy.append('every '+value.strip())
			elif slot == 'rhythm-rec-ut':
				rhy.append(value.strip())
			elif slot == 'freq-days':
				freq.append(value.strip())
			elif slot == 'freq-count':
				freq.append(value.strip())
			elif slot == 'freq-count-ut':
				freq.append(value.strip())
			elif slot == 'dur-val':
				dur_val.append(value.strip())
			elif slot == 'dur-UT':
				dur[1]=value.strip()
			elif slot == 'cma-event':
				CMA=value.strip()
			elif slot == 'dos-val':
				dos_val.append(value.strip())
			elif slot == 'dos-UF':
				qty[1]=value.strip()
			elif slot == 'dos-cond':
				cond.append(value.strip())
			elif slot == 'fasting':
				Fast=value.strip()
			elif slot == 'ROA':
				ROA=value.strip()
			elif slot == 'min-gap-val':
				gap[0]=value.strip()
			elif slot == 'min-gap-ut':
				gap[1]=value.strip()
			elif slot == 'max-unit-val':
				max[0]=value.strip()
			elif slot == 'max-unit-uf':
				max[1]=value.strip()
		INN=(" + ".join(inn)).strip()
		if drug[1] == '':
			drug[1] = inn[0]
			print(inn[0])
		Drug=(" ".join(drug)).strip()
		Rhy=(", ".join(rhy)).strip()
		Freq=(", ".join(freq)).strip()
		dur[0]=(", ".join(dur_val)).strip()
		Gap=(" ".join(gap)).strip()
		Dur=(" ".join(dur)).strip()
		qty[0]=(", ".join(dos_val)).strip()
		Qty=(" ".join(qty)).strip()
		Cond=((", ".join(cond)).strip())
		Max=(" ".join(max)).strip()
		if Rhy == '' and Freq != '':
			Freq=Freq
		elif Freq == '' and Rhy != '':
			Freq=Rhy
		elif Freq != '' and Rhy != '':
			Freq=Rhy+" & "+Freq
		Freq=Freq.strip()
		if Max == '' and Qty != '':
			Qty=Qty
		elif Qty == '' and Max != '':
			Qty='Max: '+Max
		elif Qty != '' and Max != '':
			Qty=Qty+" & Max: "+Max
		Qty=Qty.strip()
		if Cond !='':
			Cond = "if " + Cond
		if Gap !='':
			Gap = "Gap: " + Gap
		if Freq == '':
			Freq = '-'
		if CMA == '':
			CMA = '-'
		if Dur == '':
			Dur = '-'
		if Gap == '':
			Gap = '-'
		if Qty == '':
			Qty = '-'
		if ROA == '':
			ROA = '-'
		if Cond == '':
			Cond = '-'
		if Fast == '':
			Fast = '-'
		pred_dict=[Drug, INN, Freq, CMA, Dur, Gap, Qty, ROA, Cond, Fast]
		prescription.append(pred_dict)
	else:
		print(res)


def prescription_page(request):
	if request.user.is_authenticated:
		return render(request,'prescription_page.html',{'doc_info':doc_info,'pat_info':pat_info,'prescription':prescription,'date':date})
	else:
		return redirect('ulogin')

def send_prescription(request):
	if request.method=="POST":
		em = request.POST.get("pem")
		prescription_number=get_name()
		html=get_html(prescription_number,doc_info, pat_info, prescription)
		get_pdf(html,prescription_number)
		from datetime import datetime
		from email.mime.text import MIMEText
		from email.mime.multipart import MIMEMultipart
		from email.mime.base import MIMEBase
		from email import encoders
		sender_email = "me.prescribe@gmail.com"
		current=datetime.now()
		global time
		global date
		time=current.strftime("%H:%M:%S")
		date=current.strftime("%d/%m/%Y")
		sender_password = "prescription"

		filename="Prescription #"+prescription_number+".pdf"
		attachment=open(filename,'rb')
		part=MIMEBase('application','octet-stream')
		part.set_payload(attachment.read())
		encoders.encode_base64(part)
		part.add_header('Content-Disposition','attachment; filename= '+filename)

		msg = MIMEMultipart()
		msg['Subject'] = 'Prescription #' + prescription_number
		msg['From'] = sender_email 
		msg['To'] = em 
		msg.attach(MIMEText("Kindly Follow The Prescription Properly"))
		msg.attach(part)
		import smtplib
		with smtplib.SMTP_SSL('smtp.gmail.com', 465) as smtp:
			smtp.login(sender_email, sender_password)
			smtp.send_message(msg)
		return render(request,'send_prescription.html',{'msg':'Email send successfully'})
	else:
		return render(request,'send_prescription.html')

def get_name():
    from random import randrange
    alphabets="ABCDEFGHIJKLMNOPQRSTUVWXYZ"
    numbers="1234567890"
    prescription_number=""
    for i in range(8):
        if i<2 or i>5:
            prescription_number = prescription_number + alphabets[randrange(len(alphabets))]
        else:
            prescription_number = prescription_number + numbers[randrange(len(numbers))]
    return prescription_number

def get_html(prescription_number, doc_info, pat_info, prescription):
    html=['','','','','','']
    html[0], html[1]=generate_head(prescription_number)
    html[2], html[3], html[5]=generate_body(doc_info, pat_info, prescription_number)
    html[4]=generate_presc_table(prescription)
    return html

def get_pdf(html, prescription_number):
    file_name='Prescription #'+prescription_number
    print(file_name)
    html_file=open(file_name+'.html','w')
    html_file.writelines(html)
    html_file.close()
    import pdfkit, webbrowser, os
    config = pdfkit.configuration(wkhtmltopdf="C:\\Program Files\\wkhtmltopdf\\bin\\wkhtmltopdf.exe")
    pdfkit.from_file(file_name+'.html', file_name+'.pdf', configuration=config)
    filename='file:///'+os.getcwd()+'/'+file_name+'.html'
    filename='file:///'+os.getcwd()+'/'+file_name+'.pdf'
	
def generate_head(prescription_number):
    head="""<!DOCTYPE html>
    <html>
        <head>
            <title>
                Prescription #"""+prescription_number+"""
            </title>
            <link href='https://fonts.googleapis.com/css?family=Bayon' rel='stylesheet'>
            <link href='https://fonts.googleapis.com/css?family=Berkshire Swash' rel='stylesheet'>
            <link href='https://fonts.googleapis.com/css?family=Aldrich' rel='stylesheet'>
            <link href='https://fonts.googleapis.com/css?family=Baumans' rel='stylesheet'>
            <link href='https://fonts.googleapis.com/css?family=Cantata One' rel='stylesheet'>"""
    style="""
            <style>
                .drname{
                    font-family: 'Berkshire Swash';
                    font-size: 30px;
                }
                .infodr{
                    font-family: garamond, serif;
                    font-size: 15px;
                }
                .big_pat{
                    font-size: 25px;
                }
                .small_pat{
                    font-size: 15px;
                    font-weight: lighter;
                }
                .big_pat, .small_pat{
                    font-family: 'Bayon';
                    padding-left: 7%;
                }
                .Drug, .INN{
                    font-family: 'Aldrich';
                }
                .Drug{
                    font-size: 20px;
                }
                .INN{
                    font-size: 10px;
                    font-weight: lighter;
                    font-style: italic;
                }
                th{
                    font-family: 'Cantata One';
                    font-size: 15px;
                }
                .Freq, .CMA, .Dur, .Gap, .Qty, .ROA, .Cond, .Fast{
                    font-family: 'Baumans';
                    font-size: 15px;
                }
            </style>
        </head>"""
    return head, style

def generate_body(doc_info,pat_info,prescription_number):
    from datetime import datetime
    current=datetime.now()
    date=current.strftime('%d %m %Y')
    header="""<body>
        <table style="border: 0px;width: 100%;align-self: center;">
        <tr>
            <td rowspan="4" width="10%"><center><img src="http://127.0.0.1:8000/images/Caduceus.svg" style="height: 100px;"></center></td>
            <td class="drname" width="70%">Dr."""+doc_info[0]+"""</td>
        </tr>
        <tr>
            <td class="infodr">"""+doc_info[1]+"""</td>
        </tr>
        <tr>
            <td class="infodr">Registration No.: """+doc_info[2]+"""</td>
        </tr>
        <tr>
            <td class="infodr">"""+doc_info[3]+"""</td>
        </tr>
        </table>"""
    patient="""<hr color="#000080" width="85%">
        <table style="width: 100%;align-self: center;">
            <tr>
                <td class="big_pat">"""+pat_info[0]+"""</td>
                <td class="big_pat">"""+date+"""</td>
            </tr>
            <tr>
                <td class="small_pat">"""+pat_info[1]+"""</td>
                <td class="small_pat">#"""+prescription_number+"""</td>
            </tr>
        </table>"""
    footer="""<br><br><br><br><br><br><br>
        <div align="right" style="padding-right: 5%;"><img src="http://127.0.0.1:8000"""+doc_info[4]+"""" style="height: 100px;"></div>
        <div align="right" style="padding-right: 5%;">Dr. """+doc_info[0]+"""</div>
        <footer><center>Made using Prescribe.ME</center></footer>
        </body>
    </html>"""
    return header, patient, footer

def generate_presc_table(prescription):
    presc_table=''
    for pred_dict in prescription:
        presc_table=presc_table+"""<tr>
                <td>
                    <div class="Drug">"""+pred_dict[0]+"""</div>
                    <div class="INN">"""+pred_dict[1]+"""</div>
                </td>
                <td>
                    <center>
                        <div class="Freq">"""+pred_dict[2]+"""</div>
                        <hr color=#000080 width="70%">
                        <div class="CMA">"""+pred_dict[3]+"""</div>
                    </center>
                </td>
                <td>
                    <center>
                    <div class="Dur">"""+pred_dict[4]+"""</div>
                    <hr color=#000080 width="70%">
                    <div class="Gap">"""+pred_dict[5]+"""</div>
                    </center>
                </td>
                <td>
                    <center>
                        <div class="Qty">"""+pred_dict[6]+"""</div>
                    <hr color=#000080 width="70%">
                    <div class="ROA">"""+pred_dict[7]+"""</div>
                    </center>
                </td>
                <td>
                    <center>
                        <div class="Cond">"""+pred_dict[8]+"""</div>
                    <hr color=#000080 width="70%">
                    <div class="Fast">"""+pred_dict[9]+"""</div>
                    </center>
                </td>
            </tr>"""
    table="""<table border="1px" style="border-color: navy;" width=90% align="center">
            <tr>
                <th>Prescription</th>
                <th>Frequency/Rhythm</th>
                <th>Duration</th>
                <th>Quantity</th>
                <th>Condition</th>
            </tr>"""+presc_table+"""</table>"""
    return table



