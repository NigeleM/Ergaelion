# Matching Pennies

Two players show heads or tails at the same time. One wins when the coins match, the other when they differ. No fixed choice is safe, so the only stable play is to randomise.

## Traits and what each one means
- players = two: You and one counterpart. Name them in the title, for example 'me and my landlord'.
- timing = simultaneous: Everyone chooses without seeing the others' choices. Write each side's options down before anyone reveals anything.
- interaction = one-shot: The situation happens once. Do not plan on future reciprocity, and say so in the description.
- information = perfect: Everyone sees the same facts. Include every relevant fact in the description, because nothing is hidden.
- payoff = zero-sum: One side's gain is the other's loss, as in a fixed prize or winner-takes-all. The total never changes.
- communication = no: No talking or signalling is possible. Actions are the only information.
- enforcement = no: Nothing forces anyone to keep a deal. Agreements rely on trust or self-interest.
- commitment = no: Every move can be reversed. Note any reversals that are cheap or expensive.
- bargaining = no: There is nothing to divide, or the outcome is fixed by the rules.

## Steps to set up your own version
1. Title and players: name the situation and who is involved.
2. Options: list each player's choices, using the game's own options from its playbook.
3. Payoffs or stakes: say what each outcome is worth to each player. For matrix games, fill in the payoff grid.
4. Information and timing: say who moves when, and who knows what.
5. Traits: copy the values in the template file. Change any that do not fit your situation.
6. Check: run `advise` on your file, and compare with the game's simulation with `sim` if one exists.

## Options to model
- Option idea 1: Randomise your choice with equal odds, so the other player cannot predict you.
- Option idea 2: Avoid patterns: a habit such as always choosing heads is found and exploited.
- Option idea 3: Track the other player's choices to confirm they are not following a pattern of their own.

## Payoff grid
Rows (you): Heads, Tails. Columns (them): Heads, Tails.
Enter it with: solve "-1,1 1,-1; 1,-1 -1,1" --rows Heads,Tails --cols Heads,Tails

## Start from this template
```
title: My Matching Pennies situation
players: two
timing: simultaneous
interaction: one-shot
information: perfect
payoff: zero-sum
communication: no
enforcement: no
commitment: no
bargaining: no
domain: games
notes: Describe your situation here. Replace the example options with your own.
```

# Penalty Kicks and Serve Direction

A striker and a goalkeeper, or a server and a returner, choose a direction at the same time. Sport shows the same logic as Matching Pennies: a predictable choice is easy to defend against.

## Traits and what each one means
- players = two: You and one counterpart. Name them in the title, for example 'me and my landlord'.
- timing = simultaneous: Everyone chooses without seeing the others' choices. Write each side's options down before anyone reveals anything.
- interaction = one-shot: The situation happens once. Do not plan on future reciprocity, and say so in the description.
- information = perfect: Everyone sees the same facts. Include every relevant fact in the description, because nothing is hidden.
- payoff = zero-sum: One side's gain is the other's loss, as in a fixed prize or winner-takes-all. The total never changes.
- communication = no: No talking or signalling is possible. Actions are the only information.
- enforcement = no: Nothing forces anyone to keep a deal. Agreements rely on trust or self-interest.
- commitment = no: Every move can be reversed. Note any reversals that are cheap or expensive.
- bargaining = no: There is nothing to divide, or the outcome is fixed by the rules.

## Steps to set up your own version
1. Title and players: name the situation and who is involved.
2. Options: list each player's choices, using the game's own options from its playbook.
3. Payoffs or stakes: say what each outcome is worth to each player. For matrix games, fill in the payoff grid.
4. Information and timing: say who moves when, and who knows what.
5. Traits: copy the values in the template file. Change any that do not fit your situation.
6. Check: run `advise` on your file, and compare with the game's simulation with `sim` if one exists.

## Options to model
- Option idea 1: Mix your directions, and vary them so the opponent cannot learn a habit.
- Option idea 2: Watch for a tell in the run-up, and only use it when it is real.
- Option idea 3: Remember that a successful choice this time may be expected next time.

## Payoff grid
Rows (you): Shoot left, Shoot right. Columns (them): Dive left, Dive right.
Enter it with: solve "-1,1 1,-1; 1,-1 -1,1" --rows Shoot left,Shoot right --cols Dive left,Dive right

## Start from this template
```
title: My Penalty Kicks and Serve Direction situation
players: two
timing: simultaneous
interaction: one-shot
information: perfect
payoff: zero-sum
communication: no
enforcement: no
commitment: no
bargaining: no
domain: everyday, games
notes: Describe your situation here. Replace the example options with your own.
```

# Dictator Game: Fairness Without a Reply

One person decides how to split a sum with another person, who has no say. It shows how much people share when nothing forces them to, and how much of that sharing depends on being seen.

## Traits and what each one means
- players = two: You and one counterpart. Name them in the title, for example 'me and my landlord'.
- timing = sequential: Decisions come in turns. Write who moves first, and what each mover can see when they choose.
- interaction = one-shot: The situation happens once. Do not plan on future reciprocity, and say so in the description.
- information = perfect: Everyone sees the same facts. Include every relevant fact in the description, because nothing is hidden.
- payoff = mixed: Both can gain or both can lose. Write what each side gains from cooperating and what it gains from competing.
- communication = no: No talking or signalling is possible. Actions are the only information.
- enforcement = no: Nothing forces anyone to keep a deal. Agreements rely on trust or self-interest.
- commitment = no: Every move can be reversed. Note any reversals that are cheap or expensive.
- bargaining = no: There is nothing to divide, or the outcome is fixed by the rules.

## Steps to set up your own version
1. Title and players: name the situation and who is involved.
2. Options: list each player's choices, using the game's own options from its playbook.
3. Payoffs or stakes: say what each outcome is worth to each player. For matrix games, fill in the payoff grid.
4. Information and timing: say who moves when, and who knows what.
5. Traits: copy the values in the template file. Change any that do not fit your situation.
6. Check: run `advise` on your file, and compare with the game's simulation with `sim` if one exists.

## Options to model
- Option idea 1: Share fairly when your choice is seen, because reputation is a real return.
- Option idea 2: Recognise that the other person's options matter: a fair offer costs little and builds trust.
- Option idea 3: Do not expect fairness from someone with no reason to show it.

## Payoff grid
Rows (you): Split evenly, Keep everything. Columns (them): Observed, Unobserved.
Enter it with: solve "3,3 3,3; 5,0 2,0" --rows Split evenly,Keep everything --cols Observed,Unobserved

## Start from this template
```
title: My Dictator Game: Fairness Without a Reply situation
players: two
timing: sequential
interaction: one-shot
information: perfect
payoff: mixed
communication: no
enforcement: no
commitment: no
bargaining: no
domain: games, society
notes: Describe your situation here. Replace the example options with your own.
```

# Braess's Paradox: When a Shortcut Slows Everyone

Drivers choose between a slow old route and a new shortcut. Adding the shortcut can make everyone's trip slower, because each driver's choice adds congestion for the others.

## Traits and what each one means
- players = two: You and one counterpart. Name them in the title, for example 'me and my landlord'.
- timing = simultaneous: Everyone chooses without seeing the others' choices. Write each side's options down before anyone reveals anything.
- interaction = one-shot: The situation happens once. Do not plan on future reciprocity, and say so in the description.
- information = perfect: Everyone sees the same facts. Include every relevant fact in the description, because nothing is hidden.
- payoff = mixed: Both can gain or both can lose. Write what each side gains from cooperating and what it gains from competing.
- communication = no: No talking or signalling is possible. Actions are the only information.
- enforcement = no: Nothing forces anyone to keep a deal. Agreements rely on trust or self-interest.
- commitment = no: Every move can be reversed. Note any reversals that are cheap or expensive.
- bargaining = no: There is nothing to divide, or the outcome is fixed by the rules.

## Steps to set up your own version
1. Title and players: name the situation and who is involved.
2. Options: list each player's choices, using the game's own options from its playbook.
3. Payoffs or stakes: say what each outcome is worth to each player. For matrix games, fill in the payoff grid.
4. Information and timing: say who moves when, and who knows what.
5. Traits: copy the values in the template file. Change any that do not fit your situation.
6. Check: run `advise` on your file, and compare with the game's simulation with `sim` if one exists.

## Options to model
- Option idea 1: Check how the choice changes for everyone, not just for yourself.
- Option idea 2: Use a shortcut when few others take it, and avoid it when it is crowded.
- Option idea 3: For planners: test the whole network before building a new link, and price or time the link if needed.

## Payoff grid
Rows (you): Old route, Shortcut. Columns (them): Old route, Shortcut.
Enter it with: solve "-4,-4 -4,-2; -2,-4 -6,-6" --rows Old route,Shortcut --cols Old route,Shortcut

## Start from this template
```
title: My Braess's Paradox: When a Shortcut Slows Everyone situation
players: two
timing: simultaneous
interaction: one-shot
information: perfect
payoff: mixed
communication: no
enforcement: no
commitment: no
bargaining: no
domain: everyday, government, environment
notes: Describe your situation here. Replace the example options with your own.
```

# Nash Bargaining: Dividing a Fixed Prize

Two parties each name a share of a fixed prize. If the shares add up to the whole, both get what they asked for. If they claim too much, both get nothing. The question is how to ask for enough without asking for too much.

## Traits and what each one means
- players = two: You and one counterpart. Name them in the title, for example 'me and my landlord'.
- timing = simultaneous: Everyone chooses without seeing the others' choices. Write each side's options down before anyone reveals anything.
- interaction = one-shot: The situation happens once. Do not plan on future reciprocity, and say so in the description.
- information = perfect: Everyone sees the same facts. Include every relevant fact in the description, because nothing is hidden.
- payoff = mixed: Both can gain or both can lose. Write what each side gains from cooperating and what it gains from competing.
- communication = yes: You can talk before or during the decision. Say what can be promised, and whether promises are binding.
- enforcement = no: Nothing forces anyone to keep a deal. Agreements rely on trust or self-interest.
- commitment = no: Every move can be reversed. Note any reversals that are cheap or expensive.
- bargaining = yes: You are dividing something. State the total, and each side's alternative if no deal is reached (its outside option).

## Steps to set up your own version
1. Title and players: name the situation and who is involved.
2. Options: list each player's choices, using the game's own options from its playbook.
3. Payoffs or stakes: say what each outcome is worth to each player. For matrix games, fill in the payoff grid.
4. Information and timing: say who moves when, and who knows what.
5. Traits: copy the values in the template file. Change any that do not fit your situation.
6. Check: run `advise` on your file, and compare with the game's simulation with `sim` if one exists.

## Options to model
- Option idea 1: Name a fair share that the other side can accept without losing face.
- Option idea 2: Anchor on a reasoned split, such as the equal share, and explain the reasons.
- Option idea 3: Know your fallback: a deal that is slightly worse is often better than none.

## Payoff grid
Rows (you): Demand 4, Demand 5, Demand 6. Columns (them): Demand 4, Demand 5, Demand 6.
Enter it with: solve "4,4 4,5 4,6; 5,4 5,5 0,0; 6,4 0,0 0,0" --rows Demand 4,Demand 5,Demand 6 --cols Demand 4,Demand 5,Demand 6

## Start from this template
```
title: My Nash Bargaining: Dividing a Fixed Prize situation
players: two
timing: simultaneous
interaction: one-shot
information: perfect
payoff: mixed
communication: yes
enforcement: no
commitment: no
bargaining: yes
domain: work, business, everyday
notes: Describe your situation here. Replace the example options with your own.
```

# Minority Game: Choosing the Less Crowded Option

Players each pick one of two places. Those who end up in the less crowded place win, and the crowd loses. Being right means being different from most people, which makes the crowd's behaviour hard to predict.

## Traits and what each one means
- players = many: Three or more players. Either list each player, or model the rest as one group with a shared outcome. Many-player games need the group's total effect spelled out.
- timing = simultaneous: Everyone chooses without seeing the others' choices. Write each side's options down before anyone reveals anything.
- interaction = one-shot: The situation happens once. Do not plan on future reciprocity, and say so in the description.
- information = imperfect: Someone holds private information. Say who knows what, and what each side is guessing about the other.
- payoff = mixed: Both can gain or both can lose. Write what each side gains from cooperating and what it gains from competing.
- communication = no: No talking or signalling is possible. Actions are the only information.
- enforcement = no: Nothing forces anyone to keep a deal. Agreements rely on trust or self-interest.
- commitment = no: Every move can be reversed. Note any reversals that are cheap or expensive.
- bargaining = no: There is nothing to divide, or the outcome is fixed by the rules.

## Steps to set up your own version
1. Title and players: name the situation and who is involved.
2. Options: list each player's choices, using the game's own options from its playbook.
3. Payoffs or stakes: say what each outcome is worth to each player. For matrix games, fill in the payoff grid.
4. Information and timing: say who moves when, and who knows what.
5. Traits: copy the values in the template file. Change any that do not fit your situation.
6. Check: run `advise` on your file, and compare with the game's simulation with `sim` if one exists.

## Options to model
- Option idea 1: Ask what most people will choose, then think about whether they will all choose it.
- Option idea 2: Pick a less popular option when the popular one is likely to be crowded.
- Option idea 3: Use a rule rather than a guess, and test it over several rounds.

## Payoff grid
Rows (you): Bar A, Bar B. Columns (them): Bar A, Bar B.
Enter it with: solve "-1,-1 1,1; 1,1 -1,-1" --rows Bar A,Bar B --cols Bar A,Bar B

## Start from this template
```
title: My Minority Game: Choosing the Less Crowded Option situation
players: many
timing: simultaneous
interaction: one-shot
information: imperfect
payoff: mixed
communication: no
enforcement: no
commitment: no
bargaining: no
domain: society, economy
notes: Describe your situation here. Replace the example options with your own.
```

# Hotelling: Where to Open a Shop

Two shops choose where to locate along a street where customers are spread evenly. Each customer uses the nearer shop, so both shops tend to move towards the middle, where they compete for the same people.

## Traits and what each one means
- players = two: You and one counterpart. Name them in the title, for example 'me and my landlord'.
- timing = simultaneous: Everyone chooses without seeing the others' choices. Write each side's options down before anyone reveals anything.
- interaction = one-shot: The situation happens once. Do not plan on future reciprocity, and say so in the description.
- information = perfect: Everyone sees the same facts. Include every relevant fact in the description, because nothing is hidden.
- payoff = zero-sum: One side's gain is the other's loss, as in a fixed prize or winner-takes-all. The total never changes.
- communication = no: No talking or signalling is possible. Actions are the only information.
- enforcement = no: Nothing forces anyone to keep a deal. Agreements rely on trust or self-interest.
- commitment = no: Every move can be reversed. Note any reversals that are cheap or expensive.
- bargaining = no: There is nothing to divide, or the outcome is fixed by the rules.

## Steps to set up your own version
1. Title and players: name the situation and who is involved.
2. Options: list each player's choices, using the game's own options from its playbook.
3. Payoffs or stakes: say what each outcome is worth to each player. For matrix games, fill in the payoff grid.
4. Information and timing: say who moves when, and who knows what.
5. Traits: copy the values in the template file. Change any that do not fit your situation.
6. Check: run `advise` on your file, and compare with the game's simulation with `sim` if one exists.

## Options to model
- Option idea 1: Look at where the customers are, not only where the rival is.
- Option idea 2: Differentiate: a different product or a niche can avoid the centre's crowding.
- Option idea 3: Watch the rival's move, because a copy may be cheaper than a new idea.

## Payoff grid
Rows (you): Open at 2, Open at 5, Open at 8. Columns (them): Open at 2, Open at 5, Open at 8.
Enter it with: solve "11,11 8,14 11,11; 14,8 11,11 14,8; 11,11 8,14 11,11" --rows Open at 2,Open at 5,Open at 8 --cols Open at 2,Open at 5,Open at 8

## Start from this template
```
title: My Hotelling: Where to Open a Shop situation
players: two
timing: simultaneous
interaction: one-shot
information: perfect
payoff: zero-sum
communication: no
enforcement: no
commitment: no
bargaining: no
domain: business, everyday
notes: Describe your situation here. Replace the example options with your own.
```

# Tariff War and Trade Deals

Two countries decide whether to keep trade open, impose tariffs, or offer a trade deal. Each tariff can win a short advantage, but when both impose them, both lose. A credible deal often leaves both better off.

## Traits and what each one means
- players = two: You and one counterpart. Name them in the title, for example 'me and my landlord'.
- timing = simultaneous: Everyone chooses without seeing the others' choices. Write each side's options down before anyone reveals anything.
- interaction = one-shot: The situation happens once. Do not plan on future reciprocity, and say so in the description.
- information = perfect: Everyone sees the same facts. Include every relevant fact in the description, because nothing is hidden.
- payoff = mixed: Both can gain or both can lose. Write what each side gains from cooperating and what it gains from competing.
- communication = yes: You can talk before or during the decision. Say what can be promised, and whether promises are binding.
- enforcement = yes: There are binding agreements, penalties or courts. Name the penalty and who can impose it.
- commitment = yes: Someone can commit publicly or irreversibly. Write the commitment mechanism, such as a signed contract or a visible step that cannot be undone.
- bargaining = yes: You are dividing something. State the total, and each side's alternative if no deal is reached (its outside option).

## Steps to set up your own version
1. Title and players: name the situation and who is involved.
2. Options: list each player's choices, using the game's own options from its playbook.
3. Payoffs or stakes: say what each outcome is worth to each player. For matrix games, fill in the payoff grid.
4. Information and timing: say who moves when, and who knows what.
5. Traits: copy the values in the template file. Change any that do not fit your situation.
6. Check: run `advise` on your file, and compare with the game's simulation with `sim` if one exists.

## Options to model
- Option idea 1: Offer a deal with clear, checkable terms, so both sides can see what they receive.
- Option idea 2: Plan for retaliation before imposing a tariff, and count its cost to your own side.
- Option idea 3: Keep the channel open after a dispute, so the next move can be a deal.

## Payoff grid
Rows (you): Keep trade open, Impose tariffs, Offer a deal. Columns (them): Keep trade open, Impose tariffs, Offer a deal.
Enter it with: solve "3,3 0,4 3,3; 4,0 1,1 2,2; 3,3 2,2 4,4" --rows Keep trade open,Impose tariffs,Offer a deal --cols Keep trade open,Impose tariffs,Offer a deal

## Start from this template
```
title: My Tariff War and Trade Deals situation
players: two
timing: simultaneous
interaction: one-shot
information: perfect
payoff: mixed
communication: yes
enforcement: yes
commitment: yes
bargaining: yes
domain: government, economy, business
notes: Describe your situation here. Replace the example options with your own.
```

# Cyber Defence: Protecting the Critical Systems

A defender chooses where to put protection effort across its systems. An attacker chooses which system to target. This is a planning game for the defender's side: it shows why protecting the most critical systems first usually beats spreading effort thinly.

## Traits and what each one means
- players = two: You and one counterpart. Name them in the title, for example 'me and my landlord'.
- timing = simultaneous: Everyone chooses without seeing the others' choices. Write each side's options down before anyone reveals anything.
- interaction = one-shot: The situation happens once. Do not plan on future reciprocity, and say so in the description.
- information = imperfect: Someone holds private information. Say who knows what, and what each side is guessing about the other.
- payoff = mixed: Both can gain or both can lose. Write what each side gains from cooperating and what it gains from competing.
- communication = no: No talking or signalling is possible. Actions are the only information.
- enforcement = no: Nothing forces anyone to keep a deal. Agreements rely on trust or self-interest.
- commitment = yes: Someone can commit publicly or irreversibly. Write the commitment mechanism, such as a signed contract or a visible step that cannot be undone.
- bargaining = no: There is nothing to divide, or the outcome is fixed by the rules.

## Steps to set up your own version
1. Title and players: name the situation and who is involved.
2. Options: list each player's choices, using the game's own options from its playbook.
3. Payoffs or stakes: say what each outcome is worth to each player. For matrix games, fill in the payoff grid.
4. Information and timing: say who moves when, and who knows what.
5. Traits: copy the values in the template file. Change any that do not fit your situation.
6. Check: run `advise` on your file, and compare with the game's simulation with `sim` if one exists.

## Options to model
- Option idea 1: Rank your systems by what they would cost to lose, and protect the top ones first.
- Option idea 2: Assume the weakest point will be found, and remove it before anything else.
- Option idea 3: Practise recovery, so that a failure at one point does not stop the whole organisation.

## Payoff grid
Rows (you): Harden the critical systems, Spread effort thinly. Columns (them): Target critical systems, Target weakest systems.
Enter it with: solve "2,-2 1,0; -3,3 -1,1" --rows Harden the critical systems,Spread effort thinly --cols Target critical systems,Target weakest systems

## Start from this template
```
title: My Cyber Defence: Protecting the Critical Systems situation
players: two
timing: simultaneous
interaction: one-shot
information: imperfect
payoff: mixed
communication: no
enforcement: no
commitment: yes
bargaining: no
domain: military, business
notes: Describe your situation here. Replace the example options with your own.
```

# Supply Chain: Shortage and the Bullwhip Effect

A supplier decides how much stock to hold, and a retailer decides how to order. When each side orders ahead out of fear, small changes in demand grow into large swings, and everyone loses.

## Traits and what each one means
- players = two: You and one counterpart. Name them in the title, for example 'me and my landlord'.
- timing = simultaneous: Everyone chooses without seeing the others' choices. Write each side's options down before anyone reveals anything.
- interaction = repeated: It recurs. Say how many rounds, and how much the future matters to each side. A longer, more valuable future usually supports cooperation.
- information = imperfect: Someone holds private information. Say who knows what, and what each side is guessing about the other.
- payoff = common-interest: You want the same outcome. The challenge is coordinating on it, not conflicting over it.
- communication = yes: You can talk before or during the decision. Say what can be promised, and whether promises are binding.
- enforcement = no: Nothing forces anyone to keep a deal. Agreements rely on trust or self-interest.
- commitment = no: Every move can be reversed. Note any reversals that are cheap or expensive.
- bargaining = yes: You are dividing something. State the total, and each side's alternative if no deal is reached (its outside option).

## Steps to set up your own version
1. Title and players: name the situation and who is involved.
2. Options: list each player's choices, using the game's own options from its playbook.
3. Payoffs or stakes: say what each outcome is worth to each player. For matrix games, fill in the payoff grid.
4. Information and timing: say who moves when, and who knows what.
5. Traits: copy the values in the template file. Change any that do not fit your situation.
6. Check: run `advise` on your file, and compare with the game's simulation with `sim` if one exists.

## Options to model
- Option idea 1: Share real sales data with the supplier, so that orders reflect demand and not fear.
- Option idea 2: Agree on a forecast and a buffer that both sides can see and check.
- Option idea 3: Order steadily when the signal is unclear, and avoid large one-off orders.

## Payoff grid
Rows (you): Keep stock lean, Hold a safety buffer. Columns (them): Order just in time, Order ahead to be safe.
Enter it with: solve "3,3 0,1; 2,1 2,2" --rows Keep stock lean,Hold a safety buffer --cols Order just in time,Order ahead to be safe

## Start from this template
```
title: My Supply Chain: Shortage and the Bullwhip Effect situation
players: two
timing: simultaneous
interaction: repeated
information: imperfect
payoff: common-interest
communication: yes
enforcement: no
commitment: no
bargaining: yes
domain: business, economy, work
notes: Describe your situation here. Replace the example options with your own.
```

# Parent and Teen: Curfews and Trust

A parent sets a curfew, and a teenager decides whether to keep it. Clear, agreed rules that come with trust tend to be kept better than rules that are simply imposed. The game is for healthy, respectful family decisions, not for control.

## Traits and what each one means
- players = two: You and one counterpart. Name them in the title, for example 'me and my landlord'.
- timing = simultaneous: Everyone chooses without seeing the others' choices. Write each side's options down before anyone reveals anything.
- interaction = repeated: It recurs. Say how many rounds, and how much the future matters to each side. A longer, more valuable future usually supports cooperation.
- information = imperfect: Someone holds private information. Say who knows what, and what each side is guessing about the other.
- payoff = mixed: Both can gain or both can lose. Write what each side gains from cooperating and what it gains from competing.
- communication = yes: You can talk before or during the decision. Say what can be promised, and whether promises are binding.
- enforcement = no: Nothing forces anyone to keep a deal. Agreements rely on trust or self-interest.
- commitment = no: Every move can be reversed. Note any reversals that are cheap or expensive.
- bargaining = yes: You are dividing something. State the total, and each side's alternative if no deal is reached (its outside option).

## Steps to set up your own version
1. Title and players: name the situation and who is involved.
2. Options: list each player's choices, using the game's own options from its playbook.
3. Payoffs or stakes: say what each outcome is worth to each player. For matrix games, fill in the payoff grid.
4. Information and timing: say who moves when, and who knows what.
5. Traits: copy the values in the template file. Change any that do not fit your situation.
6. Check: run `advise` on your file, and compare with the game's simulation with `sim` if one exists.

## Options to model
- Option idea 1: Agree the rule together, and explain the reason for it.
- Option idea 2: Review the rule on a set date, and adjust it when it is not working.
- Option idea 3: Respond to a breach calmly, and ask what happened before deciding the consequence.

## Payoff grid
Rows (you): Strict curfew, Flexible curfew. Columns (them): Follow the curfew, Test the limit.
Enter it with: solve "3,2 -1,-1; 2,3 -2,-1" --rows Strict curfew,Flexible curfew --cols Follow the curfew,Test the limit

## Start from this template
```
title: My Parent and Teen: Curfews and Trust situation
players: two
timing: simultaneous
interaction: repeated
information: imperfect
payoff: mixed
communication: yes
enforcement: no
commitment: no
bargaining: yes
domain: everyday, society
notes: Describe your situation here. Replace the example options with your own.
```

# Traffic Signal: Correlated Equilibrium

Two drivers approach a crossing with the same trusted signal. The signal suggests who should go and who should wait. Following a shared, trusted recommendation can do better for both than any plan worked out alone.

## Traits and what each one means
- players = two: You and one counterpart. Name them in the title, for example 'me and my landlord'.
- timing = simultaneous: Everyone chooses without seeing the others' choices. Write each side's options down before anyone reveals anything.
- interaction = one-shot: The situation happens once. Do not plan on future reciprocity, and say so in the description.
- information = perfect: Everyone sees the same facts. Include every relevant fact in the description, because nothing is hidden.
- payoff = mixed: Both can gain or both can lose. Write what each side gains from cooperating and what it gains from competing.
- communication = yes: You can talk before or during the decision. Say what can be promised, and whether promises are binding.
- enforcement = yes: There are binding agreements, penalties or courts. Name the penalty and who can impose it.
- commitment = no: Every move can be reversed. Note any reversals that are cheap or expensive.
- bargaining = no: There is nothing to divide, or the outcome is fixed by the rules.

## Steps to set up your own version
1. Title and players: name the situation and who is involved.
2. Options: list each player's choices, using the game's own options from its playbook.
3. Payoffs or stakes: say what each outcome is worth to each player. For matrix games, fill in the payoff grid.
4. Information and timing: say who moves when, and who knows what.
5. Traits: copy the values in the template file. Change any that do not fit your situation.
6. Check: run `advise` on your file, and compare with the game's simulation with `sim` if one exists.

## Options to model
- Option idea 1: Set up a signal that both sides trust, and that neither controls alone.
- Option idea 2: Follow the recommendation when the other side is likely to follow it too.
- Option idea 3: Check that the signal is fair, so that the same rule applies to everyone.

## Payoff grid
Rows (you): Swerve, Dare. Columns (them): Swerve, Dare.
Enter it with: solve "3,3 1,4; 4,1 0,0" --rows Swerve,Dare --cols Swerve,Dare

## Start from this template
```
title: My Traffic Signal: Correlated Equilibrium situation
players: two
timing: simultaneous
interaction: one-shot
information: perfect
payoff: mixed
communication: yes
enforcement: yes
commitment: no
bargaining: no
domain: games, everyday
notes: Describe your situation here. Replace the example options with your own.
```

# Kin Selection: Helping Relatives

Two relatives each decide whether to help the other at a personal cost. Because they share genes, help that costs one of them a little can gain the other a lot. The game shows why helping can spread among relatives even when it looks like a loss to the helper.

## Traits and what each one means
- players = two: You and one counterpart. Name them in the title, for example 'me and my landlord'.
- timing = simultaneous: Everyone chooses without seeing the others' choices. Write each side's options down before anyone reveals anything.
- interaction = one-shot: The situation happens once. Do not plan on future reciprocity, and say so in the description.
- information = perfect: Everyone sees the same facts. Include every relevant fact in the description, because nothing is hidden.
- payoff = mixed: Both can gain or both can lose. Write what each side gains from cooperating and what it gains from competing.
- communication = no: No talking or signalling is possible. Actions are the only information.
- enforcement = no: Nothing forces anyone to keep a deal. Agreements rely on trust or self-interest.
- commitment = no: Every move can be reversed. Note any reversals that are cheap or expensive.
- bargaining = no: There is nothing to divide, or the outcome is fixed by the rules.

## Steps to set up your own version
1. Title and players: name the situation and who is involved.
2. Options: list each player's choices, using the game's own options from its playbook.
3. Payoffs or stakes: say what each outcome is worth to each player. For matrix games, fill in the payoff grid.
4. Information and timing: say who moves when, and who knows what.
5. Traits: copy the values in the template file. Change any that do not fit your situation.
6. Check: run `advise` on your file, and compare with the game's simulation with `sim` if one exists.

## Options to model
- Option idea 1: Count the benefit to a relative as part of your own gain, weighted by how closely related you are.
- Option idea 2: Compare the cost of helping with the benefit to others, not only to yourself.
- Option idea 3: Do not assume the same help is worth it between strangers, where relatedness is absent.

## Payoff grid
Rows (you): Help the relative, Keep to yourself. Columns (them): Relative helps, Relative keeps.
Enter it with: solve "6,6 1,5; 5,1 0,0" --rows Help the relative,Keep to yourself --cols Relative helps,Relative keeps

## Start from this template
```
title: My Kin Selection: Helping Relatives situation
players: two
timing: simultaneous
interaction: one-shot
information: perfect
payoff: mixed
communication: no
enforcement: no
commitment: no
bargaining: no
domain: games, environment
notes: Describe your situation here. Replace the example options with your own.
```

# Beliefs After a Surprise (Perfect Bayesian Equilibrium)

