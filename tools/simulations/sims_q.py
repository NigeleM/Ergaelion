"""Hand-written scored simulations for two popular classic games that had none. Appended with append_sims.py."""

from build_core import B, C, O, R, S

SIMS = [
    S("dictator-game", "Splitting a Gift",
      ["Classic game theory", "Society and groups"],
      "You have been given ten coins and must decide how many to share with a stranger who cannot refuse. The game shows how much people give when they have no obligation to.",
      [R("Round 1. You have ten coins and the stranger has no say. How many do you give?",
         O("Give half, five coins", 2, "An equal split is fair and shows care for the stranger.",
           C("The stranger reacts:", B(0.7, "They thank you and accept", 2, "The gift is received warmly."),
             B(0.3, "They feel you were stingy", 0, "The gift is accepted, but the relationship is cooler."))),
         O("Keep all ten", -2, "Keeping everything is allowed, but it leaves the stranger with nothing."),
         O("Give a token one coin", 0, "A small gift meets the rule but leaves the stranger little.")),
       R("Round 2. The stranger asks for a second gift. What do you do?",
         O("Give again, to keep the goodwill", 1, "A second gift shows the first was not a one-off."),
         O("Refuse, since there is no obligation", -1, "Refusing is allowed, but cuts off a relationship that could grow."),
         O("Ask them to match your gift", -2, "Asking for a match turns generosity into a bargain.")),
       ],
      4, 2, ("The gift is generous and the stranger is glad of it.", "The gift is modest and the relationship is polite.", "The gift is withheld and the stranger is left out.")),

    S("nash-bargaining-demands", "Dividing a Prize Fairly",
      ["Negotiation and fairness", "Classic game theory"],
      "You and a partner must divide a prize. You each name a demand, and if the demands add up to the whole prize, you both get them. If they add up to more, you both get nothing. Nash argued for a fair split.",
      [R("Round 1. Your partner has named a large share. What demand do you name?",
         O("Demand half of the prize", 2, "An equal demand is easy to agree and matches the fair split Nash described.",
           C("Your partner answers:", B(0.6, "They also demand half", 2, "Both demands fit, and you both get your share."),
             B(0.4, "They demand more than half", -2, "The demands exceed the prize, so you both get nothing."))),
         O("Demand most of the prize", -1, "A large demand risks the demands exceeding the prize, and both losing."),
         O("Demand a small share", 0, "A small demand is safe, but gives up the fair split.")),
       R("Round 2. The demands did not fit. How do you reach agreement?",
         O("Propose an equal split and stick to it", 2, "A clear equal split is the focal point that both can accept."),
         O("Insist on your larger share", -2, "Insisting leaves both with nothing again."),
         O("Ask a neutral person to suggest a split", 1, "A neutral suggestion can break the impasse, if both accept it.")),
       ],
      4, 2, ("You both get a fair share of the prize.", "You get a share, smaller than you wanted.", "The demands fail and you both get nothing.")),
]
