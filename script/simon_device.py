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
import json
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

def generate_stimuli(shuffle=True, n_trials=10, valid_cue_percentage=0.5):
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

    def __init__(self, stimuli=generate_stimuli(), setup=False, param_set=None):
        """Initializes a Stroop task (if there are stimuli)
           motivation_value is the chunk set to goal buffer that counts for how many times
           the model attempts to retrieve until reaching correct rule
        """
        if len(stimuli) > 0:
            self.stimuli = stimuli
            if setup:
                self.setup()
                
        # set motivation parameters
        self.set_motivation_parameters(param_set)
            

    def setup(self, win=None):
        """Sets up and prepares for first trial"""
        self.window = win
        self.index = 0
        self.log = []
        self.phase = "fixation"
        self.trial_trace = True
        self.current_trial = SimonTrial(self.stimuli[self.index])
    '''
    @property
    def motivation(self):
        return self._motivation

    @motivation.setter
    def motivation(self, val):
        self._motivation = val
    '''    
        
    def set_motivation_parameters(self, param_set):
        """
        This function sets motivation related parameters into a dict form
        self.parameters = {"motivation": 1, default value = 1
                           "production_reward_pairs": [("CHECK-PASS", 0.1), ("CHECK-DETECT-PROBLEM-UNLIMITED", -0.1)]}
        """
        self.parameters = {}
        if param_set and ('motivation' in param_set.keys()):
            self.parameters['motivation'] = param_set['motivation']
        else:
            self.parameters['motivation'] = 1 # default value
        if param_set and ('production_reward_pairs' in param_set.keys()):
            self.parameters['production_reward_pairs'] = param_set['production_reward_pairs']
        else:
            self.parameters['production_reward_pairs'] = None
        #print("TEST in set_motivation_parameters()", self.parameters)
            
            
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
    
    def load_history_file(self, record_history): 
        """
        This function will extract
        """
        file_path = os.path.dirname(os.path.realpath('__file__')) + f'/actr_traces/{record_history}-trace.txt'
        try:
            data_list = []
            with open(file_path, 'r') as f:
                data_list = json.loads(json.load(f)['data'])
            return data_list
        except:
            print("FILE DOES NOT EXIST!")
    
    def extract_production_utilities(self, data_list):
        """
        This function extract production utility. 
        """
        production_traces = [trace for trace in data_list[1:] if 'conflict-resolution' in trace]
        df_list = []
        for trace in production_traces:
            dfu = pd.DataFrame(trace[-1], columns=['production', ':utility', ':u'])
            dfu['time'] = trace[0]
            dfu['selected_p'] = trace[2]
            dfu['matched_p'] = json.dumps(trace[3])
            df_list.append(dfu)
        df = pd.concat(df_list, axis=0)
        return df
    
    def extract_reward(self, data_list):
        """
        This function extract info about reward time and amount of reward being delivered
        """
        reward_traces = [(trace[0], trace[2]) for trace in data_list[1:] if 'reward' in trace]
        dfr = pd.DataFrame(reward_traces, columns=['time', 'reward'])
        return dfr
    
    def process_history_data(self, record_history='production-history'):
        assert record_history in (None, 'production-history', 'retrieval-history')
        """
        This function merge utility data to reward data 
        """
        data_list = self.load_history_file(record_history)
        dfu = self.extract_production_utilities(data_list)
        dfr = self.extract_reward(data_list)
        df = pd.merge(dfu, dfr, how='left', on='time')
        df['time']=df['time']/1000
        
        # filter only competitive production PROCESS-SHAPE
        res = df[df['selected_p'].isin(['PROCESS-LOCATION', 'PROCESS-SHAPE', 'DONT-PROCESS-LOCATION', 'DONT-PROCESS-SHAPE']) &
                 df['production'].isin(['PROCESS-LOCATION', 'PROCESS-SHAPE', 'DONT-PROCESS-LOCATION', 'DONT-PROCESS-SHAPE'])]
        return res

    def fixation(self):
        #print("in fixation", self.phase)
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
        #print("in cue", self.phase)
        actr.clear_exp_window()
        cue = self.current_trial.stimulus.cue
        item = actr.add_visicon_features(
            ['isa', ['simon-stimulus-location', 'simon-cue'], 'kind', 'simon-cue',
             'screen-x', 400, 'screen-y', 300,
             'shape', None, 'color', 'black', 'cue', cue])

    def stimulus(self):
        #print("TEST in stimulus()", self.phase)
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
        
    def deliver_rewards(self, verbose=False):
        """
        This function delivers reward to productions. The production name and rewards are set
        as parameter at the begining 
        self.parameters['production_reward_pairs'] = [('CHECK-PASS', 0.1), ('RESPOND', -0.1)]
        """
        #print("TEST in deliver_rewards()", self.phase)
        #if (self.phase == "fixation") and self.parameters['production_reward_pairs']:
        if self.parameters['production_reward_pairs']:
            for production_name, reward_value in self.parameters['production_reward_pairs']:
                if production_name in actr.all_productions():
                    actr.spp(production_name, ':reward', reward_value)
                    if verbose: print("DELIVER REWARD:", reward_value, ">>>", production_name)
                else:
                    if verbose: print("WRONG PRODUCTION NAME", production_name, reward_value)
        else:
            if verbose: print("No reward delivered: ", self.parameters['production_reward_pairs'])
                    
    def set_motivation(self):
        """
        This function set motivation value to goal buffer
        """
        # SET GOAL (motivation value)
        #print("TEST, in set_motivation()")
        if self.phase == "fixation" and self.parameters['motivation']:
                actr.set_buffer_chunk('goal', actr.define_chunks(['isa','phase', 'step','attend-fixation', 
                                                                  'time-onset', actr.mp_time(),  # mental clock
                                                                  'motivation', self.parameters['motivation']])[0]) 
                
                     
    def verify_reward(self, *params):
        #print('TEST: in verify_reward() there is a reward being given')
        #actr.pp()
        pass
     
    
    def add_actr_commands(self):
        """
        This function adds all necessary act-r commands before model running
        functions:
            self.set_motivation() - set motivation parameter to goal buffer
            self.fixation() - display fixation on the screen
            self.cue() - display simon-cue on the screen and modify model's visicon features
            self.stimulus() - dispaly simon-stimulus on the screen and modify model's visicon features
            self.accept_response() - record model's response in self.log
            self.verify_reward() - check whether the model receives reward
        """
        actr.add_command("stroop-set-motivation", self.set_motivation, "Set motivation parameter for the model")
        actr.add_command("stroop-update-fixation", self.fixation, "Update window: fixation")
        actr.add_command("stroop-update-cue", self.cue, "Update window: cue")
        
        actr.add_command("stroop-update-stimulus", self.stimulus, "Update window: stimulus")
        actr.add_command("stroop-accept-response", self.accept_response, "Accepts a response for the Stroop task")
        actr.add_command("stroop-deliver-rewards", self.deliver_rewards, "Delivers a reward")
        actr.monitor_command("output-key", "stroop-accept-response")
        actr.add_command("reward-check",self.verify_reward, "Check for a reward delivery each trial.") 
        actr.monitor_command("trigger-reward","reward-check")
    
    def remove_actr_commands(self):
        """
        This function removes all added act-r commands after model is done
        """
        actr.remove_command("stroop-set-motivation")
        actr.remove_command("stroop-update-fixation")
        actr.remove_command("stroop-update-cue")
        
        actr.remove_command_monitor("output-key", "stroop-accept-response")
        actr.remove_command("stroop-accept-response")
        actr.remove_command_monitor("trigger-reward","reward-check")
        actr.remove_command("reward-check")
        actr.remove_command("stroop-update-stimulus")
        actr.remove_command("stroop-deliver-rewards")
    

    def update_window(self, time=200):
        if self.phase == "done":
            self.done()
            actr.run(time)
        elif self.phase == "fixation":
            #  MOTIVATION PARAMETER
            actr.schedule_event_now("stroop-set-motivation") 
            actr.schedule_event_relative(0.01,"stroop-update-fixation") 
            #self.set_motivation()
            #self.fixation()
            actr.run(time)
            #actr.run_full_time(10)
            #actr.run_until_time(0.15)
           
            self.phase = "cue"
            self.update_window()
        elif self.phase == "cue":
            actr.schedule_event_relative(0.01,"stroop-update-cue") 
            #self.cue()
            actr.run(time)
            self.phase = "stimulus"
            self.update_window()
        elif self.phase == "stimulus":
            self.current_trial.onset = actr.mp_time()
            #print('self.current_trial.onset', self.current_trial.onset)
            
            # update window
            actr.schedule_event_relative(0.01,"stroop-update-stimulus") 
            #self.stimulus()

            actr.run(time)
            # DELIVER REWARD PARAMETER TO PRODUCTION
            #self.deliver_rewards()
            actr.schedule_event_now("stroop-deliver-rewards") 
            
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
        
        # remove actr commands
        #self.remove_actr_commands()

    def accept_response(self, model, response):
        """A valid response is a key pressed during the 'stimulus' phase"""
        if self.phase == "stimulus":
            self.current_trial.response = response
        #print("TEST accept_response()", self.current_trial.response, self.current_trial.stimulus)