A sender knows whether they are strong or weak and chooses whether to send a costly signal. The receiver must update their belief about the sender, then decide whether to trust the signal. Equilibrium needs beliefs that are consistent with what each side does, including after a surprise.

## Traits and what each one means
- players = two: You and one counterpart. Name them in the title, for example 'me and my landlord'.
- timing = sequential: Decisions come in turns. Write who moves first, and what each mover can see when they choose.
- interaction = one-shot: The situation happens once. Do not plan on future reciprocity, and say so in the description.
- information = imperfect: Someone holds private information. Say who knows what, and what each side is guessing about the other.
- payoff = mixed: Both can gain or both can lose. Write what each side gains from cooperating and what it gains from competing.
- communication = yes: You can talk before or during the decision. Say what can be promised, and whether promises are binding.
- enforcement = no: Nothing forces anyone to keep a deal. Agreements rely on trust or self-interest.
- commitment = no: Every move can be reversed. Note any reversals that are cheap or expensive.
- bargaining = no: There is nothing to divide, or the outcome is fixed by the rules.

## Steps to set up your own version
1. Title and players: name the situation and who is involved.
2. Options: list each player's choices, using the game's own options from its playbook.
3. Payoffs or stakes: say what each outcome is worth to each player. For matrix games, fill in the payoff grid.
4. Information and timing: say who moves when, and who knows what.
5. Traits: copy the values in the template file. Change any that do not fit your situation.
6. Check: run `advise` on your file, and compare with the game's simulation with `sim` if one exists.

## Options to model
- Option idea 1: Ask what each type of player would gain by sending the signal, and whether a weak one could copy it.
- Option idea 2: Update your belief by how likely each type is to have acted this way.
- Option idea 3: Treat an unexpected move as information, not as noise.

## Payoff grid
Rows (you): Send the costly signal, Stay quiet. Columns (them): Trust the signal, Ignore the signal.
Enter it with: solve "2,2 0,1; 1,0 1,1" --rows Send the costly signal,Stay quiet --cols Trust the signal,Ignore the signal

## Start from this template
```
title: My Beliefs After a Surprise (Perfect Bayesian Equilibrium) situation
players: two
timing: sequential
interaction: one-shot
information: imperfect
payoff: mixed
communication: yes
enforcement: no
commitment: no
bargaining: no
domain: games, government, business
notes: Describe your situation here. Replace the example options with your own.
```

# Pandemic: Quarantine Versus Economy

Each person and each government balances restrictions that slow an outbreak against the economic and personal cost of restrictions. Compliance depends on trust and on how fairly the burden is shared.

## Traits and what each one means
- players = many: Three or more players. Either list each player, or model the rest as one group with a shared outcome. Many-player games need the group's total effect spelled out.
- timing = sequential: Decisions come in turns. Write who moves first, and what each mover can see when they choose.
- interaction = repeated: It recurs. Say how many rounds, and how much the future matters to each side. A longer, more valuable future usually supports cooperation.
- information = imperfect: Someone holds private information. Say who knows what, and what each side is guessing about the other.
- payoff = mixed: Both can gain or both can lose. Write what each side gains from cooperating and what it gains from competing.
- communication = yes: You can talk before or during the decision. Say what can be promised, and whether promises are binding.
- enforcement = yes: There are binding agreements, penalties or courts. Name the penalty and who can impose it.

## Steps to set up your own version
1. Title and players: name the situation and who is involved.
2. Options: list each player's choices, using the game's own options from its playbook.
3. Payoffs or stakes: say what each outcome is worth to each player. For matrix games, fill in the payoff grid.
4. Information and timing: say who moves when, and who knows what.
5. Traits: copy the values in the template file. Change any that do not fit your situation.
6. Check: run `advise` on your file, and compare with the game's simulation with `sim` if one exists.

## Options to model
- Option idea 1: Publish clear criteria for tightening and relaxing restrictions, so people can plan and trust the rules.
- Option idea 2: Share the burden fairly, with support for those who lose income; unfair burdens reduce compliance.
- Option idea 3: Relax on schedule when the criteria are met, to keep credibility for future measures.

## Payoff grid
Rows (you): Strict restrictions, Relax early. Columns (them): Comply, Defy.
Enter it with: solve "2,2 -2,1; 1,-2 -1,-1" --rows Strict restrictions,Relax early --cols Comply,Defy

Simulation: `sim pandemic-quarantine-game` shows the paths, and `sim pandemic-quarantine-game --play` lets you choose.

## Start from this template
```
title: My Pandemic: Quarantine Versus Economy situation
players: many
timing: sequential
interaction: repeated
information: imperfect
payoff: mixed
communication: yes
enforcement: yes
domain: environment, government, everyday
notes: Describe your situation here. Replace the example options with your own.
```

# Testing and Contact Tracing

Testing and tracing find infections early, but they require information about people's contacts and movements. Participation depends on how much people trust that the information will be used fairly.

## Traits and what each one means
- players = many: Three or more players. Either list each player, or model the rest as one group with a shared outcome. Many-player games need the group's total effect spelled out.
- timing = sequential: Decisions come in turns. Write who moves first, and what each mover can see when they choose.
- interaction = repeated: It recurs. Say how many rounds, and how much the future matters to each side. A longer, more valuable future usually supports cooperation.
- information = imperfect: Someone holds private information. Say who knows what, and what each side is guessing about the other.
- payoff = mixed: Both can gain or both can lose. Write what each side gains from cooperating and what it gains from competing.
- communication = yes: You can talk before or during the decision. Say what can be promised, and whether promises are binding.
- enforcement = yes: There are binding agreements, penalties or courts. Name the penalty and who can impose it.

## Steps to set up your own version
1. Title and players: name the situation and who is involved.
2. Options: list each player's choices, using the game's own options from its playbook.
3. Payoffs or stakes: say what each outcome is worth to each player. For matrix games, fill in the payoff grid.
4. Information and timing: say who moves when, and who knows what.
5. Traits: copy the values in the template file. Change any that do not fit your situation.
6. Check: run `advise` on your file, and compare with the game's simulation with `sim` if one exists.

## Options to model
- Option idea 1: Limit data collected to what is needed, and say how long it is kept and who sees it.
- Option idea 2: Support people who test positive, such as paid sick leave, so the cost of testing is not a reason to hide.
- Option idea 3: Make testing easy and free at the point of use, which raises participation.

## Payoff grid
Rows (you): Join testing, Stay out. Columns (them): Privacy-safe tracing, Data-heavy tracing.
Enter it with: solve "2,2 1,-1; 0,0 -1,1" --rows Join testing,Stay out --cols Privacy-safe tracing,Data-heavy tracing

Simulation: `sim testing-contact-tracing` shows the paths, and `sim testing-contact-tracing --play` lets you choose.

## Start from this template
```
title: My Testing and Contact Tracing situation
players: many
timing: sequential
interaction: repeated
information: imperfect
payoff: mixed
communication: yes
enforcement: yes
domain: environment, government, everyday
notes: Describe your situation here. Replace the example options with your own.
```

# Emergency Supplies: Hoarding Versus Sharing

When people fear shortages, they buy more than they need, which creates the shortage they feared. Each person's hoarding looks sensible alone but harms everyone together.

## Traits and what each one means
- players = many: Three or more players. Either list each player, or model the rest as one group with a shared outcome. Many-player games need the group's total effect spelled out.
- timing = simultaneous: Everyone chooses without seeing the others' choices. Write each side's options down before anyone reveals anything.
- interaction = one-shot: The situation happens once. Do not plan on future reciprocity, and say so in the description.
- information = imperfect: Someone holds private information. Say who knows what, and what each side is guessing about the other.
- payoff = mixed: Both can gain or both can lose. Write what each side gains from cooperating and what it gains from competing.
- communication = yes: You can talk before or during the decision. Say what can be promised, and whether promises are binding.

## Steps to set up your own version
1. Title and players: name the situation and who is involved.
2. Options: list each player's choices, using the game's own options from its playbook.
3. Payoffs or stakes: say what each outcome is worth to each player. For matrix games, fill in the payoff grid.
4. Information and timing: say who moves when, and who knows what.
5. Traits: copy the values in the template file. Change any that do not fit your situation.
6. Check: run `advise` on your file, and compare with the game's simulation with `sim` if one exists.

## Options to model
- Option idea 1: Buy for a realistic period, not the maximum, so supplies remain for others.
- Option idea 2: Check information on supply from reliable sources, since rumours drive panic buying.
- Option idea 3: Support fair rationing rules, which protect people who cannot stockpile.

## Payoff grid
Rows (you): Buy realistically, Hoard. Columns (them): Buy realistically, Hoard.
Enter it with: solve "3,3 0,4; 4,0 1,1" --rows Buy realistically,Hoard --cols Buy realistically,Hoard

Simulation: `sim emergency-supply-hoarding` shows the paths, and `sim emergency-supply-hoarding --play` lets you choose.

## Start from this template
```
title: My Emergency Supplies: Hoarding Versus Sharing situation
players: many
timing: simultaneous
interaction: one-shot
information: imperfect
payoff: mixed
communication: yes
domain: environment, economy, everyday
notes: Describe your situation here. Replace the example options with your own.
```

# Disaster Preparedness (Rare Events)

Preparing for a rare disaster costs money every year, but the benefit appears only when the disaster strikes. People and governments often underinvest, and shared defences are left to others.

## Traits and what each one means
- players = many: Three or more players. Either list each player, or model the rest as one group with a shared outcome. Many-player games need the group's total effect spelled out.
- timing = sequential: Decisions come in turns. Write who moves first, and what each mover can see when they choose.
- interaction = repeated: It recurs. Say how many rounds, and how much the future matters to each side. A longer, more valuable future usually supports cooperation.
- information = imperfect: Someone holds private information. Say who knows what, and what each side is guessing about the other.
- payoff = mixed: Both can gain or both can lose. Write what each side gains from cooperating and what it gains from competing.
- enforcement = no: Nothing forces anyone to keep a deal. Agreements rely on trust or self-interest.

## Steps to set up your own version
1. Title and players: name the situation and who is involved.
2. Options: list each player's choices, using the game's own options from its playbook.
3. Payoffs or stakes: say what each outcome is worth to each player. For matrix games, fill in the payoff grid.
4. Information and timing: say who moves when, and who knows what.
5. Traits: copy the values in the template file. Change any that do not fit your situation.
6. Check: run `advise` on your file, and compare with the game's simulation with `sim` if one exists.

## Options to model
- Option idea 1: Estimate expected losses, not just the chance of a disaster, when deciding how much to invest.
- Option idea 2: Share the cost of community defences, so no one is left to free-ride.
- Option idea 3: Use insurance or reserve funds to spread the cost over time.

## Payoff grid
Rows (you): Invest in defences, Skip. Columns (them): Invest in defences, Skip.
Enter it with: solve "2,2 -1,3; 3,-1 0,0" --rows Invest in defences,Skip --cols Invest in defences,Skip

Simulation: `sim disaster-preparedness-investment` shows the paths, and `sim disaster-preparedness-investment --play` lets you choose.

## Start from this template
```
title: My Disaster Preparedness (Rare Events) situation
players: many
timing: sequential
interaction: repeated
information: imperfect
payoff: mixed
enforcement: no
domain: environment, government, everyday
notes: Describe your situation here. Replace the example options with your own.
```

# Nuclear Deterrence and Second Strike

Two nuclear-armed states deter each other because each can absorb a first strike and still retaliate. Stability depends on survivable forces, clear communication, and avoiding moves that look like preparation for a first strike.

## Traits and what each one means
- players = two: You and one counterpart. Name them in the title, for example 'me and my landlord'.
- timing = simultaneous: Everyone chooses without seeing the others' choices. Write each side's options down before anyone reveals anything.
- interaction = repeated: It recurs. Say how many rounds, and how much the future matters to each side. A longer, more valuable future usually supports cooperation.
- information = imperfect: Someone holds private information. Say who knows what, and what each side is guessing about the other.
- payoff = mixed: Both can gain or both can lose. Write what each side gains from cooperating and what it gains from competing.
- enforcement = yes: There are binding agreements, penalties or courts. Name the penalty and who can impose it.
- commitment = yes: Someone can commit publicly or irreversibly. Write the commitment mechanism, such as a signed contract or a visible step that cannot be undone.

## Steps to set up your own version
1. Title and players: name the situation and who is involved.
2. Options: list each player's choices, using the game's own options from its playbook.
3. Payoffs or stakes: say what each outcome is worth to each player. For matrix games, fill in the payoff grid.
4. Information and timing: say who moves when, and who knows what.
5. Traits: copy the values in the template file. Change any that do not fit your situation.
6. Check: run `advise` on your file, and compare with the game's simulation with `sim` if one exists.

## Options to model
- Option idea 1: Maintain survivable retaliatory forces, so a first strike cannot be worth the attempt.
- Option idea 2: Communicate capabilities and intentions clearly, to reduce misreading of ambiguous moves.
- Option idea 3: Use verification and transparency measures that both sides can check.

## Payoff grid
Rows (you): Maintain second strike, Pre-emptive build-up. Columns (them): Rival maintains, Rival pre-empts.
Enter it with: solve "2,2 0,3; 3,0 -3,-3" --rows Maintain second strike,Pre-emptive build-up --cols Rival maintains,Rival pre-empts

Simulation: `sim nuclear-deterrence-second-strike` shows the paths, and `sim nuclear-deterrence-second-strike --play` lets you choose.

## Start from this template
```
title: My Nuclear Deterrence and Second Strike situation
players: two
timing: simultaneous
interaction: repeated
information: imperfect
payoff: mixed
enforcement: yes
commitment: yes
domain: military, politics, government
notes: Describe your situation here. Replace the example options with your own.
```

# Crisis Escalation Ladder

In a crisis, each side takes steps up or down a ladder of responses. Each step signals resolve, but it also raises the risk that the other side will escalate further. The aim is to show resolve while keeping a way down.

## Traits and what each one means
- players = two: You and one counterpart. Name them in the title, for example 'me and my landlord'.
- timing = sequential: Decisions come in turns. Write who moves first, and what each mover can see when they choose.
- interaction = one-shot: The situation happens once. Do not plan on future reciprocity, and say so in the description.
- information = imperfect: Someone holds private information. Say who knows what, and what each side is guessing about the other.
- payoff = mixed: Both can gain or both can lose. Write what each side gains from cooperating and what it gains from competing.
- communication = yes: You can talk before or during the decision. Say what can be promised, and whether promises are binding.
- commitment = yes: Someone can commit publicly or irreversibly. Write the commitment mechanism, such as a signed contract or a visible step that cannot be undone.

## Steps to set up your own version
1. Title and players: name the situation and who is involved.
2. Options: list each player's choices, using the game's own options from its playbook.
3. Payoffs or stakes: say what each outcome is worth to each player. For matrix games, fill in the payoff grid.
4. Information and timing: say who moves when, and who knows what.
5. Traits: copy the values in the template file. Change any that do not fit your situation.
6. Check: run `advise` on your file, and compare with the game's simulation with `sim` if one exists.

## Options to model
- Option idea 1: Match escalation proportionately rather than exceeding the other side's last step.
- Option idea 2: Keep a visible off-ramp, such as a private channel or a face-saving concession.
- Option idea 3: Communicate your reading of the situation directly, so misreading does not drive escalation.

## Payoff grid
Rows (you): Escalate, De-escalate. Columns (them): Rival escalates, Rival de-escalates.
Enter it with: solve "-3,-3 2,-1; -1,2 1,1" --rows Escalate,De-escalate --cols Rival escalates,Rival de-escalates

Simulation: `sim crisis-escalation-ladder` shows the paths, and `sim crisis-escalation-ladder --play` lets you choose.

## Start from this template
```
title: My Crisis Escalation Ladder situation
players: two
timing: sequential
interaction: one-shot
information: imperfect
payoff: mixed
communication: yes
commitment: yes
domain: military, politics, government
notes: Describe your situation here. Replace the example options with your own.
```

# Siege and Supply Lines

A besieging force must hold its position while its supply lines are stretched. A defender must keep its supplies flowing. The side that can sustain its supply for longer usually decides the contest.

## Traits and what each one means
- players = two: You and one counterpart. Name them in the title, for example 'me and my landlord'.
- timing = sequential: Decisions come in turns. Write who moves first, and what each mover can see when they choose.
- interaction = one-shot: The situation happens once. Do not plan on future reciprocity, and say so in the description.
- information = perfect: Everyone sees the same facts. Include every relevant fact in the description, because nothing is hidden.
- payoff = zero-sum: One side's gain is the other's loss, as in a fixed prize or winner-takes-all. The total never changes.
- commitment = no: Every move can be reversed. Note any reversals that are cheap or expensive.

## Steps to set up your own version
1. Title and players: name the situation and who is involved.
2. Options: list each player's choices, using the game's own options from its playbook.
3. Payoffs or stakes: say what each outcome is worth to each player. For matrix games, fill in the payoff grid.
4. Information and timing: say who moves when, and who knows what.
5. Traits: copy the values in the template file. Change any that do not fit your situation.
6. Check: run `advise` on your file, and compare with the game's simulation with `sim` if one exists.

## Options to model
- Option idea 1: Count supplies on both sides before committing; the side that runs out first usually loses.
- Option idea 2: Protect your own supply lines before attacking the other side's.
- Option idea 3: Look for ways to shorten your own line or lengthen the enemy's, rather than trying to win by direct assault.

## Payoff grid
Rows (you): Besiege, Assault. Columns (them): Hold, Sortie.
Enter it with: solve "1,1 -1,2; 2,-1 0,0" --rows Besiege,Assault --cols Hold,Sortie

Simulation: `sim siege-and-logistics` shows the paths, and `sim siege-and-logistics --play` lets you choose.

## Start from this template
```
title: My Siege and Supply Lines situation
players: two
timing: sequential
interaction: one-shot
information: perfect
payoff: zero-sum
commitment: no
domain: military, games
notes: Describe your situation here. Replace the example options with your own.
```

# Surprise and Reconnaissance

Acting by surprise can change the outcome, but surprise depends on what the other side expects. Gathering information before acting reduces uncertainty, while being observed while gathering it gives the other side warning.

## Traits and what each one means
- players = two: You and one counterpart. Name them in the title, for example 'me and my landlord'.
- timing = simultaneous: Everyone chooses without seeing the others' choices. Write each side's options down before anyone reveals anything.
- interaction = one-shot: The situation happens once. Do not plan on future reciprocity, and say so in the description.
- information = imperfect: Someone holds private information. Say who knows what, and what each side is guessing about the other.
- payoff = zero-sum: One side's gain is the other's loss, as in a fixed prize or winner-takes-all. The total never changes.
- communication = no: No talking or signalling is possible. Actions are the only information.

## Steps to set up your own version
1. Title and players: name the situation and who is involved.
2. Options: list each player's choices, using the game's own options from its playbook.
3. Payoffs or stakes: say what each outcome is worth to each player. For matrix games, fill in the payoff grid.
4. Information and timing: say who moves when, and who knows what.
5. Traits: copy the values in the template file. Change any that do not fit your situation.
6. Check: run `advise` on your file, and compare with the game's simulation with `sim` if one exists.

## Options to model
- Option idea 1: Gather information in ways that do not signal intent, such as routine activity.
- Option idea 2: Surprise is most effective where the other side's expectations are most mistaken; check where those expectations come from.
- Option idea 3: Prepare a fallback, since surprise can fail.

## Payoff grid
Rows (you): Strike A, Strike B. Columns (them): Guard A, Guard B.
Enter it with: solve "-1,1 1,-1; 1,-1 -1,1" --rows Strike A,Strike B --cols Guard A,Guard B

Simulation: `sim surprise-and-reconnaissance` shows the paths, and `sim surprise-and-reconnaissance --play` lets you choose.

## Start from this template
```
title: My Surprise and Reconnaissance situation
players: two
timing: simultaneous
interaction: one-shot
information: imperfect
payoff: zero-sum
communication: no
domain: military, business, games
notes: Describe your situation here. Replace the example options with your own.
```

# Mechanism Design: Truthful Auctions

A designer sets the rules of an auction or allocation so that each participant's best strategy is to report their true value. Good design makes honesty the winning move rather than relying on trust.

## Traits and what each one means
- players = many: Three or more players. Either list each player, or model the rest as one group with a shared outcome. Many-player games need the group's total effect spelled out.
- timing = simultaneous: Everyone chooses without seeing the others' choices. Write each side's options down before anyone reveals anything.
- interaction = one-shot: The situation happens once. Do not plan on future reciprocity, and say so in the description.
- information = imperfect: Someone holds private information. Say who knows what, and what each side is guessing about the other.
- payoff = mixed: Both can gain or both can lose. Write what each side gains from cooperating and what it gains from competing.
- communication = no: No talking or signalling is possible. Actions are the only information.
- enforcement = yes: There are binding agreements, penalties or courts. Name the penalty and who can impose it.

## Steps to set up your own version
1. Title and players: name the situation and who is involved.
2. Options: list each player's choices, using the game's own options from its playbook.
3. Payoffs or stakes: say what each outcome is worth to each player. For matrix games, fill in the payoff grid.
4. Information and timing: say who moves when, and who knows what.
5. Traits: copy the values in the template file. Change any that do not fit your situation.
6. Check: run `advise` on your file, and compare with the game's simulation with `sim` if one exists.

## Options to model
- Option idea 1: As designer: choose rules where truthful reporting is the best strategy for every participant.
- Option idea 2: As participant in a truthful mechanism: bid or report your true value; strategic misreporting does not help.
- Option idea 3: Check that the rules do not depend on information the designer cannot verify.

## Payoff grid
Rows (you): Bid 3, Bid 4, Bid 5, Bid 6. Columns (them): Bid 3, Bid 4, Bid 5, Bid 6.
Enter it with: solve "0,0 0,1 0,1 0,1; 3,0 0,0 0,0 0,0; 3,0 2,0 0,0 0,-1; 3,0 2,0 1,0 0,0" --rows Bid 3,Bid 4,Bid 5,Bid 6 --cols Bid 3,Bid 4,Bid 5,Bid 6

Simulation: `sim vcg-mechanism-design` shows the paths, and `sim vcg-mechanism-design --play` lets you choose.

## Start from this template
```
title: My Mechanism Design: Truthful Auctions situation
players: many
timing: simultaneous
interaction: one-shot
information: imperfect
payoff: mixed
communication: no
enforcement: yes
domain: economy, business, government
notes: Describe your situation here. Replace the example options with your own.
```

# Bayesian Persuasion: Choosing What to Reveal

A sender knows more than a receiver and chooses what information to reveal. Clever disclosure can shape what the receiver believes and does, even when every statement is true.

## Traits and what each one means
- players = two: You and one counterpart. Name them in the title, for example 'me and my landlord'.
- timing = sequential: Decisions come in turns. Write who moves first, and what each mover can see when they choose.
- interaction = one-shot: The situation happens once. Do not plan on future reciprocity, and say so in the description.
- information = imperfect: Someone holds private information. Say who knows what, and what each side is guessing about the other.
- payoff = mixed: Both can gain or both can lose. Write what each side gains from cooperating and what it gains from competing.
- communication = yes: You can talk before or during the decision. Say what can be promised, and whether promises are binding.

## Steps to set up your own version
1. Title and players: name the situation and who is involved.
2. Options: list each player's choices, using the game's own options from its playbook.
3. Payoffs or stakes: say what each outcome is worth to each player. For matrix games, fill in the payoff grid.
4. Information and timing: say who moves when, and who knows what.
5. Traits: copy the values in the template file. Change any that do not fit your situation.
6. Check: run `advise` on your file, and compare with the game's simulation with `sim` if one exists.

## Options to model
- Option idea 1: As receiver: ask how the information was chosen and what was left out, since selective truths can mislead.
- Option idea 2: As sender: disclose in ways that remain fair and checkable, because selective disclosure is discovered and damages trust.
- Option idea 3: Compare the signal with the base rate, so a striking statistic is not read out of context.

## Payoff grid
Rows (you): Reveal fully, Conceal. Columns (them): Act, Hold.
Enter it with: solve "2,2 0,1; 1,0 0,1" --rows Reveal fully,Conceal --cols Act,Hold

Simulation: `sim bayesian-persuasion` shows the paths, and `sim bayesian-persuasion --play` lets you choose.

## Start from this template
```
title: My Bayesian Persuasion: Choosing What to Reveal situation
players: two
timing: sequential
interaction: one-shot
information: imperfect
payoff: mixed
communication: yes
domain: business, politics, government
notes: Describe your situation here. Replace the example options with your own.
```

# Sharing Gains in a Coalition (Shapley Value)

Several parties form a coalition that produces a joint gain. The Shapley value divides the gain by averaging each party's contribution across all the orders in which parties could join. It is one fair way to split a shared prize.

## Traits and what each one means
- players = many: Three or more players. Either list each player, or model the rest as one group with a shared outcome. Many-player games need the group's total effect spelled out.
- timing = sequential: Decisions come in turns. Write who moves first, and what each mover can see when they choose.
- interaction = one-shot: The situation happens once. Do not plan on future reciprocity, and say so in the description.
- information = perfect: Everyone sees the same facts. Include every relevant fact in the description, because nothing is hidden.
- payoff = common-interest: You want the same outcome. The challenge is coordinating on it, not conflicting over it.
- bargaining = yes: You are dividing something. State the total, and each side's alternative if no deal is reached (its outside option).

## Steps to set up your own version
1. Title and players: name the situation and who is involved.
2. Options: list each player's choices, using the game's own options from its playbook.
3. Payoffs or stakes: say what each outcome is worth to each player. For matrix games, fill in the payoff grid.
4. Information and timing: say who moves when, and who knows what.
5. Traits: copy the values in the template file. Change any that do not fit your situation.
6. Check: run `advise` on your file, and compare with the game's simulation with `sim` if one exists.

## Options to model
- Option idea 1: Estimate each party's contribution to the total, not only what it asks for.
- Option idea 2: Use the average over possible joining orders as a fair benchmark for a split.
- Option idea 3: Check whether any sub-group could do better alone; if so, the split is unstable.

## Payoff grid
Rows (you): Form the coalition, Go alone. Columns (them): Partner joins, Partner goes alone.
Enter it with: solve "2,2 0,0; 0,0 1,1" --rows Form the coalition,Go alone --cols Partner joins,Partner goes alone

Simulation: `sim shapley-value-sharing` shows the paths, and `sim shapley-value-sharing --play` lets you choose.

## Start from this template
```
title: My Sharing Gains in a Coalition (Shapley Value) situation
players: many
timing: sequential
interaction: one-shot
information: perfect
payoff: common-interest
bargaining: yes
domain: business, economy, government
notes: Describe your situation here. Replace the example options with your own.
```

# Voting Paradoxes (Condorcet and Arrow)

Majority preferences can cycle: A beats B, B beats C, and C beats A. Arrow's theorem shows that no voting rule satisfies all reasonable fairness conditions, so every system involves trade-offs.

## Traits and what each one means
- players = many: Three or more players. Either list each player, or model the rest as one group with a shared outcome. Many-player games need the group's total effect spelled out.
- timing = simultaneous: Everyone chooses without seeing the others' choices. Write each side's options down before anyone reveals anything.
- interaction = one-shot: The situation happens once. Do not plan on future reciprocity, and say so in the description.
- information = perfect: Everyone sees the same facts. Include every relevant fact in the description, because nothing is hidden.
- payoff = mixed: Both can gain or both can lose. Write what each side gains from cooperating and what it gains from competing.
- communication = yes: You can talk before or during the decision. Say what can be promised, and whether promises are binding.

## Steps to set up your own version
1. Title and players: name the situation and who is involved.
2. Options: list each player's choices, using the game's own options from its playbook.
3. Payoffs or stakes: say what each outcome is worth to each player. For matrix games, fill in the payoff grid.
4. Information and timing: say who moves when, and who knows what.
5. Traits: copy the values in the template file. Change any that do not fit your situation.
6. Check: run `advise` on your file, and compare with the game's simulation with `sim` if one exists.

## Options to model
- Option idea 1: Check whether a majority winner exists before relying on a vote; a cycle means the result depends on the voting rule.
- Option idea 2: Choose a voting method deliberately, and state its trade-offs.
- Option idea 3: Use runoffs or ranked ballots where the stakes call for broad acceptance.

## Payoff grid
Rows (you): Vote for A first, Vote for B first. Columns (them): Ranking one, Ranking two.
Enter it with: solve "1,1 -1,-1; -1,-1 1,1" --rows Vote for A first,Vote for B first --cols Ranking one,Ranking two

Simulation: `sim voting-paradoxes` shows the paths, and `sim voting-paradoxes --play` lets you choose.

## Start from this template
```
title: My Voting Paradoxes (Condorcet and Arrow) situation
players: many
timing: simultaneous
interaction: one-shot
information: perfect
payoff: mixed
communication: yes
domain: politics, government, society
notes: Describe your situation here. Replace the example options with your own.
```

# Credible Threats (Subgame Perfection)

A threat is credible only if carrying it out would be in the threatener's interest when the time comes. Subgame perfection rules out threats that would be irrational to carry out.

## Traits and what each one means
- players = two: You and one counterpart. Name them in the title, for example 'me and my landlord'.
- timing = sequential: Decisions come in turns. Write who moves first, and what each mover can see when they choose.
- interaction = one-shot: The situation happens once. Do not plan on future reciprocity, and say so in the description.
- information = perfect: Everyone sees the same facts. Include every relevant fact in the description, because nothing is hidden.
- payoff = mixed: Both can gain or both can lose. Write what each side gains from cooperating and what it gains from competing.
- commitment = yes: Someone can commit publicly or irreversibly. Write the commitment mechanism, such as a signed contract or a visible step that cannot be undone.

## Steps to set up your own version
1. Title and players: name the situation and who is involved.
2. Options: list each player's choices, using the game's own options from its playbook.
3. Payoffs or stakes: say what each outcome is worth to each player. For matrix games, fill in the payoff grid.
4. Information and timing: say who moves when, and who knows what.
5. Traits: copy the values in the template file. Change any that do not fit your situation.
6. Check: run `advise` on your file, and compare with the game's simulation with `sim` if one exists.

## Options to model
- Option idea 1: Solve backward: ask whether you would actually carry out the threat once the other side has moved.
- Option idea 2: Make a threat credible by binding yourself in advance, such as a costly commitment.
- Option idea 3: If the other side's threat is not credible, call it out calmly and offer an alternative path.

