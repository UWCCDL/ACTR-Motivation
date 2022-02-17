# ACTR-Simon
 This repo is a revised version of Stocco (2017)'s ACT-R Simon Model



## The model 
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


### How to run this model

1. Run standalone ACT-R and Python interpreter

2. Import the `script/simon-device.py` file first. This will load the
   experimental Simon task 

3. Run `>> run_experiment()`

4. If you want to change parameters, run `>> run_experiment(visible=False, trace=False, param_set={"ans":0.1, "le":0.1})`

4. (Optional) If you want to compare model data to emperical data, run ` >> model_error(model="simon", n=1)`

## References

Stocco, A., Murray, N. L., Yamasaki, B. L., Renno, T. J., Nguyen, J.,
& Prat, C. S. (2017). Individual differences in the Simon effect are
underpinned by differences in the  competitive dynamics in the basal
ganglia: An experimental verification and a computational
model. _Cognition_, _164_, 31-45.


Stocco, A. (2018). A Biologically Plausible Action Selection System
for Cognitive Architectures: Implications of Basal Ganglia Anatomy for
Learning and Decision‐Making Models. _Cognitive Science_.
