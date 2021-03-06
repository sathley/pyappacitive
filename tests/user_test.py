__author__ = 'sathley'

from pyappacitive import AppacitiveUser, AppacitiveQuery, PropertyFilter, UserAuthError, ApplicationContext, AppacitiveError
import random
import datetime
from nose.tools import *


def get_random_string(number_of_characters=10):
    arr = [str(i) for i in range(number_of_characters)]
    random.shuffle(arr)
    return ''.join(arr)


def get_random_number(number_of_digits=10):
    arr = [str(i) for i in range(number_of_digits)]
    random.shuffle(arr)
    return int(''.join(arr))


def get_random_user():
    user = AppacitiveUser()
    user.username = 'jon'+get_random_string()
    user.password = 'test123!@#'
    user.email = 'jon' + get_random_string() + '@gmail.com'
    user.firstname = 'Jon'
    return user


def create_user_test():
    user = get_random_user()

    user.birthdate = datetime.date.today()
    user.location = '10.10,20.20'
    user.connectionid = 100
    user.isemailverified = True
    user.isenabled = True
    user.isonline = False
    user.lastname = 'Doe'
    user.phone = '555-444-333'
    user.secretquestion = 'Favourite programming language?'
    user.secretanswer = 'python'

    user.create()
    assert user.id > 0


def get_user_by_id_test():
    user = get_random_user()
    user.create()
    user.authenticate('test123!@#')
    user1 = AppacitiveUser.get_by_id(user.id)
    assert user.id == user1.id


def get_user_by_username_test():
    user = get_random_user()
    user.create()
    user.authenticate('test123!@#')
    resp = AppacitiveUser.get_by_username(user.username)
    assert user.id == resp.id


def get_logged_in_user_test():
    user = get_random_user()
    user.create()
    user.authenticate('test123!@#')
    resp = AppacitiveUser.get_logged_in_user()
    assert user.id == resp.id


def multiget_user_test():
    user_ids = []
    for i in range(2):
        user = get_random_user()
        user.create()
        user_ids.append(user.id)
    user.authenticate('test123!@#')

    users = AppacitiveUser.multi_get(user_ids)
    assert len(users) == 2

@raises(AppacitiveError)
def delete_user_test():
    user = get_random_user()
    user.create()
    user_id = user.id
    user.authenticate('test123!@#')
    user.delete()
    try:
        user1 = AppacitiveUser.get_by_id(user_id)
    except AppacitiveError as e:
        assert e.code == '404'
        raise e


def delete_by_username_test():
    user = get_random_user()
    user.create()
    user_id = user.id
    user.authenticate('test123!@#')
    AppacitiveUser.delete_by_username(user.username)
    try:
        user1 = AppacitiveUser.get_by_id(user_id)
    except AppacitiveError as e:
        assert e.code == '404'
        pass


def delete_logged_in_user_test():
    user = get_random_user()
    user.create()
    user_id = user.id
    user.authenticate('test123!@#')
    AppacitiveUser.delete_logged_in_user()
    try:
        user1 = AppacitiveUser.get_by_id(user_id)
    except AppacitiveError as e:
        assert e.code == '404'
        pass


def update_user_test():
    user = get_random_user()
    user.set_attribute('a1', 'v1')
    user.set_attribute('a2', 'v2')
    user.add_tags(['t1', 't2', 't3]'])
    user.birthdate = datetime.date.today()
    user.lastname = 'LN'

    user.create()
    user.authenticate('test123!@#')

    user.remove_tag('t1')
    user.add_tag('t4')
    user.remove_attribute('a1')
    user.set_attribute('a3', 'v3')
    user.lastname = 'LN2'

    user.update()
    assert user.tag_exists('t1') is False
    assert user.tag_exists('t4')
    assert user.get_attribute('a1') is None
    assert user.get_attribute('a3') == 'v3'
    assert user.lastname == 'LN2'


def update_password_user_test():
    user = get_random_user()
    user.create()
    user.authenticate('test123!@#')

    user.update_password('test123!@#', 'zaq1ZAQ!')
    user.authenticate('zaq1ZAQ!')
    try:
        user.authenticate('test123!@#')
    except AppacitiveError as e:
        assert e.code != '200'
        pass


def validate_session_user_test():
    user = get_random_user()
    user.create()
    user.authenticate('test123!@#')

    AppacitiveUser.validate_session()

    AppacitiveUser.invalidate_session()

    try:
        AppacitiveUser.validate_session()
    except AppacitiveError as e:
        pass