## Payoff grid
Rows (you): Stay out, Enter. Columns (them): Fight, Accommodate.
Enter it with: solve "0,2 0,2; -1,-1 1,1" --rows Stay out,Enter --cols Fight,Accommodate

Simulation: `sim subgame-perfection-threats` shows the paths, and `sim subgame-perfection-threats --play` lets you choose.

## Start from this template
```
title: My Credible Threats (Subgame Perfection) situation
players: two
timing: sequential
interaction: one-shot
information: perfect
payoff: mixed
commitment: yes
domain: business, military, politics
notes: Describe your situation here. Replace the example options with your own.
```

# Folk Theorem: Sustaining Cooperation

In a repeated game where the future matters enough, almost any outcome that beats each side's worst outcome can be sustained as an equilibrium, because deviation can be punished. Cooperation is therefore possible, but not automatic.

## Traits and what each one means
- players = two: You and one counterpart. Name them in the title, for example 'me and my landlord'.
- timing = simultaneous: Everyone chooses without seeing the others' choices. Write each side's options down before anyone reveals anything.
- interaction = repeated: It recurs. Say how many rounds, and how much the future matters to each side. A longer, more valuable future usually supports cooperation.
- information = perfect: Everyone sees the same facts. Include every relevant fact in the description, because nothing is hidden.
- payoff = mixed: Both can gain or both can lose. Write what each side gains from cooperating and what it gains from competing.
- communication = yes: You can talk before or during the decision. Say what can be promised, and whether promises are binding.
- enforcement = no: Nothing forces anyone to keep a deal. Agreements rely on trust or self-interest.

## Steps to set up your own version
1. Title and players: name the situation and who is involved.
2. Options: list each player's choices, using the game's own options from its playbook.
3. Payoffs or stakes: say what each outcome is worth to each player. For matrix games, fill in the payoff grid.
4. Information and timing: say who moves when, and who knows what.
5. Traits: copy the values in the template file. Change any that do not fit your situation.
6. Check: run `advise` on your file, and compare with the game's simulation with `sim` if one exists.

## Options to model
- Option idea 1: Make the future valuable to both sides; cooperation is sustainable only when the shadow of the future is long.
- Option idea 2: Agree a punishment for defection in advance, and make it proportionate and clear.
- Option idea 3: Include a path back to cooperation after punishment, so one mistake does not end the relationship.

## Payoff grid
Rows (you): Cooperate, Defect. Columns (them): Cooperate, Defect.
Enter it with: solve "3,3 0,5; 5,0 1,1" --rows Cooperate,Defect --cols Cooperate,Defect

Simulation: `sim folk-theorem-cooperation` shows the paths, and `sim folk-theorem-cooperation --play` lets you choose.

## Start from this template
```
title: My Folk Theorem: Sustaining Cooperation situation
players: two
timing: simultaneous
interaction: repeated
information: perfect
payoff: mixed
communication: yes
enforcement: no
domain: business, economy, everyday
notes: Describe your situation here. Replace the example options with your own.
```

# Incomplete Contracts and Incentives

No contract can list every future event. Parties must decide who has control over unforeseen decisions, and how to share the gains from investments, so that each has the incentive to invest and to act well.

## Traits and what each one means
- players = two: You and one counterpart. Name them in the title, for example 'me and my landlord'.
- timing = sequential: Decisions come in turns. Write who moves first, and what each mover can see when they choose.
- interaction = repeated: It recurs. Say how many rounds, and how much the future matters to each side. A longer, more valuable future usually supports cooperation.
- information = imperfect: Someone holds private information. Say who knows what, and what each side is guessing about the other.
- payoff = mixed: Both can gain or both can lose. Write what each side gains from cooperating and what it gains from competing.
- enforcement = yes: There are binding agreements, penalties or courts. Name the penalty and who can impose it.
- bargaining = yes: You are dividing something. State the total, and each side's alternative if no deal is reached (its outside option).

## Steps to set up your own version
1. Title and players: name the situation and who is involved.
2. Options: list each player's choices, using the game's own options from its playbook.
3. Payoffs or stakes: say what each outcome is worth to each player. For matrix games, fill in the payoff grid.
4. Information and timing: say who moves when, and who knows what.
5. Traits: copy the values in the template file. Change any that do not fit your situation.
6. Check: run `advise` on your file, and compare with the game's simulation with `sim` if one exists.

## Options to model
- Option idea 1: Agree who controls decisions the contract does not cover, and why that party is the right one.
- Option idea 2: Share the gains from specific investments, so each side benefits from investing.
- Option idea 3: Use clear review points where the contract can be renegotiated fairly.

## Payoff grid
Rows (you): Specify in contract, Leave open. Columns (them): Invest, Hold back.
Enter it with: solve "2,2 -1,1; 1,-1 0,0" --rows Specify in contract,Leave open --cols Invest,Hold back

Simulation: `sim contract-incentives-incomplete` shows the paths, and `sim contract-incentives-incomplete --play` lets you choose.

## Start from this template
```
title: My Incomplete Contracts and Incentives situation
players: two
timing: sequential
interaction: repeated
information: imperfect
payoff: mixed
enforcement: yes
bargaining: yes
domain: business, work, economy
notes: Describe your situation here. Replace the example options with your own.
```

# Global Games (Coordination Under Noisy Information)

When everyone has a slightly different private signal about the fundamentals, coordination becomes unique and predictable: each person acts based on their own signal and what they think others will do, and a threshold emerges.

## Traits and what each one means
- players = many: Three or more players. Either list each player, or model the rest as one group with a shared outcome. Many-player games need the group's total effect spelled out.
- timing = simultaneous: Everyone chooses without seeing the others' choices. Write each side's options down before anyone reveals anything.
- interaction = one-shot: The situation happens once. Do not plan on future reciprocity, and say so in the description.
- information = imperfect: Someone holds private information. Say who knows what, and what each side is guessing about the other.
- payoff = common-interest: You want the same outcome. The challenge is coordinating on it, not conflicting over it.
- communication = no: No talking or signalling is possible. Actions are the only information.

## Steps to set up your own version
1. Title and players: name the situation and who is involved.
2. Options: list each player's choices, using the game's own options from its playbook.
3. Payoffs or stakes: say what each outcome is worth to each player. For matrix games, fill in the payoff grid.
4. Information and timing: say who moves when, and who knows what.
5. Traits: copy the values in the template file. Change any that do not fit your situation.
6. Check: run `advise` on your file, and compare with the game's simulation with `sim` if one exists.

## Options to model
- Option idea 1: Estimate the threshold: how strong must the fundamentals be before others act together?
- Option idea 2: Use your own signal carefully; noise is what turns a multiple-equilibrium problem into a predictable one.
- Option idea 3: Watch whether public information is shifting the threshold, since public signals can dominate private ones.

## Payoff grid
Rows (you): Invest, Hold. Columns (them): Invest, Hold.
Enter it with: solve "2,2 -1,1; 1,-1 0,0" --rows Invest,Hold --cols Invest,Hold

Simulation: `sim global-games-coordination` shows the paths, and `sim global-games-coordination --play` lets you choose.

## Start from this template
```
title: My Global Games (Coordination Under Noisy Information) situation
players: many
timing: simultaneous
interaction: one-shot
information: imperfect
payoff: common-interest
communication: no
domain: economy, business, government
notes: Describe your situation here. Replace the example options with your own.
```

# Rock-Paper-Scissors

Two players choose rock, paper or scissors at the same time. Each choice beats one and loses to another, so the only sound strategy is to be unpredictable.

## Traits and what each one means
- players = two: You and one counterpart. Name them in the title, for example 'me and my landlord'.
- timing = simultaneous: Everyone chooses without seeing the others' choices. Write each side's options down before anyone reveals anything.
- interaction = one-shot: The situation happens once. Do not plan on future reciprocity, and say so in the description.
- information = perfect: Everyone sees the same facts. Include every relevant fact in the description, because nothing is hidden.
- payoff = zero-sum: One side's gain is the other's loss, as in a fixed prize or winner-takes-all. The total never changes.
- communication = no: No talking or signalling is possible. Actions are the only information.

## Steps to set up your own version
1. Title and players: name the situation and who is involved.
2. Options: list each player's choices, using the game's own options from its playbook.
3. Payoffs or stakes: say what each outcome is worth to each player. For matrix games, fill in the payoff grid.
4. Information and timing: say who moves when, and who knows what.
5. Traits: copy the values in the template file. Change any that do not fit your situation.
6. Check: run `advise` on your file, and compare with the game's simulation with `sim` if one exists.

## Options to model
- Option idea 1: Randomise evenly: each option one third of the time, and avoid sequences that feel random but repeat.
- Option idea 2: Watch for the opponent's biases, such as opening with rock or repeating after a win, and exploit only once the pattern is clear.
- Option idea 3: Do not chase the last result: switching to beat the previous winning move is a pattern that a learning opponent will exploit.

## Payoff grid
Rows (you): Rock, Paper, Scissors. Columns (them): Rock, Paper, Scissors.
Enter it with: solve "0,0 -1,1 1,-1; 1,-1 0,0 -1,1; -1,1 1,-1 0,0" --rows Rock,Paper,Scissors --cols Rock,Paper,Scissors

Simulation: `sim rock-paper-scissors` shows the paths, and `sim rock-paper-scissors --play` lets you choose.

## Start from this template
```
title: My Rock-Paper-Scissors situation
players: two
timing: simultaneous
interaction: one-shot
information: perfect
payoff: zero-sum
communication: no
domain: games
notes: Describe your situation here. Replace the example options with your own.
```

# Tic-Tac-Toe and Perfect Play

A small, fully solved game. With perfect play from both sides, the result is a draw, and every losing move can be identified in advance. It is the standard example of how minimax search works.

## Traits and what each one means
- players = two: You and one counterpart. Name them in the title, for example 'me and my landlord'.
- timing = sequential: Decisions come in turns. Write who moves first, and what each mover can see when they choose.
- interaction = one-shot: The situation happens once. Do not plan on future reciprocity, and say so in the description.
- information = perfect: Everyone sees the same facts. Include every relevant fact in the description, because nothing is hidden.
- payoff = zero-sum: One side's gain is the other's loss, as in a fixed prize or winner-takes-all. The total never changes.
- communication = no: No talking or signalling is possible. Actions are the only information.

## Steps to set up your own version
1. Title and players: name the situation and who is involved.
2. Options: list each player's choices, using the game's own options from its playbook.
3. Payoffs or stakes: say what each outcome is worth to each player. For matrix games, fill in the payoff grid.
4. Information and timing: say who moves when, and who knows what.
5. Traits: copy the values in the template file. Change any that do not fit your situation.
6. Check: run `advise` on your file, and compare with the game's simulation with `sim` if one exists.

## Options to model
- Option idea 1: Take the centre first when it is open; it is part of more winning lines than any other square.
- Option idea 2: Block an opponent who has two in a row, and take a winning square if you have one.
- Option idea 3: Look for forks: a move that creates two threats at once wins against a player who only blocks one.

## Payoff grid
Rows (you): Take the centre, Take a corner. Columns (them): Opponent blocks, Opponent ignores.
Enter it with: solve "0,0 -1,1; 1,-1 -2,2" --rows Take the centre,Take a corner --cols Opponent blocks,Opponent ignores

Simulation: `sim tic-tac-toe-minimax` shows the paths, and `sim tic-tac-toe-minimax --play` lets you choose.

## Start from this template
```
title: My Tic-Tac-Toe and Perfect Play situation
players: two
timing: sequential
interaction: one-shot
information: perfect
payoff: zero-sum
communication: no
domain: games
notes: Describe your situation here. Replace the example options with your own.
```

# Liar's Dice

Players roll hidden dice and bid on how many of a given face are showing across everyone's dice. Each bid must be higher than the last, and a player may challenge the previous bid. Success depends on reading probabilities and on bluffing well.

## Traits and what each one means
- players = many: Three or more players. Either list each player, or model the rest as one group with a shared outcome. Many-player games need the group's total effect spelled out.
- timing = sequential: Decisions come in turns. Write who moves first, and what each mover can see when they choose.
- interaction = repeated: It recurs. Say how many rounds, and how much the future matters to each side. A longer, more valuable future usually supports cooperation.
- information = imperfect: Someone holds private information. Say who knows what, and what each side is guessing about the other.
- payoff = zero-sum: One side's gain is the other's loss, as in a fixed prize or winner-takes-all. The total never changes.
- communication = no: No talking or signalling is possible. Actions are the only information.

## Steps to set up your own version
1. Title and players: name the situation and who is involved.
2. Options: list each player's choices, using the game's own options from its playbook.
3. Payoffs or stakes: say what each outcome is worth to each player. For matrix games, fill in the payoff grid.
4. Information and timing: say who moves when, and who knows what.
5. Traits: copy the values in the template file. Change any that do not fit your situation.
6. Check: run `advise` on your file, and compare with the game's simulation with `sim` if one exists.

## Options to model
- Option idea 1: Estimate the expected count of a face across all dice: each unseen die shows a given face with probability one sixth.
- Option idea 2: Challenge when the bid is above the expected count by a clear margin; accept when the bid is within the normal range.
- Option idea 3: Bluff occasionally, with a reason: bid high on a face you hold several of, so the bid looks like a strong hand.

## Payoff grid
Rows (you): Bluff, Bid honestly. Columns (them): Call, Believe.
Enter it with: solve "1,-1 -1,1; -1,1 1,-1" --rows Bluff,Bid honestly --cols Call,Believe

Simulation: `sim liars-dice` shows the paths, and `sim liars-dice --play` lets you choose.

## Start from this template
```
title: My Liar's Dice situation
players: many
timing: sequential
interaction: repeated
information: imperfect
payoff: zero-sum
communication: no
domain: games
notes: Describe your situation here. Replace the example options with your own.
```

# All-Pay Contest (Tug of War and Lobbying Races)

Every contestant pays their effort whether or not they win, and the prize goes to the highest effort. Tug of war, lobbying races and litigation arms races follow this pattern, and they often dissipate far more than the prize is worth.

## Traits and what each one means
- players = two: You and one counterpart. Name them in the title, for example 'me and my landlord'.
- timing = simultaneous: Everyone chooses without seeing the others' choices. Write each side's options down before anyone reveals anything.
- interaction = one-shot: The situation happens once. Do not plan on future reciprocity, and say so in the description.
- information = imperfect: Someone holds private information. Say who knows what, and what each side is guessing about the other.
- payoff = zero-sum: One side's gain is the other's loss, as in a fixed prize or winner-takes-all. The total never changes.
- commitment = no: Every move can be reversed. Note any reversals that are cheap or expensive.

## Steps to set up your own version
1. Title and players: name the situation and who is involved.
2. Options: list each player's choices, using the game's own options from its playbook.
3. Payoffs or stakes: say what each outcome is worth to each player. For matrix games, fill in the payoff grid.
4. Information and timing: say who moves when, and who knows what.
5. Traits: copy the values in the template file. Change any that do not fit your situation.
6. Check: run `advise` on your file, and compare with the game's simulation with `sim` if one exists.

## Options to model
- Option idea 1: Before entering, compare the prize with the total you would need to spend to win; contests often cost more than the prize.
- Option idea 2: Consider whether you can win with less effort through a different route, such as a better proposal or a partner.
- Option idea 3: If you have a cost advantage, use it: a higher-cost rival may choose to stop, which lets you win cheaply.

## Payoff grid
Rows (you): High effort, Low effort. Columns (them): Rival high effort, Rival low effort.
Enter it with: solve "-1,-1 2,-2; -2,2 1,1" --rows High effort,Low effort --cols Rival high effort,Rival low effort

Simulation: `sim all-pay-contest` shows the paths, and `sim all-pay-contest --play` lets you choose.

## Start from this template
```
title: My All-Pay Contest (Tug of War and Lobbying Races) situation
players: two
timing: simultaneous
interaction: one-shot
information: imperfect
payoff: zero-sum
commitment: no
domain: games, politics, business, work
notes: Describe your situation here. Replace the example options with your own.
```

# Lanchester's Laws (Combat Attrition)

A model of how forces grind each other down. Under the square law, a force's fighting power grows with the square of its numbers, so concentration of force matters more than the size of the whole. Under the linear law, every unit counts equally.

## Traits and what each one means
- players = two: You and one counterpart. Name them in the title, for example 'me and my landlord'.
- timing = sequential: Decisions come in turns. Write who moves first, and what each mover can see when they choose.
- interaction = one-shot: The situation happens once. Do not plan on future reciprocity, and say so in the description.
- information = perfect: Everyone sees the same facts. Include every relevant fact in the description, because nothing is hidden.
- payoff = zero-sum: One side's gain is the other's loss, as in a fixed prize or winner-takes-all. The total never changes.
- commitment = no: Every move can be reversed. Note any reversals that are cheap or expensive.

## Steps to set up your own version
1. Title and players: name the situation and who is involved.
2. Options: list each player's choices, using the game's own options from its playbook.
3. Payoffs or stakes: say what each outcome is worth to each player. For matrix games, fill in the payoff grid.
4. Information and timing: say who moves when, and who knows what.
5. Traits: copy the values in the template file. Change any that do not fit your situation.
6. Check: run `advise` on your file, and compare with the game's simulation with `sim` if one exists.

## Options to model
- Option idea 1: Concentrate force on a single point, rather than spreading it: under the square law, a concentrated force gains a disproportionate advantage.
- Option idea 2: Avoid engaging a larger force in a way that spreads your units across several fronts.
- Option idea 3: Choose the type of engagement: aimed, long-range contests favour the larger force, while close, unaimed fights reduce that advantage.

## Payoff grid
Rows (you): Concentrate forces, Spread forces. Columns (them): Concentrate forces, Spread forces.
Enter it with: solve "0,0 2,-1; -1,2 1,1" --rows Concentrate forces,Spread forces --cols Concentrate forces,Spread forces

Simulation: `sim lanchester-combat` shows the paths, and `sim lanchester-combat --play` lets you choose.

## Start from this template
```
title: My Lanchester's Laws (Combat Attrition) situation
players: two
timing: sequential
interaction: one-shot
information: perfect
payoff: zero-sum
commitment: no
domain: military, games
notes: Describe your situation here. Replace the example options with your own.
```

# Secretary Problem (Optimal Stopping)

You interview candidates one at a time and must accept or reject each on the spot, with no recall. The best strategy rejects the first portion of candidates to learn the benchmark, then picks the next one who beats it. This also describes choosing a home, a partner or a job.

## Traits and what each one means
- players = two: You and one counterpart. Name them in the title, for example 'me and my landlord'.
- timing = sequential: Decisions come in turns. Write who moves first, and what each mover can see when they choose.
- interaction = one-shot: The situation happens once. Do not plan on future reciprocity, and say so in the description.
- information = imperfect: Someone holds private information. Say who knows what, and what each side is guessing about the other.
- payoff = common-interest: You want the same outcome. The challenge is coordinating on it, not conflicting over it.
- communication = no: No talking or signalling is possible. Actions are the only information.

## Steps to set up your own version
1. Title and players: name the situation and who is involved.
2. Options: list each player's choices, using the game's own options from its playbook.
3. Payoffs or stakes: say what each outcome is worth to each player. For matrix games, fill in the payoff grid.
4. Information and timing: say who moves when, and who knows what.
5. Traits: copy the values in the template file. Change any that do not fit your situation.
6. Check: run `advise` on your file, and compare with the game's simulation with `sim` if one exists.

## Options to model
- Option idea 1: Set a learning period: observe about a third of the options without committing, to set a benchmark.
- Option idea 2: After the learning period, accept the first option that beats the benchmark, even if you hope for better.
- Option idea 3: If the options are not all known in advance or cannot be ranked, use the rule of thumb: decide earlier than your instinct says.

## Payoff grid
Rows (you): Accept the candidate now, Wait for a better one. Columns (them): Candidate is good, Candidate is poor.
Enter it with: solve "2,1 0,0; 1,1 2,0" --rows Accept the candidate now,Wait for a better one --cols Candidate is good,Candidate is poor

Simulation: `sim secretary-problem` shows the paths, and `sim secretary-problem --play` lets you choose.

## Start from this template
```
title: My Secretary Problem (Optimal Stopping) situation
players: two
timing: sequential
interaction: one-shot
information: imperfect
payoff: common-interest
communication: no
domain: everyday, work
notes: Describe your situation here. Replace the example options with your own.
```

# Explore or Exploit (Multi-Armed Bandit)

You choose repeatedly between options whose payoffs are unknown. Trying new options gathers information; using the best known option earns reward now. Balancing these is the core of learning, from restaurants to research and clinical trials.

## Traits and what each one means
- players = two: You and one counterpart. Name them in the title, for example 'me and my landlord'.
- timing = sequential: Decisions come in turns. Write who moves first, and what each mover can see when they choose.
- interaction = repeated: It recurs. Say how many rounds, and how much the future matters to each side. A longer, more valuable future usually supports cooperation.
- information = imperfect: Someone holds private information. Say who knows what, and what each side is guessing about the other.
- payoff = common-interest: You want the same outcome. The challenge is coordinating on it, not conflicting over it.
- communication = no: No talking or signalling is possible. Actions are the only information.

## Steps to set up your own version
1. Title and players: name the situation and who is involved.
2. Options: list each player's choices, using the game's own options from its playbook.
3. Payoffs or stakes: say what each outcome is worth to each player. For matrix games, fill in the payoff grid.
4. Information and timing: say who moves when, and who knows what.
5. Traits: copy the values in the template file. Change any that do not fit your situation.
6. Check: run `advise` on your file, and compare with the game's simulation with `sim` if one exists.

## Options to model
- Option idea 1: Explore more early, when there is a long time to benefit from what you learn, and exploit more as the horizon shortens.
- Option idea 2: Give options that have been tried little a fair chance, rather than dismissing them after one bad result.
- Option idea 3: Use simple rules that work well in practice: try the option with the best optimistic estimate, or sample in proportion to your belief that each is best.

## Payoff grid
Rows (you): Explore a new option, Exploit the known option. Columns (them): New option is good, New option is poor.
Enter it with: solve "2,0 0,0; 1,1 1,1" --rows Explore a new option,Exploit the known option --cols New option is good,New option is poor

Simulation: `sim explore-exploit-bandit` shows the paths, and `sim explore-exploit-bandit --play` lets you choose.

## Start from this template
```
title: My Explore or Exploit (Multi-Armed Bandit) situation
players: two
timing: sequential
interaction: repeated
information: imperfect
payoff: common-interest
communication: no
domain: everyday, work, business, economy
notes: Describe your situation here. Replace the example options with your own.
```

# Team Production and Shirking

A team's output depends on everyone's effort, but each member's contribution is hard to see. Each member can shirk while the others carry the output, so teams need monitoring, shared rewards or peer pressure to keep effort up.

## Traits and what each one means
- players = many: Three or more players. Either list each player, or model the rest as one group with a shared outcome. Many-player games need the group's total effect spelled out.
- timing = simultaneous: Everyone chooses without seeing the others' choices. Write each side's options down before anyone reveals anything.
- interaction = repeated: It recurs. Say how many rounds, and how much the future matters to each side. A longer, more valuable future usually supports cooperation.
- information = imperfect: Someone holds private information. Say who knows what, and what each side is guessing about the other.
- payoff = mixed: Both can gain or both can lose. Write what each side gains from cooperating and what it gains from competing.
- communication = yes: You can talk before or during the decision. Say what can be promised, and whether promises are binding.
- enforcement = no: Nothing forces anyone to keep a deal. Agreements rely on trust or self-interest.

## Steps to set up your own version
1. Title and players: name the situation and who is involved.
2. Options: list each player's choices, using the game's own options from its playbook.
3. Payoffs or stakes: say what each outcome is worth to each player. For matrix games, fill in the payoff grid.
4. Information and timing: say who moves when, and who knows what.
5. Traits: copy the values in the template file. Change any that do not fit your situation.
6. Check: run `advise` on your file, and compare with the game's simulation with `sim` if one exists.

## Options to model
- Option idea 1: Make individual contributions visible through clear tasks, deliverables and regular updates.
- Option idea 2: Tie a meaningful part of rewards to individual results, not just the team total, so effort is rewarded.
- Option idea 3: Set peer review or rotating responsibility so that shirking is noticed by the people who share the output.

## Payoff grid
Rows (you): Work, Shirk. Columns (them): Work, Shirk.
Enter it with: solve "3,3 0,4; 4,0 1,1" --rows Work,Shirk --cols Work,Shirk

Simulation: `sim team-production-shirking` shows the paths, and `sim team-production-shirking --play` lets you choose.

## Start from this template
```
title: My Team Production and Shirking situation
players: many
timing: simultaneous
interaction: repeated
information: imperfect
payoff: mixed
communication: yes
enforcement: no
domain: work, business
notes: Describe your situation here. Replace the example options with your own.
```

# Playing Against an AI Opponent

When you play against an AI in a game, the opponent may follow a fixed rule, learn your habits, or play near equilibrium. The best response depends on which kind it is: against a fixed or weak bot, exploit its pattern; against a strong or adaptive one, play close to equilibrium and avoid predictable patterns.

## Traits and what each one means
- players = two: You and one counterpart. Name them in the title, for example 'me and my landlord'.
- timing = sequential: Decisions come in turns. Write who moves first, and what each mover can see when they choose.
- interaction = repeated: It recurs. Say how many rounds, and how much the future matters to each side. A longer, more valuable future usually supports cooperation.
- information = imperfect: Someone holds private information. Say who knows what, and what each side is guessing about the other.
- payoff = zero-sum: One side's gain is the other's loss, as in a fixed prize or winner-takes-all. The total never changes.
- communication = no: No talking or signalling is possible. Actions are the only information.

## Steps to set up your own version
1. Title and players: name the situation and who is involved.
2. Options: list each player's choices, using the game's own options from its playbook.
3. Payoffs or stakes: say what each outcome is worth to each player. For matrix games, fill in the payoff grid.
4. Information and timing: say who moves when, and who knows what.
5. Traits: copy the values in the template file. Change any that do not fit your situation.
6. Check: run `advise` on your file, and compare with the game's simulation with `sim` if one exists.

## Options to model
- Option idea 1: Observe first: spend a few rounds identifying whether the AI is fixed, adaptive or near-optimal before committing to a plan.
- Option idea 2: Against a fixed-rule opponent, find its predictable response and exploit it; this is usually where the largest gains are.
- Option idea 3: Against an adaptive opponent, randomise and avoid repeating winning moves, since it will learn to counter them.

## Payoff grid
Rows (you): Exploit its habit, Play the equilibrium. Columns (them): Bot repeats, Bot adapts.
Enter it with: solve "3,1 1,0; 2,2 2,2" --rows Exploit its habit,Play the equilibrium --cols Bot repeats,Bot adapts

Simulation: `sim ai-opponent-exploitation` shows the paths, and `sim ai-opponent-exploitation --play` lets you choose.

## Start from this template
```
title: My Playing Against an AI Opponent situation
players: two
timing: sequential
interaction: repeated
information: imperfect
payoff: zero-sum
communication: no
domain: games
notes: Describe your situation here. Replace the example options with your own.
```

# Algorithmic Collusion (AI Pricing Agents)

Pricing algorithms that learn from market outcomes can end up charging high prices together without communicating, because each learns to punish price cuts. This is tacit collusion produced by learning rules, and it raises questions for competition policy.

## Traits and what each one means
- players = two: You and one counterpart. Name them in the title, for example 'me and my landlord'.
- timing = simultaneous: Everyone chooses without seeing the others' choices. Write each side's options down before anyone reveals anything.
- interaction = repeated: It recurs. Say how many rounds, and how much the future matters to each side. A longer, more valuable future usually supports cooperation.
- information = perfect: Everyone sees the same facts. Include every relevant fact in the description, because nothing is hidden.
- payoff = mixed: Both can gain or both can lose. Write what each side gains from cooperating and what it gains from competing.
- communication = no: No talking or signalling is possible. Actions are the only information.
- enforcement = no: Nothing forces anyone to keep a deal. Agreements rely on trust or self-interest.

## Steps to set up your own version
1. Title and players: name the situation and who is involved.
2. Options: list each player's choices, using the game's own options from its playbook.
3. Payoffs or stakes: say what each outcome is worth to each player. For matrix games, fill in the payoff grid.
4. Information and timing: say who moves when, and who knows what.
5. Traits: copy the values in the template file. Change any that do not fit your situation.
6. Check: run `advise` on your file, and compare with the game's simulation with `sim` if one exists.

## Options to model
- Option idea 1: For firms: do not assume that a rival's algorithm will compete aggressively; learning systems may settle on higher prices with no agreement.
- Option idea 2: For firms: review what your pricing software is optimising, and check whether it is punishing rivals' price cuts; this is a risk to compliance.
- Option idea 3: For regulators: monitor prices and outcomes over time, since the absence of communication does not guarantee competitive behaviour.

## Payoff grid
Rows (you): Price high, Price low. Columns (them): Price high, Price low.
Enter it with: solve "3,3 0,5; 5,0 1,1" --rows Price high,Price low --cols Price high,Price low

Simulation: `sim algorithmic-collusion` shows the paths, and `sim algorithmic-collusion --play` lets you choose.

## Start from this template
```
title: My Algorithmic Collusion (AI Pricing Agents) situation
players: two
timing: simultaneous
interaction: repeated
information: perfect
payoff: mixed
communication: no
enforcement: no
domain: business, economy
notes: Describe your situation here. Replace the example options with your own.
```

# Self-Play and AI Learning Dynamics

Two learning agents improve by playing each other. Their strategies can cycle, drift or converge to an equilibrium, depending on how they learn. Understanding these dynamics matters when AI systems negotiate, compete or cooperate with one another.

## Traits and what each one means
- players = two: You and one counterpart. Name them in the title, for example 'me and my landlord'.
- timing = simultaneous: Everyone chooses without seeing the others' choices. Write each side's options down before anyone reveals anything.
- interaction = repeated: It recurs. Say how many rounds, and how much the future matters to each side. A longer, more valuable future usually supports cooperation.
- information = perfect: Everyone sees the same facts. Include every relevant fact in the description, because nothing is hidden.
- payoff = mixed: Both can gain or both can lose. Write what each side gains from cooperating and what it gains from competing.
- communication = no: No talking or signalling is possible. Actions are the only information.

## Steps to set up your own version
1. Title and players: name the situation and who is involved.
2. Options: list each player's choices, using the game's own options from its playbook.
3. Payoffs or stakes: say what each outcome is worth to each player. For matrix games, fill in the payoff grid.
4. Information and timing: say who moves when, and who knows what.
5. Traits: copy the values in the template file. Change any that do not fit your situation.
6. Check: run `advise` on your file, and compare with the game's simulation with `sim` if one exists.

