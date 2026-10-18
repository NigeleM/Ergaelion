# Intelligence Strategy Playbook

This playbook covers intelligence as a strategic and analytic discipline: how the intelligence cycle works, how analysts reason under uncertainty, how warning, deception and counterintelligence can be understood as games, and how different countries organise their intelligence services. It draws on general published doctrine and academic work.

It deliberately does **not** cover operational tradecraft: recruiting or handling people, surveillance of individuals, or intrusion into systems. Those activities can seriously harm people and are governed by law. The games in the `Intelligence and deception` family are about judgement, credibility and information sharing.

## 1. The intelligence cycle

Most published descriptions of intelligence work follow a loop:

1. **Direction (planning):** decision-makers set the questions that matter.
2. **Collection:** information is gathered from open sources, reporting, technical sources and partners.
3. **Processing:** raw material is translated, sorted and checked.
4. **Analysis:** analysts weigh the evidence, form judgements and state confidence.
5. **Dissemination:** judgements reach the people who need them, in a usable form.
6. **Feedback:** decision-makers say what helped, which feeds the next round of direction.

Failures usually happen at the edges: questions that were never set, judgements that were not tested, or conclusions that never reached a decision-maker in time.

**Game link:** the loop is a sequence of decisions, each made under uncertainty. Use `sim intel-warning-problem` to see how timing and threshold choices change outcomes.

## 2. Analytic standards and methods

Published analytic standards from several services converge on a few principles:

- **Separate evidence from judgement.** Say what is known, what is assumed, and what is inferred.
- **State confidence and alternatives.** A judgement is more useful when it says how sure the analyst is and what else could explain the evidence.
- **Test hypotheses against all the evidence.** Structured methods such as Analysis of Competing Hypotheses (Heuer, 1999) ask which explanation is least inconsistent with the evidence, rather than which one is easiest to confirm.
- **Check assumptions.** A key-assumptions check lists what must be true for a judgement to hold, and what would change it.
- **Red teaming.** Assigning someone to argue the opposing case exposes weak reasoning before it reaches decision-makers.
- **Indicators.** Watch for evidence that would appear if a hypothesis were true, and for evidence that would appear if it were false.

**Game link:** `sim analysis-bayesian-updating` and `sim intel-analysis-methods` practise these habits. The most common error is confirmation bias: collecting only the evidence that fits the first explanation.

## 3. Warning and surprise

Warning is a judgement about whether a threat is developing, made early enough to act. It faces a basic trade-off:

- Warn too often and the warnings are discounted, which the literature calls the "cry wolf" problem.
- Warn too rarely and the surprise is costly.

Good practice separates the **warning threshold** (when to say something) from the **response threshold** (when decision-makers should act), and states which indicators would change the assessment.

**Game link:** `game intel-warning-problem` and `sim intel-warning-problem` model this trade-off. Track your miss and false-alarm rates so the threshold can be tuned.

## 4. Deception and credibility

Cheap talk costs nothing to send, so it carries little information on its own. Messages become informative when they are costly to fake or can be checked independently. The practical rules are:

- Give more weight to claims that are costly to make or that can be verified.
- Ask what the other side would gain from deceiving you.
- Corroborate with sources that are genuinely independent. Sources that share an origin are one piece of evidence, not several.
- Test assurances with small, verifiable steps before relying on them.

**Game link:** `game deception-cheap-talk` and `sim deception-cheap-talk` make this concrete.

## 5. Counterintelligence as a repeated contest

Counterintelligence can be modelled as a repeated game of detection and concealment, closely related to the inspection game. Predictable checks are easy to avoid; randomised, proportionate checks raise the cost of deception. The defender must also protect against false accusations, which damage innocent people and the organisation's trust.

**Game link:** `game double-agent-counterintelligence` and `sim double-agent-counterintelligence` show why blanket suspicion fails and why proportionate review works.

## 6. Disclosure, silence and sharing

Information games show two recurring patterns:

- **Unravelling:** if silence is read as bad news, parties with good news disclose it, and the remaining silence reveals the worst case (see Milgrom, 1981).
- **Free-riding on shared information:** partners gain from pooling information, but each is tempted to take more than it gives. Reciprocity rules, handling rules and visible contribution keep exchange going.

**Game link:** `game disclosure-game`, `game information-sharing-alliance` and their simulations.

## 7. How countries organise intelligence

Public sources describe a common pattern: intelligence is split by function (foreign, domestic or security, signals, and military) and coordinated by a central body or council. The details differ by country, and many arrangements are only partly public. These examples are drawn from widely published descriptions:

| Country | Public structure (general) |
| --- | --- |
| United States | An intelligence community of many agencies, coordinated by the Office of the Director of National Intelligence. Includes foreign human, signals, geospatial and military components. |
| United Kingdom | Foreign intelligence (SIS, usually called MI6), domestic security (MI5) and signals intelligence (GCHQ), with national assessments coordinated through the Joint Intelligence Committee. |
| Israel | Foreign intelligence (Mossad), domestic security (Shin Bet), and military intelligence within the defence forces. |
| Russia | Several services with overlapping roles, including the Federal Security Service (FSB), the Foreign Intelligence Service (SVR) and the military intelligence directorate (GRU). |
| China | The Ministry of State Security handles most civilian intelligence and counterintelligence, alongside military intelligence within the armed forces. |

**Comparative lesson:** centralised coordination reduces duplication and improves national assessments, but can slow responses and concentrate risk. Federated systems are more resilient and can be more responsive, but make coordination harder. Each design is a trade-off that can be studied as a coordination game: whether agencies share, and how much each trusts the others.

## 8. Strategic games for intelligence work

| Question | Game to use | Simulation |
| --- | --- | --- |
| When should a warning be issued? | The Warning Problem | `sim intel-warning-problem` |
| How far should new evidence move a belief? | Updating on Evidence | `sim analysis-bayesian-updating` |
| Is an assurance credible? | Deception and Cheap Talk | `sim deception-cheap-talk` |
| How should sensitive access be checked? | Counterintelligence | `sim double-agent-counterintelligence` |
| Should evidence be disclosed? | Disclose or Conceal | `sim disclosure-game` |
| Will partners share? | Sharing Among Partners | `sim information-sharing-alliance` |

Run `playbook problems intelligence` for the games that suit each problem, and `playbook areas intelligence` for the reading list.

## 9. Further reading

- Heuer, R. J., *Psychology of Intelligence Analysis* (CIA, 1999).
- Jervis, R., *Perception and Misperception in International Politics* (1976).
- Milgrom, P., "Good News and Bad News: Representation Theorems and Applications" (1981).
- Schelling, T., *The Strategy of Conflict* (1960).
