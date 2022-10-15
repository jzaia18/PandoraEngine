from string import ascii_lowercase, digits

alphanumeric = ascii_lowercase + digits


class GameStatus:
    STOPPED = 0
    PAUSED = 1
    RUNNING = 2
    ERROR = 3


class Player:
    def __init__(self, name, user_id):
        self.name = name
        self.user_id = user_id
        self.score = 0
        self.isWinner = False


class Game:
    def __init__(self, name, max_players, question_banks, widgets):
        self.name = name
        self.max_players = max_players
        self.players = set()
        self.question_banks = question_banks
        self.widgets = widgets
        self.status = GameStatus.STOPPED

    def add_player(self, player: Player):
        self.players.add(player)

    def remove_player(self, player: Player):
        if player in self.players:
            self.players.remove(player)

        else:
            print("Player " + player.name + " is not in this game")

    def declare_winner(self):
        winner = None
        for player in self.players:
            if not winner:
                winner = player

            if winner['score'] < player['score']:
                winner = player

        winner.isWinner = True
        return winner