## Options to model
- Option idea 1: Expect cycling in games with no pure equilibrium: stable convergence needs a method that averages strategies over time.
- Option idea 2: Use opponent modelling only when the model is updated; a stale model is exploited by an agent that changes.
- Option idea 3: For designers: test learning agents against a diverse set of opponents, not only copies of themselves.

## Payoff grid
Rows (you): Learn to cooperate, Learn to defect. Columns (them): Learn to cooperate, Learn to defect.
Enter it with: solve "3,3 0,5; 5,0 1,1" --rows Learn to cooperate,Learn to defect --cols Learn to cooperate,Learn to defect

Simulation: `sim ai-self-play-learning` shows the paths, and `sim ai-self-play-learning --play` lets you choose.

## Start from this template
```
title: My Self-Play and AI Learning Dynamics situation
players: two
timing: simultaneous
interaction: repeated
information: perfect
payoff: mixed
communication: no
domain: games, business, economy
notes: Describe your situation here. Replace the example options with your own.
```

# Dating and Partner Search

Two people look for a partner while meeting candidates one at a time. Each must decide whether to commit, and the other person is making the same choice. Patience, realistic expectations and clear communication decide whether both find good matches.

## Traits and what each one means
- players = many: Three or more players. Either list each player, or model the rest as one group with a shared outcome. Many-player games need the group's total effect spelled out.
- timing = sequential: Decisions come in turns. Write who moves first, and what each mover can see when they choose.
- interaction = one-shot: The situation happens once. Do not plan on future reciprocity, and say so in the description.
- information = imperfect: Someone holds private information. Say who knows what, and what each side is guessing about the other.
- payoff = mixed: Both can gain or both can lose. Write what each side gains from cooperating and what it gains from competing.
- communication = yes: You can talk before or during the decision. Say what can be promised, and whether promises are binding.

## Steps to set up your own version
1. Title and players: name the situation and who is involved.
2. Options: list each player's choices, using the game's own options from its playbook.
3. Payoffs or stakes: say what each outcome is worth to each player. For matrix games, fill in the payoff grid.
4. Information and timing: say who moves when, and who knows what.
5. Traits: copy the values in the template file. Change any that do not fit your situation.
6. Check: run `advise` on your file, and compare with the game's simulation with `sim` if one exists.

## Options to model
- Option idea 1: Communicate what you want early and clearly; mismatched expectations waste the time of both sides.
- Option idea 2: Set a realistic benchmark from your experience, and be willing to commit once an option clearly meets it.
- Option idea 3: Recognise that the other person is also choosing: a good match may be reachable only if your own offer is credible.

## Payoff grid
Rows (you): Accept the first offer, Keep searching. Columns (them): Accept the first offer, Keep searching.
Enter it with: solve "2,2 0,1; 1,0 1,1" --rows Accept the first offer,Keep searching --cols Accept the first offer,Keep searching

Simulation: `sim dating-marriage-market-search` shows the paths, and `sim dating-marriage-market-search --play` lets you choose.

## Start from this template
```
title: My Dating and Partner Search situation
players: many
timing: sequential
interaction: one-shot
information: imperfect
payoff: mixed
communication: yes
domain: everyday
notes: Describe your situation here. Replace the example options with your own.
```

# Poker and Bluffing

Players hold private cards and bet. Bluffing works only if it is unpredictable and sometimes made, so the game is about mixing strategies and reading opponents, not about guessing outcomes.

## Traits and what each one means
- players = two: You and one counterpart. Name them in the title, for example 'me and my landlord'.
- timing = sequential: Decisions come in turns. Write who moves first, and what each mover can see when they choose.
- interaction = repeated: It recurs. Say how many rounds, and how much the future matters to each side. A longer, more valuable future usually supports cooperation.
- information = imperfect: Someone holds private information. Say who knows what, and what each side is guessing about the other.
- payoff = zero-sum: One side's gain is the other's loss, as in a fixed prize or winner-takes-all. The total never changes.
- communication = no: No talking or signalling is possible. Actions are the only information.

## Steps to set up your own version
1. Title and players: name the situation and who is involved.
2. Options: list each player's choices, using the game's own options from its playbook.
3. Payoffs or stakes: say what each outcome is worth to each player. For matrix games, fill in the payoff grid.
4. Information and timing: say who moves when, and who knows what.
5. Traits: copy the values in the template file. Change any that do not fit your situation.
6. Check: run `advise` on your file, and compare with the game's simulation with `sim` if one exists.

## Options to model
- Option idea 1: Mix your play: a predictable pattern is exploited, so vary bet sizes and lines with similar hands.
- Option idea 2: Compare the price of a call with your chance of winning (pot odds) before deciding; fold when the price is too high.
- Option idea 3: Exploit clear tendencies only after you have enough evidence; overreacting to small samples loses money.

## Payoff grid
Rows (you): Bet with a bluff, Check with a weak hand. Columns (them): Call, Fold.
Enter it with: solve "1,-1 -1,1; -1,1 0,0" --rows Bet with a bluff,Check with a weak hand --cols Call,Fold

Simulation: `sim poker-bluffing` shows the paths, and `sim poker-bluffing --play` lets you choose.

## Start from this template
```
title: My Poker and Bluffing situation
players: two
timing: sequential
interaction: repeated
information: imperfect
payoff: zero-sum
communication: no
domain: games
notes: Describe your situation here. Replace the example options with your own.
```

# Chess and Minimax Search

Both players see the full position and alternate moves. The best play can in principle be found by looking ahead, but in practice players use principles and calculation to choose moves that keep their options open.

## Traits and what each one means
- players = two: You and one counterpart. Name them in the title, for example 'me and my landlord'.
- timing = sequential: Decisions come in turns. Write who moves first, and what each mover can see when they choose.
- interaction = one-shot: The situation happens once. Do not plan on future reciprocity, and say so in the description.
- information = perfect: Everyone sees the same facts. Include every relevant fact in the description, because nothing is hidden.
- payoff = zero-sum: One side's gain is the other's loss, as in a fixed prize or winner-takes-all. The total never changes.
- communication = no: No talking or signalling is possible. Actions are the only information.

## Steps to set up your own version
1. Title and players: name the situation and who is involved.
2. Options: list each player's choices, using the game's own options from its playbook.
3. Payoffs or stakes: say what each outcome is worth to each player. For matrix games, fill in the payoff grid.
4. Information and timing: say who moves when, and who knows what.
5. Traits: copy the values in the template file. Change any that do not fit your situation.
6. Check: run `advise` on your file, and compare with the game's simulation with `sim` if one exists.

## Options to model
- Option idea 1: Before each move, check your opponent's forcing replies: checks, captures and threats, then choose the move that stays safe.
- Option idea 2: Look for forcing lines that win material or position; they limit the opponent's options more than quiet moves do.
- Option idea 3: Prefer positions where your pieces are active and your king is safe, rather than grabbing material that loosens your defence.

## Payoff grid
Rows (you): Attack, Develop. Columns (them): Opponent defends, Opponent counterattacks.
Enter it with: solve "1,1 -1,2; 0,0 1,1" --rows Attack,Develop --cols Opponent defends,Opponent counterattacks

Simulation: `sim chess-minimax` shows the paths, and `sim chess-minimax --play` lets you choose.

## Start from this template
```
title: My Chess and Minimax Search situation
players: two
timing: sequential
interaction: one-shot
information: perfect
payoff: zero-sum
communication: no
domain: games
notes: Describe your situation here. Replace the example options with your own.
```

# Guess-the-Average (Keynes Beauty Contest)

Each player picks a number and the one closest to a fraction of the group's average wins. Pure logic leads to zero, but real players stop at different depths of reasoning, so the winning move depends on predicting how others think.

## Traits and what each one means
- players = many: Three or more players. Either list each player, or model the rest as one group with a shared outcome. Many-player games need the group's total effect spelled out.
- timing = simultaneous: Everyone chooses without seeing the others' choices. Write each side's options down before anyone reveals anything.
- interaction = one-shot: The situation happens once. Do not plan on future reciprocity, and say so in the description.
- information = perfect: Everyone sees the same facts. Include every relevant fact in the description, because nothing is hidden.
- payoff = zero-sum: One side's gain is the other's loss, as in a fixed prize or winner-takes-all. The total never changes.
- communication = no: No talking or signalling is possible. Actions are the only information.

## Steps to set up your own version
1. Title and players: name the situation and who is involved.
2. Options: list each player's choices, using the game's own options from its playbook.
3. Payoffs or stakes: say what each outcome is worth to each player. For matrix games, fill in the payoff grid.
4. Information and timing: say who moves when, and who knows what.
5. Traits: copy the values in the template file. Change any that do not fit your situation.
6. Check: run `advise` on your file, and compare with the game's simulation with `sim` if one exists.

## Options to model
- Option idea 1: Estimate the typical depth of reasoning in your group; if most people are shallow thinkers, choose slightly below their likely average.
- Option idea 2: If everyone is perfectly rational, the answer is zero; if you are not sure, expect a mix and aim near the typical answer, not the extreme.
- Option idea 3: In markets, ask what others expect others to expect; prices often reflect that second-order guess rather than fundamentals.

## Payoff grid
Rows (you): Guess 1, Guess 2, Guess 3. Columns (them): Guess 1, Guess 2, Guess 3.
Enter it with: solve "1,1 2,0 2,0; 0,2 1,1 2,0; 0,2 0,2 1,1" --rows Guess 1,Guess 2,Guess 3 --cols Guess 1,Guess 2,Guess 3

Simulation: `sim keynes-beauty-contest` shows the paths, and `sim keynes-beauty-contest --play` lets you choose.

## Start from this template
```
title: My Guess-the-Average (Keynes Beauty Contest) situation
players: many
timing: simultaneous
interaction: one-shot
information: perfect
payoff: zero-sum
communication: no
domain: games, economy
notes: Describe your situation here. Replace the example options with your own.
```

# Dollar Auction and Escalation Traps

A dollar is auctioned, with the highest bidder paying their bid but the second-highest bidder also paying theirs. Both bidders can end up paying far more than the prize, because each is trapped by what they have already spent.

## Traits and what each one means
- players = two: You and one counterpart. Name them in the title, for example 'me and my landlord'.
- timing = sequential: Decisions come in turns. Write who moves first, and what each mover can see when they choose.
- interaction = one-shot: The situation happens once. Do not plan on future reciprocity, and say so in the description.
- information = perfect: Everyone sees the same facts. Include every relevant fact in the description, because nothing is hidden.
- payoff = zero-sum: One side's gain is the other's loss, as in a fixed prize or winner-takes-all. The total never changes.
- commitment = yes: Someone can commit publicly or irreversibly. Write the commitment mechanism, such as a signed contract or a visible step that cannot be undone.

## Steps to set up your own version
1. Title and players: name the situation and who is involved.
2. Options: list each player's choices, using the game's own options from its playbook.
3. Payoffs or stakes: say what each outcome is worth to each player. For matrix games, fill in the payoff grid.
4. Information and timing: say who moves when, and who knows what.
5. Traits: copy the values in the template file. Change any that do not fit your situation.
6. Check: run `advise` on your file, and compare with the game's simulation with `sim` if one exists.

## Options to model
- Option idea 1: Set your maximum price or spending limit before the contest starts, and stick to it.
- Option idea 2: Recognise sunk costs: what you have already spent should not decide whether you spend more.
- Option idea 3: Ask whether walking away now is better than the expected cost of continuing; often it is.

## Payoff grid
Rows (you): Stop bidding, Raise. Columns (them): Stop bidding, Raise.
Enter it with: solve "0,0 -1,1; 1,-1 -2,-2" --rows Stop bidding,Raise --cols Stop bidding,Raise

Simulation: `sim dollar-auction-escalation` shows the paths, and `sim dollar-auction-escalation --play` lets you choose.

## Start from this template
```
title: My Dollar Auction and Escalation Traps situation
players: two
timing: sequential
interaction: one-shot
information: perfect
payoff: zero-sum
commitment: yes
domain: games, business, military
notes: Describe your situation here. Replace the example options with your own.
```

# Prisoner's Dilemma

Each player is tempted to defect, yet both do better if both cooperate. Defection is dominant in a one-shot game, so the outcome is worse for everyone.

## Traits and what each one means
- players = two: You and one counterpart. Name them in the title, for example 'me and my landlord'.
- timing = simultaneous: Everyone chooses without seeing the others' choices. Write each side's options down before anyone reveals anything.
- interaction = one-shot: The situation happens once. Do not plan on future reciprocity, and say so in the description.
- payoff = mixed: Both can gain or both can lose. Write what each side gains from cooperating and what it gains from competing.
- enforcement = no: Nothing forces anyone to keep a deal. Agreements rely on trust or self-interest.

## Steps to set up your own version
1. Title and players: name the situation and who is involved.
2. Options: list each player's choices, using the game's own options from its playbook.
3. Payoffs or stakes: say what each outcome is worth to each player. For matrix games, fill in the payoff grid.
4. Information and timing: say who moves when, and who knows what.
5. Traits: copy the values in the template file. Change any that do not fit your situation.
6. Check: run `advise` on your file, and compare with the game's simulation with `sim` if one exists.

## Options to model
- Option idea 1: If the game is truly one-shot, defection is dominant. Do not expect cooperation to appear on its own.
- Option idea 2: Change the structure, not the choice: add binding contracts, penalties, or escrow so that defecting costs more than it gains.
- Option idea 3: If the relationship can be made repeated, switch to the repeated-game playbook.

## Payoff grid
Rows (you): Cooperate, Defect. Columns (them): Cooperate, Defect.
Enter it with: solve "3,3 0,5; 5,0 1,1" --rows Cooperate,Defect --cols Cooperate,Defect

Simulation: `sim prisoners-dilemma` shows the paths, and `sim prisoners-dilemma --play` lets you choose.

## Start from this template
```
title: My Prisoner's Dilemma situation
players: two
timing: simultaneous
interaction: one-shot
payoff: mixed
enforcement: no
domain: business, military, politics, everyday
notes: Describe your situation here. Replace the example options with your own.
```

# Repeated Prisoner's Dilemma

When the same players meet again and the future matters, cooperation can be sustained by the threat of future punishment (the folk theorem).

## Traits and what each one means
- players = two: You and one counterpart. Name them in the title, for example 'me and my landlord'.
- timing = simultaneous: Everyone chooses without seeing the others' choices. Write each side's options down before anyone reveals anything.
- interaction = repeated: It recurs. Say how many rounds, and how much the future matters to each side. A longer, more valuable future usually supports cooperation.
- information = perfect: Everyone sees the same facts. Include every relevant fact in the description, because nothing is hidden.
- payoff = mixed: Both can gain or both can lose. Write what each side gains from cooperating and what it gains from competing.

## Steps to set up your own version
1. Title and players: name the situation and who is involved.
2. Options: list each player's choices, using the game's own options from its playbook.
3. Payoffs or stakes: say what each outcome is worth to each player. For matrix games, fill in the payoff grid.
4. Information and timing: say who moves when, and who knows what.
5. Traits: copy the values in the template file. Change any that do not fit your situation.
6. Check: run `advise` on your file, and compare with the game's simulation with `sim` if one exists.

## Options to model
- Option idea 1: Start cooperative, then reciprocate: cooperate when they cooperate, retaliate when they defect.
- Option idea 2: Forgive occasionally after a punishment so one mistake does not lock in endless retaliation (generous Tit-for-Tat).
- Option idea 3: Make the future valuable: extend the relationship and raise the cost of ending it.

## Payoff grid
Rows (you): Cooperate, Defect. Columns (them): Cooperate, Defect.
Enter it with: solve "3,3 0,5; 5,0 1,1" --rows Cooperate,Defect --cols Cooperate,Defect

Simulation: `sim repeated-prisoners-dilemma` shows the paths, and `sim repeated-prisoners-dilemma --play` lets you choose.

## Start from this template
```
title: My Repeated Prisoner's Dilemma situation
players: two
timing: simultaneous
interaction: repeated
information: perfect
payoff: mixed
domain: business, politics, everyday, military
notes: Describe your situation here. Replace the example options with your own.
```

# Stag Hunt

Both players do best by cooperating on a risky joint action, but either can take a safe, lower-payoff option. Both outcomes are equilibria; the question is which one will happen.

## Traits and what each one means
- players = two: You and one counterpart. Name them in the title, for example 'me and my landlord'.
- timing = simultaneous: Everyone chooses without seeing the others' choices. Write each side's options down before anyone reveals anything.
- interaction = one-shot: The situation happens once. Do not plan on future reciprocity, and say so in the description.
- payoff = common-interest: You want the same outcome. The challenge is coordinating on it, not conflicting over it.
- communication = yes: You can talk before or during the decision. Say what can be promised, and whether promises are binding.

## Steps to set up your own version
1. Title and players: name the situation and who is involved.
2. Options: list each player's choices, using the game's own options from its playbook.
3. Payoffs or stakes: say what each outcome is worth to each player. For matrix games, fill in the payoff grid.
4. Information and timing: say who moves when, and who knows what.
5. Traits: copy the values in the template file. Change any that do not fit your situation.
6. Check: run `advise` on your file, and compare with the game's simulation with `sim` if one exists.

## Options to model
- Option idea 1: Compare the two equilibria: the risk-dominant one is the safer choice. If you doubt the other side, play safe.
- Option idea 2: Build trust before committing: communicate and make a credible pledge.
- Option idea 3: Start with small, reversible joint steps that show the other side is committed.

## Payoff grid
Rows (you): Stag, Hare. Columns (them): Stag, Hare.
Enter it with: solve "4,4 0,3; 3,0 3,3" --rows Stag,Hare --cols Stag,Hare

Simulation: `sim stag-hunt` shows the paths, and `sim stag-hunt --play` lets you choose.

## Start from this template
```
title: My Stag Hunt situation
players: two
timing: simultaneous
interaction: one-shot
payoff: common-interest
communication: yes
domain: work, business, politics, everyday
notes: Describe your situation here. Replace the example options with your own.
```

# Chicken (Hawk-Dove)

Each player prefers to hold firm while the other yields, but mutual firmness is disastrous. A credible commitment not to yield often wins.

## Traits and what each one means
- players = two: You and one counterpart. Name them in the title, for example 'me and my landlord'.
- timing = simultaneous: Everyone chooses without seeing the others' choices. Write each side's options down before anyone reveals anything.
- interaction = one-shot: The situation happens once. Do not plan on future reciprocity, and say so in the description.
- payoff = mixed: Both can gain or both can lose. Write what each side gains from cooperating and what it gains from competing.
- commitment = yes: Someone can commit publicly or irreversibly. Write the commitment mechanism, such as a signed contract or a visible step that cannot be undone.

## Steps to set up your own version
1. Title and players: name the situation and who is involved.
2. Options: list each player's choices, using the game's own options from its playbook.
3. Payoffs or stakes: say what each outcome is worth to each player. For matrix games, fill in the payoff grid.
4. Information and timing: say who moves when, and who knows what.
5. Traits: copy the values in the template file. Change any that do not fit your situation.
6. Check: run `advise` on your file, and compare with the game's simulation with `sim` if one exists.

## Options to model
- Option idea 1: Make your commitment visible and irreversible, for example by removing your own option to swerve.
- Option idea 2: If the other side has credibly committed, yield: a crash costs more than backing down.
- Option idea 3: Avoid random brinkmanship. Mixing produces high-variance disasters.

## Payoff grid
Rows (you): Swerve, Straight. Columns (them): Swerve, Straight.
Enter it with: solve "3,3 1,4; 4,1 0,0" --rows Swerve,Straight --cols Swerve,Straight

Simulation: `sim chicken` shows the paths, and `sim chicken --play` lets you choose.

## Start from this template
```
title: My Chicken (Hawk-Dove) situation
players: two
timing: simultaneous
interaction: one-shot
payoff: mixed
commitment: yes
domain: military, politics, business, games
notes: Describe your situation here. Replace the example options with your own.
```

# Battle of the Sexes

Both players want to coordinate, but they disagree about which joint outcome is best. The challenge is agreeing on a focal point.

## Traits and what each one means
- players = two: You and one counterpart. Name them in the title, for example 'me and my landlord'.
- timing = simultaneous: Everyone chooses without seeing the others' choices. Write each side's options down before anyone reveals anything.
- interaction = one-shot: The situation happens once. Do not plan on future reciprocity, and say so in the description.
- payoff = mixed: Both can gain or both can lose. Write what each side gains from cooperating and what it gains from competing.
- communication = yes: You can talk before or during the decision. Say what can be promised, and whether promises are binding.

## Steps to set up your own version
1. Title and players: name the situation and who is involved.
2. Options: list each player's choices, using the game's own options from its playbook.
3. Payoffs or stakes: say what each outcome is worth to each player. For matrix games, fill in the payoff grid.
4. Information and timing: say who moves when, and who knows what.
5. Traits: copy the values in the template file. Change any that do not fit your situation.
6. Check: run `advise` on your file, and compare with the game's simulation with `sim` if one exists.

## Options to model
- Option idea 1: Find a focal point both sides would accept, such as alternating turns.
- Option idea 2: Communicate before the decision and make a visible commitment.
- Option idea 3: Trade concessions in another dimension to move the outcome toward your preference.

## Payoff grid
Rows (you): Opera, Football. Columns (them): Opera, Football.
Enter it with: solve "2,1 0,0; 0,0 1,2" --rows Opera,Football --cols Opera,Football

Simulation: `sim battle-of-the-sexes` shows the paths, and `sim battle-of-the-sexes --play` lets you choose.

## Start from this template
```
title: My Battle of the Sexes situation
players: two
timing: simultaneous
interaction: one-shot
payoff: mixed
communication: yes
domain: everyday, business, work, politics
notes: Describe your situation here. Replace the example options with your own.
```

# Zero-Sum Games

One player's gain is exactly the other's loss. The safe approach is maximin: maximise your worst-case payoff. The best play is often a randomised mix that cannot be exploited.

## Traits and what each one means
- players = two: You and one counterpart. Name them in the title, for example 'me and my landlord'.
- timing = simultaneous: Everyone chooses without seeing the others' choices. Write each side's options down before anyone reveals anything.
- interaction = one-shot: The situation happens once. Do not plan on future reciprocity, and say so in the description.
- information = perfect: Everyone sees the same facts. Include every relevant fact in the description, because nothing is hidden.
- payoff = zero-sum: One side's gain is the other's loss, as in a fixed prize or winner-takes-all. The total never changes.

## Steps to set up your own version
1. Title and players: name the situation and who is involved.
2. Options: list each player's choices, using the game's own options from its playbook.
3. Payoffs or stakes: say what each outcome is worth to each player. For matrix games, fill in the payoff grid.
4. Information and timing: say who moves when, and who knows what.
5. Traits: copy the values in the template file. Change any that do not fit your situation.
6. Check: run `advise` on your file, and compare with the game's simulation with `sim` if one exists.

## Options to model
- Option idea 1: Compute your maximin (the best worst case) and play it.
- Option idea 2: If there is no saddle point, randomise with the equilibrium probabilities. Any predictable pattern will be exploited.
- Option idea 3: Track the opponent's tendencies, but exploit them only when the signal is strong, since unpredictability protects you.

## Payoff grid
Rows (you): Heads, Tails. Columns (them): Heads, Tails.
Enter it with: solve "1,-1 -1,1; -1,1 1,-1" --rows Heads,Tails --cols Heads,Tails

Simulation: `sim zero-sum-games` shows the paths, and `sim zero-sum-games --play` lets you choose.

## Start from this template
```
title: My Zero-Sum Games situation
players: two
timing: simultaneous
interaction: one-shot
information: perfect
payoff: zero-sum
domain: games, military, business
notes: Describe your situation here. Replace the example options with your own.
```

# Inspection Game

An inspector wants to catch violations and a potential violator wants to break the rules. Neither can be fully predictable, so the equilibrium is a random inspection schedule.

## Traits and what each one means
- players = two: You and one counterpart. Name them in the title, for example 'me and my landlord'.
- timing = simultaneous: Everyone chooses without seeing the others' choices. Write each side's options down before anyone reveals anything.
- interaction = one-shot: The situation happens once. Do not plan on future reciprocity, and say so in the description.
- information = imperfect: Someone holds private information. Say who knows what, and what each side is guessing about the other.
- payoff = mixed: Both can gain or both can lose. Write what each side gains from cooperating and what it gains from competing.
- enforcement = yes: There are binding agreements, penalties or courts. Name the penalty and who can impose it.

## Steps to set up your own version
1. Title and players: name the situation and who is involved.
2. Options: list each player's choices, using the game's own options from its playbook.
3. Payoffs or stakes: say what each outcome is worth to each player. For matrix games, fill in the payoff grid.
4. Information and timing: say who moves when, and who knows what.
5. Traits: copy the values in the template file. Change any that do not fit your situation.
6. Check: run `advise` on your file, and compare with the game's simulation with `sim` if one exists.

## Options to model
- Option idea 1: Randomise inspection timing and targets so violators cannot predict the cycle.
- Option idea 2: Set the inspection rate so that cheating and complying pay the violator the same. That is the indifference point.
- Option idea 3: If inspections are expensive, raise the penalty instead. A larger penalty deters at lower cost.

## Payoff grid
Rows (you): Inspect, Don't inspect. Columns (them): Comply, Violate.
Enter it with: solve "-1,0 2,-3; 0,0 -2,2" --rows Inspect,Don't inspect --cols Comply,Violate

Simulation: `sim inspection-game` shows the paths, and `sim inspection-game --play` lets you choose.

## Start from this template
```
title: My Inspection Game situation
players: two
timing: simultaneous
interaction: one-shot
information: imperfect
payoff: mixed
enforcement: yes
domain: business, politics, military, work
notes: Describe your situation here. Replace the example options with your own.
```

# Public Goods Game

Each person gains more by free-riding on others' contributions, but the group does best if everyone contributes. Without enforcement, contributions unravel.

## Traits and what each one means
- players = many: Three or more players. Either list each player, or model the rest as one group with a shared outcome. Many-player games need the group's total effect spelled out.
- timing = simultaneous: Everyone chooses without seeing the others' choices. Write each side's options down before anyone reveals anything.
- interaction = one-shot: The situation happens once. Do not plan on future reciprocity, and say so in the description.
- payoff = mixed: Both can gain or both can lose. Write what each side gains from cooperating and what it gains from competing.
- enforcement = yes: There are binding agreements, penalties or courts. Name the penalty and who can impose it.

## Steps to set up your own version
1. Title and players: name the situation and who is involved.
2. Options: list each player's choices, using the game's own options from its playbook.
3. Payoffs or stakes: say what each outcome is worth to each player. For matrix games, fill in the payoff grid.
4. Information and timing: say who moves when, and who knows what.
5. Traits: copy the values in the template file. Change any that do not fit your situation.
6. Check: run `advise` on your file, and compare with the game's simulation with `sim` if one exists.

## Options to model
- Option idea 1: Make contributions visible. Visibility and reciprocity raise contributions.
- Option idea 2: Introduce graduated sanctions: punish free-riders at a cost low enough to be credible.
- Option idea 3: Use conditional cooperation: contribute if most others do, and say so publicly.

## Payoff grid
Rows (you): Contribute, Free-ride. Columns (them): Others contribute, Others free-ride.
Enter it with: solve "3,3 0,4; 4,0 1,1" --rows Contribute,Free-ride --cols Others contribute,Others free-ride

Simulation: `sim public-goods` shows the paths, and `sim public-goods --play` lets you choose.

## Start from this template
```
title: My Public Goods Game situation
players: many
timing: simultaneous
interaction: one-shot
payoff: mixed
enforcement: yes
domain: work, politics, business, everyday
notes: Describe your situation here. Replace the example options with your own.
```

# Tragedy of the Commons

Individuals rationally overuse a shared resource because they capture the benefit while the cost of depletion is spread across everyone. Clear rules and local monitoring usually solve it.

## Traits and what each one means
- players = many: Three or more players. Either list each player, or model the rest as one group with a shared outcome. Many-player games need the group's total effect spelled out.
- interaction = repeated: It recurs. Say how many rounds, and how much the future matters to each side. A longer, more valuable future usually supports cooperation.
- payoff = mixed: Both can gain or both can lose. Write what each side gains from cooperating and what it gains from competing.
- enforcement = no: Nothing forces anyone to keep a deal. Agreements rely on trust or self-interest.

## Steps to set up your own version
1. Title and players: name the situation and who is involved.
2. Options: list each player's choices, using the game's own options from its playbook.
3. Payoffs or stakes: say what each outcome is worth to each player. For matrix games, fill in the payoff grid.
4. Information and timing: say who moves when, and who knows what.
5. Traits: copy the values in the template file. Change any that do not fit your situation.
6. Check: run `advise` on your file, and compare with the game's simulation with `sim` if one exists.

## Options to model
- Option idea 1: Define who may use the resource and how much, with clear boundaries.
- Option idea 2: Monitor use locally, ideally by the users themselves.
- Option idea 3: Use graduated sanctions that escalate with repeated violations.

## Payoff grid
Rows (you): Restrain, Exploit. Columns (them): Restrain, Exploit.
Enter it with: solve "3,3 1,4; 4,1 2,2" --rows Restrain,Exploit --cols Restrain,Exploit

Simulation: `sim tragedy-of-the-commons` shows the paths, and `sim tragedy-of-the-commons --play` lets you choose.

## Start from this template
```
title: My Tragedy of the Commons situation
players: many
interaction: repeated
payoff: mixed
enforcement: no
domain: environment, economy, everyday, politics
notes: Describe your situation here. Replace the example options with your own.
```

# Ultimatum Game

One player proposes how to split a sum and the other accepts or rejects. Rejection leaves both with nothing. Pure self-interest predicts tiny offers, but real responders reject unfair ones.

## Traits and what each one means
- players = two: You and one counterpart. Name them in the title, for example 'me and my landlord'.
- timing = sequential: Decisions come in turns. Write who moves first, and what each mover can see when they choose.
- interaction = one-shot: The situation happens once. Do not plan on future reciprocity, and say so in the description.
- information = perfect: Everyone sees the same facts. Include every relevant fact in the description, because nothing is hidden.
- payoff = zero-sum: One side's gain is the other's loss, as in a fixed prize or winner-takes-all. The total never changes.
- bargaining = yes: You are dividing something. State the total, and each side's alternative if no deal is reached (its outside option).

