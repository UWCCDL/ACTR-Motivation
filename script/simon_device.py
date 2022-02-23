## ================================================================ ##
## SIMON.PY                                                        ##
## ================================================================ ##
## A simple ACT-R device for the SIMON task                        ##
## -----------------------------------------                        ##
## This is a device that showcases the unique capacities of the new ##
## JSON-RPC-based ACT-R interface. The device is written in Python, ##
## and interacts with ACT-R entirely through Python code.           ##
## The Simon task is modeled after Andrea Stocco's (2016)          ##
## paper on the Simon task.                           ##
## ================================================================ ##

import os
import actr
import random
import numpy as np
import pandas as pd
import time
import scipy.optimize as opt

SHAPES = ("CIRCLE", "SQUARE")
LOCATIONS = ("LEFT", "RIGHT")
CONDITIONS = ("CONGRUENT", "INCONGRUENT")

SIMON_MAPPINGS = {"CIRCLE": "LEFT", "SQUARE": "RIGHT"}
RESPONSE_MAPPINGS = {"LEFT": "f", "RIGHT": "j"}
CUE_CONDITIONS = ("CONGRUENT-VALID", "CONGRUENT-INVALID", "INCONGRUENT-VALID", "INCONGRUENT-INVALID")

random.seed(100)


class SimonStimulus:
    """An abstract Stroop task stimulus"""

    def __init__(self, shape, location, cue):
        assert (shape in SHAPES and location in LOCATIONS and cue in LOCATIONS)
        self.shape = shape
        self.location = location
        self.cue = cue

    @property
    def location(self):
        return self._location

    @location.setter
    def location(self, val):
        self._location = val

    @property
    def shape(self):
        return self._shape

    @shape.setter
    def shape(self, val):
        self._shape = val

    @property
    def cue(self):
        return self._cue

    @cue.setter
    def cue(self, val):
        self._cue = val

    @property
    def congruent(self):
        if SIMON_MAPPINGS[self.shape] == self.location:
            return True
        else:
            return False

    @property
    def incongruent(self):
        if SIMON_MAPPINGS[self.shape] != self.location:
            return True
        else:
            return False

    @property
    def valid(self):
        if SIMON_MAPPINGS[self.shape] == self.cue:
            return True
        else:
            return False

    @property
    def invalid(self):
        if SIMON_MAPPINGS[self.shape] != self.cue:
            return True
        else:
            return False

    @property
    def kind(self):
        """Returns the trial type (congruent, incongruent)"""
        res = ""
        if self.congruent:
            res = "congruent"
        elif self.incongruent:
            res = "incongruent"
        return res

    @property
    def cue_kind(self):
        """Returns the cue type (valid, invalid)"""
        res = ""
        if self.valid:
            res = "valid"
        elif self.invalid:
            res = "invalid"
        return res

    def __str__(self):
        return "<[%s]'%s' at %s; cue: '%s' is [%s]>" % (self.kind, self.shape, self.location, self.cue, self.cue_kind)

    def __repr__(self):
        return self.__str__()

class SimonTrial:
    """A class for recording a Stroop trial"""

    def __init__(self, stimulus):
        """Inits a stroop trial"""
        self.stimulus = stimulus
        self.setup()

    def setup(self):
        "Sets up properly"
        self.shape = self.stimulus.shape
        self.location = self.stimulus.location
        self.cue = self.stimulus.cue
        self.onset = 0.0
        self.offset = 0.0
        self.response = None

    @property
    def correct_response(self):
        return RESPONSE_MAPPINGS[SIMON_MAPPINGS[self.shape]]

    @property
    def accuracy(self):
        if self.response is not None and \
                self.response == self.correct_response:
            return 1.0
        else:
            return 0.0

    @property
    def response_time(self):
        return self.offset - self.onset

def generate_stimuli(shuffle=True, n_trials=20, valid_cue_percentage=0.5):
    "Generates stimuli according to the Boksem(2006)'s paradigm"
    congr_valid = [("CIRCLE", "LEFT", "LEFT"), ("SQUARE", "RIGHT", "RIGHT")]
    incongr_valid = [("CIRCLE", "RIGHT", "LEFT"), ("SQUARE", "LEFT", "RIGHT")]
    congr_invalid = [("CIRCLE", "LEFT", "RIGHT"), ("SQUARE", "RIGHT", "LEFT")]
    incongr_invalid = [("CIRCLE", "RIGHT", "RIGHT"), ("SQUARE", "LEFT", "LEFT")]

    valid = congr_valid * int(n_trials * (valid_cue_percentage)) + incongr_valid * int(
        n_trials * (valid_cue_percentage))
    invalid = congr_invalid * int(n_trials * (1 - valid_cue_percentage)) + incongr_invalid * int(
        n_trials * (1 - valid_cue_percentage))
    lst = valid + invalid

    if shuffle:  # Randomized if needed
        random.shuffle(lst)

    return [SimonStimulus(shape=x[0], location=x[1], cue=x[2]) for x in lst]


