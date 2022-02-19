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
import time
import scipy.optimize as opt

SHAPES = ("CIRCLE", "SQUARE") 
LOCATIONS = ("LEFT", "RIGHT")
CONDITIONS = ("CONGRUENT", "INCONGRUENT")

SIMON_MAPPINGS = {"CIRCLE" : "LEFT", "SQUARE" : "RIGHT"}
RESPONSE_MAPPINGS = {"LEFT" : "f", "RIGHT" : "j"}
random.seed(100)


class SimonStimulus:
    """An abstract Stroop task stimulus"""
    def __init__(self, shape, location):
        if shape in SHAPES:
            self.shape = shape
            self.location = location
            

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
    def kind(self):
        """Returns the trial type (congruent, incongruent)"""
        res = ""
        if self.congruent:
            res = "congruent"
        elif self.incongruent:
            res = "incongruent"
        return res
        
    def __str__(self):
        return "<[%s]'%s' at %s>" % (self.kind, self.shape, self.location)

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


def generate_stimuli(shuffle = True):
    "Generates stimuli according to the Stocco(2016) paradigm" 
    congr = [("CIRCLE", "LEFT"), ("SQUARE", "RIGHT")]
    incongr = [("CIRCLE", "RIGHT"), ("SQUARE", "LEFT")]

    lst = congr * 10 + incongr * 10

    if shuffle:  # Randomized if needed
        random.shuffle(lst)
    
    return [SimonStimulus(shape = x[0], location = x[1]) for x in lst]


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
        self.update_window()
        actr.schedule_event_relative(1, "stroop-next")

        
    def run_stats(self):
        """Returns some aggregate analysis of model behavior.
        Stats are calculated only when the model successfully completes the task. 
        When data are missing or the experiment is not completed, NA values 
        are returned
        """
        R = dict(zip(CONDITIONS, [(0, np.nan, np.nan)] * 2))
        
        if len(self.log) > 0:  
            
            cong = [x for x in self.log if x.stimulus.congruent]
            incn = [x for x in self.log if x.stimulus.incongruent]
            #neut = [x for x in self.log if x.stimulus.neutral]

            for cond, data in zip(CONDITIONS,
                                  [cong, incn]):
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

    def modify_stimulus_feature(self):
        """Cheap hack to remoe strings from visual objects AFTER the visual object
        has been created through the standard 'exp-window' methods. The algorithm 
        takes advantage of the fact that visual features are named in a predictable way,
        with one feature for every item added to the window. During each trial, N = 5
        items are added to the window (the main stimulus, three response buttons, and
        one fixation), thus making it possible to calculate the feature ID as such:
        
             ID = N * I + 1
             
        where N = 5 = number of features per trial, and I = trial index.
        """
        id = 5 * self.index + 1
        feature = "visicon-id%d" % (id,)
        shape = self.current_trial.stimulus.shape
        location = self.current_trial.stimulus.location
        #print("TEST:modify_stimulus_feature", shape, location, feature)
        #actr.modify_visicon_features([feature, "value", text.upper()])
        actr.modify_visicon_features([feature, "shape", shape.upper(), "location", location.upper()])
        #actr.print_visicon()
            
            
    def update_window(self):
        """Updates the experiment window"""
        if self.window is not None:
            # First, clean-up
            actr.clear_exp_window()
            
            shape = self.current_trial.stimulus.shape.upper()
            location = self.current_trial.stimulus.location.upper()
            kind = self.current_trial.stimulus.kind.upper()

            # Then, add new elements
            if self.phase == "fixation":
                item = actr.add_text_to_exp_window(self.window, "+", font_size=50,
                                                   x = 400, y = 300,
                                                   color = "black")
                #time.sleep(1)
            
            elif self.phase == "stimulus":
                actr.clear_buffer("VISUAL")
                if location == "LEFT":
                    x = 250
                else:
                    x = 550
                #item = actr.add_text_to_exp_window(self.window, shape,
                #                                   x=x, y=300)
                #print("TEST:update_window", shape, location)
                actr.clear_buffer("VISUAL")
                item = actr.add_visicon_features(['isa', ['simon-stimulus-location', 'simon-stimulus'], 'kind', 'simon-stimulus',
                           'screen-x', x, 'screen-y', 300, #'value', ('circle', "'circle 1'"),
                           'shape', shape, 'color', 'black', 'location', location])
                #actr.add_items_to_exp_window(self.window, item)
                #actr.print_visicon()

                for i, shape in enumerate(SIMON_MAPPINGS):
                    item = actr.add_text_to_exp_window(self.window,
                                                       RESPONSE_MAPPINGS[SIMON_MAPPINGS[shape]],
                                                       x = 600 + i * 50,
                                                       y = 500)
                #time.sleep(2)
                actr.schedule_event_relative(0.001, "stroop-modify-stimulus-feature", params=[])

            elif self.phase == "done":
                shape = self.current_trial.shape
                location = self.current_trial.location
                item = actr.add_text_to_exp_window(self.window, "done",
                                                   x=395, y= 300)
                #actr.delete_all_visicon_features()
                #print("TEST actr.print_visicon():")
                #actr.print_visicon()

                
    def accept_response(self, model, response):
        """A valid response is a key pressed during the 'stimulus' phase"""
        if self.phase == "stimulus":
            self.current_trial.response = response
            actr.schedule_event_now("stroop-next") 
            
    def next(self):
        """Moves on in th task progression"""
        if self.phase == "fixation":
            self.phase = "stimulus"
            self.current_trial.onset = actr.mp_time()
            
            # If we plan to record the trace, print a marker
            if self.trial_trace:
                stim = self.current_trial.stimulus
                shape = stim.shape.upper()
                location = stim.location.upper()
                kind = stim.kind.upper()
            
                print("NEW %s SIMON TRIAL: (SHAPE %s LOCATION %s)" % (kind, shape, location))

        elif self.phase == "stimulus":
            self.current_trial.offset = actr.mp_time()
            self.index += 1
            self.log.append(self.current_trial)
            if self.index >= len(self.stimuli):
                self.phase = "done"

            else:
                self.current_trial = SimonTrial(self.stimuli[self.index])
                self.phase = "fixation"
                actr.schedule_event_relative(1, "stroop-next")

        actr.schedule_event_now("stroop-update-window")