## Steps to set up your own version
1. Title and players: name the situation and who is involved.
2. Options: list each player's choices, using the game's own options from its playbook.
3. Payoffs or stakes: say what each outcome is worth to each player. For matrix games, fill in the payoff grid.
4. Information and timing: say who moves when, and who knows what.
5. Traits: copy the values in the template file. Change any that do not fit your situation.
6. Check: run `advise` on your file, and compare with the game's simulation with `sim` if one exists.

## Options to model
- Option idea 1: As proposer: offer a split the other side sees as fair, not the minimum. A lowball risks losing everything.
- Option idea 2: As responder: weigh what accepting gains against the signal rejection sends. A credible reputation for rejecting unfair deals can pay off in repeat dealings.
- Option idea 3: Consider reputation: fair offers and firm rejections both build trust or deterrence over time.

## Payoff grid
Rows (you): Offer 50/50, Offer 80/20. Columns (them): Accept any offer, Reject offers below 50.
Enter it with: solve "5,5 5,5; 8,2 0,0" --rows Offer 50/50,Offer 80/20 --cols Accept any offer,Reject offers below 50

Simulation: `sim ultimatum-game` shows the paths, and `sim ultimatum-game --play` lets you choose.

## Start from this template
```
title: My Ultimatum Game situation
players: two
timing: sequential
interaction: one-shot
information: perfect
payoff: zero-sum
bargaining: yes
domain: work, business, politics, everyday
notes: Describe your situation here. Replace the example options with your own.
```

# Rubinstein Bargaining

Players alternate offers over a pie, and each round of delay costs something. The outcome depends on relative patience and outside options, not on who is 'right'.

## Traits and what each one means
- players = two: You and one counterpart. Name them in the title, for example 'me and my landlord'.
- timing = sequential: Decisions come in turns. Write who moves first, and what each mover can see when they choose.
- interaction = repeated: It recurs. Say how many rounds, and how much the future matters to each side. A longer, more valuable future usually supports cooperation.
- information = perfect: Everyone sees the same facts. Include every relevant fact in the description, because nothing is hidden.
- payoff = zero-sum: One side's gain is the other's loss, as in a fixed prize or winner-takes-all. The total never changes.
- bargaining = yes: You are dividing something. State the total, and each side's alternative if no deal is reached (its outside option).

## Steps to set up your own version
1. Title and players: name the situation and who is involved.
2. Options: list each player's choices, using the game's own options from its playbook.
3. Payoffs or stakes: say what each outcome is worth to each player. For matrix games, fill in the payoff grid.
4. Information and timing: say who moves when, and who knows what.
5. Traits: copy the values in the template file. Change any that do not fit your situation.
6. Check: run `advise` on your file, and compare with the game's simulation with `sim` if one exists.

## Options to model
- Option idea 1: Estimate your patience compared with theirs. The more patient side should hold out for a larger share.
- Option idea 2: Improve your outside option before bargaining. It moves the split more than rhetoric does.
- Option idea 3: Make the cost of delay visible to them, so they feel the time pressure too.

## Payoff grid
Rows (you): Offer a fair split, Offer a greedy split. Columns (them): Accept, Reject.
Enter it with: solve "2,2 0,0; 3,1 0,0" --rows Offer a fair split,Offer a greedy split --cols Accept,Reject

Simulation: `sim rubinstein-bargaining` shows the paths, and `sim rubinstein-bargaining --play` lets you choose.

## Start from this template
```
title: My Rubinstein Bargaining situation
players: two
timing: sequential
interaction: repeated
information: perfect
payoff: zero-sum
bargaining: yes
domain: work, business, politics, everyday
notes: Describe your situation here. Replace the example options with your own.
```

# Centipede Game

Players take turns either taking a growing pot or passing it on. Backward induction says the first player should take immediately, but real players often pass because they expect cooperation and reputation matters.

## Traits and what each one means
- players = two: You and one counterpart. Name them in the title, for example 'me and my landlord'.
- timing = sequential: Decisions come in turns. Write who moves first, and what each mover can see when they choose.
- interaction = one-shot: The situation happens once. Do not plan on future reciprocity, and say so in the description.
- information = perfect: Everyone sees the same facts. Include every relevant fact in the description, because nothing is hidden.
- payoff = mixed: Both can gain or both can lose. Write what each side gains from cooperating and what it gains from competing.
- communication = no: No talking or signalling is possible. Actions are the only information.

## Steps to set up your own version
1. Title and players: name the situation and who is involved.
2. Options: list each player's choices, using the game's own options from its playbook.
3. Payoffs or stakes: say what each outcome is worth to each player. For matrix games, fill in the payoff grid.
4. Information and timing: say who moves when, and who knows what.
5. Traits: copy the values in the template file. Change any that do not fit your situation.
6. Check: run `advise` on your file, and compare with the game's simulation with `sim` if one exists.

## Options to model
- Option idea 1: Reason backward: where would a purely rational opponent take the pot, and when?
- Option idea 2: Estimate the chance that the other side is cooperative. Passing early is cheap if they are.
- Option idea 3: Build a reputation for passing when it pays over repeated dealings.

## Payoff grid
Rows (you): Stop now, Continue. Columns (them): Opponent continues, Opponent stops.
Enter it with: solve "2,2 2,2; 0,3 1,1" --rows Stop now,Continue --cols Opponent continues,Opponent stops

Simulation: `sim centipede-game` shows the paths, and `sim centipede-game --play` lets you choose.

## Start from this template
```
title: My Centipede Game situation
players: two
timing: sequential
interaction: one-shot
information: perfect
payoff: mixed
communication: no
domain: business, work, everyday, politics
notes: Describe your situation here. Replace the example options with your own.
```

# Trust Game

An investor sends money that grows in transit, and a trustee decides how much to return. Trust can pay for both, but a purely self-interested trustee returns nothing in a one-shot game.

## Traits and what each one means
- players = two: You and one counterpart. Name them in the title, for example 'me and my landlord'.
- timing = sequential: Decisions come in turns. Write who moves first, and what each mover can see when they choose.
- interaction = one-shot: The situation happens once. Do not plan on future reciprocity, and say so in the description.
- information = perfect: Everyone sees the same facts. Include every relevant fact in the description, because nothing is hidden.
- payoff = mixed: Both can gain or both can lose. Write what each side gains from cooperating and what it gains from competing.
- enforcement = no: Nothing forces anyone to keep a deal. Agreements rely on trust or self-interest.

## Steps to set up your own version
1. Title and players: name the situation and who is involved.
2. Options: list each player's choices, using the game's own options from its playbook.
3. Payoffs or stakes: say what each outcome is worth to each player. For matrix games, fill in the payoff grid.
4. Information and timing: say who moves when, and who knows what.
5. Traits: copy the values in the template file. Change any that do not fit your situation.
6. Check: run `advise` on your file, and compare with the game's simulation with `sim` if one exists.

## Options to model
- Option idea 1: As investor: start with a small test amount and increase it as returns prove trustworthy.
- Option idea 2: As trustee: reciprocating builds reputation and future investment, which often beats one-shot defection.
- Option idea 3: Make returns visible and verifiable. Transparency raises trust.

## Payoff grid
Rows (you): Trust, Keep. Columns (them): Reciprocate, Keep.
Enter it with: solve "3,3 0,5; 1,1 1,0" --rows Trust,Keep --cols Reciprocate,Keep

Simulation: `sim trust-game` shows the paths, and `sim trust-game --play` lets you choose.

## Start from this template
```
title: My Trust Game situation
players: two
timing: sequential
interaction: one-shot
information: perfect
payoff: mixed
enforcement: no
domain: business, politics, work, everyday
notes: Describe your situation here. Replace the example options with your own.
```

# Entry Deterrence

A potential entrant decides whether to enter a market, and the incumbent decides whether to fight or accommodate. A threat to fight only works if it is credible, which usually requires a costly commitment made in advance.

## Traits and what each one means
- players = two: You and one counterpart. Name them in the title, for example 'me and my landlord'.
- timing = sequential: Decisions come in turns. Write who moves first, and what each mover can see when they choose.
- interaction = one-shot: The situation happens once. Do not plan on future reciprocity, and say so in the description.
- information = perfect: Everyone sees the same facts. Include every relevant fact in the description, because nothing is hidden.
- payoff = mixed: Both can gain or both can lose. Write what each side gains from cooperating and what it gains from competing.
- commitment = yes: Someone can commit publicly or irreversibly. Write the commitment mechanism, such as a signed contract or a visible step that cannot be undone.

## Steps to set up your own version
1. Title and players: name the situation and who is involved.
2. Options: list each player's choices, using the game's own options from its playbook.
3. Payoffs or stakes: say what each outcome is worth to each player. For matrix games, fill in the payoff grid.
4. Information and timing: say who moves when, and who knows what.
5. Traits: copy the values in the template file. Change any that do not fit your situation.
6. Check: run `advise` on your file, and compare with the game's simulation with `sim` if one exists.

## Options to model
- Option idea 1: Incumbents: make the threat credible before entry, through capacity, long-term contracts, or sunk investment. A bare promise is not enough.
- Option idea 2: Entrants: test the threat by asking whether the incumbent would really fight once you have entered.
- Option idea 3: If the incumbent cannot commit, consider differentiation or a niche entry.

## Payoff grid
Rows (you): Enter, Stay out. Columns (them): Incumbent fights, Incumbent accommodates.
Enter it with: solve "-1,0 2,1; 0,3 0,3" --rows Enter,Stay out --cols Incumbent fights,Incumbent accommodates

Simulation: `sim entry-deterrence` shows the paths, and `sim entry-deterrence --play` lets you choose.

## Start from this template
```
title: My Entry Deterrence situation
players: two
timing: sequential
interaction: one-shot
information: perfect
payoff: mixed
commitment: yes
domain: business, military, politics, games
notes: Describe your situation here. Replace the example options with your own.
```

# Stackelberg Leadership

A leader commits to an action first and the follower responds. Moving first can be an advantage if the commitment is credible and the follower cannot undo it.

## Traits and what each one means
- players = two: You and one counterpart. Name them in the title, for example 'me and my landlord'.
- timing = sequential: Decisions come in turns. Write who moves first, and what each mover can see when they choose.
- interaction = one-shot: The situation happens once. Do not plan on future reciprocity, and say so in the description.
- information = perfect: Everyone sees the same facts. Include every relevant fact in the description, because nothing is hidden.
- payoff = mixed: Both can gain or both can lose. Write what each side gains from cooperating and what it gains from competing.
- commitment = yes: Someone can commit publicly or irreversibly. Write the commitment mechanism, such as a signed contract or a visible step that cannot be undone.

## Steps to set up your own version
1. Title and players: name the situation and who is involved.
2. Options: list each player's choices, using the game's own options from its playbook.
3. Payoffs or stakes: say what each outcome is worth to each player. For matrix games, fill in the payoff grid.
4. Information and timing: say who moves when, and who knows what.
5. Traits: copy the values in the template file. Change any that do not fit your situation.
6. Check: run `advise` on your file, and compare with the game's simulation with `sim` if one exists.

## Options to model
- Option idea 1: If you can move first credibly (announce, invest, pre-commit), do so. The follower will adjust to your choice.
- Option idea 2: If you are the follower, anticipate the leader's move and respond to the outcome that is best for you, not to what they said.
- Option idea 3: Do not commit to an action that hurts you if the follower can simply ignore it.

## Payoff grid
Rows (you): Produce 1, Produce 2, Produce 3. Columns (them): Produce 1, Produce 2, Produce 3.
Enter it with: solve "8,8 7,14 6,18; 14,7 12,12 10,15; 18,6 15,10 12,12" --rows Produce 1,Produce 2,Produce 3 --cols Produce 1,Produce 2,Produce 3

Simulation: `sim stackelberg-leadership` shows the paths, and `sim stackelberg-leadership --play` lets you choose.

## Start from this template
```
title: My Stackelberg Leadership situation
players: two
timing: sequential
interaction: one-shot
information: perfect
payoff: mixed
commitment: yes
domain: business, military, politics
notes: Describe your situation here. Replace the example options with your own.
```

# Cournot Competition

Firms choose output at the same time. Each firm's best choice depends on the other's output. The equilibrium output is above the monopoly level and profits are below it.

## Traits and what each one means
- players = two: You and one counterpart. Name them in the title, for example 'me and my landlord'.
- timing = simultaneous: Everyone chooses without seeing the others' choices. Write each side's options down before anyone reveals anything.
- interaction = one-shot: The situation happens once. Do not plan on future reciprocity, and say so in the description.
- payoff = mixed: Both can gain or both can lose. Write what each side gains from cooperating and what it gains from competing.
- communication = no: No talking or signalling is possible. Actions are the only information.

## Steps to set up your own version
1. Title and players: name the situation and who is involved.
2. Options: list each player's choices, using the game's own options from its playbook.
3. Payoffs or stakes: say what each outcome is worth to each player. For matrix games, fill in the payoff grid.
4. Information and timing: say who moves when, and who knows what.
5. Traits: copy the values in the template file. Change any that do not fit your situation.
6. Check: run `advise` on your file, and compare with the game's simulation with `sim` if one exists.

## Options to model
- Option idea 1: Estimate the rival's best response and choose the quantity that maximises your profit given it.
- Option idea 2: Expand capacity only when the cost is recoverable. Large capacity can credibly commit you to high output.
- Option idea 3: In a repeated market, consider tacit collusion. It is sustained by the threat of punishment (see the repeated-game entry).

## Payoff grid
Rows (you): Produce high, Produce moderate. Columns (them): Produce high, Produce moderate.
Enter it with: solve "1,1 4,0; 0,4 3,3" --rows Produce high,Produce moderate --cols Produce high,Produce moderate

Simulation: `sim cournot-competition` shows the paths, and `sim cournot-competition --play` lets you choose.

## Start from this template
```
title: My Cournot Competition situation
players: two
timing: simultaneous
interaction: one-shot
payoff: mixed
communication: no
domain: business, economy
notes: Describe your situation here. Replace the example options with your own.
```

# Sealed-Bid Auctions

Bidders submit private bids and the highest wins. In a first-price auction, bidders shade below their value. In a second-price (Vickrey) auction, bidding your true value is dominant.

## Traits and what each one means
- players = many: Three or more players. Either list each player, or model the rest as one group with a shared outcome. Many-player games need the group's total effect spelled out.
- timing = simultaneous: Everyone chooses without seeing the others' choices. Write each side's options down before anyone reveals anything.
- interaction = one-shot: The situation happens once. Do not plan on future reciprocity, and say so in the description.
- information = imperfect: Someone holds private information. Say who knows what, and what each side is guessing about the other.
- payoff = zero-sum: One side's gain is the other's loss, as in a fixed prize or winner-takes-all. The total never changes.

## Steps to set up your own version
1. Title and players: name the situation and who is involved.
2. Options: list each player's choices, using the game's own options from its playbook.
3. Payoffs or stakes: say what each outcome is worth to each player. For matrix games, fill in the payoff grid.
4. Information and timing: say who moves when, and who knows what.
5. Traits: copy the values in the template file. Change any that do not fit your situation.
6. Check: run `advise` on your file, and compare with the game's simulation with `sim` if one exists.

## Options to model
- Option idea 1: First-price: shade your bid below your value. The amount depends on the number of rivals and their likely values.
- Option idea 2: Second-price: bid your true value. Strategic bidding gives you nothing.
- Option idea 3: Common value (for example, oil rights of unknown worth): discount your estimate for the winner's curse.

## Payoff grid
Rows (you): Bid 2, Bid 4, Bid 6. Columns (them): Bid 2, Bid 4, Bid 6.
Enter it with: solve "2,1 0,0 0,-2; 2,0 1,0 0,-2; 0,0 0,0 0,-1" --rows Bid 2,Bid 4,Bid 6 --cols Bid 2,Bid 4,Bid 6

Simulation: `sim sealed-bid-auctions` shows the paths, and `sim sealed-bid-auctions --play` lets you choose.

## Start from this template
```
title: My Sealed-Bid Auctions situation
players: many
timing: simultaneous
interaction: one-shot
information: imperfect
payoff: zero-sum
domain: business, economy, games
notes: Describe your situation here. Replace the example options with your own.
```

# War of Attrition

Two players compete to be the last to concede. Staying in costs time or resources, and the first to give up loses. Outcomes depend on each side's cost of waiting and what its commitment signals.

## Traits and what each one means
- players = two: You and one counterpart. Name them in the title, for example 'me and my landlord'.
- timing = simultaneous: Everyone chooses without seeing the others' choices. Write each side's options down before anyone reveals anything.
- interaction = one-shot: The situation happens once. Do not plan on future reciprocity, and say so in the description.
- information = imperfect: Someone holds private information. Say who knows what, and what each side is guessing about the other.
- payoff = zero-sum: One side's gain is the other's loss, as in a fixed prize or winner-takes-all. The total never changes.

## Steps to set up your own version
1. Title and players: name the situation and who is involved.
2. Options: list each player's choices, using the game's own options from its playbook.
3. Payoffs or stakes: say what each outcome is worth to each player. For matrix games, fill in the payoff grid.
4. Information and timing: say who moves when, and who knows what.
5. Traits: copy the values in the template file. Change any that do not fit your situation.
6. Check: run `advise` on your file, and compare with the game's simulation with `sim` if one exists.

## Options to model
- Option idea 1: Compare the cost of waiting per period with the value of winning. Concede when waiting costs more than the prize.
- Option idea 2: Make costs visible and sunk early. Investment commits you and signals resolve, which can deter the other side.
- Option idea 3: Look for the other side's cost of waiting. If they are more exposed, increase pressure on them.

## Payoff grid
Rows (you): Stay in, Concede. Columns (them): Rival stays in, Rival concedes.
Enter it with: solve "-2,-2 2,0; 0,2 1,1" --rows Stay in,Concede --cols Rival stays in,Rival concedes

Simulation: `sim war-of-attrition` shows the paths, and `sim war-of-attrition --play` lets you choose.

## Start from this template
```
title: My War of Attrition situation
players: two
timing: simultaneous
interaction: one-shot
information: imperfect
payoff: zero-sum
domain: military, business, politics, work
notes: Describe your situation here. Replace the example options with your own.
```

# Colonel Blotto

Two players divide limited forces across several battlefields. Each battlefield goes to the side with more force there, and the winner is whoever takes more battlefields.

## Traits and what each one means
- players = two: You and one counterpart. Name them in the title, for example 'me and my landlord'.
- timing = simultaneous: Everyone chooses without seeing the others' choices. Write each side's options down before anyone reveals anything.
- interaction = one-shot: The situation happens once. Do not plan on future reciprocity, and say so in the description.
- information = perfect: Everyone sees the same facts. Include every relevant fact in the description, because nothing is hidden.
- payoff = zero-sum: One side's gain is the other's loss, as in a fixed prize or winner-takes-all. The total never changes.

## Steps to set up your own version
1. Title and players: name the situation and who is involved.
2. Options: list each player's choices, using the game's own options from its playbook.
3. Payoffs or stakes: say what each outcome is worth to each player. For matrix games, fill in the payoff grid.
4. Information and timing: say who moves when, and who knows what.
5. Traits: copy the values in the template file. Change any that do not fit your situation.
6. Check: run `advise` on your file, and compare with the game's simulation with `sim` if one exists.

## Options to model
- Option idea 1: Do not spread evenly across every front. An even split can be out-concentrated on the fronts that matter.
- Option idea 2: Win the fronts you can, by concentrating enough to beat the opponent's likely allocation there.
- Option idea 3: Randomise your allocation within a plausible range so the opponent cannot target you.

## Payoff grid
Rows (you): 3 then 0, 2 then 1, 1 then 2, 0 then 3. Columns (them): 2 then 0, 1 then 1, 0 then 2.
Enter it with: solve "1,-1 0,0 0,0; 1,-1 1,-1 0,0; 0,0 1,-1 1,-1; 0,0 0,0 1,-1" --rows 3 then 0,2 then 1,1 then 2,0 then 3 --cols 2 then 0,1 then 1,0 then 2

Simulation: `sim colonel-blotto` shows the paths, and `sim colonel-blotto --play` lets you choose.

## Start from this template
```
title: My Colonel Blotto situation
players: two
timing: simultaneous
interaction: one-shot
information: perfect
payoff: zero-sum
domain: military, games, politics, business
notes: Describe your situation here. Replace the example options with your own.
```

# Signaling Game

One player knows something the other does not, such as quality or ability. The informed player can send a signal and the other player infers the hidden type from it. Signals work only if they are costly enough to separate the types.

## Traits and what each one means
- players = two: You and one counterpart. Name them in the title, for example 'me and my landlord'.
- timing = sequential: Decisions come in turns. Write who moves first, and what each mover can see when they choose.
- interaction = one-shot: The situation happens once. Do not plan on future reciprocity, and say so in the description.
- information = imperfect: Someone holds private information. Say who knows what, and what each side is guessing about the other.
- payoff = mixed: Both can gain or both can lose. Write what each side gains from cooperating and what it gains from competing.
- communication = yes: You can talk before or during the decision. Say what can be promised, and whether promises are binding.

## Steps to set up your own version
1. Title and players: name the situation and who is involved.
2. Options: list each player's choices, using the game's own options from its playbook.
3. Payoffs or stakes: say what each outcome is worth to each player. For matrix games, fill in the payoff grid.
4. Information and timing: say who moves when, and who knows what.
5. Traits: copy the values in the template file. Change any that do not fit your situation.
6. Check: run `advise` on your file, and compare with the game's simulation with `sim` if one exists.

## Options to model
- Option idea 1: As the informed party: send signals that are costly for those lacking your quality, such as credentials, warranties, or a track record.
- Option idea 2: As the uninformed party: screen by offering choices that different types will sort themselves into.
- Option idea 3: Discount cheap talk. Promises that cost nothing carry little information.

## Payoff grid
Rows (you): Get the credential, Skip it. Columns (them): Pay high wage, Pay low wage.
Enter it with: solve "1,2 -1,1; 0,0 1,0" --rows Get the credential,Skip it --cols Pay high wage,Pay low wage

Simulation: `sim signaling-game` shows the paths, and `sim signaling-game --play` lets you choose.

## Start from this template
```
title: My Signaling Game situation
players: two
timing: sequential
interaction: one-shot
information: imperfect
payoff: mixed
communication: yes
domain: work, business, politics, everyday
notes: Describe your situation here. Replace the example options with your own.
```

# Principal-Agent (Incentives)

A principal hires an agent whose effort is hidden. The principal must design incentives so the agent's own interests align with the principal's goal.

## Traits and what each one means
- players = two: You and one counterpart. Name them in the title, for example 'me and my landlord'.
- timing = sequential: Decisions come in turns. Write who moves first, and what each mover can see when they choose.
- interaction = repeated: It recurs. Say how many rounds, and how much the future matters to each side. A longer, more valuable future usually supports cooperation.
- information = imperfect: Someone holds private information. Say who knows what, and what each side is guessing about the other.
- payoff = mixed: Both can gain or both can lose. Write what each side gains from cooperating and what it gains from competing.
- enforcement = yes: There are binding agreements, penalties or courts. Name the penalty and who can impose it.

## Steps to set up your own version
1. Title and players: name the situation and who is involved.
2. Options: list each player's choices, using the game's own options from its playbook.
3. Payoffs or stakes: say what each outcome is worth to each player. For matrix games, fill in the payoff grid.
4. Information and timing: say who moves when, and who knows what.
5. Traits: copy the values in the template file. Change any that do not fit your situation.
6. Check: run `advise` on your file, and compare with the game's simulation with `sim` if one exists.

## Options to model
- Option idea 1: Pay for outcomes you can measure, and tie rewards to results the agent actually controls.
- Option idea 2: Monitor in proportion to the value at risk. Cheap signals such as reports and audits help.
- Option idea 3: Check incentive compatibility: would the agent prefer the effort you want?

## Payoff grid
Rows (you): Bonus, Flat pay. Columns (them): Work hard, Shirk.
Enter it with: solve "3,2 0,0; 1,1 0,1" --rows Bonus,Flat pay --cols Work hard,Shirk

Simulation: `sim principal-agent` shows the paths, and `sim principal-agent --play` lets you choose.

## Start from this template
```
title: My Principal-Agent (Incentives) situation
players: two
timing: sequential
interaction: repeated
information: imperfect
payoff: mixed
enforcement: yes
domain: work, business, politics
notes: Describe your situation here. Replace the example options with your own.
```

# Coalition Formation and Government Building

Parties must agree on a government, and the party that proposes the deal has real power. The winning coalition is usually the smallest one that can pass its programme, because every extra member takes a share of the spoils.

## Traits and what each one means
- players = many: Three or more players. Either list each player, or model the rest as one group with a shared outcome. Many-player games need the group's total effect spelled out.
- timing = sequential: Decisions come in turns. Write who moves first, and what each mover can see when they choose.
- interaction = repeated: It recurs. Say how many rounds, and how much the future matters to each side. A longer, more valuable future usually supports cooperation.
- information = perfect: Everyone sees the same facts. Include every relevant fact in the description, because nothing is hidden.
- payoff = zero-sum: One side's gain is the other's loss, as in a fixed prize or winner-takes-all. The total never changes.
- communication = yes: You can talk before or during the decision. Say what can be promised, and whether promises are binding.
- bargaining = yes: You are dividing something. State the total, and each side's alternative if no deal is reached (its outside option).

## Steps to set up your own version
1. Title and players: name the situation and who is involved.
2. Options: list each player's choices, using the game's own options from its playbook.
3. Payoffs or stakes: say what each outcome is worth to each player. For matrix games, fill in the payoff grid.
4. Information and timing: say who moves when, and who knows what.
5. Traits: copy the values in the template file. Change any that do not fit your situation.
6. Check: run `advise` on your file, and compare with the game's simulation with `sim` if one exists.

## Options to model
- Option idea 1: As proposer: offer just enough to the smallest coalition that passes; overpaying members you do not need wastes resources.
- Option idea 2: As a minority party: your value is your ability to join any winning coalition, so keep alternative partners credible.
- Option idea 3: Know who is patient. The side that can afford delay usually obtains the better share.

## Payoff grid
Rows (you): Join the coalition, Go alone. Columns (them): Join the coalition, Go alone.
Enter it with: solve "3,3 0,1; 1,0 1,1" --rows Join the coalition,Go alone --cols Join the coalition,Go alone

Simulation: `sim coalition-formation` shows the paths, and `sim coalition-formation --play` lets you choose.

## Start from this template
```
title: My Coalition Formation and Government Building situation
players: many
timing: sequential
interaction: repeated
information: perfect
payoff: zero-sum
communication: yes
bargaining: yes
domain: government, politics
notes: Describe your situation here. Replace the example options with your own.
```

# Agenda Setting and Strategic Voting

Who controls the order in which options are voted on can decide the result. Voters may vote for an option they do not prefer, to block a worse outcome, and majorities can cycle with no stable winner.

## Traits and what each one means
- players = many: Three or more players. Either list each player, or model the rest as one group with a shared outcome. Many-player games need the group's total effect spelled out.
- timing = sequential: Decisions come in turns. Write who moves first, and what each mover can see when they choose.
- interaction = one-shot: The situation happens once. Do not plan on future reciprocity, and say so in the description.
- information = perfect: Everyone sees the same facts. Include every relevant fact in the description, because nothing is hidden.
- payoff = mixed: Both can gain or both can lose. Write what each side gains from cooperating and what it gains from competing.
- communication = yes: You can talk before or during the decision. Say what can be promised, and whether promises are binding.

## Steps to set up your own version
1. Title and players: name the situation and who is involved.
2. Options: list each player's choices, using the game's own options from its playbook.
3. Payoffs or stakes: say what each outcome is worth to each player. For matrix games, fill in the payoff grid.
4. Information and timing: say who moves when, and who knows what.
5. Traits: copy the values in the template file. Change any that do not fit your situation.
6. Check: run `advise` on your file, and compare with the game's simulation with `sim` if one exists.

## Options to model
- Option idea 1: As voter: work backward from the final vote and ask what your sincere choice will actually produce.
- Option idea 2: If your favourite cannot win, vote for the option that best blocks the worst outcome, rather than wasting the vote.
- Option idea 3: As agenda setter: control the order of comparisons; where preferences cycle, the order decides the result.

## Payoff grid
Rows (you): Put reform first, Put status quo first. Columns (them): Support, Oppose.
Enter it with: solve "2,2 -1,1; 1,-1 0,0" --rows Put reform first,Put status quo first --cols Support,Oppose

Simulation: `sim agenda-setting-voting` shows the paths, and `sim agenda-setting-voting --play` lets you choose.

## Start from this template
```
title: My Agenda Setting and Strategic Voting situation
players: many
timing: sequential
interaction: one-shot
information: perfect
payoff: mixed
communication: yes
domain: government, politics
notes: Describe your situation here. Replace the example options with your own.
```

# Median Voter and Spatial Competition

Two candidates or parties position themselves on a single scale of opinion. Each tries to win the most voters, which tends to push both toward the centre, unless a voter base or a niche gives reason to stay apart.

## Traits and what each one means
- players = two: You and one counterpart. Name them in the title, for example 'me and my landlord'.
- timing = simultaneous: Everyone chooses without seeing the others' choices. Write each side's options down before anyone reveals anything.
- interaction = one-shot: The situation happens once. Do not plan on future reciprocity, and say so in the description.
- information = perfect: Everyone sees the same facts. Include every relevant fact in the description, because nothing is hidden.
- payoff = zero-sum: One side's gain is the other's loss, as in a fixed prize or winner-takes-all. The total never changes.
- communication = yes: You can talk before or during the decision. Say what can be promised, and whether promises are binding.

## Steps to set up your own version
1. Title and players: name the situation and who is involved.
2. Options: list each player's choices, using the game's own options from its playbook.
3. Payoffs or stakes: say what each outcome is worth to each player. For matrix games, fill in the payoff grid.
4. Information and timing: say who moves when, and who knows what.
5. Traits: copy the values in the template file. Change any that do not fit your situation.
6. Check: run `advise` on your file, and compare with the game's simulation with `sim` if one exists.

## Options to model
- Option idea 1: If you are a two-party contender, the centre is the big prize; expect the rival to move toward it as well.
- Option idea 2: If you have a committed base, you may gain more by energising it than by moving to the centre; weigh turnout against persuasion.
- Option idea 3: Differentiate on issues where you have a credible advantage, rather than matching the rival on everything.

