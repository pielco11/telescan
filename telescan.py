import time, sys

from colorama import init, Fore, Style
from pyrogram import Client
from pyrogram.errors import BadRequest, FloodWait, UnknownError
from tqdm import tqdm

cFile = sys.argv[1]
app = Client(
    config_file=cFile,
    session_name=cFile.split('.')[0]
)

init(autoreset=True)
print(Fore.CYAN + """
████████╗███████╗██╗     ███████╗███████╗ ██████╗ █████╗ ███╗   ██╗
╚══██╔══╝██╔════╝██║     ██╔════╝██╔════╝██╔════╝██╔══██╗████╗  ██║
   ██║   █████╗  ██║     █████╗  ███████╗██║     ███████║██╔██╗ ██║
   ██║   ██╔══╝  ██║     ██╔══╝  ╚════██║██║     ██╔══██║██║╚██╗██║
   ██║   ███████╗███████╗███████╗███████║╚██████╗██║  ██║██║ ╚████║
   ╚═╝   ╚══════╝╚══════╝╚══════╝╚══════╝ ╚═════╝╚═╝  ╚═╝╚═╝  ╚═══╝
--- v1.0 by @Pielco11 ---
""")

def userID(userInput):
    if userInput.startswith("pn-") or userInput.startswith("u-"):
        return userInput.split('-')[1]
    elif userInput.startswith("id-"):
        return int(userInput.split('-')[1])
    else:
        print(Fore.RED + "[x] please specify a correct prefix (id-/u-/pn-). Exiting!" + Style.RESET_ALL)
        exit()


def chatListPrint(data):
    _id = data['id']
    _type = data['type']
    _title = data['title']
    _dc = data['dc_id']
    _username = data['username']
    print("[id] {} | Title: {} | Username: {} | Type: {} | DC: {}".format(_id, _title, _username, _type, _dc))

def singleUserLookup(user):
    _id = user['user']['id']
    _contact = user['user']['is_contact']
    _first_name = user['user']['first_name']
    _last_name = user['user']['last_name']
    _fullName = _first_name + " " + _last_name if _last_name else _first_name
    _username = user['user']['username']
    _phone = user['user']['phone_number']
    _dc = user['user']['dc_id']
    _lod = user['user']['last_online_date']
    if _lod:
        _lod = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(_lod))
    print("------\n|-> ID: {}\n|-> Contact: {}\n|-> Full name: {}\n|-> Username: {}\n|-> Phone: {}".format(_id, _contact, _fullName, _username, _phone))
    print("|-> DC: {}\n|-> Last Online Date: {}".format(_dc, _lod))



def chatMembersInfoPrint(data, total=True):
    if total:
        totalCount = len(data)
        print("[+++] Users count: {}".format(totalCount))
        userList = data
    else:
        userList = data
    print(Fore.GREEN + "[user infos]" + Style.RESET_ALL)
    for user in userList:
        singleUserLookup(user)
        _status = user['status']
        _date = None
        try:
            _date = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(user['joined_date']))
        except AttributeError:
            pass
        if user['invited_by']:
            _invitedByID = user['invited_by']['id']
            _invitedByUsername = user['invited_by']['username']
            _invitedByFirstName = user['invited_by']['first_name']
            _invitedBySurname = user['invited_by']['last_name']
            _invitedByFullName = _invitedByFirstName + " " + _invitedBySurname if _invitedBySurname else _invitedByFirstName
        else:
            _invitedByID = 0
            _invitedByFullName = ""
            _invitedByUsername = ""
        print("|-> Status: {}\n|-> Join date: {}".format(_status, _date))
        print("|-> Invited by id: {} | username: {} | Full name: {}".format(_invitedByID, _invitedByUsername, _invitedByFullName))


with app:
    while True:
        choice = input(Fore.CYAN + "[1] => chats lookup\n[2] => users lookup\n" + 
                                   "[3] => search user in groups\n" +
                                   "[anything else] => exit\n" +
                                   "[<] " + Style.RESET_ALL)
        if choice == "1":
            dialogs = app.get_dialogs()
            i = 0
            for d in dialogs:
                chatListPrint(d['chat'])
                i += 1
                if i >= 10:
                    cmd = input(Fore.CYAN + "[(c)/x]: " + Style.RESET_ALL)
                    i = 0
                    if cmd == 'x':
                        break
            chatID = input(Fore.CYAN + "[chat lookup]: " + Style.RESET_ALL)
            choice = input(Fore.CYAN + "[1] => Bulk search\n[2] => single user lookup\n[<]: " + Style.RESET_ALL)
            if choice == "1":
                limit = input(Fore.CYAN + "[# of users]: " + Style.RESET_ALL)
                members = app.get_chat_members(chat_id=int(chatID), limit=int(limit))
                chatMembersInfoPrint(members)
            elif choice == "2":
                userInput = input(Fore.CYAN + "[user-id (id)/username (u)/phone number (pn)]: " + Style.RESET_ALL)
                members = app.get_chat_member(chat_id=int(chatID), user_id=userID(userInput))
                chatMembersInfoPrint(members, total=False)
        elif choice == "2":
            userInput = input(Fore.CYAN + "[user-id (id)/username (u)/phone number (pn)]: " + Style.RESET_ALL)
            lookupResult = app.get_users([userID(userInput)])
            singleUserLookup({'user': lookupResult[0]})
        elif choice == "3":
            dialogs = app.get_dialogs()
            userInput = input(Fore.CYAN + "[user-id (id)/username (u)/phone number (pn)]: " + Style.RESET_ALL)
            for d in dialogs:
                if int(d['chat']['id']) < 0:
                    try:
                        members = app.get_chat_member(chat_id=int(d['chat']['id']), user_id=userID(userInput))
                        if members:
                            chatListPrint(d['chat'])
                    except BadRequest as e:
                        if not ("CHAT_ADMIN_REQUIRED" or "USER_NOT_PARTICIPANT" in str(e)):
                            print(str(e))
        else:
            print(Fore.RED + "\n[x] exiting!" +Style.RESET_ALL)
            app.stop()
            exit()
