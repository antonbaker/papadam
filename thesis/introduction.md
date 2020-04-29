# Introduction 

[This text](https://github.com/antonbaker/papadam)

## Section 1

blabla This is a sentence.  blabla This is half a
sentence.  blabla This is a quarter sentence.  blabla
This is a sentence.blabla This is a quarter sentence.
blabla This is a sentence.blabla This is a quarter
sentence.  blabla This is a sentence.blabla This is a
quarter sentence.  blabla This is a sentence.blabla This
is a quarter sentence.  blabla This is a sentence.blabla
This is a quarter sentence.  blabla This is a
sentence.blabla This is a quarter sentence.  blabla This
is a sentence.blabla This is a quarter sentence.  blabla
This is a sentence.blabla This is a quarter sentence.
blabla This is a sentence.blabla This is a quarter
sentence.  blabla This is a sentence.blabla This is a
quarter sentence.  blabla This is a sentence.blabla This
is a quarter sentence.  blabla This is a sentence.blabla
This is a quarter sentence.  blabla This is a
sentence.blabla This is a quarter sentence.  blabla This
is a sentence.

This is a numbered list:
1. Bla
1. Bla
1. Bla
1. Bla
1. Bla
1. Bla
1. Bla
1. Bla
1. Bla


```
def apply_rules_to_datalines(rules=None, datalines=None):
    """Returns filename-to-lines dictionary after applying rules to datalines."""
    if not rules:
        raise RulesError("No rules specified.")
    if not datalines:
        raise DataError("No data specified.")

    f2lines_dict = defaultdict(list)
    is_first_rule = True
    for rule in rules:
        pattern = rule.source_matchpattern
        matchfield = rule.source_matchfield
        if is_first_rule:
            f2lines_dict[rule.source] = datalines
            is_first_rule = False

        for line in f2lines_dict[rule.source][:]:
            if _line_matches_pattern(pattern, matchfield, line):
                f2lines_dict[rule.target].append(line)
                f2lines_dict[rule.source].remove(line)

        target_lines = f2lines_dict[rule.target]
        sortorder = rule.target_sortorder
        f2lines_dict[rule.target] = _dsusort_lines(target_lines, sortorder)

    return dict(f2lines_dict)
```
