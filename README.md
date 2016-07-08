#Push your luck - FSND P4

## Set-Up Instructions:
1.  Update the value of application in app.yaml to the app ID you have registered
 in the App Engine admin console and would like to use to host your instance of this sample.
1.  Run the app with the devserver using dev_appserver.py DIR, and ensure it's
 running by visiting the API Explorer - by default localhost:8080/_ah/api/explorer.
1.  (Optional) Generate your client library(ies) with the endpoints tool.
 Deploy your application.



##Game Description & rules:
Push your luck is a game for the brave ones. You can have multiple open games,
but your score equals to your **last score** (and not your highest score!).
If you lost in your last game, your score will be 0 and you cannot push your
luck on that game anymore. If you win, the game's attempts increases by one and
your score will be the number of attempts in that game.
The high score returns the most attempts of the ended games, but the
**point is to be the first in the rankings**, which shows your **last** score
(and not your highest score!)

*Note*: If the ranking would return the highest score of a user (instead of the
last score), then the only strategy would be to push your luck whenever you can.
If you push your luck on a game where you have 5 points, you can find yourself
in the bottom of the list, without any games in your pocket. If you start a new,
you can see the bottom of the ranking as well, but you can be in the top again
with only one lucky push!

##Files Included:
 - api.py: Contains endpoints and game playing logic.
 - app.yaml: App configuration.
 - cron.yaml: Cronjob configuration.
 - main.py: Handler for taskqueue handler.
 - models.py: Entity and message definitions including helper methods.
 - utils.py: Helper function for retrieving ndb.Models by urlsafe Key string.

##Endpoints Included:
 - **create_user**
    - Path: 'user'
    - Method: POST
    - Parameters: user_name, email (optional)
    - Returns: Message confirming creation of the User.
    - Description: Creates a new User. user_name provided must be unique. Will
    raise a ConflictException if a User with that user_name already exists.

 - **new_game**
    - Path: 'game'
    - Method: POST
    - Parameters: user_name, min, max, attempts
    - Returns: GameForm with initial game state.
    - Description: Creates a new Game. user_name provided must correspond to an
    existing user - will raise a NotFoundException if not. Also adds a task to
    a task queue to update the average moves remaining for active games. Also
    creates Score entity for user.

 - **get_game**
    - Path: 'game/{urlsafe_game_key}'
    - Method: GET
    - Parameters: urlsafe_game_key
    - Returns: GameForm with current game state.
    - Description: Returns the current state of a game.

 - **push_luck**
    - Path: 'game/push_luck/{urlsafe_game_key}'
    - Method: PUT
    - Parameters: urlsafe_game_key
    - Returns: GameForm with new game state.
    - Description: Pushes your luck. If you won, increases
    attempts and sets new score. If you lost, ends game and sets score to 0.

 - **get_scores**
    - Path: 'scores'
    - Method: GET
    - Parameters: None
    - Returns: ScoreForms.
    - Description: Returns all Scores in the database (unordered).

- **get_high_scores**
    - Path: 'scores/high'
    - Method: GET
    - Parameters: None
    - Returns: GameForms.
    - Description: Returns the ended games ordered by attempts.

- **get_user_rankings**
    - Path: 'rankings'
    - Method: GET
    - Parameters: None
    - Returns: ScoreForms.
    - Description: Returns current scores of users ordered by attempts.

- **get_user_scores**
    - Path: 'scores/user/{user_name}'
    - Method: GET
    - Parameters: user_name
    - Returns: ScoreForms.
    - Description: Returns all Scores recorded by the provided player (unordered).
    Will raise a NotFoundException if the User does not exist.

- **get_user_games**
    - Path: 'games/user/{user_name}'
    - Method: GET
    - Parameters: user_name
    - Returns: GameForms
    - Description: Returns every games of a user.

- **cancel_game**
    - Path: 'games/cancel/{urlsafe_game_key}'
    - Method: DELETE
    - Parameters: urlsafe_game_key
    - Returns: StringMessage
    - Description: Cancel (delete) a game.

- **get_game_history**
    - Path: 'game/history/{urlsafe_game_key}'
    - Method: GET
    - Parameters: urlsafe_game_key
    - Returns: HistoryForms
    - Description: Returns the history of a game (the dates where the
    user pushed his/her luck)

- **get_average_attempts**
    - Path: 'games/average_attempts'
    - Method: GET
    - Parameters: None
    - Returns: StringMessage
    - Description: Returns the average attempt.

##Models Included:
 - **User**
    - Stores unique user_name and (optional) email address.

 - **Game**
    - Stores unique game states. Associated with User model via KeyProperty.

 - **Score**
    - Records completed games. Associated with Users model via KeyProperty.

##Forms Included:
 - **GameForm**
    - Representation of a Game's state (urlsafe_key, attempts_remaining,
    game_over flag, message, user_name).
 - **GameForms**
    - Multiple GameForm container.
 - **ScoreForm**
    - Representation of a completed game's Score (user_name, date, won flag,
    guesses).
 - **ScoreForms**
    - Multiple ScoreForm container.
 - **StringMessage**
    - General purpose String container.
 - **HistoryForms**
    - Returns multiple StringMessages with the history of a game.