# Task: Set the future cost quotas

You are a financial analyst. Your task is to set the future cost quotas of one company
for a common-size forecast of its operating expenses.

## The common-size method

A cost quota is one expense item divided by the revenue of the same year:

```
Quota(t) = Expense(t) / Revenue(t)
```

The forecast turns this around. The revenue of the next years is already predicted.
Multiplying it by a quota gives the expense of that year:

```
Expense(+n) = Revenue(+n) x Quota(+n)
```

The formula is always the same. The only open number is the quota. This is what you set.
The quota is not a calculation, it is a judgement: two different quotas are both
arithmetically correct, and no formula tells which one is right.

## Your task

The context contains a table with the historical quota of every expense item, one row
per fiscal year. For **every** quota column in that table you set exactly **6** quotas,
one for each of the next six years (year +1 to year +6).

Report every quota as a decimal number, not as a percentage. A quota of 34 percent is
`0.34`.

## How to set a quota

Three ways are common. You may follow one of them or reason differently, as long as you
explain your choice:

- **Last quota, held constant.** The conservative choice and always available.
- **Average of the historical quotas.** Smooths out a single unusual year.
- **A continued trend.** The quota keeps falling or rising.

Look at the whole series, not only at the last value. A trend over several years says
more than a single year. But be careful with a falling quota: writing it further down
assumes that the company keeps gaining efficiency, and it lifts the profit margin of the
whole forecast. If you cannot explain why the quota should keep falling, hold the last
quota constant instead.

If the context contains further documents about the company, use them. Management often
explains there why a cost item moved, and what it expects for the coming years.

## Reasoning and confidence

For every expense item give a short reasoning of one or two sentences saying why you
chose these quotas.

Set the confidence per expense item:

- `high` - the series is stable or follows a clear trend.
- `medium` - the series moves, but the direction is still readable.
- `low` - the series swings strongly, or the history is too short to judge.
