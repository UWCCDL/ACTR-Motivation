# ACTR-Simon
 This repo is a revised version of Stocco (2017)'s ACT-R Simon Model: [Github](https://github.com/UWCCDL/PSS_Simon)

<img src="https://ars.els-cdn.com/content/image/1-s2.0-S0010027717300598-gr6.jpg" width="400"/>

## The original model 
The model itself borrows from Marsha Lovett's (2005) NJAMOS model of
the Stroop task. It also explcitly models the competition between
direct and indirect pathways of the basal ganglia as two separate set
of rules, "process" and "dont-process" rules.

In turn, this idea is borrowed from my model of Frank's (2004)
_Probabilistic Stimulus Selection_ (PSS) Task. The same result
could possibily be achieved through other means, but this
solution is simple, intutitive, and permits to model competitive
dynamics of the BG without changing ACT-R.  For an in-depth analysis
of why this particular approach is preferrable, see Stocco (2018).

### Motivation Model1

In this model (simon-motivation-model1), motivation parameter refers to "the times of retrieval (at most)" before providing response. (Motivation parameter has to be an positive integer, default value is 1). For instance,

- motivation parameter = 1, it means that the model would never check the rule.

- motivation parameter = 2, it means the model only have ONE chance of checking the rule. As a problem is detected, the model would redo once. But no matter what rule being retrieved, it will respond with the available answer.

- motivation paramter = 10, it means that the model would go back AT MOST 9 times before giving a response. However, if the retrieved rule passes the check (check-pass) fires, there is no need to redo the retrieve, the model would proceed with the correct answer.



### Motivation Model2

In this model(simon-motivation-model2), motivation parameter is like a mental clock, refering to "how many seconds (at most) it would spend before providing response. Now, motivation parameter is in second unit, so it should be a float number. For instance, motivation paramter = 1.5, it means that when model's mental clock exceeds motivation clock (> 0.1s), it would not checking the rule anymore, but if the mental clock is within the motivation clock(< 0.1s), it would continue retrieving and checking the rule.


### How to run this model

1. Run standalone ACT-R and Python interpreter

2. Import the `simon-device.py` module first. This will load the experimental Simon task 

3. Run `>> run_experiment()`

4. If you want to change parameters, run `>> run_experiment(visible=False, trace=False, param_set={"ans":0.1, "le":0.1})` 

   - The motivation parameter follows `{"motivation":0.1}`
   
   - The production reward setup follows `{"production_reward_pairs":[('CHECK-PASS', 0.1), ('CHECK-DETECT-PROBLEM-UNLIMITED')}`

4. (Optional) If you want to switch model, run ` >> run_experiment(model="simon-motivation-model1")`

## References

Stocco, A., Murray, N. L., Yamasaki, B. L., Renno, T. J., Nguyen, J.,
& Prat, C. S. (2017). Individual differences in the Simon effect are
underpinned by differences in the  competitive dynamics in the basal
ganglia: An experimental verification and a computational
model. _Cognition_, _164_, 31-45.


Stocco, A. (2018). A Biologically Plausible Action Selection System
for Cognitive Architectures: Implications of Basal Ganglia Anatomy for
Learning and Decision‐Making Models. _Cognitive Science_.