###################################################
####                SIMULATION                   ##
###################################################
def run_experiment(model="simon-motivation-model3",
                   time=200,
                   verbose=True,
                   visible=True,
                   trace=True,
                   param_set=None,
                   reload=True, 
                   record_history=None): 
    """Runs an experiment"""

    # Everytime ACT-R is reloaded, all parameters are set to init
    if reload: load_model(model, param_set)
    if record_history: actr.record_history(record_history)

    win = actr.open_exp_window("* SIMON TASK *", width=800,
                               height=600, visible=visible)

    actr.install_device(win)
    task = SimonTask(setup=False, param_set=param_set)
    #print("TEST: in run_experiment()", task.parameters)
    task.setup(win)
    if not trace:
        actr.set_parameter_value(":v", False)
        task.trial_trace = False
    
    task.add_actr_commands()
    task.update_window(time)
    task.remove_actr_commands()
    
    if verbose:
        print("-" * 80)
        task.print_stats(task.run_stats())
    if record_history: 
        actr.save_history_data(record_history, file=os.path.dirname(os.path.realpath('__file__'))+f'/actr_traces/{record_history}-trace.txt')
        actr.stop_recording_history(record_history)

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

    return accuracy_res, rt_res


BOKSEM1 = pd.DataFrame({'condition':['incongruent', 'congruent'], 'accuracy':[1-0.153, 1-0.075], 'response_time':[0.483, 0.451]}) 
BOKSEM2 = pd.DataFrame({'condition':['invalid', 'valid'], 'accuracy':[1-0.157, 1-0.071], 'response_time':[0.488, 0.446]}) 


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

