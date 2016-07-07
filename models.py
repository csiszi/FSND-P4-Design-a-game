"""models.py - This file contains the class definitions for the Datastore
entities used by the Game. Because these classes are also regular Python
classes they can include methods (such as 'to_form' and 'new_game')."""

import random
from datetime import date
from protorpc import messages
from google.appengine.ext import ndb


class User(ndb.Model):
    """User profile"""
    name = ndb.StringProperty(required=True)
    email =ndb.StringProperty()


class Game(ndb.Model):
    """Game object"""
    attempts = ndb.IntegerProperty(required=True, default=0)
    game_over = ndb.BooleanProperty(required=True, default=False)
    user = ndb.KeyProperty(required=True, kind='User')
    history = ndb.DateProperty(repeated=True) # when he pushed his luck

    @classmethod
    def new_game(cls, user):
        """Creates and returns a new game"""
        # if max < min:
        #     raise ValueError('Maximum must be greater than minimum')
        game = Game(user=user,
                    attempts=0,
                    game_over=False)
        game.put()
        return game

    def to_form(self, message):
        """Returns a GameForm representation of the Game"""
        form = GameForm()
        form.urlsafe_key = self.key.urlsafe()
        form.user_name = self.user.get().name
        form.attempts = self.attempts
        form.game_over = self.game_over
        form.message = message
        return form

    def end_game(self):
        """Ends the game"""
        self.game_over = True
        # Reset the score of the user
        score = Score.query(Score.user==self.user).get()
        score.date = date.today()
        score.attempts = 0
        score.put()
        self.put()

    def cancel_game(self):
        """Cancel the game"""
        self.key.delete()

    def update_history(self):
        """Updates history"""
        self.history.append(date.today())
        self.put()


class Score(ndb.Model):
    """Score object"""
    user = ndb.KeyProperty(required=True, kind='User')
    date = ndb.DateProperty(required=True)
    attempts = ndb.IntegerProperty(required=True)

    def to_form(self):
        return ScoreForm(user_name=self.user.get().name, date=str(self.date), attempts=self.attempts)


class GameForm(messages.Message):
    """GameForm for outbound game state information"""
    urlsafe_key = messages.StringField(1, required=True)
    attempts = messages.IntegerField(2, required=True)
    game_over = messages.BooleanField(3, required=True)
    message = messages.StringField(4, required=True)
    user_name = messages.StringField(5, required=True)

class GameForms(messages.Message):
    """Return multiple GameForms"""
    items = messages.MessageField(GameForm, 1, repeated=True)


class ScoreForm(messages.Message):
    """ScoreForm for outbound Score information"""
    user_name = messages.StringField(1, required=True)
    date = messages.StringField(2, required=True)
    attempts = messages.IntegerField(3, required=True)


class ScoreForms(messages.Message):
    """Return multiple ScoreForms"""
    items = messages.MessageField(ScoreForm, 1, repeated=True)


class StringMessage(messages.Message):
    """StringMessage-- outbound (single) string message"""
    message = messages.StringField(1, required=True)

class HistoryForms(messages.Message):
    """Return history of game"""
    items = messages.MessageField(StringMessage, 1, repeated=True)
