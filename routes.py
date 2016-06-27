from views.comment import CommentView
from views.user import UserView

comment_view = CommentView()
user_view = UserView()

routes = [
    ('GET', '/user/', user_view.list, 'user_list'),
    ('GET', '/user/{user_id}', user_view.get, 'user_details'),
    ('POST', '/user/', user_view.create, 'user_create'),
    ('DELETE', '/user/{user_id}', user_view.delete, 'user_delete'),

    ('GET', '/comment/', comment_view.list, 'comment_list'),
    ('GET', '/comment/{comment_id}', comment_view.get, 'comment_details'),
    ('POST', '/comment/', comment_view.create, 'comment_create'),
    ('DELETE', '/comment/{comment_id}', comment_view.delete, 'comment_delete'),
]
