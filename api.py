# -*- coding: utf-8 -*-`
"""api.py - Contains primarily with communication to/from the API's users."""


import endpoints
from protorpc import remote, messages
from datetime import datetime
from google.appengine.api import memcache
from google.appengine.api import taskqueue

from models import User, Game, Score
from models import (StringMessage, GameForm, GameForms,
                    ScoreForm, ScoreForms, HistoryForms)
from utils import get_by_urlsafe

GET_GAME_REQUEST = endpoints.ResourceContainer(
        urlsafe_game_key=messages.StringField(1),)
USER_REQUEST = endpoints.ResourceContainer(user_name=messages.StringField(1),
                                           email=messages.StringField(2))
HIGH_SCORES_REQUEST = endpoints.ResourceContainer(
        number_of_results=messages.IntegerField(1))

MEMCACHE_AVG_SCORE = 'AVG_SCORE'


@endpoints.api(name='push_your_luck', version='v1')
class PushYourLuckApi(remote.Service):
    """Game API"""
    @endpoints.method(request_message=USER_REQUEST,
                      response_message=StringMessage,
                      path='user',
                      name='create_user',
                      http_method='POST')
    def create_user(self, request):
        """Create a User. Requires a unique username"""
        if User.query(User.name == request.user_name).get():
            raise endpoints.ConflictException(
                    'A User with that name already exists!')
        message = User.new_user(user_name=request.user_name,
                                email=request.email)
        return StringMessage(message=message)

    @endpoints.method(request_message=USER_REQUEST,
                      response_message=GameForm,
                      path='game',
                      name='new_game',
                      http_method='POST')
    def new_game(self, request):
        """Creates new game"""
        user = User.query(User.name == request.user_name).get()
        if not user:
            raise endpoints.NotFoundException(
                    'A User with that name does not exist!')

        game = Game.new_game(user.key)

        # Use a task queue to update the average attempts remaining.
        # This operation is not needed to complete the creation of a new game
        # so it is performed out of sequence.
        taskqueue.add(url='/tasks/cache_average_attempts')
        return game.to_form('Good luck playing Push your luck!')

    @endpoints.method(request_message=GET_GAME_REQUEST,
                      response_message=GameForm,
                      path='game/{urlsafe_game_key}',
                      name='get_game',
                      http_method='GET')
    def get_game(self, request):
        """Return the current game state."""
        game = get_by_urlsafe(request.urlsafe_game_key, Game)
        if game:
            return game.to_form('Time to push your luck!')
        else:
            raise endpoints.NotFoundException('Game not found!')

    @endpoints.method(request_message=GET_GAME_REQUEST,
                      response_message=GameForm,
                      path='game/push_luck/{urlsafe_game_key}',
                      name='push_luck',
                      http_method='PUT')
    def push_luck(self, request):
        """Push the luck. Returns a game state with message"""
        game = get_by_urlsafe(request.urlsafe_game_key, Game)
        print('PUSHLUCK')
        print(game)
        if not game:
            raise endpoints.NotFoundException('Game not found')
        if game.game_over:
            raise endpoints.ForbiddenException(
                'Illegal action: Game is already over.')
        if game.key.parent().get().can_push():
            return game.push_luck()
        else:
            raise endpoints.ForbiddenException(
                'You cannot push your luck yet.')

    @endpoints.method(response_message=ScoreForms,
                      path='scores',
                      name='get_scores',
                      http_method='GET')
    def get_scores(self, request):
        """Return all scores"""
        return ScoreForms(items=[score.to_form() for score in Score.query()])

    @endpoints.method(request_message=HIGH_SCORES_REQUEST,
                      response_message=GameForms,
                      path='scores/high',
                      name='get_high_scores',
                      http_method='GET')
    def get_high_scores(self, request):
        """Return ended games"""
        games = Game.query(Game.game_over == True).order(-Game.attempts)
        if request.number_of_results:
            fetched = games.fetch(request.number_of_results)
        else:
            fetched = games.fetch()
        return GameForms(items=[game.to_form('') for game in fetched])

    @endpoints.method(response_message=ScoreForms,
                      path='rankings',
                      name='get_user_rankings',
                      http_method='GET')
    def get_user_rankings(self, request):
        """Return the current rankings.
           Each player can have multiple games,
           but only the last score counts!"""
        scores = Score.query().order(-Score.attempts)
        return ScoreForms(items=[score.to_form() for score in scores])

    @endpoints.method(request_message=USER_REQUEST,
                      response_message=ScoreForm,
                      path='scores/user/{user_name}',
                      name='get_user_scores',
                      http_method='GET')
    def get_user_score(self, request):
        """Returns an individual User's latest score"""
        user = User.query(User.name == request.user_name).get()
        if not user:
            raise endpoints.NotFoundException(
                    'A User with that name does not exist!')
        score = Score.query(ancestor=user.key).get()
        return score.to_form()

    @endpoints.method(request_message=USER_REQUEST,
                      response_message=GameForms,
                      path='games/user/{user_name}',
                      name='get_user_games',
                      http_method='GET')
    def get_user_games(self, request):
        """Returns an individual User's games"""
        user = User.query(User.name == request.user_name).get()
        if not user:
            raise endpoints.NotFoundException(
                    'A User with that name does not exist!')
        games = Game.query(Game.game_over == False, ancestor=user.key)
        return GameForms(items=[game.to_form('') for game in games])

    @endpoints.method(request_message=GET_GAME_REQUEST,
                      response_message=StringMessage,
                      path='game/cancel/{urlsafe_game_key}',
                      name='cancel_game',
                      http_method='DELETE')
    def cancel_game(self, request):
        """Cancel a game."""
        game = get_by_urlsafe(request.urlsafe_game_key, Game)
        if not game:
            raise endpoints.NotFoundException('Game not found!')
        if game.game_over:
            raise endpoints.ForbiddenException('Game already ended')
        game.cancel_game()
        return StringMessage(message='No idea why you would do this...')

    @endpoints.method(request_message=GET_GAME_REQUEST,
                      response_message=HistoryForms,
                      path='game/history/{urlsafe_game_key}',
                      name='get_game_history',
                      http_method='GET')
    def get_game_history(self, request):
        """Return a game's history"""
        game = get_by_urlsafe(request.urlsafe_game_key, Game)
        if not game:
            raise endpoints.NotFoundException('Game not found!')
        if game:
            return HistoryForms(items=[
                StringMessage(message=history.strftime("%B %d, %Y"))
                for history in game.history])
        else:
            raise endpoints.NotFoundException('Game not found!')

    @endpoints.method(response_message=StringMessage,
                      path='games/average_attempts',
                      name='get_average_attempts_remaining',
                      http_method='GET')
    def get_average_attempts(self, request):
        """Get the cached average moves remaining"""
        return StringMessage(message=memcache.get(MEMCACHE_AVG_SCORE) or '')

    @staticmethod
    def _cache_average_attempts():
        """Populates memcache with the average scores"""
        games = Game.query(Game.game_over == True).fetch()
        if games:
            count = len(games)
            total_attempts = sum([game.attempts for game in games])
            average = float(total_attempts)/count
            memcache.set(MEMCACHE_AVG_SCORE,
                         'The average streak score is {:.2f}'.format(average))


api = endpoints.api_server([PushYourLuckApi])