def run_experiment(model="simon-model0",
                   time=200,
                   verbose=True,
                   visible=True,
                   trace=True,
                   param_set=None, 
                   reload=True):
    """Runs an experiment"""
    
    # Everytime ACT-R is reloaded, all parameters are set to init
    if reload: load_model(model, param_set)
    # Set then model parameters
    #for name, val in params:
    #    actr.set_parameter_value(name, val)
    
    win = actr.open_exp_window("* SIMON TASK *", width = 800,
                               height = 600, visible=visible)

    actr.install_device(win)

    task = SimonTask(setup=False)
    #print("TEST SIMON TASK:", task.stimuli)
    #task.window = win

    actr.add_command("stroop-next", task.next,
                     "Updates the internal task")
    actr.add_command("stroop-update-window", task.update_window,
                     "Updates the window")
    actr.add_command("stroop-accept-response", task.accept_response,
                     "Accepts a response for the Stroop task")
    actr.add_command("stroop-modify-stimulus-feature", task.modify_stimulus_feature,
                    "Post-hoc removal of strings from stimuli features")
    actr.monitor_command("output-key",
                         "stroop-accept-response")

    task.setup(win)
    if not trace:
        actr.set_parameter_value(":V", False)
        task.trial_trace = False
    actr.run(time)
    if verbose:
        print("-" * 80)
        task.print_stats(task.run_stats())

    # Cleans up the interface
    # (Removes all the links between ACT-R and this object).

    actr.remove_command_monitor("output-key",
                                "stroop-accept-response")
    actr.remove_command("stroop-next")
    actr.remove_command("stroop-update-window")
    actr.remove_command("stroop-accept-response")
    actr.remove_command("stroop-modify-stimulus-feature")
    
    # Returns the task as a Python object for further analysis of data
    return task

def simulate_behavior(model, param_set=None, n=100, verbose=False):
    """Simulates N runs of the model"""
    accuracy_res = np.zeros((n, len(CONDITIONS)))
    rt_res = np.zeros((n, len(CONDITIONS)))
    for j in range(n):
        if verbose: print("Run #%03d" % j)
        task = run_experiment(model,
                              visible=False,
                              verbose=False,
                              trace=False,
                              param_set=param_set)
        stats = task.run_stats()
        accuracy_res[j] = np.array([stats[x][1] for x in CONDITIONS])
        rt_res[j] = np.array([stats[x][2] for x in CONDITIONS])

    return accuracy_res, rt_res#res.mean(0) # Column mean


#VERSTYNEN = [0.720, 0.755, 0.810] # Verstynen's original results
STOCCO = {"ACCURACY_MEAN":[0.98, 0.88], "ACCURACY_SD":[0.10, 0.03],
          "RT_MEAN":[0.421, 0.489], "RT_SD":[0.073, 0.088]}


def stats_qc(stats):
    """Quality check for data stats. A good set of aggregagated data should have the 
    following characteristics:
    
    1. A correct number of trials for each condition (N = 20, 20)
    2. All the data should be real numbers, and no NaN should be present
    """
    if len(stats) == 3:
        numtrials_check = True
        for condition, expected in list(zip(CONDITIONS, [20,20])):
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


def model_error(model, n=25, param_set=None, observed=STOCCO):
    """Loss function for the model (RMSE)"""
    predicted_accuracy, predicted_rt = simulate_behavior(model, param_set, n)
    sqerr_accuracy = (predicted_accuracy.mean(axis=0) - observed['ACCURACY_MEAN'])**2
    res_accuracy = np.round(np.sqrt(np.mean(sqerr_accuracy)), 4)
    sqerr_rt = (predicted_rt.mean(axis=0) - observed['RT_MEAN'])**2
    res_rt = np.round(np.sqrt(np.mean(sqerr_rt)), 4)
    if res_accuracy is np.nan:
        res_accuracy = 100000000
    if res_rt is np.nan:
        res_rt = 100000000
    print("MODEL (RMSE): (ACCURACY: %s \tRT: %s)" % (res_accuracy, res_rt))
    return res_accuracy, res_rt

def chery_model_error(model="simon", param_set={"ans":0.1, "mas":0.5}):
    return model_error(model, n=50, param_set=param_set)

# Example:

#res = opt.minimize(stroop.micah_model_error, [1.5], method='nelder-mead', options={'disp':True}) 


#################### LOAD MODEL CORE ####################
def load_model(model="simon-model0", param_set=None, verbose=True):
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
    has_model = actr.current_model().lower() == model
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