class SimonTask:
    """A simple version of the Stroop task"""

    def __init__(self, stimuli=generate_stimuli(), setup=False):
        """Initializes a Stroop task (if there are stimuli)"""
        if len(stimuli) > 0:
            self.stimuli = stimuli
            if setup:
                self.setup()

    def setup(self, win=None):
        """Sets up and prepares for first trial"""
        self.window = win
        self.index = 0
        self.log = []
        self.phase = "fixation"
        self.trial_trace = True
        self.current_trial = SimonTrial(self.stimuli[self.index])

    def run_stats(self):
        """Returns some aggregate analysis of model behavior.
        Stats are calculated only when the model successfully completes the task.
        When data are missing or the experiment is not completed, NA values
        are returned
        """
        R = dict(zip(CUE_CONDITIONS, [(0, np.nan, np.nan)] * len(CUE_CONDITIONS)))

        if len(self.log) > 0:

            cong_valid = [x for x in self.log if (x.stimulus.congruent & x.stimulus.valid)]
            incn_valid = [x for x in self.log if (x.stimulus.incongruent & x.stimulus.valid)]
            cong_invalid = [x for x in self.log if (x.stimulus.congruent & x.stimulus.invalid)]
            incn_invalid = [x for x in self.log if (x.stimulus.incongruent & x.stimulus.invalid)]

            #for cond, data in zip(CONDITIONS, [cong, incn]):
            for cond, data in zip(CUE_CONDITIONS, [cong_valid, cong_invalid, incn_valid, incn_invalid]):
                if len(data) > 0:
                    acc = sum([x.accuracy for x in data]) / len(data)
                    rt = sum([x.response_time for x in data]) / len(data)

                    R[cond] = (len(data), acc, rt)

        return R

    def print_stats(self, stats={}):
        """Pretty prints stats about the experiment"""
        for cond in stats.keys():
            n, acc, rt = stats[cond]
            print("%s (N=%d): Accuracy = %.2f, Response Times = %.2f ms" % \
                  (cond, n, acc, rt * 1000))

    def df_stats_model_outputs(self):
        accuracy = [x.accuracy for x in self.log]
        rt = [x.response_time for x in self.log]
        condition_stimulus = [x.stimulus.kind for x in self.log]
        condition_cue = [x.stimulus.cue_kind for x in self.log]
        df_curr = pd.DataFrame([condition_stimulus, condition_cue, accuracy, rt]).T
        df_curr.columns = ["condition_stimulus", "condition_cue", "accuracy", "response_time"]
        return df_curr

    def df_stats_post_error(self):
        """
        This function organizes model output data into post-correct and post-error category
        """
        if len(self.log) == len(self.stimuli):
            corrects = []
            errors = []
            for j in range(len(self.log)-1):
                if self.log[j].accuracy==0:
                    errors.append(self.log[j+1])
                else:
                    corrects.append(self.log[j+1])
            df_corrects = pd.DataFrame({'response_time':[x.response_time for x in corrects],
                                        'trial_type':["post_correct"]*len(corrects)})
            df_errors = pd.DataFrame({'response_time':[x.response_time for x in errors],
                                      'trial_type':["post_errors"]*len(errors)})
            df_curr = pd.concat([df_corrects, df_errors], axis=0)
        return df_curr





    def fixation(self):
        # print("in fixation", self.phase)
        actr.clear_exp_window()
        item = actr.add_text_to_exp_window(self.window, "+", font_size=50,
                                           x=400, y=300,
                                           color="black")
        stim = self.current_trial.stimulus
        shape = stim.shape.upper()
        location = stim.location.upper()
        kind = stim.kind.upper()
        cue = stim.cue.upper()
        cue_kind = stim.cue_kind.upper()
        if self.trial_trace:
            print("NEW %s SIMON TRIAL: (SHAPE %s LOCATION %s CUE %s [%s])" % (kind, shape, location, cue, cue_kind))

    def cue(self):
        # print("in cue", self.phase)
        actr.clear_exp_window()
        cue = self.current_trial.stimulus.cue
        item = actr.add_visicon_features(
            ['isa', ['simon-stimulus-location', 'simon-cue'], 'kind', 'simon-cue',
             'screen-x', 400, 'screen-y', 300,
             'shape', None, 'color', 'black', 'cue', cue])

    def stimulus(self):
        # print("in stimulus", self.phase)
        
        actr.clear_exp_window()
        shape = self.current_trial.stimulus.shape
        location = self.current_trial.stimulus.location
        item = actr.add_visicon_features(
            ['isa', ['simon-stimulus-location', 'simon-stimulus'], 'kind', 'simon-stimulus',
             'screen-x', 200, 'screen-y', 300,
             'shape', shape, 'color', 'black', 'location', location])
        for i, shape in enumerate(SIMON_MAPPINGS):
            item = actr.add_text_to_exp_window(self.window,
                                               RESPONSE_MAPPINGS[SIMON_MAPPINGS[shape]],
                                               x=600 + i * 50,
                                               y=500)

    def done(self):
        actr.clear_exp_window()
        item = actr.add_text_to_exp_window(self.window, "done", x=400, y=300)

    def update_window(self, time=200):
        if self.phase == "done":
            self.done()
            actr.run(time)
        elif self.phase == "fixation":
            self.fixation()
            actr.run(time)
            self.phase = "cue"
            self.update_window()
        elif self.phase == "cue":
            self.cue()
            actr.run(time)
            self.phase = "stimulus"
            self.update_window()
        elif self.phase == "stimulus":
            self.current_trial.onset = actr.mp_time()
            #print('self.current_trial.onset', self.current_trial.onset)
            actr.add_command("stroop-accept-response", self.accept_response, "Accepts a response for the Stroop task")
            actr.monitor_command("output-key", "stroop-accept-response")
            self.stimulus()

            actr.run(time)

            actr.remove_command_monitor("output-key", "stroop-accept-response")
            actr.remove_command("stroop-accept-response")
            self.current_trial.offset = actr.mp_time()
            #print('self.current_trial.offset', self.current_trial.offset)

            self.index += 1
            self.log.append(self.current_trial)
            if self.index >= len(self.stimuli):
                self.phase = "done"
            else:
                self.current_trial = SimonTrial(self.stimuli[self.index])
                self.phase = "fixation"
            self.update_window()

    def accept_response(self, model, response):
        """A valid response is a key pressed during the 'stimulus' phase"""
        if self.phase == "stimulus":
            self.current_trial.response = response
        #print("TEST accept_response", self.current_trial.response, self.current_trial.stimulus)


