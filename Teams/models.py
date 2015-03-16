from django.db import models
from django.db.models import Q
from django.utils.functional import cached_property
from datetime import datetime


class Team(models.Model):
    full_name = models.CharField(max_length=64)
    short_name = models.CharField(max_length=5)
    logo = models.ImageField(default='team_logos/default.png', upload_to='team_logos')
    description = models.TextField(max_length=1024, blank=True, default='')

    @cached_property
    def count_players(self):
        """Returns the number of players on the team"""
        from Players.models import Player

        return Player.objects.filter(team=self).count()

    @cached_property
    def captain(self):
        """Returns the captain of the team"""
        from Players.models import Player

        return Player.objects.get(Q(team=self), Q(is_captain=True))

    def team_players(self):
        """Returns the list of players in the team"""
        from Players.models import Player

        team_players = list()
        for player in Player.objects.filter(team=self):
            team_players.append(player)

        return team_players

    def team_average_leader(self, stat):
        # TODO: Poprawić z sortowaniem po stronie bazy (.extra)
        # https://docs.djangoproject.com/en/dev/ref/models/querysets/#django.db.models.query.QuerySet.extra
        """Returns the player (and value) with best average in given statistic"""
        from Players.models import Player

        top_player = Player.objects.filter(team=self)[0]
        top_value = top_player.cat_average(stat)

        for player in Player.objects.filter(team=self):
            value = player.cat_average(stat)
            if value > top_value:
                top_player = player
                top_value = value

        return top_player, top_value

    def next_games(self, n):
        """Creates a list of `n` previous (if `n` is negative) or next (if `n` is positive) games of a team."""
        from Games.models import Game

        today = datetime.today().date()
        games_list = list()

        if n > 0:
            games = Game.objects.filter(Q(home_team=self) | Q(away_team=self)).filter(date__gte=today).order_by('date')[:n]
        elif n < 0:
            games = Game.objects.filter(Q(home_team=self) | Q(away_team=self)).filter(date__lt=today).order_by('-date')[:-n]
        else:
            raise Exception('Argument can\'t be 0')

        for game in games:
            games_list.append(game)

        return games_list

    def get_absolute_url(self):
        from django.core.urlresolvers import reverse

        return reverse('team_page', args=[str(self.full_name.replace(' ', '_'))])

    def __str__(self):
        """Example: Chicago Bulls (CHI)"""
        return '{full_name} ({short_name})'.format(full_name=self.full_name,
                                                   short_name=self.short_name)