## Payoff grid
Rows (you): Left, Centre, Right. Columns (them): Left, Centre, Right.
Enter it with: solve "0,0 -1,1 0,0; 1,-1 0,0 1,-1; 0,0 -1,1 0,0" --rows Left,Centre,Right --cols Left,Centre,Right

Simulation: `sim median-voter-spatial-competition` shows the paths, and `sim median-voter-spatial-competition --play` lets you choose.

## Start from this template
```
title: My Median Voter and Spatial Competition situation
players: two
timing: simultaneous
interaction: one-shot
information: perfect
payoff: zero-sum
communication: yes
domain: politics, business, government
notes: Describe your situation here. Replace the example options with your own.
```

# Authoritarian Survival (Selectorate Analysis)

Political scientists analyse how autocracies keep power: rulers keep a small winning coalition loyal with private benefits, and must manage the threat of rivals inside their own security forces. Understanding this game helps observers, citizens and opposition predict when a regime is stable and when it is vulnerable.

## Traits and what each one means
- players = many: Three or more players. Either list each player, or model the rest as one group with a shared outcome. Many-player games need the group's total effect spelled out.
- timing = sequential: Decisions come in turns. Write who moves first, and what each mover can see when they choose.
- interaction = repeated: It recurs. Say how many rounds, and how much the future matters to each side. A longer, more valuable future usually supports cooperation.
- information = imperfect: Someone holds private information. Say who knows what, and what each side is guessing about the other.
- payoff = zero-sum: One side's gain is the other's loss, as in a fixed prize or winner-takes-all. The total never changes.
- enforcement = no: Nothing forces anyone to keep a deal. Agreements rely on trust or self-interest.
- commitment = no: Every move can be reversed. Note any reversals that are cheap or expensive.

## Steps to set up your own version
1. Title and players: name the situation and who is involved.
2. Options: list each player's choices, using the game's own options from its playbook.
3. Payoffs or stakes: say what each outcome is worth to each player. For matrix games, fill in the payoff grid.
4. Information and timing: say who moves when, and who knows what.
5. Traits: copy the values in the template file. Change any that do not fit your situation.
6. Check: run `advise` on your file, and compare with the game's simulation with `sim` if one exists.

## Options to model
- Option idea 1: For observers: watch the loyalty of the small group whose support keeps the leader in power, not the public mood alone.
- Option idea 2: For observers: economic shocks that reduce what the regime can pay its supporters raise the risk of elite defection.
- Option idea 3: For citizens and the opposition: the regime's stability depends on insiders expecting it to last. Credible signs that it is weakening change those expectations.

## Payoff grid
Rows (you): Stay loyal, Defect. Columns (them): Reward, Purge.
Enter it with: solve "2,2 -2,1; 1,-2 -3,-3" --rows Stay loyal,Defect --cols Reward,Purge

Simulation: `sim authoritarian-survival` shows the paths, and `sim authoritarian-survival --play` lets you choose.

## Start from this template
```
title: My Authoritarian Survival (Selectorate Analysis) situation
players: many
timing: sequential
interaction: repeated
information: imperfect
payoff: zero-sum
enforcement: no
commitment: no
domain: government, politics
notes: Describe your situation here. Replace the example options with your own.
```

# Elite Defection and Coordination

Powerful actors inside an institution each decide whether to back a leader, or to break from them. Each is safer acting only if enough others act too, so the outcome depends on what each expects others to do, and on credible signals.

## Traits and what each one means
- players = many: Three or more players. Either list each player, or model the rest as one group with a shared outcome. Many-player games need the group's total effect spelled out.
- timing = simultaneous: Everyone chooses without seeing the others' choices. Write each side's options down before anyone reveals anything.
- interaction = one-shot: The situation happens once. Do not plan on future reciprocity, and say so in the description.
- information = imperfect: Someone holds private information. Say who knows what, and what each side is guessing about the other.
- payoff = common-interest: You want the same outcome. The challenge is coordinating on it, not conflicting over it.
- communication = no: No talking or signalling is possible. Actions are the only information.
- enforcement = no: Nothing forces anyone to keep a deal. Agreements rely on trust or self-interest.

## Steps to set up your own version
1. Title and players: name the situation and who is involved.
2. Options: list each player's choices, using the game's own options from its playbook.
3. Payoffs or stakes: say what each outcome is worth to each player. For matrix games, fill in the payoff grid.
4. Information and timing: say who moves when, and who knows what.
5. Traits: copy the values in the template file. Change any that do not fit your situation.
6. Check: run `advise` on your file, and compare with the game's simulation with `sim` if one exists.

## Options to model
- Option idea 1: For actors inside an institution: waiting for a clear, public focal signal reduces the risk of acting alone and being isolated.
- Option idea 2: For actors inside an institution: estimate what happens to you if the move fails, not just what happens if it succeeds.
- Option idea 3: For leaders: loyalty that depends on being watched is fragile. Visible, credible reasons to stay committed raise the threshold others need.

## Payoff grid
Rows (you): Defect, Stay. Columns (them): Defect, Stay.
Enter it with: solve "3,3 0,1; 1,0 2,2" --rows Defect,Stay --cols Defect,Stay

Simulation: `sim elite-defection-coordination` shows the paths, and `sim elite-defection-coordination --play` lets you choose.

## Start from this template
```
title: My Elite Defection and Coordination situation
players: many
timing: simultaneous
interaction: one-shot
information: imperfect
payoff: common-interest
communication: no
enforcement: no
domain: government, politics
notes: Describe your situation here. Replace the example options with your own.
```

# Mass Mobilisation and Preference Falsification

People may privately oppose a regime yet publicly comply, because they do not know how many others feel the same. Small visible acts can reveal this, and large changes can happen suddenly when enough people believe enough others will join.

## Traits and what each one means
- players = many: Three or more players. Either list each player, or model the rest as one group with a shared outcome. Many-player games need the group's total effect spelled out.
- timing = simultaneous: Everyone chooses without seeing the others' choices. Write each side's options down before anyone reveals anything.
- interaction = one-shot: The situation happens once. Do not plan on future reciprocity, and say so in the description.
- information = imperfect: Someone holds private information. Say who knows what, and what each side is guessing about the other.
- payoff = mixed: Both can gain or both can lose. Write what each side gains from cooperating and what it gains from competing.
- communication = yes: You can talk before or during the decision. Say what can be promised, and whether promises are binding.
- enforcement = no: Nothing forces anyone to keep a deal. Agreements rely on trust or self-interest.

## Steps to set up your own version
1. Title and players: name the situation and who is involved.
2. Options: list each player's choices, using the game's own options from its playbook.
3. Payoffs or stakes: say what each outcome is worth to each player. For matrix games, fill in the payoff grid.
4. Information and timing: say who moves when, and who knows what.
5. Traits: copy the values in the template file. Change any that do not fit your situation.
6. Check: run `advise` on your file, and compare with the game's simulation with `sim` if one exists.

## Options to model
- Option idea 1: For organisers: plan for the early threshold. Visible, peaceful first participation lowers the perceived risk for those who would join later.
- Option idea 2: For organisers: broad, inclusive participation makes the movement harder to isolate and harder to portray as a fringe.
- Option idea 3: For observers: do not assume that a regime is secure because public opposition is quiet; private opposition can be large.

## Payoff grid
Rows (you): Join, Stay home. Columns (them): Join, Stay home.
Enter it with: solve "3,3 -1,0; 0,-1 1,1" --rows Join,Stay home --cols Join,Stay home

Simulation: `sim mass-uprising-threshold` shows the paths, and `sim mass-uprising-threshold --play` lets you choose.

## Start from this template
```
title: My Mass Mobilisation and Preference Falsification situation
players: many
timing: simultaneous
interaction: one-shot
information: imperfect
payoff: mixed
communication: yes
enforcement: no
domain: government, politics, society
notes: Describe your situation here. Replace the example options with your own.
```

# Nonviolent Resistance Campaigns

Political scientists studying civil resistance find that broad nonviolent campaigns have, on average, succeeded more often than violent ones. Success depends on discipline, broad coalitions, and the loyalty of the institutions a regime relies on.

## Traits and what each one means
- players = many: Three or more players. Either list each player, or model the rest as one group with a shared outcome. Many-player games need the group's total effect spelled out.
- timing = sequential: Decisions come in turns. Write who moves first, and what each mover can see when they choose.
- interaction = repeated: It recurs. Say how many rounds, and how much the future matters to each side. A longer, more valuable future usually supports cooperation.
- information = imperfect: Someone holds private information. Say who knows what, and what each side is guessing about the other.
- payoff = mixed: Both can gain or both can lose. Write what each side gains from cooperating and what it gains from competing.
- communication = yes: You can talk before or during the decision. Say what can be promised, and whether promises are binding.
- enforcement = no: Nothing forces anyone to keep a deal. Agreements rely on trust or self-interest.

## Steps to set up your own version
1. Title and players: name the situation and who is involved.
2. Options: list each player's choices, using the game's own options from its playbook.
3. Payoffs or stakes: say what each outcome is worth to each player. For matrix games, fill in the payoff grid.
4. Information and timing: say who moves when, and who knows what.
5. Traits: copy the values in the template file. Change any that do not fit your situation.
6. Check: run `advise` on your file, and compare with the game's simulation with `sim` if one exists.

## Options to model
- Option idea 1: Keep the campaign disciplined and nonviolent; this keeps the broadest range of people willing to take part.
- Option idea 2: Build a wide coalition, including groups that do not usually join protests, to increase the cost of repression.
- Option idea 3: Target the pillars of the regime's power, such as economic cooperation and public legitimacy, rather than individuals.

## Payoff grid
Rows (you): Persist, Retreat. Columns (them): Accommodate, Repress.
Enter it with: solve "3,0 -1,2; 1,2 0,1" --rows Persist,Retreat --cols Accommodate,Repress

Simulation: `sim nonviolent-resistance` shows the paths, and `sim nonviolent-resistance --play` lets you choose.

## Start from this template
```
title: My Nonviolent Resistance Campaigns situation
players: many
timing: sequential
interaction: repeated
information: imperfect
payoff: mixed
communication: yes
enforcement: no
domain: government, politics, society
notes: Describe your situation here. Replace the example options with your own.
```

# Crisis Negotiation and Hostage Situations

In a crisis such as a hostage incident, both sides want to avoid disaster but are pressured to make demands and concessions. Communication and time usually help more than ultimatums, and rewarding violence tends to invite more of it.

## Traits and what each one means
- players = two: You and one counterpart. Name them in the title, for example 'me and my landlord'.
- timing = sequential: Decisions come in turns. Write who moves first, and what each mover can see when they choose.
- interaction = one-shot: The situation happens once. Do not plan on future reciprocity, and say so in the description.
- information = imperfect: Someone holds private information. Say who knows what, and what each side is guessing about the other.
- payoff = mixed: Both can gain or both can lose. Write what each side gains from cooperating and what it gains from competing.
- communication = yes: You can talk before or during the decision. Say what can be promised, and whether promises are binding.
- commitment = yes: Someone can commit publicly or irreversibly. Write the commitment mechanism, such as a signed contract or a visible step that cannot be undone.

## Steps to set up your own version
1. Title and players: name the situation and who is involved.
2. Options: list each player's choices, using the game's own options from its playbook.
3. Payoffs or stakes: say what each outcome is worth to each player. For matrix games, fill in the payoff grid.
4. Information and timing: say who moves when, and who knows what.
5. Traits: copy the values in the template file. Change any that do not fit your situation.
6. Check: run `advise` on your file, and compare with the game's simulation with `sim` if one exists.

## Options to model
- Option idea 1: Open a channel of communication early, through a trained negotiator where possible, and keep it open.
- Option idea 2: Buy time. Most crises lose intensity as the situation is slowed down and information improves.
- Option idea 3: Break demands into smaller steps and look for things that help the other side save face without rewarding harm.

## Payoff grid
Rows (you): Concede, Hold firm. Columns (them): Concede, Hold firm.
Enter it with: solve "2,2 0,3; 3,0 -3,-3" --rows Concede,Hold firm --cols Concede,Hold firm

Simulation: `sim crisis-negotiation` shows the paths, and `sim crisis-negotiation --play` lets you choose.

## Start from this template
```
title: My Crisis Negotiation and Hostage Situations situation
players: two
timing: sequential
interaction: one-shot
information: imperfect
payoff: mixed
communication: yes
commitment: yes
domain: military, politics, everyday, government
notes: Describe your situation here. Replace the example options with your own.
```

# Arms Race and Security Dilemma

Each side builds up its defences for safety, but its rival reads that build-up as a threat and responds in kind. Both end up less secure and poorer, even though neither wanted the race.

## Traits and what each one means
- players = two: You and one counterpart. Name them in the title, for example 'me and my landlord'.
- timing = simultaneous: Everyone chooses without seeing the others' choices. Write each side's options down before anyone reveals anything.
- interaction = repeated: It recurs. Say how many rounds, and how much the future matters to each side. A longer, more valuable future usually supports cooperation.
- information = imperfect: Someone holds private information. Say who knows what, and what each side is guessing about the other.
- payoff = mixed: Both can gain or both can lose. Write what each side gains from cooperating and what it gains from competing.
- communication = yes: You can talk before or during the decision. Say what can be promised, and whether promises are binding.
- enforcement = yes: There are binding agreements, penalties or courts. Name the penalty and who can impose it.
- commitment = yes: Someone can commit publicly or irreversibly. Write the commitment mechanism, such as a signed contract or a visible step that cannot be undone.

## Steps to set up your own version
1. Title and players: name the situation and who is involved.
2. Options: list each player's choices, using the game's own options from its playbook.
3. Payoffs or stakes: say what each outcome is worth to each player. For matrix games, fill in the payoff grid.
4. Information and timing: say who moves when, and who knows what.
5. Traits: copy the values in the template file. Change any that do not fit your situation.
6. Check: run `advise` on your file, and compare with the game's simulation with `sim` if one exists.

## Options to model
- Option idea 1: Make defensive capabilities visible and limited, so they reassure rather than threaten.
- Option idea 2: Use verification and transparency; a rival that can confirm your restraint is more willing to show its own.
- Option idea 3: Adopt tit-for-tat restraint: reciprocate reductions and respond to build-ups proportionately, without an open-ended race.

## Payoff grid
Rows (you): Build up, Restrain. Columns (them): Rival builds up, Rival restrains.
Enter it with: solve "1,1 3,0; 0,3 2,2" --rows Build up,Restrain --cols Rival builds up,Rival restrains

Simulation: `sim arms-race-security-dilemma` shows the paths, and `sim arms-race-security-dilemma --play` lets you choose.

## Start from this template
```
title: My Arms Race and Security Dilemma situation
players: two
timing: simultaneous
interaction: repeated
information: imperfect
payoff: mixed
communication: yes
enforcement: yes
commitment: yes
domain: military, politics, government
notes: Describe your situation here. Replace the example options with your own.
```

# Asymmetric Conflict (Insurgency and Counter-Insurgency)

A strong state faces a weaker armed or political movement. The stronger side can win battles but struggles to win the population, and the weaker side usually wins by surviving and outlasting, rather than by defeating its opponent militarily.

## Traits and what each one means
- players = two: You and one counterpart. Name them in the title, for example 'me and my landlord'.
- timing = sequential: Decisions come in turns. Write who moves first, and what each mover can see when they choose.
- interaction = repeated: It recurs. Say how many rounds, and how much the future matters to each side. A longer, more valuable future usually supports cooperation.
- information = imperfect: Someone holds private information. Say who knows what, and what each side is guessing about the other.
- payoff = zero-sum: One side's gain is the other's loss, as in a fixed prize or winner-takes-all. The total never changes.
- commitment = no: Every move can be reversed. Note any reversals that are cheap or expensive.

## Steps to set up your own version
1. Title and players: name the situation and who is involved.
2. Options: list each player's choices, using the game's own options from its playbook.
3. Payoffs or stakes: say what each outcome is worth to each player. For matrix games, fill in the payoff grid.
4. Information and timing: say who moves when, and who knows what.
5. Traits: copy the values in the template file. Change any that do not fit your situation.
6. Check: run `advise` on your file, and compare with the game's simulation with `sim` if one exists.

## Options to model
- Option idea 1: For the stronger side: the decisive contest is for public legitimacy; actions that harm civilians often strengthen the opposing side.
- Option idea 2: For the stronger side: the most effective approaches combine security with political, economic and service-based offers.
- Option idea 3: For the weaker side: endurance and political cost matter more than battlefield victories; plan for a long timeline.

## Payoff grid
Rows (you): Hit and run, Stand and fight. Columns (them): Patrol, Mass search.
Enter it with: solve "2,-1 1,1; -1,2 -2,1" --rows Hit and run,Stand and fight --cols Patrol,Mass search

Simulation: `sim asymmetric-insurgency` shows the paths, and `sim asymmetric-insurgency --play` lets you choose.

## Start from this template
```
title: My Asymmetric Conflict (Insurgency and Counter-Insurgency) situation
players: two
timing: sequential
interaction: repeated
information: imperfect
payoff: zero-sum
commitment: no
domain: military, politics, government
notes: Describe your situation here. Replace the example options with your own.
```

# The Warning Problem

An analyst must decide whether evidence is strong enough to issue a warning. Warn too early or too often and decision-makers stop listening; warn too late, or not at all, and the surprise is costly.

## Traits and what each one means
- players = two: You and one counterpart. Name them in the title, for example 'me and my landlord'.
- timing = sequential: Decisions come in turns. Write who moves first, and what each mover can see when they choose.
- interaction = repeated: It recurs. Say how many rounds, and how much the future matters to each side. A longer, more valuable future usually supports cooperation.
- information = imperfect: Someone holds private information. Say who knows what, and what each side is guessing about the other.
- payoff = mixed: Both can gain or both can lose. Write what each side gains from cooperating and what it gains from competing.
- communication = yes: You can talk before or during the decision. Say what can be promised, and whether promises are binding.

## Steps to set up your own version
1. Title and players: name the situation and who is involved.
2. Options: list each player's choices, using the game's own options from its playbook.
3. Payoffs or stakes: say what each outcome is worth to each player. For matrix games, fill in the payoff grid.
4. Information and timing: say who moves when, and who knows what.
5. Traits: copy the values in the template file. Change any that do not fit your situation.
6. Check: run `advise` on your file, and compare with the game's simulation with `sim` if one exists.

## Options to model
- Option idea 1: State the evidence, your confidence and the alternative explanations together, so decision-makers can weigh the warning.
- Option idea 2: Separate the warning threshold from the response threshold: a warning can be issued at lower confidence than the action it recommends.
- Option idea 3: Track your false-alarm and miss rates, so the cost of each kind of error is visible and the threshold can be tuned.

## Payoff grid
Rows (you): Warn, Stay quiet. Columns (them): Act on warning, Ignore.
Enter it with: solve "1,2 -1,1; 0,1 -2,-2" --rows Warn,Stay quiet --cols Act on warning,Ignore

Simulation: `sim intel-warning-problem` shows the paths, and `sim intel-warning-problem --play` lets you choose.

## Start from this template
```
title: My The Warning Problem situation
players: two
timing: sequential
interaction: repeated
information: imperfect
payoff: mixed
communication: yes
domain: military, politics, government
notes: Describe your situation here. Replace the example options with your own.
```

# Updating on Evidence (Bayesian Analysis)

Analysts hold a belief about what is happening and must revise it as evidence arrives. Bayesian updating says how far each new piece of evidence should move the belief, depending on how likely that evidence is under each explanation.

## Traits and what each one means
- players = two: You and one counterpart. Name them in the title, for example 'me and my landlord'.
- timing = sequential: Decisions come in turns. Write who moves first, and what each mover can see when they choose.
- interaction = repeated: It recurs. Say how many rounds, and how much the future matters to each side. A longer, more valuable future usually supports cooperation.
- information = imperfect: Someone holds private information. Say who knows what, and what each side is guessing about the other.
- payoff = common-interest: You want the same outcome. The challenge is coordinating on it, not conflicting over it.
- communication = no: No talking or signalling is possible. Actions are the only information.

## Steps to set up your own version
1. Title and players: name the situation and who is involved.
2. Options: list each player's choices, using the game's own options from its playbook.
3. Payoffs or stakes: say what each outcome is worth to each player. For matrix games, fill in the payoff grid.
4. Information and timing: say who moves when, and who knows what.
5. Traits: copy the values in the template file. Change any that do not fit your situation.
6. Check: run `advise` on your file, and compare with the game's simulation with `sim` if one exists.

## Options to model
- Option idea 1: Write down the explanations you are weighing before reading the evidence, and give each a rough prior.
- Option idea 2: Ask how likely each new fact is under each explanation, not just how likely it is under your favourite one.
- Option idea 3: Avoid updating too strongly on a single vivid report, and check whether sources share a common origin.

## Payoff grid
Rows (you): Update on the evidence, Ignore the evidence. Columns (them): Evidence strong, Evidence weak.
Enter it with: solve "2,1 0,0; 1,0 1,2" --rows Update on the evidence,Ignore the evidence --cols Evidence strong,Evidence weak

Simulation: `sim analysis-bayesian-updating` shows the paths, and `sim analysis-bayesian-updating --play` lets you choose.

## Start from this template
```
title: My Updating on Evidence (Bayesian Analysis) situation
players: two
timing: sequential
interaction: repeated
information: imperfect
payoff: common-interest
communication: no
domain: military, politics, government, business
notes: Describe your situation here. Replace the example options with your own.
```

# Deception and Cheap Talk

One side can send messages that may or may not be true. Cheap talk costs nothing to send, so it carries little information unless it is backed by something costly or checkable.

## Traits and what each one means
- players = two: You and one counterpart. Name them in the title, for example 'me and my landlord'.
- timing = sequential: Decisions come in turns. Write who moves first, and what each mover can see when they choose.
- interaction = one-shot: The situation happens once. Do not plan on future reciprocity, and say so in the description.
- information = imperfect: Someone holds private information. Say who knows what, and what each side is guessing about the other.
- payoff = mixed: Both can gain or both can lose. Write what each side gains from cooperating and what it gains from competing.
- communication = yes: You can talk before or during the decision. Say what can be promised, and whether promises are binding.

## Steps to set up your own version
1. Title and players: name the situation and who is involved.
2. Options: list each player's choices, using the game's own options from its playbook.
3. Payoffs or stakes: say what each outcome is worth to each player. For matrix games, fill in the payoff grid.
4. Information and timing: say who moves when, and who knows what.
5. Traits: copy the values in the template file. Change any that do not fit your situation.
6. Check: run `advise` on your file, and compare with the game's simulation with `sim` if one exists.

## Options to model
- Option idea 1: Give more weight to claims that are costly to fake or that can be checked independently than to claims that are merely asserted.
- Option idea 2: Ask what the sender would gain by deceiving you; if the answer is nothing, the message may be honest.
- Option idea 3: If you want to be believed, back your words with a verifiable action that would be costly to reverse.

## Payoff grid
Rows (you): Tell the truth, Mislead. Columns (them): Trust, Verify.
Enter it with: solve "2,2 0,1; 3,-1 -2,2" --rows Tell the truth,Mislead --cols Trust,Verify

Simulation: `sim deception-cheap-talk` shows the paths, and `sim deception-cheap-talk --play` lets you choose.

## Start from this template
```
title: My Deception and Cheap Talk situation
players: two
timing: sequential
interaction: one-shot
information: imperfect
payoff: mixed
communication: yes
domain: military, politics, government
notes: Describe your situation here. Replace the example options with your own.
```

# Counterintelligence: Detecting and Misleading

Counterintelligence is a repeated contest: one side tries to detect hidden influence and the other tries to avoid detection or mislead. Each side's checks shape what the other can safely do, which makes it a close relative of the inspection game.

## Traits and what each one means
- players = two: You and one counterpart. Name them in the title, for example 'me and my landlord'.
- timing = simultaneous: Everyone chooses without seeing the others' choices. Write each side's options down before anyone reveals anything.
- interaction = repeated: It recurs. Say how many rounds, and how much the future matters to each side. A longer, more valuable future usually supports cooperation.
- information = imperfect: Someone holds private information. Say who knows what, and what each side is guessing about the other.
- payoff = zero-sum: One side's gain is the other's loss, as in a fixed prize or winner-takes-all. The total never changes.
- enforcement = yes: There are binding agreements, penalties or courts. Name the penalty and who can impose it.

## Steps to set up your own version
1. Title and players: name the situation and who is involved.
2. Options: list each player's choices, using the game's own options from its playbook.
3. Payoffs or stakes: say what each outcome is worth to each player. For matrix games, fill in the payoff grid.
4. Information and timing: say who moves when, and who knows what.
5. Traits: copy the values in the template file. Change any that do not fit your situation.
6. Check: run `advise` on your file, and compare with the game's simulation with `sim` if one exists.

## Options to model
- Option idea 1: Vary checks so that they cannot be predicted; a fixed schedule is easy to plan around.
- Option idea 2: Compare reports from sources that should be independent; agreement among sources that share a origin is not corroboration.
- Option idea 3: Calibrate responses to evidence: a proportionate review is better than an accusation that cannot be supported.

## Payoff grid
Rows (you): Monitor, Act on suspicion. Columns (them): Loyal, Double.
Enter it with: solve "1,1 -1,2; 0,-1 2,-2" --rows Monitor,Act on suspicion --cols Loyal,Double

Simulation: `sim double-agent-counterintelligence` shows the paths, and `sim double-agent-counterintelligence --play` lets you choose.

## Start from this template
```
title: My Counterintelligence: Detecting and Misleading situation
players: two
timing: simultaneous
interaction: repeated
information: imperfect
payoff: zero-sum
enforcement: yes
domain: military, government, politics
notes: Describe your situation here. Replace the example options with your own.
```

# Disclose or Conceal (Evidence Games)

A party holds evidence and decides whether to reveal it. Strong evidence is usually disclosed, but the absence of disclosure can itself signal that the evidence is bad. Often what is not said is the most informative message.

## Traits and what each one means
- players = two: You and one counterpart. Name them in the title, for example 'me and my landlord'.
- timing = sequential: Decisions come in turns. Write who moves first, and what each mover can see when they choose.
- interaction = one-shot: The situation happens once. Do not plan on future reciprocity, and say so in the description.
- information = imperfect: Someone holds private information. Say who knows what, and what each side is guessing about the other.
- payoff = mixed: Both can gain or both can lose. Write what each side gains from cooperating and what it gains from competing.
- communication = yes: You can talk before or during the decision. Say what can be promised, and whether promises are binding.

## Steps to set up your own version
1. Title and players: name the situation and who is involved.
2. Options: list each player's choices, using the game's own options from its playbook.
3. Payoffs or stakes: say what each outcome is worth to each player. For matrix games, fill in the payoff grid.
4. Information and timing: say who moves when, and who knows what.
5. Traits: copy the values in the template file. Change any that do not fit your situation.
6. Check: run `advise` on your file, and compare with the game's simulation with `sim` if one exists.

## Options to model
- Option idea 1: As the holder of good evidence, disclose it early and in a checkable form, since the market for silence punishes concealment.
- Option idea 2: As the receiver, ask what a silent party would have to hide, and weigh silence as a signal.
- Option idea 3: If disclosure would expose sources or methods, disclose the conclusion and its confidence rather than the raw material.

## Payoff grid
Rows (you): Disclose, Conceal. Columns (them): Inspect, Trust.
Enter it with: solve "1,1 2,2; -2,1 3,0" --rows Disclose,Conceal --cols Inspect,Trust

Simulation: `sim disclosure-game` shows the paths, and `sim disclosure-game --play` lets you choose.

## Start from this template
```
title: My Disclose or Conceal (Evidence Games) situation
players: two
timing: sequential
interaction: one-shot
information: imperfect
payoff: mixed
communication: yes
domain: military, politics, government
notes: Describe your situation here. Replace the example options with your own.
```

# Sharing Information Among Partners

Partners gain from pooling information, but each prefers to take what others share while sharing less. Like a public good, shared information is under-supplied unless trust, reciprocity and visible contribution are in place.

## Traits and what each one means
- players = many: Three or more players. Either list each player, or model the rest as one group with a shared outcome. Many-player games need the group's total effect spelled out.
- timing = simultaneous: Everyone chooses without seeing the others' choices. Write each side's options down before anyone reveals anything.
- interaction = repeated: It recurs. Say how many rounds, and how much the future matters to each side. A longer, more valuable future usually supports cooperation.
- information = imperfect: Someone holds private information. Say who knows what, and what each side is guessing about the other.
- payoff = mixed: Both can gain or both can lose. Write what each side gains from cooperating and what it gains from competing.
- communication = yes: You can talk before or during the decision. Say what can be promised, and whether promises are binding.
- enforcement = no: Nothing forces anyone to keep a deal. Agreements rely on trust or self-interest.

## Steps to set up your own version
1. Title and players: name the situation and who is involved.
2. Options: list each player's choices, using the game's own options from its playbook.
3. Payoffs or stakes: say what each outcome is worth to each player. For matrix games, fill in the payoff grid.
4. Information and timing: say who moves when, and who knows what.
5. Traits: copy the values in the template file. Change any that do not fit your situation.
6. Check: run `advise` on your file, and compare with the game's simulation with `sim` if one exists.

## Options to model
- Option idea 1: Set reciprocity rules up front: what is shared, how it is handled, and what each partner gets back.
- Option idea 2: Share first in a limited, low-risk way to build the trust that makes fuller exchange possible.
- Option idea 3: Track contributions visibly, so free-riding is noticed early rather than after trust has eroded.

## Payoff grid
Rows (you): Share, Withhold. Columns (them): Share, Withhold.
Enter it with: solve "3,3 0,2; 2,0 1,1" --rows Share,Withhold --cols Share,Withhold

Simulation: `sim information-sharing-alliance` shows the paths, and `sim information-sharing-alliance --play` lets you choose.

## Start from this template
```
title: My Sharing Information Among Partners situation
players: many
timing: simultaneous
interaction: repeated
information: imperfect
payoff: mixed
communication: yes
enforcement: no
domain: military, politics, government
notes: Describe your situation here. Replace the example options with your own.
```

# Nim (Combinatorial Game)

Players take turns removing objects from piles, and whoever takes the last object (or is forced to leave none) wins. It has a complete winning strategy that depends only on the binary structure of the pile sizes.