#################### ########## ####################
####                SIMULATION                  ###
#################### ########## ####################
def run_experiment(model="simon-model3",
                   time=200,
                   verbose=True,
                   visible=True,
                   trace=True,
                   param_set=None,
                   reload=True):
    """Runs an experiment"""

    # Everytime ACT-R is reloaded, all parameters are set to init
    if reload: load_model(model, param_set)

    win = actr.open_exp_window("* SIMON TASK *", width=800,
                               height=600, visible=visible)

    actr.install_device(win)
    task = SimonTask(setup=False)
    task.setup(win)
    if not trace:
        actr.set_parameter_value(":V", False)
        task.trial_trace = False
    task.update_window(time)
    if verbose:
        print("-" * 80)
        task.print_stats(task.run_stats())

    # Returns the task as a Python object for further analysis of data
    return task


def simulate_behavior(model, param_set=None, n=100, verbose=False):
    """Simulates N runs of the model"""
    accuracy_res = np.zeros((n, len(CUE_CONDITIONS)))
    rt_res = np.zeros((n, len(CUE_CONDITIONS)))
    for j in range(n):
        if verbose: print("Run #%03d" % j)
        task = run_experiment(model,
                              visible=False,
                              verbose=False,
                              trace=False,
                              param_set=param_set)
        stats = task.run_stats()
        accuracy_res[j] = np.array([stats[x][1] for x in CUE_CONDITIONS])
        rt_res[j] = np.array([stats[x][2] for x in CUE_CONDITIONS])

    return accuracy_res, rt_res  # res.mean(0) # Column mean


# VERSTYNEN = [0.720, 0.755, 0.810] # Verstynen's original results
# ERROR RATE
#BOKSEM = {'CONGRUENCY_EFFECT': 0.075, 'VALIDITY_EFFECT': 0.157,
#          'INCONGRUENT_CORRECT_RT':483, 'CONGRUENT_CORRECT_RT':451,
#          'INVALID_RT':446, 'VALID_RT':488}
BOKSEM_FAKE = {'accuracy':[1, 0.95, 0.9,0.7],'rt':[440, 460,470,490]}


