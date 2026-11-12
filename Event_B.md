# P29 Event B — Hidden dependencies in a neighbouring module

**Group:** 30 / P29  
**Operator:** Tadhg Austin
**Report prepared:** 9 November 2026  

## 1. What we were trying to find out

Event B gave us a new evolution pressure: the next pull request contains a change whose correctness depends on a neighbouring module that is not present in the minimal diff. We were asked to determine whether our preprocessing and context policy hides or preserves that dependency, and to revise our design only if the evidence justified it.

Our pre-Event-B state is the Week 9 design decision recorded in the shared tracker and frozen at the `PRE_EVENT_B` tag. In Event A we found that reference preparation was coupled to preprocessing and scoring: flattening code before removing `//` comments could delete the rest of a method. We chose to keep the original results and add a separate complete-reference check, in which raw and cleaned predictions are compared against the same reference, verified against the saved Java files. We did not replace the original scorer.

Our pipeline follows the authors' T5/S2 setting. P1 method extraction gives the model only the method containing the review comment, together with the comment, and scores the prediction against that same method after revision. Event B therefore tests whether working at method level is still adequate when a correct revision relies on code outside that method.

## 2. Our prediction

We predict the new pressure will mainly affect model-input preparation rather than our Week 9 complete-reference check. Our pipeline gives the model only the method containing the review comment, so code the change depends on elsewhere, in the same file or in a neighbouring class or file, is left out. Raw and cleaned both use the same method extraction, so we expect the dependency to be hidden in both conditions. Our Week 9 check controls how answers are scored, so we expect it to keep raw and cleaned scoring consistent. However, it also works at method level, so it cannot show whether the neighbouring change was needed. We therefore expect the Week 9 decision to be only partly supported: correct for scoring, but not covering hidden dependencies. This prediction would be challenged if the dependency turned out to be visible in the extracted method, or if the complete-reference check gave different results for raw and cleaned on this case.