def model_error(model, n=2, param_set=None, observed=BOKSEM1):
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

def model_error_old(model, n=25, param_set=None, observed=BOKSEM1):
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
def load_model(model="simon-motivation-model3", param_set=None, verbose=True):
    """
    Load simon-core.lisp and simon-body.lisp and print current parameter sets
    Set parameters using param_set {"ans":0.1, "lf":0.5, "motivation":1, "production_reward_pairs":[("CHECK-PASS", 0.1), ("", 0.1)]}
    """
    curr_dir = os.path.dirname(os.path.realpath('__file__'))
    actr.load_act_r_model(os.path.join(curr_dir, "simon-core.lisp"))
    # load new pramsets
    if param_set: 
        actr_param_set = param_set.copy()
        if "motivation" in param_set.keys(): actr_param_set.pop("motivation")
        if "production_reward_pairs" in param_set.keys(): actr_param_set.pop("production_reward_pairs")
        set_parameters(**actr_param_set)
    actr.load_act_r_model(os.path.join(curr_dir, model+".lisp"))
    if verbose:
        print("######### LOADED MODEL " +model+ " #########")
        print(">> ACT-R: ", get_parameters(*get_parameters_name()), "<<") 
        try: param_set_motivation = param_set["motivation"]
        except: param_set_motivation = 1
        try: param_set_reward = param_set["production_reward_pairs"]
        except: param_set_reward = None
        print(">> motivation param: ", param_set_motivation, "<<")
        print(">> production_reward_pairs param: ", param_set_reward, "<<")
        
def check_load(model_name="simon-motivation-model3"):
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
    for key, value in kwargs.items():
        actr.set_parameter_value(':' + key, value)