def stats_qc(stats):
    """Quality check for data stats. A good set of aggregagated data should have the
    following characteristics:

    1. A correct number of trials for each condition (N = 20, 20)
    2. All the data should be real numbers, and no NaN should be present
    """
    if len(stats) == 3:
        numtrials_check = True
        for condition, expected in list(zip(CONDITIONS, [20, 20])):
            if stats[condition][0] is not expected:
                numtrials_check = False

        if numtrials_check:
            # If we have the correct number of trials, let's make sure we have
            # sensible accuracies and rt values
            allvalues = []
            for condition in CONDITIONS:
                allvalues += list(stats[condition])
            print(allvalues)
            if len([x for x in allvalues if x is not np.nan]) == 9:
                return True
            else:
                return False
        else:
            return False
    else:
        return False

def model_error(model, n=1, param_set=None, observed=BOKSEM_FAKE):
    """Loss function for the model (RMSE)"""
    predicted_accuracy, predicted_rt = simulate_behavior(model, param_set, n)
    sqerr_accuracy = (predicted_accuracy.mean(axis=0) - observed["accuracy"]) ** 2
    res_accuracy = np.round(np.sqrt(np.mean(sqerr_accuracy)), 4)
    sqerr_rt = (predicted_rt.mean(axis=0) - observed['rt']) ** 2
    res_rt = np.round(np.sqrt(np.mean(sqerr_rt)), 4)
    if res_accuracy is np.nan:
        res_accuracy = 100000000
    if res_rt is np.nan:
        res_rt = 100000000
    print("MODEL (RMSE): (ACCURACY: %s \tRT: %s)" % (res_accuracy, res_rt))
    return res_accuracy, res_rt

def model_error_old(model, n=25, param_set=None, observed=BOKSEM_FAKE):
    """Loss function for the model (RMSE)"""
    predicted_accuracy, predicted_rt = simulate_behavior(model, param_set, n)
    sqerr_accuracy = (predicted_accuracy.mean(axis=0) - observed['ACCURACY_MEAN']) ** 2
    res_accuracy = np.round(np.sqrt(np.mean(sqerr_accuracy)), 4)
    sqerr_rt = (predicted_rt.mean(axis=0) - observed['RT_MEAN']) ** 2
    res_rt = np.round(np.sqrt(np.mean(sqerr_rt)), 4)
    if res_accuracy is np.nan:
        res_accuracy = 100000000
    if res_rt is np.nan:
        res_rt = 100000000
    print("MODEL (RMSE): (ACCURACY: %s \tRT: %s)" % (res_accuracy, res_rt))
    return res_accuracy, res_rt

def chery_model_error(model="simon", param_set={"ans": 0.1, "mas": 0.5}):
    return model_error(model, n=50, param_set=param_set)

# Example:

# res = opt.minimize(stroop.micah_model_error, [1.5], method='nelder-mead', options={'disp':True})


#################### LOAD MODEL CORE ####################
def load_model(model="simon-model3", param_set=None, verbose=True):
    """
    Load simon-core.lisp and simon-body.lisp and print current parameter sets
    Set parameters using param_set {"ans":0.1, "lf":0.5}
    """
    curr_dir = os.path.dirname(os.path.realpath('__file__'))
    actr.load_act_r_model(os.path.join(curr_dir, "simon-core.lisp"))
    # load new pramsets
    if param_set: set_parameters(**param_set)
    actr.load_act_r_model(os.path.join(curr_dir, model+".lisp"))
    if verbose:
        print("######### LOADED MODEL " +model+ " #########")
        print(">>", get_parameters(*get_parameters_name()), "<<")

def check_load(model_name="competitive-simon-py"):
    has_model = actr.current_model().lower() == model_name
    has_productions = actr.all_productions() != None
    return has_model & has_productions

#################### PARAMETER SET ####################

def get_parameters_name():
    param_names = ['seed', 'ans', 'le', 'mas', 'egs', 'alpha', 'imaginal-activation', 'motor-feature-prep-time']
    return param_names

def get_parameter(param_name):
    """
    get parameter from current model
    :param keys: string, the parameter name (e.g. ans, bll, r1, r2)
    :return:
    """
    assert param_name in ('seed', 'ans', 'le', 'mas', 'egs', 'alpha', 'imaginal-activation', 'motor-feature-prep-time')
    if param_name=="r": return reward
    else: return actr.get_parameter_value(":"+param_name)

def get_parameters(*kwargs):
    param_set = {}
    for param_name in kwargs:
        param_set[param_name] = get_parameter(param_name)
    return param_set

def set_parameters(**kwargs):
    """
    set parameter to current model
    :param kwargs: dict pair, indicating the parameter name and value (e.g. ans=0.1, r1=1, r2=-1)
    :return:
    """
    global reward
    for key, value in kwargs.items():
        if key == "r": reward = value
        else: actr.set_parameter_value(':' + key, value)


