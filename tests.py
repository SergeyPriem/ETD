#from pony_users import get_appl_emails, get_registered_emails, create_user, get_settings,check_user, get_appl_user_data
from projects import get_sets, get_tasks
#import streamlit as st

#print(get_appl_emails())
#print(type(get_registered_emails()))

# print(create_user('Serhii', 'Pryiemshyi', '+998909598030', '+998909598030',
#                   'sergey.priemshiy@uzliti-en-com', "Exdiibt3"))

# print(get_settings('sergey.priemshiy@uzliti-en-com'))

#print(get_appl_user_data('sergey.priemshiy@uzliti-en-com'))

# print(add_in_to_db('1', 'DD', "In", "Telecom", date.today(), "description", r"\\uz-fs\Uzle\Work\Отдел ССБ\АНГЛ",
#                    "source", datetime.now(), datetime.now(), 'comment'))

#add_in_to_db(project, single_set, stage, direction, speciality[0], date, description, link, source, comments)


# print(create_sod(proj_short='BGPP', set_name="Прачечная", stage='Detail Design', status='0%',
#                  set_start_date=date(2023, 5, 12)))

# print(get_sets_names('BGPP'))

# print(create_project('M-55', 'БГПЗ. Инфраструктура 55', 'sgcoc', 'Сим Александр', 'sergey.priemshiy@uzliti-en.com', '44', '', '', '', '', ''))

print(get_tasks('sergey.priemshiy@uzliti-en-com'))