## Traits and what each one means
- players = two: You and one counterpart. Name them in the title, for example 'me and my landlord'.
- timing = sequential: Decisions come in turns. Write who moves first, and what each mover can see when they choose.
- interaction = one-shot: The situation happens once. Do not plan on future reciprocity, and say so in the description.
- information = perfect: Everyone sees the same facts. Include every relevant fact in the description, because nothing is hidden.
- payoff = zero-sum: One side's gain is the other's loss, as in a fixed prize or winner-takes-all. The total never changes.
- communication = no: No talking or signalling is possible. Actions are the only information.

## Steps to set up your own version
1. Title and players: name the situation and who is involved.
2. Options: list each player's choices, using the game's own options from its playbook.
3. Payoffs or stakes: say what each outcome is worth to each player. For matrix games, fill in the payoff grid.
4. Information and timing: say who moves when, and who knows what.
5. Traits: copy the values in the template file. Change any that do not fit your situation.
6. Check: run `advise` on your file, and compare with the game's simulation with `sim` if one exists.

## Options to model
- Option idea 1: Compute the nim-sum of the pile sizes. If it is zero, you are losing against perfect play; make the move that keeps the position as hard as possible for the opponent.
- Option idea 2: If the nim-sum is non-zero, find a pile where reducing it makes the total zero, and take the right number of objects from it.
- Option idea 3: Recognise independent sub-games: their values combine by nim-sum, which lets you analyse large positions piece by piece.

## Payoff grid
Rows (you): Leave an even pile count, Leave an odd pile count. Columns (them): Opponent leaves even, Opponent leaves odd.
Enter it with: solve "1,1 -1,-1; -1,-1 1,1" --rows Leave an even pile count,Leave an odd pile count --cols Opponent leaves even,Opponent leaves odd

Simulation: `sim nim` shows the paths, and `sim nim --play` lets you choose.

## Start from this template
```
title: My Nim (Combinatorial Game) situation
players: two
timing: sequential
interaction: one-shot
information: perfect
payoff: zero-sum
communication: no
domain: games
notes: Describe your situation here. Replace the example options with your own.
```

# Cake Cutting and Fair Division

Two or more people must divide a shared resource so that each believes they got a fair share. Simple procedures can produce outcomes that every party prefers to the alternatives, without anyone needing to trust the others.

## Traits and what each one means
- players = two: You and one counterpart. Name them in the title, for example 'me and my landlord'.
- timing = sequential: Decisions come in turns. Write who moves first, and what each mover can see when they choose.
- interaction = one-shot: The situation happens once. Do not plan on future reciprocity, and say so in the description.
- information = imperfect: Someone holds private information. Say who knows what, and what each side is guessing about the other.
- payoff = mixed: Both can gain or both can lose. Write what each side gains from cooperating and what it gains from competing.
- communication = yes: You can talk before or during the decision. Say what can be promised, and whether promises are binding.
- bargaining = yes: You are dividing something. State the total, and each side's alternative if no deal is reached (its outside option).

## Steps to set up your own version
1. Title and players: name the situation and who is involved.
2. Options: list each player's choices, using the game's own options from its playbook.
3. Payoffs or stakes: say what each outcome is worth to each player. For matrix games, fill in the payoff grid.
4. Information and timing: say who moves when, and who knows what.
5. Traits: copy the values in the template file. Change any that do not fit your situation.
6. Check: run `advise` on your file, and compare with the game's simulation with `sim` if one exists.

## Options to model
- Option idea 1: Use I-cut-you-choose: one person divides, the other chooses. The divider has every reason to make fair halves.
- Option idea 2: Value the items yourself before negotiating; knowing your own valuation is the basis for any fair claim.
- Option idea 3: With several people, use a procedure that everyone can check, rather than a single arbiter whose fairness is disputed.

## Payoff grid
Rows (you): Cut evenly, Cut unevenly. Columns (them): Take the larger piece, Take the smaller piece.
Enter it with: solve "1,1 0,2; 2,0 1,1" --rows Cut evenly,Cut unevenly --cols Take the larger piece,Take the smaller piece

Simulation: `sim cake-cutting-fair-division` shows the paths, and `sim cake-cutting-fair-division --play` lets you choose.

## Start from this template
```
title: My Cake Cutting and Fair Division situation
players: two
timing: sequential
interaction: one-shot
information: imperfect
payoff: mixed
communication: yes
bargaining: yes
domain: everyday, business, politics
notes: Describe your situation here. Replace the example options with your own.
```

# Search Game (Hide and Seek)

One player hides a target among several locations and the other searches. Searching a location finds the target only if it is there, so both sides mix their choices, and the searcher's cost of covering each location matters.

## Traits and what each one means
- players = two: You and one counterpart. Name them in the title, for example 'me and my landlord'.
- timing = simultaneous: Everyone chooses without seeing the others' choices. Write each side's options down before anyone reveals anything.
- interaction = one-shot: The situation happens once. Do not plan on future reciprocity, and say so in the description.
- information = imperfect: Someone holds private information. Say who knows what, and what each side is guessing about the other.
- payoff = zero-sum: One side's gain is the other's loss, as in a fixed prize or winner-takes-all. The total never changes.
- enforcement = yes: There are binding agreements, penalties or courts. Name the penalty and who can impose it.

## Steps to set up your own version
1. Title and players: name the situation and who is involved.
2. Options: list each player's choices, using the game's own options from its playbook.
3. Payoffs or stakes: say what each outcome is worth to each player. For matrix games, fill in the payoff grid.
4. Information and timing: say who moves when, and who knows what.
5. Traits: copy the values in the template file. Change any that do not fit your situation.
6. Check: run `advise` on your file, and compare with the game's simulation with `sim` if one exists.

## Options to model
- Option idea 1: As searcher: vary your route and timing; a predictable schedule is exploited by anyone who observes it.
- Option idea 2: As searcher: weight your search toward high-value or high-probability locations, but keep enough coverage that the hider cannot safely use the rest.
- Option idea 3: As hider: choose places the searcher is least likely to check, and avoid patterns that reveal your choice.

## Payoff grid
Rows (you): Hide in A, Hide in B. Columns (them): Search A, Search B.
Enter it with: solve "-1,1 1,-1; 1,-1 -1,1" --rows Hide in A,Hide in B --cols Search A,Search B

Simulation: `sim search-game-hide-and-seek` shows the paths, and `sim search-game-hide-and-seek --play` lets you choose.

## Start from this template
```
title: My Search Game (Hide and Seek) situation
players: two
timing: simultaneous
interaction: one-shot
information: imperfect
payoff: zero-sum
enforcement: yes
domain: military, games, business
notes: Describe your situation here. Replace the example options with your own.
```

# Evolutionarily Stable Strategies (Population Games)

In a population where individuals meet at random and their success depends on their strategy, a strategy is evolutionarily stable if no small group of mutants can do better against it. It explains animal conflict and some social norms without anyone choosing consciously.

## Traits and what each one means
- players = many: Three or more players. Either list each player, or model the rest as one group with a shared outcome. Many-player games need the group's total effect spelled out.
- timing = simultaneous: Everyone chooses without seeing the others' choices. Write each side's options down before anyone reveals anything.
- interaction = repeated: It recurs. Say how many rounds, and how much the future matters to each side. A longer, more valuable future usually supports cooperation.
- information = perfect: Everyone sees the same facts. Include every relevant fact in the description, because nothing is hidden.
- payoff = mixed: Both can gain or both can lose. Write what each side gains from cooperating and what it gains from competing.
- communication = no: No talking or signalling is possible. Actions are the only information.
- enforcement = no: Nothing forces anyone to keep a deal. Agreements rely on trust or self-interest.

## Steps to set up your own version
1. Title and players: name the situation and who is involved.
2. Options: list each player's choices, using the game's own options from its playbook.
3. Payoffs or stakes: say what each outcome is worth to each player. For matrix games, fill in the payoff grid.
4. Information and timing: say who moves when, and who knows what.
5. Traits: copy the values in the template file. Change any that do not fit your situation.
6. Check: run `advise` on your file, and compare with the game's simulation with `sim` if one exists.

## Options to model
- Option idea 1: Ask whether your strategy can be invaded: if a rare mutant strategy does better against the common one, the common one is not stable.
- Option idea 2: Expect stable mixed populations, rather than a single winning type, when the costs of conflict are high.
- Option idea 3: Use this reasoning to predict how a norm will hold: it persists if deviants do worse than conformists.

## Payoff grid
Rows (you): Hawk, Dove. Columns (them): Hawk, Dove.
Enter it with: solve "-1,-1 2,0; 0,2 1,1" --rows Hawk,Dove --cols Hawk,Dove

Simulation: `sim ess-hawk-dove-population` shows the paths, and `sim ess-hawk-dove-population --play` lets you choose.

## Start from this template
```
title: My Evolutionarily Stable Strategies (Population Games) situation
players: many
timing: simultaneous
interaction: repeated
information: perfect
payoff: mixed
communication: no
enforcement: no
domain: games, society, economy
notes: Describe your situation here. Replace the example options with your own.
```

# Vaccination and Herd Immunity (Free-Riding)

Each person can benefit from others' vaccination without being vaccinated, because when enough people are protected, the disease cannot spread. The individual temptation to skip the vaccine can erode the protection the group depends on.

## Traits and what each one means
- players = many: Three or more players. Either list each player, or model the rest as one group with a shared outcome. Many-player games need the group's total effect spelled out.
- timing = simultaneous: Everyone chooses without seeing the others' choices. Write each side's options down before anyone reveals anything.
- interaction = repeated: It recurs. Say how many rounds, and how much the future matters to each side. A longer, more valuable future usually supports cooperation.
- information = imperfect: Someone holds private information. Say who knows what, and what each side is guessing about the other.
- payoff = mixed: Both can gain or both can lose. Write what each side gains from cooperating and what it gains from competing.
- communication = yes: You can talk before or during the decision. Say what can be promised, and whether promises are binding.
- enforcement = yes: There are binding agreements, penalties or courts. Name the penalty and who can impose it.

## Steps to set up your own version
1. Title and players: name the situation and who is involved.
2. Options: list each player's choices, using the game's own options from its playbook.
3. Payoffs or stakes: say what each outcome is worth to each player. For matrix games, fill in the payoff grid.
4. Information and timing: say who moves when, and who knows what.
5. Traits: copy the values in the template file. Change any that do not fit your situation.
6. Check: run `advise` on your file, and compare with the game's simulation with `sim` if one exists.

## Options to model
- Option idea 1: Use reliable, specific information about the actual risks and side effects; misinformation pushes choices toward free-riding.
- Option idea 2: Make vaccination convenient and visible, and track uptake so people can see that protection is widely shared.
- Option idea 3: Where the benefit is shared, consider incentives or requirements, since private choices alone may not reach the protective level.

## Payoff grid
Rows (you): Vaccinate, Skip. Columns (them): Others vaccinate, Others skip.
Enter it with: solve "3,3 2,1; 4,2 0,0" --rows Vaccinate,Skip --cols Others vaccinate,Others skip

Simulation: `sim vaccination-free-riding` shows the paths, and `sim vaccination-free-riding --play` lets you choose.

## Start from this template
```
title: My Vaccination and Herd Immunity (Free-Riding) situation
players: many
timing: simultaneous
interaction: repeated
information: imperfect
payoff: mixed
communication: yes
enforcement: yes
domain: everyday, society, economy
notes: Describe your situation here. Replace the example options with your own.
```

# International Climate Treaty (Global Public Good)

Countries benefit from emission reductions by others while bearing the costs of their own. Treaties succeed when they make participation stable, which usually requires side-payments, monitoring and conditional commitments.

## Traits and what each one means
- players = many: Three or more players. Either list each player, or model the rest as one group with a shared outcome. Many-player games need the group's total effect spelled out.
- timing = simultaneous: Everyone chooses without seeing the others' choices. Write each side's options down before anyone reveals anything.
- interaction = repeated: It recurs. Say how many rounds, and how much the future matters to each side. A longer, more valuable future usually supports cooperation.
- information = imperfect: Someone holds private information. Say who knows what, and what each side is guessing about the other.
- payoff = mixed: Both can gain or both can lose. Write what each side gains from cooperating and what it gains from competing.
- communication = yes: You can talk before or during the decision. Say what can be promised, and whether promises are binding.
- enforcement = no: Nothing forces anyone to keep a deal. Agreements rely on trust or self-interest.

## Steps to set up your own version
1. Title and players: name the situation and who is involved.
2. Options: list each player's choices, using the game's own options from its playbook.
3. Payoffs or stakes: say what each outcome is worth to each player. For matrix games, fill in the payoff grid.
4. Information and timing: say who moves when, and who knows what.
5. Traits: copy the values in the template file. Change any that do not fit your situation.
6. Check: run `advise` on your file, and compare with the game's simulation with `sim` if one exists.

## Options to model
- Option idea 1: Design side-payments or technology transfers so that the costs of joining fall on those who gain least from acting alone.
- Option idea 2: Use conditional commitments: each party agrees to act if enough others do, which makes cooperation worth joining.
- Option idea 3: Build monitoring and transparent reporting, so that compliance is observable and cheating is detectable.

## Payoff grid
Rows (you): Cut emissions, Do not cut. Columns (them): Other cuts, Other does not cut.
Enter it with: solve "3,3 0,4; 4,0 1,1" --rows Cut emissions,Do not cut --cols Other cuts,Other does not cut

Simulation: `sim climate-treaty-public-goods` shows the paths, and `sim climate-treaty-public-goods --play` lets you choose.

## Start from this template
```
title: My International Climate Treaty (Global Public Good) situation
players: many
timing: simultaneous
interaction: repeated
information: imperfect
payoff: mixed
communication: yes
enforcement: no
domain: environment, politics, economy
notes: Describe your situation here. Replace the example options with your own.
```

# Standards War and Network Effects

When a product becomes more valuable as more people use it, rival firms compete to set the standard. Winning the market can matter more than having the best technology, and early choices lock in whole ecosystems.

## Traits and what each one means
- players = two: You and one counterpart. Name them in the title, for example 'me and my landlord'.
- timing = sequential: Decisions come in turns. Write who moves first, and what each mover can see when they choose.
- interaction = one-shot: The situation happens once. Do not plan on future reciprocity, and say so in the description.
- information = perfect: Everyone sees the same facts. Include every relevant fact in the description, because nothing is hidden.
- payoff = common-interest: You want the same outcome. The challenge is coordinating on it, not conflicting over it.
- communication = yes: You can talk before or during the decision. Say what can be promised, and whether promises are binding.
- commitment = yes: Someone can commit publicly or irreversibly. Write the commitment mechanism, such as a signed contract or a visible step that cannot be undone.

## Steps to set up your own version
1. Title and players: name the situation and who is involved.
2. Options: list each player's choices, using the game's own options from its playbook.
3. Payoffs or stakes: say what each outcome is worth to each player. For matrix games, fill in the payoff grid.
4. Information and timing: say who moves when, and who knows what.
5. Traits: copy the values in the template file. Change any that do not fit your situation.
6. Check: run `advise` on your file, and compare with the game's simulation with `sim` if one exists.

## Options to model
- Option idea 1: Build alliances early: a standard with committed partners wins more users than a better standard with none.
- Option idea 2: Consider openness: licensing or open standards can widen adoption even when they give up some control.
- Option idea 3: Pre-announce and commit to a roadmap, so buyers and developers can plan around your standard.

## Payoff grid
Rows (you): Adopt standard A, Adopt standard B. Columns (them): Adopt standard A, Adopt standard B.
Enter it with: solve "3,3 0,0; 0,0 2,2" --rows Adopt standard A,Adopt standard B --cols Adopt standard A,Adopt standard B

Simulation: `sim standards-war-network-effects` shows the paths, and `sim standards-war-network-effects --play` lets you choose.

## Start from this template
```
title: My Standards War and Network Effects situation
players: two
timing: sequential
interaction: one-shot
information: perfect
payoff: common-interest
communication: yes
commitment: yes
domain: business, economy
notes: Describe your situation here. Replace the example options with your own.
```

# Insurance and Moral Hazard

An insurer cannot observe how careful the insured person is, so full coverage can reduce the insured's care. Deductibles, monitoring and contract design realign incentives while keeping protection in place.

## Traits and what each one means
- players = two: You and one counterpart. Name them in the title, for example 'me and my landlord'.
- timing = sequential: Decisions come in turns. Write who moves first, and what each mover can see when they choose.
- interaction = one-shot: The situation happens once. Do not plan on future reciprocity, and say so in the description.
- information = imperfect: Someone holds private information. Say who knows what, and what each side is guessing about the other.
- payoff = mixed: Both can gain or both can lose. Write what each side gains from cooperating and what it gains from competing.
- enforcement = yes: There are binding agreements, penalties or courts. Name the penalty and who can impose it.
- bargaining = yes: You are dividing something. State the total, and each side's alternative if no deal is reached (its outside option).

## Steps to set up your own version
1. Title and players: name the situation and who is involved.
2. Options: list each player's choices, using the game's own options from its playbook.
3. Payoffs or stakes: say what each outcome is worth to each player. For matrix games, fill in the payoff grid.
4. Information and timing: say who moves when, and who knows what.
5. Traits: copy the values in the template file. Change any that do not fit your situation.
6. Check: run `advise` on your file, and compare with the game's simulation with `sim` if one exists.

## Options to model
- Option idea 1: As insurer: use deductibles or co-payments so that the insured keeps some stake in preventing losses.
- Option idea 2: As insurer: reward verified precautions with lower premiums, and check claims against evidence.
- Option idea 3: As insured: understand which precautions the policy expects; sticking to them protects your claim and your premium.

## Payoff grid
Rows (you): Careful, Careless. Columns (them): Audit, Trust.
Enter it with: solve "2,1 2,2; 1,1 4,-2" --rows Careful,Careless --cols Audit,Trust

Simulation: `sim insurance-moral-hazard` shows the paths, and `sim insurance-moral-hazard --play` lets you choose.

## Start from this template
```
title: My Insurance and Moral Hazard situation
players: two
timing: sequential
interaction: one-shot
information: imperfect
payoff: mixed
enforcement: yes
bargaining: yes
domain: business, economy
notes: Describe your situation here. Replace the example options with your own.
```

# Household Chores and Shared Bills

Housemates or partners share tasks and costs that are easy to avoid. Without clear rules and visible records, one person often ends up doing more, and resentment grows. A simple system of fair shares and visible tallies keeps cooperation going.

## Traits and what each one means
- players = many: Three or more players. Either list each player, or model the rest as one group with a shared outcome. Many-player games need the group's total effect spelled out.
- timing = simultaneous: Everyone chooses without seeing the others' choices. Write each side's options down before anyone reveals anything.
- interaction = repeated: It recurs. Say how many rounds, and how much the future matters to each side. A longer, more valuable future usually supports cooperation.
- information = perfect: Everyone sees the same facts. Include every relevant fact in the description, because nothing is hidden.
- payoff = mixed: Both can gain or both can lose. Write what each side gains from cooperating and what it gains from competing.
- communication = yes: You can talk before or during the decision. Say what can be promised, and whether promises are binding.
- enforcement = no: Nothing forces anyone to keep a deal. Agreements rely on trust or self-interest.

## Steps to set up your own version
1. Title and players: name the situation and who is involved.
2. Options: list each player's choices, using the game's own options from its playbook.
3. Payoffs or stakes: say what each outcome is worth to each player. For matrix games, fill in the payoff grid.
4. Information and timing: say who moves when, and who knows what.
5. Traits: copy the values in the template file. Change any that do not fit your situation.
6. Check: run `advise` on your file, and compare with the game's simulation with `sim` if one exists.

## Options to model
- Option idea 1: Agree on clear tasks and a rotation, written down where everyone can see it.
- Option idea 2: Split shared bills by a simple rule, such as proportional to income or equal, and settle on a fixed schedule.
- Option idea 3: Keep a visible tally of contributions; people adjust their behaviour when they can see imbalance.

## Payoff grid
Rows (you): Do your share, Free-ride. Columns (them): Do your share, Free-ride.
Enter it with: solve "2,2 0,3; 3,0 1,1" --rows Do your share,Free-ride --cols Do your share,Free-ride

Simulation: `sim household-chores-bills` shows the paths, and `sim household-chores-bills --play` lets you choose.

## Start from this template
```
title: My Household Chores and Shared Bills situation
players: many
timing: simultaneous
interaction: repeated
information: perfect
payoff: mixed
communication: yes
enforcement: no
domain: everyday
notes: Describe your situation here. Replace the example options with your own.
```

# Alliance Commitments and Entrapment

Allies make commitments that can drag them into conflicts they did not want, while the other side may test whether those commitments are real. Clear, limited commitments deter attacks; vague or unlimited ones invite both entrapment and abandonment.

## Traits and what each one means
- players = many: Three or more players. Either list each player, or model the rest as one group with a shared outcome. Many-player games need the group's total effect spelled out.
- timing = sequential: Decisions come in turns. Write who moves first, and what each mover can see when they choose.
- interaction = repeated: It recurs. Say how many rounds, and how much the future matters to each side. A longer, more valuable future usually supports cooperation.
- information = imperfect: Someone holds private information. Say who knows what, and what each side is guessing about the other.
- payoff = mixed: Both can gain or both can lose. Write what each side gains from cooperating and what it gains from competing.
- communication = yes: You can talk before or during the decision. Say what can be promised, and whether promises are binding.
- commitment = yes: Someone can commit publicly or irreversibly. Write the commitment mechanism, such as a signed contract or a visible step that cannot be undone.

## Steps to set up your own version
1. Title and players: name the situation and who is involved.
2. Options: list each player's choices, using the game's own options from its playbook.
3. Payoffs or stakes: say what each outcome is worth to each player. For matrix games, fill in the payoff grid.
4. Information and timing: say who moves when, and who knows what.
5. Traits: copy the values in the template file. Change any that do not fit your situation.
6. Check: run `advise` on your file, and compare with the game's simulation with `sim` if one exists.

## Options to model
- Option idea 1: Define your commitments clearly and limit them to what you can actually deliver; vague or unlimited promises invite testing.
- Option idea 2: Set consultation rules with allies before crises, so that escalation decisions are made together.
- Option idea 3: As the smaller partner: seek assurances that are specific, and avoid actions that pull your ally into conflicts you did not agree to.

## Payoff grid
Rows (you): Support, Withdraw. Columns (them): Commit, Abandon.
Enter it with: solve "2,2 -2,0; 0,-1 1,1" --rows Support,Withdraw --cols Commit,Abandon

Simulation: `sim alliance-entrapment` shows the paths, and `sim alliance-entrapment --play` lets you choose.

## Start from this template
```
title: My Alliance Commitments and Entrapment situation
players: many
timing: sequential
interaction: repeated
information: imperfect
payoff: mixed
communication: yes
commitment: yes
domain: military, politics
notes: Describe your situation here. Replace the example options with your own.
```

# Policy Reform with Veto Players

Reform needs the agreement of several actors who each can block it. The more veto players there are, and the further apart their preferences, the harder change becomes. Packaging, sequencing and compensation can make reform possible.

## Traits and what each one means
- players = many: Three or more players. Either list each player, or model the rest as one group with a shared outcome. Many-player games need the group's total effect spelled out.
- timing = sequential: Decisions come in turns. Write who moves first, and what each mover can see when they choose.
- interaction = one-shot: The situation happens once. Do not plan on future reciprocity, and say so in the description.
- information = perfect: Everyone sees the same facts. Include every relevant fact in the description, because nothing is hidden.
- payoff = mixed: Both can gain or both can lose. Write what each side gains from cooperating and what it gains from competing.
- enforcement = yes: There are binding agreements, penalties or courts. Name the penalty and who can impose it.
- commitment = yes: Someone can commit publicly or irreversibly. Write the commitment mechanism, such as a signed contract or a visible step that cannot be undone.
- bargaining = yes: You are dividing something. State the total, and each side's alternative if no deal is reached (its outside option).

## Steps to set up your own version
1. Title and players: name the situation and who is involved.
2. Options: list each player's choices, using the game's own options from its playbook.
3. Payoffs or stakes: say what each outcome is worth to each player. For matrix games, fill in the payoff grid.
4. Information and timing: say who moves when, and who knows what.
5. Traits: copy the values in the template file. Change any that do not fit your situation.
6. Check: run `advise` on your file, and compare with the game's simulation with `sim` if one exists.

## Options to model
- Option idea 1: Map the veto players and their preferences before proposing; know who can block and who can be persuaded.
- Option idea 2: Package the reform with side-payments that give each veto player something they value.
- Option idea 3: Sequence the reform so that early steps build support for later ones, and so that losses are spread over time.

## Payoff grid
Rows (you): Propose a large reform, Propose a small reform. Columns (them): Accept, Block.
Enter it with: solve "2,2 -1,1; 1,-1 1,0" --rows Propose a large reform,Propose a small reform --cols Accept,Block

Simulation: `sim veto-players-reform` shows the paths, and `sim veto-players-reform --play` lets you choose.

## Start from this template
```
title: My Policy Reform with Veto Players situation
players: many
timing: sequential
interaction: one-shot
information: perfect
payoff: mixed
enforcement: yes
commitment: yes
bargaining: yes
domain: government, politics
notes: Describe your situation here. Replace the example options with your own.
```

# Lobbying and Political Influence

Interest groups try to shape decisions by providing information, support and resources to decision-makers. Credible information and long-run reputation matter more than one-off persuasion, and transparency decides whether influence is trusted.

## Traits and what each one means
- players = many: Three or more players. Either list each player, or model the rest as one group with a shared outcome. Many-player games need the group's total effect spelled out.
- timing = simultaneous: Everyone chooses without seeing the others' choices. Write each side's options down before anyone reveals anything.
- interaction = repeated: It recurs. Say how many rounds, and how much the future matters to each side. A longer, more valuable future usually supports cooperation.
- information = imperfect: Someone holds private information. Say who knows what, and what each side is guessing about the other.
- payoff = mixed: Both can gain or both can lose. Write what each side gains from cooperating and what it gains from competing.
- communication = yes: You can talk before or during the decision. Say what can be promised, and whether promises are binding.
- enforcement = yes: There are binding agreements, penalties or courts. Name the penalty and who can impose it.

## Steps to set up your own version
1. Title and players: name the situation and who is involved.
2. Options: list each player's choices, using the game's own options from its playbook.
3. Payoffs or stakes: say what each outcome is worth to each player. For matrix games, fill in the payoff grid.
4. Information and timing: say who moves when, and who knows what.
5. Traits: copy the values in the template file. Change any that do not fit your situation.
6. Check: run `advise` on your file, and compare with the game's simulation with `sim` if one exists.

## Options to model
- Option idea 1: Provide accurate, checkable information; a decision-maker who catches one false claim discounts everything you say.
- Option idea 2: Make your interests and affiliations transparent, so that your evidence is judged on its merits.
- Option idea 3: Build coalitions with groups that share an interest, which is more persuasive than a single voice.

## Payoff grid
Rows (you): Lobby, Do not lobby. Columns (them): Accommodate, Resist.
Enter it with: solve "3,2 -1,0; 0,1 1,1" --rows Lobby,Do not lobby --cols Accommodate,Resist

Simulation: `sim lobbying-influence` shows the paths, and `sim lobbying-influence --play` lets you choose.

## Start from this template
```
title: My Lobbying and Political Influence situation
players: many
timing: simultaneous
interaction: repeated
information: imperfect
payoff: mixed
communication: yes
enforcement: yes
domain: politics, government, business
notes: Describe your situation here. Replace the example options with your own.
```

# Coercive Groups and Cults

Some groups make leaving very costly, control what members learn, and raise commitment over time. The game is lopsided: the group controls information and exit costs, while the member and their family often know less than they need to. Protecting people means keeping exit cheap, information open and outside relationships intact.

## Traits and what each one means
- players = two: You and one counterpart. Name them in the title, for example 'me and my landlord'.
- timing = sequential: Decisions come in turns. Write who moves first, and what each mover can see when they choose.
- interaction = repeated: It recurs. Say how many rounds, and how much the future matters to each side. A longer, more valuable future usually supports cooperation.
- information = imperfect: Someone holds private information. Say who knows what, and what each side is guessing about the other.
- payoff = mixed: Both can gain or both can lose. Write what each side gains from cooperating and what it gains from competing.
- communication = no: No talking or signalling is possible. Actions are the only information.
- enforcement = no: Nothing forces anyone to keep a deal. Agreements rely on trust or self-interest.
- commitment = yes: Someone can commit publicly or irreversibly. Write the commitment mechanism, such as a signed contract or a visible step that cannot be undone.

## Steps to set up your own version
1. Title and players: name the situation and who is involved.
2. Options: list each player's choices, using the game's own options from its playbook.
3. Payoffs or stakes: say what each outcome is worth to each player. For matrix games, fill in the payoff grid.
4. Information and timing: say who moves when, and who knows what.
5. Traits: copy the values in the template file. Change any that do not fit your situation.
6. Check: run `advise` on your file, and compare with the game's simulation with `sim` if one exists.

## Options to model
- Option idea 1: For prospective members: keep outside relationships and independent advice; be wary of any demand to cut them off.
- Option idea 2: For prospective members: test claims against independent evidence, and set time limits on commitments and money you will not give.
- Option idea 3: For prospective members: agree in advance on a trusted person you can call to leave; a pre-planned exit is far easier than one improvised under pressure.

## Payoff grid
Rows (you): Stay, Leave. Columns (them): Loosen control, Tighten control.
Enter it with: solve "2,2 -1,1; 0,0 1,-1" --rows Stay,Leave --cols Loosen control,Tighten control

Simulation: `sim cults-coercive-groups` shows the paths, and `sim cults-coercive-groups --play` lets you choose.

## Start from this template
```
title: My Coercive Groups and Cults situation
players: two
timing: sequential
interaction: repeated
information: imperfect
payoff: mixed
communication: no
enforcement: no
commitment: yes
domain: society, everyday
notes: Describe your situation here. Replace the example options with your own.
```

# Whistleblowing and Reporting Wrongdoing

An insider knows about wrongdoing that the organisation would prefer to hide. Reporting carries a personal risk of retaliation, while staying silent lets the wrongdoing continue. Good documentation and the right channel change the calculation.

## Traits and what each one means
- players = two: You and one counterpart. Name them in the title, for example 'me and my landlord'.
- timing = sequential: Decisions come in turns. Write who moves first, and what each mover can see when they choose.
- interaction = one-shot: The situation happens once. Do not plan on future reciprocity, and say so in the description.
- information = imperfect: Someone holds private information. Say who knows what, and what each side is guessing about the other.
- payoff = mixed: Both can gain or both can lose. Write what each side gains from cooperating and what it gains from competing.
- communication = yes: You can talk before or during the decision. Say what can be promised, and whether promises are binding.
- enforcement = yes: There are binding agreements, penalties or courts. Name the penalty and who can impose it.

