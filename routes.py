"""Main router"""

from views.comment import CommentView
from views.user import UserView
from views.entity import EntityView

comment_view = CommentView()
user_view = UserView()
entity_view = EntityView()

routes = [
    ('GET', '/user/', user_view.get_all, 'user_list'),
    ('GET', '/user/{user_id}', user_view.get, 'user_details'),
    ('POST', '/user/', user_view.create, 'user_create'),
    ('DELETE', '/user/{user_id}', user_view.delete, 'user_delete'),

    ('GET', '/entity/', entity_view.get_all, 'entity_list'),
    ('GET', '/entity/{entity_id}', entity_view.get, 'entity_details'),
    ('POST', '/entity/', entity_view.create, 'entity_create'),
    ('DELETE', '/entity/{entity_id}', entity_view.delete, 'entity_delete'),

    ('GET', '/comment/', comment_view.get_all, 'comment_list'),
    ('GET', '/comment/{comment_id}', comment_view.get, 'comment_details'),
    ('POST', '/comment/', comment_view.create, 'comment_create'),
    ('DELETE', '/comment/{comment_id}', comment_view.delete, 'comment_delete'),
]
