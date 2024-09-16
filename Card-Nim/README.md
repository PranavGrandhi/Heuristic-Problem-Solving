# Heuristic-Problem-Solving

You and your opponent are presented with some number of stones s that I will announce the day of the competition. The winner removes the last stone(s). Each player has a set of cards with numbers 1 through k (another number that I will provide but whose sum exceeds s). The number s won't exceed 500 and k of 200. So, if s = 100 cards and k = 25, then each player will have one 1, one 2, ... one 25. The first player chooses a card and removes exactly that number of stones. The card then disappears from the first player's hand. Similarly for the second player.

Play continues until on his or her turn, a player either (i) chooses a card whose number exactly matches the number of stones remaining in which case that player wins or (ii) chooses a card that exceeds the number of stones remaining in which case that player loses (if all the player's cards exceed the number of stones remaining, the player loses automatically).

Here is an example to get you started. Suppose there are 5 stones left and each of the two players Bob and Alice has three cards with 1, 2, and 3, respectively. Alice goes first. Who wins?

Solution: Bob wins. If Alice removes 2 or 3, then Bob can win immediately with 3 or 2 respectively. So, Alice removes 1. Now Bob removes 3, leaving 1. Now Alice has only cards with numbers greater than 1 so she loses.

Hint: dynamic programming is a good idea, but you must keep track of which player's turn it is, how many stones are left, and which sets of cards are remaining in each player's hand.