## Steps to set up your own version
1. Title and players: name the situation and who is involved.
2. Options: list each player's choices, using the game's own options from its playbook.
3. Payoffs or stakes: say what each outcome is worth to each player. For matrix games, fill in the payoff grid.
4. Information and timing: say who moves when, and who knows what.
5. Traits: copy the values in the template file. Change any that do not fit your situation.
6. Check: run `advise` on your file, and compare with the game's simulation with `sim` if one exists.

## Options to model
- Option idea 1: Document carefully and privately: dates, facts and copies you are allowed to keep, without taking confidential material you should not hold.
- Option idea 2: Find out what legal protections apply to you before reporting, and seek advice from a lawyer or a protected reporting body.
- Option idea 3: Use the formal internal channel if it is credible; use an external regulator or authority if it is not, or if retaliation is likely.

## Payoff grid
Rows (you): Report, Stay silent. Columns (them): Firm corrects, Firm covers up.
Enter it with: solve "2,3 -1,-2; 1,2 0,0" --rows Report,Stay silent --cols Firm corrects,Firm covers up

Simulation: `sim whistleblowing` shows the paths, and `sim whistleblowing --play` lets you choose.

## Start from this template
```
title: My Whistleblowing and Reporting Wrongdoing situation
players: two
timing: sequential
interaction: one-shot
information: imperfect
payoff: mixed
communication: yes
enforcement: yes
domain: work, society, government
notes: Describe your situation here. Replace the example options with your own.
```

# Plea Bargaining and Legal Settlement

A prosecutor offers a reduced charge or sentence in exchange for a guilty plea. Both sides compare the certainty of the deal with the risk of trial, and the outcome depends mostly on the strength of the evidence and the cost of delay.

## Traits and what each one means
- players = two: You and one counterpart. Name them in the title, for example 'me and my landlord'.
- timing = sequential: Decisions come in turns. Write who moves first, and what each mover can see when they choose.
- interaction = one-shot: The situation happens once. Do not plan on future reciprocity, and say so in the description.
- information = imperfect: Someone holds private information. Say who knows what, and what each side is guessing about the other.
- payoff = zero-sum: One side's gain is the other's loss, as in a fixed prize or winner-takes-all. The total never changes.
- enforcement = yes: There are binding agreements, penalties or courts. Name the penalty and who can impose it.
- bargaining = yes: You are dividing something. State the total, and each side's alternative if no deal is reached (its outside option).

## Steps to set up your own version
1. Title and players: name the situation and who is involved.
2. Options: list each player's choices, using the game's own options from its playbook.
3. Payoffs or stakes: say what each outcome is worth to each player. For matrix games, fill in the payoff grid.
4. Information and timing: say who moves when, and who knows what.
5. Traits: copy the values in the template file. Change any that do not fit your situation.
6. Check: run `advise` on your file, and compare with the game's simulation with `sim` if one exists.

## Options to model
- Option idea 1: Get a realistic estimate of trial outcomes from a lawyer who has seen the evidence, not just a hope or a fear.
- Option idea 2: Compare the offer with the expected value of trial, including the costs of time, money and the risk of a harsher sentence.
- Option idea 3: Ask what happens to the offer if you wait; deals often change as the trial date approaches.

## Payoff grid
Rows (you): Confess, Stay silent. Columns (them): Confess, Stay silent.
Enter it with: solve "-5,-5 0,-10; -10,0 -1,-1" --rows Confess,Stay silent --cols Confess,Stay silent

Simulation: `sim plea-bargaining` shows the paths, and `sim plea-bargaining --play` lets you choose.

## Start from this template
```
title: My Plea Bargaining and Legal Settlement situation
players: two
timing: sequential
interaction: one-shot
information: imperfect
payoff: zero-sum
enforcement: yes
bargaining: yes
domain: society, government
notes: Describe your situation here. Replace the example options with your own.
```

# Hiring and Screening

An employer must pick a candidate whose ability it cannot see directly. Candidates know more about themselves than the employer does, so signals like credentials and track record carry the weight.

## Traits and what each one means
- players = two: You and one counterpart. Name them in the title, for example 'me and my landlord'.
- timing = sequential: Decisions come in turns. Write who moves first, and what each mover can see when they choose.
- interaction = one-shot: The situation happens once. Do not plan on future reciprocity, and say so in the description.
- information = imperfect: Someone holds private information. Say who knows what, and what each side is guessing about the other.
- payoff = mixed: Both can gain or both can lose. Write what each side gains from cooperating and what it gains from competing.
- communication = yes: You can talk before or during the decision. Say what can be promised, and whether promises are binding.
- bargaining = yes: You are dividing something. State the total, and each side's alternative if no deal is reached (its outside option).

## Steps to set up your own version
1. Title and players: name the situation and who is involved.
2. Options: list each player's choices, using the game's own options from its playbook.
3. Payoffs or stakes: say what each outcome is worth to each player. For matrix games, fill in the payoff grid.
4. Information and timing: say who moves when, and who knows what.
5. Traits: copy the values in the template file. Change any that do not fit your situation.
6. Check: run `advise` on your file, and compare with the game's simulation with `sim` if one exists.

## Options to model
- Option idea 1: As employer: rely on verifiable signals (work samples, trial projects, structured tasks) rather than charisma or self-description.
- Option idea 2: As employer: use the same questions and scoring for every candidate so that ability, not interviewer mood, drives the decision.
- Option idea 3: As candidate: offer proof that is hard to fake, such as a portfolio, a paid trial, or a reference who has seen your work directly.

## Payoff grid
Rows (you): Screen first, Hire untested. Columns (them): Qualified, Unqualified.
Enter it with: solve "3,3 1,0; 2,3 -1,1" --rows Screen first,Hire untested --cols Qualified,Unqualified

Simulation: `sim hiring-screening` shows the paths, and `sim hiring-screening --play` lets you choose.

## Start from this template
```
title: My Hiring and Screening situation
players: two
timing: sequential
interaction: one-shot
information: imperfect
payoff: mixed
communication: yes
bargaining: yes
domain: work, business
notes: Describe your situation here. Replace the example options with your own.
```

# Firing and Performance Management

A manager wants good performance from an employee whose effort is hard to observe, and must sometimes end the employment. Fair, documented process protects both the organisation and the person.

## Traits and what each one means
- players = two: You and one counterpart. Name them in the title, for example 'me and my landlord'.
- timing = sequential: Decisions come in turns. Write who moves first, and what each mover can see when they choose.
- interaction = repeated: It recurs. Say how many rounds, and how much the future matters to each side. A longer, more valuable future usually supports cooperation.
- information = imperfect: Someone holds private information. Say who knows what, and what each side is guessing about the other.
- payoff = mixed: Both can gain or both can lose. Write what each side gains from cooperating and what it gains from competing.
- enforcement = yes: There are binding agreements, penalties or courts. Name the penalty and who can impose it.
- bargaining = yes: You are dividing something. State the total, and each side's alternative if no deal is reached (its outside option).

## Steps to set up your own version
1. Title and players: name the situation and who is involved.
2. Options: list each player's choices, using the game's own options from its playbook.
3. Payoffs or stakes: say what each outcome is worth to each player. For matrix games, fill in the payoff grid.
4. Information and timing: say who moves when, and who knows what.
5. Traits: copy the values in the template file. Change any that do not fit your situation.
6. Check: run `advise` on your file, and compare with the game's simulation with `sim` if one exists.

## Options to model
- Option idea 1: Set specific, measurable expectations in writing before any decision, and review them on a schedule.
- Option idea 2: Give feedback early and specifically; most performance problems are cheaper to fix in the first month than the last.
- Option idea 3: Document facts and dates, not impressions. Records are what make a decision defensible and fair.

## Payoff grid
Rows (you): Support and keep, Fire. Columns (them): Improve, Stay static.
Enter it with: solve "3,3 0,2; -1,0 1,-1" --rows Support and keep,Fire --cols Improve,Stay static

Simulation: `sim firing-and-performance` shows the paths, and `sim firing-and-performance --play` lets you choose.

## Start from this template
```
title: My Firing and Performance Management situation
players: two
timing: sequential
interaction: repeated
information: imperfect
payoff: mixed
enforcement: yes
bargaining: yes
domain: work, business
notes: Describe your situation here. Replace the example options with your own.
```

# Promotion Tournaments

When a single promotion goes to the best of several people, the contest itself motivates effort, but it can also encourage sabotage, hoarding and short-term politics.

## Traits and what each one means
- players = many: Three or more players. Either list each player, or model the rest as one group with a shared outcome. Many-player games need the group's total effect spelled out.
- timing = simultaneous: Everyone chooses without seeing the others' choices. Write each side's options down before anyone reveals anything.
- interaction = repeated: It recurs. Say how many rounds, and how much the future matters to each side. A longer, more valuable future usually supports cooperation.
- information = imperfect: Someone holds private information. Say who knows what, and what each side is guessing about the other.
- payoff = zero-sum: One side's gain is the other's loss, as in a fixed prize or winner-takes-all. The total never changes.
- enforcement = no: Nothing forces anyone to keep a deal. Agreements rely on trust or self-interest.

## Steps to set up your own version
1. Title and players: name the situation and who is involved.
2. Options: list each player's choices, using the game's own options from its playbook.
3. Payoffs or stakes: say what each outcome is worth to each player. For matrix games, fill in the payoff grid.
4. Information and timing: say who moves when, and who knows what.
5. Traits: copy the values in the template file. Change any that do not fit your situation.
6. Check: run `advise` on your file, and compare with the game's simulation with `sim` if one exists.

## Options to model
- Option idea 1: If you are a candidate, build a visible record of results and make your contribution to shared goals explicit.
- Option idea 2: If you are the manager, reward collaboration explicitly, or the tournament will reward hoarding and quiet sabotage.
- Option idea 3: Judge by criteria stated in advance and share them. Secret criteria fuel suspicion and leak into team behaviour.

## Payoff grid
Rows (you): High effort, Low effort. Columns (them): High effort, Low effort.
Enter it with: solve "2,2 0,3; 3,0 1,1" --rows High effort,Low effort --cols High effort,Low effort

Simulation: `sim promotion-tournament` shows the paths, and `sim promotion-tournament --play` lets you choose.

## Start from this template
```
title: My Promotion Tournaments situation
players: many
timing: simultaneous
interaction: repeated
information: imperfect
payoff: zero-sum
enforcement: no
domain: work, business
notes: Describe your situation here. Replace the example options with your own.
```

# Defending a Position

An incumbent holds a role, market share, territory or post that a challenger wants. The incumbent can reinforce what matters most, and the challenger must decide whether the fight is worth its cost.

## Traits and what each one means
- players = two: You and one counterpart. Name them in the title, for example 'me and my landlord'.
- timing = sequential: Decisions come in turns. Write who moves first, and what each mover can see when they choose.
- interaction = one-shot: The situation happens once. Do not plan on future reciprocity, and say so in the description.
- information = imperfect: Someone holds private information. Say who knows what, and what each side is guessing about the other.
- payoff = zero-sum: One side's gain is the other's loss, as in a fixed prize or winner-takes-all. The total never changes.
- commitment = yes: Someone can commit publicly or irreversibly. Write the commitment mechanism, such as a signed contract or a visible step that cannot be undone.

## Steps to set up your own version
1. Title and players: name the situation and who is involved.
2. Options: list each player's choices, using the game's own options from its playbook.
3. Payoffs or stakes: say what each outcome is worth to each player. For matrix games, fill in the payoff grid.
4. Information and timing: say who moves when, and who knows what.
5. Traits: copy the values in the template file. Change any that do not fit your situation.
6. Check: run `advise` on your file, and compare with the game's simulation with `sim` if one exists.

## Options to model
- Option idea 1: Identify the few positions that matter most and reinforce them, rather than defending everything evenly.
- Option idea 2: Make your strength visible and credible in advance. A challenger who believes you are strong will often not attack.
- Option idea 3: As challenger, look for the weakest point rather than the strongest, and commit only after checking what the defence can really do.

## Payoff grid
Rows (you): Attack, Hold. Columns (them): Reinforce, Withdraw.
Enter it with: solve "-1,1 2,-2; 0,0 1,0" --rows Attack,Hold --cols Reinforce,Withdraw

Simulation: `sim defending-a-position` shows the paths, and `sim defending-a-position --play` lets you choose.

## Start from this template
```
title: My Defending a Position situation
players: two
timing: sequential
interaction: one-shot
information: imperfect
payoff: zero-sum
commitment: yes
domain: work, business, military, politics
notes: Describe your situation here. Replace the example options with your own.
```

# Hold-Up and Relationship-Specific Investment

One party invests in something that only works with its partner. The partner can then demand better terms, because the investor is now locked in. Anticipating this, the investor may underinvest.

## Traits and what each one means
- players = two: You and one counterpart. Name them in the title, for example 'me and my landlord'.
- timing = sequential: Decisions come in turns. Write who moves first, and what each mover can see when they choose.
- interaction = one-shot: The situation happens once. Do not plan on future reciprocity, and say so in the description.
- information = perfect: Everyone sees the same facts. Include every relevant fact in the description, because nothing is hidden.
- payoff = mixed: Both can gain or both can lose. Write what each side gains from cooperating and what it gains from competing.
- enforcement = no: Nothing forces anyone to keep a deal. Agreements rely on trust or self-interest.
- commitment = no: Every move can be reversed. Note any reversals that are cheap or expensive.
- bargaining = yes: You are dividing something. State the total, and each side's alternative if no deal is reached (its outside option).

## Steps to set up your own version
1. Title and players: name the situation and who is involved.
2. Options: list each player's choices, using the game's own options from its playbook.
3. Payoffs or stakes: say what each outcome is worth to each player. For matrix games, fill in the payoff grid.
4. Information and timing: say who moves when, and who knows what.
5. Traits: copy the values in the template file. Change any that do not fit your situation.
6. Check: run `advise` on your file, and compare with the game's simulation with `sim` if one exists.

## Options to model
- Option idea 1: Before investing, agree on price, scope and remedies in a contract that covers the specific investment.
- Option idea 2: Stage payments so that each side's exposure stays limited while trust builds.
- Option idea 3: Share ownership or control of the specific asset, so neither side can hold the other up by threat alone.

## Payoff grid
Rows (you): Invest, Do not invest. Columns (them): Supplier shares fairly, Supplier holds up.
Enter it with: solve "4,4 1,5; 0,0 0,0" --rows Invest,Do not invest --cols Supplier shares fairly,Supplier holds up

Simulation: `sim hold-up` shows the paths, and `sim hold-up --play` lets you choose.

## Start from this template
```
title: My Hold-Up and Relationship-Specific Investment situation
players: two
timing: sequential
interaction: one-shot
information: perfect
payoff: mixed
enforcement: no
commitment: no
bargaining: yes
domain: business, work
notes: Describe your situation here. Replace the example options with your own.
```

# Lemons Market (Asymmetric Quality)

Sellers know the quality of what they sell and buyers do not. Buyers offer an average price, which drives good sellers out, leaving a market of poor quality. Signals and guarantees can rescue it.

## Traits and what each one means
- players = many: Three or more players. Either list each player, or model the rest as one group with a shared outcome. Many-player games need the group's total effect spelled out.
- timing = sequential: Decisions come in turns. Write who moves first, and what each mover can see when they choose.
- interaction = repeated: It recurs. Say how many rounds, and how much the future matters to each side. A longer, more valuable future usually supports cooperation.
- information = imperfect: Someone holds private information. Say who knows what, and what each side is guessing about the other.
- payoff = mixed: Both can gain or both can lose. Write what each side gains from cooperating and what it gains from competing.
- communication = yes: You can talk before or during the decision. Say what can be promised, and whether promises are binding.
- enforcement = yes: There are binding agreements, penalties or courts. Name the penalty and who can impose it.

## Steps to set up your own version
1. Title and players: name the situation and who is involved.
2. Options: list each player's choices, using the game's own options from its playbook.
3. Payoffs or stakes: say what each outcome is worth to each player. For matrix games, fill in the payoff grid.
4. Information and timing: say who moves when, and who knows what.
5. Traits: copy the values in the template file. Change any that do not fit your situation.
6. Check: run `advise` on your file, and compare with the game's simulation with `sim` if one exists.

## Options to model
- Option idea 1: As seller of good quality: offer a warranty, inspection report or third-party certification that costs more for poor sellers to imitate.
- Option idea 2: As buyer: pay for verification and use return rights; do not assume the average price is fair.
- Option idea 3: Build a track record through repeated honest dealing, which is a signal that becomes more credible over time.

## Payoff grid
Rows (you): Pay high price, Pay low price. Columns (them): Sell good, Sell bad.
Enter it with: solve "3,2 -2,3; -1,2 1,1" --rows Pay high price,Pay low price --cols Sell good,Sell bad

Simulation: `sim lemons-market` shows the paths, and `sim lemons-market --play` lets you choose.

## Start from this template
```
title: My Lemons Market (Asymmetric Quality) situation
players: many
timing: sequential
interaction: repeated
information: imperfect
payoff: mixed
communication: yes
enforcement: yes
domain: business, economy
notes: Describe your situation here. Replace the example options with your own.
```

# Bertrand Price Competition

Firms selling near-identical products compete on price. Undercutting is tempting, and without differentiation or capacity limits, price can fall to cost.

## Traits and what each one means
- players = two: You and one counterpart. Name them in the title, for example 'me and my landlord'.
- timing = simultaneous: Everyone chooses without seeing the others' choices. Write each side's options down before anyone reveals anything.
- interaction = one-shot: The situation happens once. Do not plan on future reciprocity, and say so in the description.
- information = perfect: Everyone sees the same facts. Include every relevant fact in the description, because nothing is hidden.
- payoff = mixed: Both can gain or both can lose. Write what each side gains from cooperating and what it gains from competing.
- communication = no: No talking or signalling is possible. Actions are the only information.

## Steps to set up your own version
1. Title and players: name the situation and who is involved.
2. Options: list each player's choices, using the game's own options from its playbook.
3. Payoffs or stakes: say what each outcome is worth to each player. For matrix games, fill in the payoff grid.
4. Information and timing: say who moves when, and who knows what.
5. Traits: copy the values in the template file. Change any that do not fit your situation.
6. Check: run `advise` on your file, and compare with the game's simulation with `sim` if one exists.

## Options to model
- Option idea 1: Differentiate on something buyers value that a competitor cannot copy quickly: service, speed, location or brand trust.
- Option idea 2: Limit capacity so that undercutting cannot win you the whole market; a price cut then gains you little.
- Option idea 3: In a repeated market, avoid starting a price war. A price cut that is matched immediately usually costs both firms.

## Payoff grid
Rows (you): Hold high price, Cut price. Columns (them): Hold high price, Cut price.
Enter it with: solve "4,4 0,6; 6,0 2,2" --rows Hold high price,Cut price --cols Hold high price,Cut price

Simulation: `sim bertrand-price-war` shows the paths, and `sim bertrand-price-war --play` lets you choose.

## Start from this template
```
title: My Bertrand Price Competition situation
players: two
timing: simultaneous
interaction: one-shot
information: perfect
payoff: mixed
communication: no
domain: business, economy
notes: Describe your situation here. Replace the example options with your own.
```

# Reputation Systems and Reviews

Buyers rate sellers after each transaction. Good ratings reward quality over time, but ratings are only useful when they are honest, and both sides face incentives to game them.

## Traits and what each one means
- players = many: Three or more players. Either list each player, or model the rest as one group with a shared outcome. Many-player games need the group's total effect spelled out.
- timing = sequential: Decisions come in turns. Write who moves first, and what each mover can see when they choose.
- interaction = repeated: It recurs. Say how many rounds, and how much the future matters to each side. A longer, more valuable future usually supports cooperation.
- information = imperfect: Someone holds private information. Say who knows what, and what each side is guessing about the other.
- payoff = mixed: Both can gain or both can lose. Write what each side gains from cooperating and what it gains from competing.
- enforcement = yes: There are binding agreements, penalties or courts. Name the penalty and who can impose it.

## Steps to set up your own version
1. Title and players: name the situation and who is involved.
2. Options: list each player's choices, using the game's own options from its playbook.
3. Payoffs or stakes: say what each outcome is worth to each player. For matrix games, fill in the payoff grid.
4. Information and timing: say who moves when, and who knows what.
5. Traits: copy the values in the template file. Change any that do not fit your situation.
6. Check: run `advise` on your file, and compare with the game's simulation with `sim` if one exists.

## Options to model
- Option idea 1: As seller: deliver consistently, respond to problems quickly, and let the record build; reputation is slow to earn and fast to lose.
- Option idea 2: As buyer: read the pattern of reviews, not just the average, and be wary of a sudden burst of perfect ratings.
- Option idea 3: As buyer: leave honest feedback, since the system is only as good as the reviews it collects.

## Payoff grid
Rows (you): Deliver quality, Cut corners. Columns (them): Review honestly, Skip review.
Enter it with: solve "2,2 2,1; 0,-2 0,0" --rows Deliver quality,Cut corners --cols Review honestly,Skip review

Simulation: `sim reputation-reviews` shows the paths, and `sim reputation-reviews --play` lets you choose.

## Start from this template
```
title: My Reputation Systems and Reviews situation
players: many
timing: sequential
interaction: repeated
information: imperfect
payoff: mixed
enforcement: yes
domain: business, everyday
notes: Describe your situation here. Replace the example options with your own.
```

# Matching Markets (Jobs, Schools, Dating)

Two sides with preferences must be matched: students and schools, workers and employers, people looking for partners. The outcome depends on whether anyone prefers to leave their assigned match for someone they would rather have.

## Traits and what each one means
- players = many: Three or more players. Either list each player, or model the rest as one group with a shared outcome. Many-player games need the group's total effect spelled out.
- timing = simultaneous: Everyone chooses without seeing the others' choices. Write each side's options down before anyone reveals anything.
- interaction = one-shot: The situation happens once. Do not plan on future reciprocity, and say so in the description.
- information = imperfect: Someone holds private information. Say who knows what, and what each side is guessing about the other.
- payoff = mixed: Both can gain or both can lose. Write what each side gains from cooperating and what it gains from competing.
- communication = yes: You can talk before or during the decision. Say what can be promised, and whether promises are binding.

## Steps to set up your own version
1. Title and players: name the situation and who is involved.
2. Options: list each player's choices, using the game's own options from its playbook.
3. Payoffs or stakes: say what each outcome is worth to each player. For matrix games, fill in the payoff grid.
4. Information and timing: say who moves when, and who knows what.
5. Traits: copy the values in the template file. Change any that do not fit your situation.
6. Check: run `advise` on your file, and compare with the game's simulation with `sim` if one exists.

## Options to model
- Option idea 1: Rank options by your true preference when the mechanism uses deferred acceptance; gaming the list rarely helps.
- Option idea 2: Apply to a realistic set: include your best option, a good match, and at least one safe option you would accept.
- Option idea 3: Judge your own market value honestly. Aiming far above what the other side wants wastes time and offers.

## Payoff grid
Rows (you): Propose to top choice, Propose to second choice. Columns (them): Accept, Reject.
Enter it with: solve "2,2 0,0; 1,1 1,1" --rows Propose to top choice,Propose to second choice --cols Accept,Reject

Simulation: `sim matching-markets` shows the paths, and `sim matching-markets --play` lets you choose.

## Start from this template
```
title: My Matching Markets (Jobs, Schools, Dating) situation
players: many
timing: simultaneous
interaction: one-shot
information: imperfect
payoff: mixed
communication: yes
domain: everyday, work
notes: Describe your situation here. Replace the example options with your own.
```

# Bank Run (Coordination Failure)

A bank can pay depositors only if most do not withdraw at once. Each depositor is safer withdrawing early if others do, so a rumour can cause a run even when the bank is sound.

## Traits and what each one means
- players = many: Three or more players. Either list each player, or model the rest as one group with a shared outcome. Many-player games need the group's total effect spelled out.
- timing = simultaneous: Everyone chooses without seeing the others' choices. Write each side's options down before anyone reveals anything.
- interaction = one-shot: The situation happens once. Do not plan on future reciprocity, and say so in the description.
- information = imperfect: Someone holds private information. Say who knows what, and what each side is guessing about the other.
- payoff = common-interest: You want the same outcome. The challenge is coordinating on it, not conflicting over it.
- communication = yes: You can talk before or during the decision. Say what can be promised, and whether promises are binding.
- enforcement = yes: There are binding agreements, penalties or courts. Name the penalty and who can impose it.

## Steps to set up your own version
1. Title and players: name the situation and who is involved.
2. Options: list each player's choices, using the game's own options from its playbook.
3. Payoffs or stakes: say what each outcome is worth to each player. For matrix games, fill in the payoff grid.
4. Information and timing: say who moves when, and who knows what.
5. Traits: copy the values in the template file. Change any that do not fit your situation.
6. Check: run `advise` on your file, and compare with the game's simulation with `sim` if one exists.

## Options to model
- Option idea 1: As depositor: check the fundamentals and whether reassurance from a credible authority exists before acting on a rumour.
- Option idea 2: As institution: communicate clearly and early, and make deposit insurance or a lender of last resort visible.
- Option idea 3: As regulator: a credible backstop removes the reason for the run, so it is rarely used but very valuable.

## Payoff grid
Rows (you): Wait, Withdraw early. Columns (them): Wait, Withdraw early.
Enter it with: solve "2,2 0,1; 1,0 1,1" --rows Wait,Withdraw early --cols Wait,Withdraw early

Simulation: `sim bank-run` shows the paths, and `sim bank-run --play` lets you choose.

## Start from this template
```
title: My Bank Run (Coordination Failure) situation
players: many
timing: simultaneous
interaction: one-shot
information: imperfect
payoff: common-interest
communication: yes
enforcement: yes
domain: economy, business
notes: Describe your situation here. Replace the example options with your own.
```

# Herding and Information Cascades

People decide one after another, and each can see earlier choices. After a few early choices, rational people may copy the crowd even against their own private information, so the group can lock onto a wrong answer.

## Traits and what each one means
- players = many: Three or more players. Either list each player, or model the rest as one group with a shared outcome. Many-player games need the group's total effect spelled out.
- timing = sequential: Decisions come in turns. Write who moves first, and what each mover can see when they choose.
- interaction = one-shot: The situation happens once. Do not plan on future reciprocity, and say so in the description.
- information = imperfect: Someone holds private information. Say who knows what, and what each side is guessing about the other.
- payoff = mixed: Both can gain or both can lose. Write what each side gains from cooperating and what it gains from competing.
- communication = no: No talking or signalling is possible. Actions are the only information.

## Steps to set up your own version
1. Title and players: name the situation and who is involved.
2. Options: list each player's choices, using the game's own options from its playbook.
3. Payoffs or stakes: say what each outcome is worth to each player. For matrix games, fill in the payoff grid.
4. Information and timing: say who moves when, and who knows what.
5. Traits: copy the values in the template file. Change any that do not fit your situation.
6. Check: run `advise` on your file, and compare with the game's simulation with `sim` if one exists.

## Options to model
- Option idea 1: Make your private information count: when your own evidence is strong, act on it even if the crowd disagrees.
- Option idea 2: Seek independent sources, since copying the crowd gives you no new information once a cascade has started.
- Option idea 3: If you are first or early, be transparent about how confident you are; your choice shapes everyone who follows.

## Payoff grid
Rows (you): Follow the crowd, Decide privately. Columns (them): Follow the crowd, Decide privately.
Enter it with: solve "2,2 0,1; 1,0 1,1" --rows Follow the crowd,Decide privately --cols Follow the crowd,Decide privately

Simulation: `sim herding-cascades` shows the paths, and `sim herding-cascades --play` lets you choose.

## Start from this template
```
title: My Herding and Information Cascades situation
players: many
timing: sequential
interaction: one-shot
information: imperfect
payoff: mixed
communication: no
domain: economy, everyday, politics
notes: Describe your situation here. Replace the example options with your own.
```

# Traveler's Dilemma

Two travellers each claim a value for a lost bag, and the airline pays the lower claim, with a bonus to the honest claimant. The logic says undercut by one unit, but experiments show people claim high and reward the honest.

## Traits and what each one means
- players = two: You and one counterpart. Name them in the title, for example 'me and my landlord'.
- timing = simultaneous: Everyone chooses without seeing the others' choices. Write each side's options down before anyone reveals anything.
- interaction = one-shot: The situation happens once. Do not plan on future reciprocity, and say so in the description.
- information = perfect: Everyone sees the same facts. Include every relevant fact in the description, because nothing is hidden.
- payoff = mixed: Both can gain or both can lose. Write what each side gains from cooperating and what it gains from competing.
- communication = no: No talking or signalling is possible. Actions are the only information.

## Steps to set up your own version
1. Title and players: name the situation and who is involved.
2. Options: list each player's choices, using the game's own options from its playbook.
3. Payoffs or stakes: say what each outcome is worth to each player. For matrix games, fill in the payoff grid.
4. Information and timing: say who moves when, and who knows what.
5. Traits: copy the values in the template file. Change any that do not fit your situation.
6. Check: run `advise` on your file, and compare with the game's simulation with `sim` if one exists.

## Options to model
- Option idea 1: If you are the one who knows the true value, claim it honestly; the logic of undercutting assumes the other side will race to the bottom.
- Option idea 2: If the rules reward a small undercut, expect the other side to be tempted, and do not start a race you can see is pointless.
- Option idea 3: Where the claim can be checked, honesty is safest: a reputation for accurate claims pays over repeated dealings.

## Payoff grid
Rows (you): Claim 2, Claim 3, Claim 4. Columns (them): Claim 2, Claim 3, Claim 4.
Enter it with: solve "2,2 4,0 4,0; 0,4 3,3 5,1; 0,4 1,5 4,4" --rows Claim 2,Claim 3,Claim 4 --cols Claim 2,Claim 3,Claim 4

Simulation: `sim travelers-dilemma` shows the paths, and `sim travelers-dilemma --play` lets you choose.

## Start from this template
```
title: My Traveler's Dilemma situation
players: two
timing: simultaneous
interaction: one-shot
information: perfect
payoff: mixed
communication: no
domain: business, everyday
notes: Describe your situation here. Replace the example options with your own.
```

