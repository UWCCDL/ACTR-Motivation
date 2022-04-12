# ACT-R Simon Task

This script is to play with the ACT-R Simon Model created by A.S.(2017)

The Simon Task demo is here: https://www.psytoolkit.org/experiment-library/experiment_simon.html 

<img src="https://ars.els-cdn.com/content/image/1-s2.0-S0010027717300598-gr6.jpg" width="400"/>

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


# Updated ACT-R Simon Model with Motivation Component

This updated model (simon-motivation-model) implements a simple motivation component in GOAL buffer and self-monitoring component 


<img src="https://docs.google.com/drawings/d/e/2PACX-1vS_YKK6E75H-XYmQMRBH1xLt7vjmDSMrB0Ykgw0AnppxTx2KwN5OiReoi77Hr5xkdfKc8kVmMDgrYuQ/pub?w=1359&h=1561" width="400"/>

## Motivation Parameter in count unit

In this model (**simon-motivation-model1**), motivation parameter refers to "the maximum times(counts) of retrieval" before giving a response. (Motivation parameter has to be an positive integer, default value is 1). For instance, 

- motivation parameter = 1, it means that the model would never check the rule. 
- motivation parameter = 2, it means the model only have *ONE* chance of checking the rule. As a problem is detected, the model would redo once. But no matter what rule being retrieved, it will respond with the available answer. 
- motivation paramter = 10, it means that the model would go back *AT MOST 9* times before giving a response. However, if the retrieved rule passes the check (check-pass) fires, there is no need to redo the retrieve, the model would proceed with the correct answer. 


## Motivation Parameter in time unit


In this model(**simon-motivation-model2**), motivation parameter is like a mental clock, refering to "the maximum time (in sec) it would spend before providing response. Now, motivation parameter is in second unit, so it should be a float number. For instance,

- motivation paramter = 1.5, it means that when model's mental clock exceeds motivation clock (> 1.5s), it would stop checking the rule anymore, but if the mental clock is within the motivation clock(< 1.5s), it would continue retrieving and checking the rule. 

## Motivation Parameter + Reward delivery


In this model(**simon-motivation-model3**), similar to model3, motivation parameter is like a mental clock, refering to "the maximum time (in sec) it would spend before providing response. However, the reward delivery mechanisms is different. In this model, how much reward is provided depends on how long the model attempts to retrieve. If motivation parameter is high enought, when production `check-pass` fires, it delivers a reward which is equal to the duration of time the model takes since fixation cross appearing on the screen. If motivation parameter is low, the model will not check the answer (dont-check production fires), no reward will be given. 

- motivation paramter = 1.5, it means that when model's mental clock exceeds motivation clock (> 1.5s), it would stop checking the rule anymore, but if the mental clock is within the motivation clock(< 1.5s), it would continue retrieving and checking the rule.

- If check-pass fires, it will deliver a reward (equal to the total duration time the model spends on retrieval).



## How to run this model

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

Boksem, M. A., Meijman, T. F., & Lorist, M. M. (2006). 
Mental fatigue, motivation and action monitoring. 
_Biological psychology, 72_(2), 123-132.