def checkin_user_test():
    user = get_random_user()
    user.create()
    user.authenticate('test123!@#')
    user.checkin(10.10, 20.20)
    user.fetch_latest()
    assert user.location == '10.1,20.2'


def find_user_test():
    user = get_random_user()
    user.create()
    user.authenticate('test123!@#')
    query = AppacitiveQuery()
    query.filter = PropertyFilter('firstname').is_equal_to('Jon')
    response_collection = AppacitiveUser.find(query)
    assert hasattr(response_collection,  'users')
    assert len(response_collection.users) > 0


def authenticate_user_test():
    user = get_random_user()
    user.create()
    token = AppacitiveUser.authenticate_user(user.username, 'test123!@#')
    assert token is not None
    assert token == ApplicationContext.get_logged_in_user_token()
    assert ApplicationContext.get_logged_in_user() is not None
    assert user.id == ApplicationContext.get_logged_in_user().id


@raises(UserAuthError)
def get_user_without_token_test():
    user = get_random_user()
    user.create()
    ApplicationContext.set_logged_in_user_token(None)
    user1 = AppacitiveUser.get_by_username(user.username)

@raises(AppacitiveError)
def get_user_with_invalid_token_test():
    user = get_random_user()
    user.create()
    user.authenticate('test123!@#')
    AppacitiveUser.invalidate_session()
    user1 = AppacitiveUser.get_by_username(user.username)


def link_fb_account_test():
    user = get_random_user()
    user.create()
    user.authenticate('test123!@#')
    user.link_facebook_account('''CAACEdEose0cBAEJfp0FSR94yUbh4NACAi1ZA6XBZAE7pNS0TtOPQGIRFLFNTPqk3aMlhT2EZA89dWM3wf9Nww3ZB24dOqSGmO2vy3z6LPs2Uho1b4QeBwiS8bjb4MkGLpJRT7TXXm4924cNnqq9BSWw91QxET3EnkPlZBfglelkmcybCKNGjnPw9nZCoskUxoZCWzCsukaM5wZDZD''')
    link = user.get_linked_account('facebook')
    assert link.username == 'sushant.athley'
    user.delete()


def link_twitter_account_test():
    user = get_random_user()
    user.create()
    user.authenticate('test123!@#')
    user.link_twitter_account('431607023-yb8pICZ1WKdu3qFqCDo5gWbRHwHs9Rg7FoV1PZt9', 'PIEx8WA5iQ4xicHzttMuq83ZZqOoEBUdQR4g1e4JAA', 'MRlvKD2KZaSnJzecYNK2RA', 'Pn0tKisq7EfIOkzUF568yGmHdc9bMTM9OPoT6a5wmRc')
    link = user.get_linked_account('twitter')
    assert link.username == 'SushantAthley'
    user.delete()


def get_all_links_test():
    user = get_random_user()
    user.create()
    user.authenticate('test123!@#')
    user.link_facebook_account('''CAACEdEose0cBAEJfp0FSR94yUbh4NACAi1ZA6XBZAE7pNS0TtOPQGIRFLFNTPqk3aMlhT2EZA89dWM3wf9Nww3ZB24dOqSGmO2vy3z6LPs2Uho1b4QeBwiS8bjb4MkGLpJRT7TXXm4924cNnqq9BSWw91QxET3EnkPlZBfglelkmcybCKNGjnPw9nZCoskUxoZCWzCsukaM5wZDZD''')
    user.link_twitter_account('431607023-yb8pICZ1WKdu3qFqCDo5gWbRHwHs9Rg7FoV1PZt9', 'PIEx8WA5iQ4xicHzttMuq83ZZqOoEBUdQR4g1e4JAA', 'MRlvKD2KZaSnJzecYNK2RA', 'Pn0tKisq7EfIOkzUF568yGmHdc9bMTM9OPoT6a5wmRc')
    links = user.get_all_linked_accounts()
    assert len(links) == 2
    user.delete()


def delink_account_test():
    user = get_random_user()
    user.create()
    user.authenticate('test123!@#')
    user.link_facebook_account('''CAACEdEose0cBAEJfp0FSR94yUbh4NACAi1ZA6XBZAE7pNS0TtOPQGIRFLFNTPqk3aMlhT2EZA89dWM3wf9Nww3ZB24dOqSGmO2vy3z6LPs2Uho1b4QeBwiS8bjb4MkGLpJRT7TXXm4924cNnqq9BSWw91QxET3EnkPlZBfglelkmcybCKNGjnPw9nZCoskUxoZCWzCsukaM5wZDZD''')
    user.delink_account('facebook')
    links = user.get_all_linked_accounts()
    assert len(links) == 0
    user.delete()
