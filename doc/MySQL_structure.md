#Base

Location: location of a tournament
Tournament: name of the tournament
Surface: eg - clay/court/grass..
Size: number of players enrolled in tournament
Level: level of play
Date: date when tournament started (not match date)

Winner: winner
Winner_hand: L - left, R - right, U - universal
Winner_ioc: winner's country
Winner_rank: winner's ATP rank

Loser: loser
Loser_hand: L - left, R - right, U - universal
Loser_ioc: loser's country
Loser_rank: loser's ATP rank

Score: result as a string, eg - "7-5 6-1"
Best_of: either 3 or 5, depending on type of tournament
Round: F - finals, SF - semifinals, QF - quaterfinals, R16, R32...
Minutes: length of match

W_sv: how many serves winner made
W_1stIn: how many first serves of winner were in
W_ace: how many aces winner made
W_1stWon: how many first serves winner won
W_2ndWon: how many second serves winner won

L_sv: how many serves loser made
L_1stIn: how many first serves of loser were in
L_ace: how many aces loser made
L_1stWon: how many first serves loser won
L_2ndWon: how many second serves loser won

Winner_odds: odds for winner according to B365
Loser_odds: odds for loser according to B365

#Games

Winner_ID: id of the winenr
Loser_ID: id of the loser
Tournament_ID: id of the tournament
Score: result as a string, eg - "7-5 6-1"
Minutes: length of the match in minutes

#Players

Name: name of the player
Hand: his strongest hand (L - left, R - right, U - universal)
Country: player's country of birth

#Tournaments

Tournament: name of the tournament
Size: how many players entered tournament
Surface: surface on which tournament is played, as a string (eg. "Hard")
Date: starting date of the tournament
Best_of: how many sets to win (3 or 5)