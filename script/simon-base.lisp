;;; ================================================================
;;; SIMON TASK MODEL
;;; ================================================================
;;; (c) 2016, Andrea Stocco, University of Washington
;;;           stocco@uw.edu
;;; (c) 2022, Modified by Cher Yang, University of Washington
;;;           chery@uw.edu
;;; ================================================================
;;; This is an ACT-R model of the Simon task. It is based on ideas
;;; heavily borrowed from Marsha Lovett's (2005) NJAMOS model of
;;; the Stroop task. It also explcitly models the competition
;;; between direct and indirect pathways of the basal ganglia as two
;;; separate set of rules, "process" and "dont-process" rules. In
;;; turn, this idea is borrowed from my model of Frank's (2004)
;;; Probabilistic Stimulus Selection Task. The same result
;;; could possibily be achieved through other means, but this
;;; solution is simple, intutitive, and permits to model competitive
;;; dynamics of the BG without changing ACT-R.
;;; ================================================================
;;;

;;;  -*- mode: LISP; Syntax: COMMON-LISP;  Base: 10 -*-
;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;
;;; 
;;; Author      :Andrea Stocco 
;;; Author      :Cher Yang
;;; 
;;; 
;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;
;;; 
;;; Filename    :simon-motivation-model1.lisp
;;; Version     :v3.1
;;; 
;;; Description :This declarative model simulates simon task based on Boksem (2006)'s 
;;;              paradigm. This model takes motivation parameter as mental clock: 
;;;              if the time used longer than model's motivation parameter (in sec unit), 
;;;              it would give up checking; the the time used withine the limit, the 
;;;              model would continue retrieving.
;;; 
;;; Bugs        : DONE 2/17 After 5 times run, the model will give nan responses
;;;                    2/18 Change check-detect-problem(): rather than retrieve
;;;                         once, but try to retrieve as many times until successfully
;;;                         retrieve the rule consistent with the shape on screen. 
;;;                         This gaurentee 100% correct answers for both conditions, 
;;;                         so should add a boundary to limit how many retrieval attampts.
;;;                    2/23 set goal buffer in simon_device.py rather than in simon-model3.lisp
;;;                         
;;;
;;; To do       : DONE 2/17: fix bugs because of retrival failure; add goal
;;;               DONE 2/18: DONE 1) Change whether the cue is consistent with stimulus, we
;;;                          might control for task difficulty.
;;;                          2) Add a control mechanism - whether keep retrieving:
;;;                          DONE - qualitative motivation: =1 no check; =2 check once; =3
;;;                                 check 2 times... 
;;;                          - quantative control: no check vs. go check unlimited time
;;;                          DONE 3) Add a reward delivery mechanism - when check-failed
;;;                                  deliver negative rewards, when check passed, positive.
;;;                          DONE 4) Use Boksem's paradigm, add cue
;;;                    2/23 1) Following Mareka's mind-windering model? When task-relevant goal
;;;                          is retrieved
;;;                         DONE 2) Goal buffer delivers reward
;;;                         DONE 3) GOAL buffer check-time, rather than how many times one retrieves
;;;                    2/25 1) Encode feedback - post-error-slow? After negative feedback, adjust 
;;;                         motivation parameter - longer duration for checking, or more times of 
;;;                         checking
;;;                    3/03 Add temporal buffer to inccorporate reward and time
;;; 
;;; ----- History -----
;;;
;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;
;;;
;;; General Docs:
;;; 
;;;
;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;
;;;
;;; Public API:
;;;
;;;
;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;
;;;
;;; Design Choices:
;;; 
;;; Task description 
;;; The model looks at the fixation cross on the screen and prepare wm. Once 
;;; the simon-stimulus occurs, it would encode the stimulus in WM.
;;; Four productions compete: process-shape(), process-location(), 
;;; dont-process-shape(), dont-process-location(). 
;;; The model retrieves simon rule from LTM
;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;
;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;
;;; 
;;; Productions: 
;;; 
;;; p find-screen ()
;;; p prepare-wm ()
;;; p process-shape()
;;; p dont-process-shape()
;;; p process-location ()
;;; p dont-process-location ()
;;; p check-pass()
;;; p check-detect-problem ()
;;; p respond()
;;;;
;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;

;;; --------- CHUNK TYPE ---------
(chunk-type (simon-stimulus (:include visual-object))
      kind 
      shape 
      color 
      location)

;;; Bokesem (2006)
(chunk-type (simon-cue (:include visual-object))
      kind 
      shape 
      color 
      cue)

(chunk-type (simon-screen (:include visual-object))
      kind 
      value)

(chunk-type (simon-stimulus-location (:include visual-location))
      shape 
      color 
      location
      cue)

(chunk-type simon-rule 
  kind 
  has-motor-response 
  shape 
  hand 
  dimension)

(chunk-type compatible-response 
  has-motor-response 
  hand 
  location)


(chunk-type wm       ;; Working Memory. Simple imaginal chunk with 3 slots
      state
      value1
      value2 
      value3         ;;; Bokesem (2006) CUE
      checked)

(chunk-type phase
      step
      motivation        ;;; mental counts
      time-onset        ;;; mental clock
      time-duration)    ;;; mental clock 


;;; --------- DM ---------
(add-dm (simon-rule isa chunk)
  (simon-stimulus isa chunk)
  (simon-screen isa chunk)
  (stimulus isa chunk)
  (circle isa chunk)
  (square isa chunk)
  (arrow isa chunk)
  (shape isa chunk)
  (yes isa chunk)
  (no isa chunk)
  (proceed isa chunk)
  (process isa chunk)
  (zero isa chunk)
  (done isa chunk)
  (pause isa chunk)
  (screen isa chunk)
  (attend-fixation isa chunk)
  (attend-cue isa chunk)
  (attend-stimulus isa chunk)
  (retrieve-rule isa chunk)

;;; --------- The Simon Task rules ---------
  (circle-left isa simon-rule
         kind simon-rule
         has-motor-response yes
         hand left
         shape circle
         dimension shape)

  (square-right isa simon-rule
          kind simon-rule
          has-motor-response yes
          hand right
          shape square
          dimension shape)

;;; --------- GOAL ---------

)



;;; ------------------------------------------------------------------
;;; INITIALIZATION
;;; ------------------------------------------------------------------

(p prepare-wm
   "If there are no contents in WM, prepare contents"
   ?imaginal>
     buffer empty
     state free

   ?manual>
     preparation free
     processor free
     execution free

   ?goal>
     ;buffer   empty
     state    free
   
   =goal>
     isa      phase
     step     attend-fixation
     motivation =MOT
     time-onset =TIME
==>
   ;+goal>
   ;  isa        phase
   ;  step       attend-fixation
   ;  motivation 10 ;;; 1 (low) 2(medium) 3(high) 4(very high)
   +imaginal>
     isa wm
     state process
     checked no

   !output! (in prepare-wm motivation value is =MOT time-onset is =TIME)
)

(p find-screen
   "Look at the screen (if you were not already looking at it)"
    =visual-location>
    ?visual>
     state      free
    ?goal>
     state      free
==>
    +visual>
      cmd      move-attention
      screen-pos =visual-location

   !eval! (trigger-reward 0) ; CLEAR REWARD TRACE
)

(p process-fixation
    ?visual>
      state    free
    =visual>
      text     T
      value    "+"
    ?imaginal>
      state    free
    =goal>
     isa        phase
     step       attend-fixation
     motivation   =VAL
==>
    *goal>
      step       attend-cue
    ;!output! (in process-fixation() the motivation value is =VAL)
)

;;; ----------------------------------------------------------------
;;; ATTEND CUE
;;; ----------------------------------------------------------------
;;; This production process cues and encode in WM
;;; ----------------------------------------------------------------
(p process-cue
   "Encodes the cue in WM"
   ?visual>
      state    free
   ?imaginal>
      state    free
   =visual>
     kind simon-cue
     cue =CUE
   =imaginal>
     state process
     checked no
     value3 nil
   =goal>
     isa        phase
     step       attend-cue
     motivation =VAL
==>
   *goal>
     step       attend-stimulus
   =imaginal>
     value3 =CUE
   ;!output! (in process-cue() the motivation value is =VAL)
)


;;; ----------------------------------------------------------------
;;; SELECTIVE ATTENTION
;;; ----------------------------------------------------------------
;;; These production compete for attention to shape and location of
;;; the stimulus
;;; ----------------------------------------------------------------

(p process-shape
   "Encodes the shape in WM"
   =visual>
     kind simon-stimulus
     shape =SHAPE
     
   =imaginal>
     state process
     value1 nil

   ?retrieval>
     state free
     buffer empty

   =goal>
     isa        phase
     step       attend-stimulus
==>
   =goal>
   =visual>
   =imaginal>
     value1 =SHAPE
)

(p dont-process-shape
   "Does not encode the shape (focuses on location as a side effect)"
   =visual>
     kind simon-stimulus
     location =POS
     
   =imaginal>
     state process
     value1 nil

   ?retrieval>
     state free
     buffer empty

   =goal>
     isa        phase
     step       attend-stimulus
==>
   =goal>
   =visual>
   =imaginal>
    value1 =POS
    ;value1 zero
   
)

(p process-location
   "Encodes the stimulus location in WM"
   =visual>
     kind simon-stimulus
     location =POS
     
   =imaginal>
     state process
     value2 nil

   ?retrieval>
     state free
     buffer empty

   =goal>
     isa        phase
     step       attend-stimulus
==>
   =goal>
   =visual>
   =imaginal>
     value2 =POS
)

(p dont-process-location
   "Does not encode the location (focuses on the shape as a side effect"
   =visual>
     kind simon-stimulus
     shape =SHAPE
     
   =imaginal>
     state process
     value2 nil

   ?retrieval>
     state free
     buffer empty

   =goal>
     isa        phase
     step       attend-stimulus
==>
   =goal>
   =visual>     
   =imaginal>
     value2 =SHAPE
)

;;; ----------------------------------------------------------------
;;; RESPONSE SELECTION
;;; ----------------------------------------------------------------
;;; The more responds by harvesting the most active Simon rule.
;;; Thus, response is guided by spreading activation from WM.
;;; A one-time check routine is also granted.
;;; ----------------------------------------------------------------

(p retrieve-intended-response
   "Retrieves the relevant part of the Simon Task rule"
   =visual>
     kind simon-stimulus
     shape =SHAPE
     
   =imaginal>
     state process
   - value1 nil
   - value2 nil
   
   ?retrieval>
     state free
     buffer empty

   =goal>
     isa        phase
     step       attend-stimulus
     motivation   =MOT
     time-onset   =TIME
==>
   =visual>   ; Keep visual
   =imaginal> ; Keep WM
   +retrieval>
     kind simon-rule
     has-motor-response yes
   !bind! =NEW-MOT (- =MOT 1)
   *goal>
     step       retrieve-rule
     motivation   =NEW-MOT
   !output! (in retrieve-intended-response() the motivation val is =MOT discount value is 1 new motivation val is =NEW-MOT)
)


;;; ------------------------------------------------------------------
;;; RESPONSE VERIFICATION AND PERFORMANCE MONITORING
;;; ------------------------------------------------------------------
;;; After selecting a response, the model has ONE-UNLIMITED chance to check
;;; and correct any eventual mistake. The motivation chunk determines how
;;; much effort this model decides to invest: redo retrieval once or redo
;;; until correct rule when check-detect-problem fires. 
;;; When check-pass fires, a positive reward will be given; while when
;;; check-detect-problem fires or retrieval failure, a negative reward 
;;; will be given. 

(p dont-check
   =visual>
     - shape nil

   =retrieval>
     kind  simon-rule
     - shape nil

   =imaginal>
     state process
     checked no

   ?imaginal>
     state free

   =goal>
     isa        phase
     step       retrieve-rule
     <= motivation   0  ;;; count number of attempts, if <=0 do not check
     motivation   =MOT
==>
   *goal>
     step       check-rule
   =visual>
   =retrieval>
   =imaginal>
     checked yes
   
   !output! (in dont-check() motivation is =MOT)
)
;;; Check
;;; Last time to catch yourself making a mistake

(p check-pass
   "Makes sure the response is compatible with the rules"
   =visual>
     shape =SHAPE
   
   =retrieval>
     kind  simon-rule
     shape =SHAPE

   =imaginal>
     state process
     checked no
   
   ?imaginal>
     state free

   =goal>
     isa        phase
     step       retrieve-rule
     motivation   =MOT
     > motivation   0 ;;; compete with dont-check, higher utility fires
==>
   *goal>
     step       check-rule
   =visual>
   =retrieval>
   =imaginal>
     ;value2 nil
     checked yes
   !output! (in check-pass() motivation is =MOT)
)

(p check-detect-problem-unlimited
   "If there is a problem, redo until retrieving the rule with correct shape"
   =visual>
     shape =SHAPE
   
   =retrieval>
     kind  simon-rule
   - shape =SHAPE

   =imaginal>
     state process
     checked no
   
   ?imaginal>
     state free

   =goal>
     isa        phase
     step       retrieve-rule
     motivation   =VAL
     > motivation   0 ; when motivation>0: go checking, motivation<=0, dont-check fires
==> 
   *goal>
     step       attend-stimulus
   =visual>
   -retrieval>
   =imaginal>
     value1 nil     ;;; Bokesem (2006)
     value2 nil
     ;checked yes

   ;;;!output! (in check-detect-problem-unlimited() the motivation is =VAL)
 )


(p retrieve-failure
    ?imaginal>
      state    free
    ?retrieval>
      buffer   failure

    =visual>
     kind simon-stimulus
     shape =SHAPE

    =imaginal>
     state process
     - value1 nil
     - value2 nil

     =goal>
      isa        phase
      step       retrieve-rule
==>
    =goal>
    =visual>
    =imaginal>

    +retrieval>
     kind simon-rule
     has-motor-response yes
)
 
(p respond
   "If we have a response and it has been checked, we respond"
   =visual>
     kind simon-stimulus
     shape =SHAPE 

   =imaginal>
     state process
     checked yes

   =retrieval>
     kind simon-rule
     has-motor-response yes
     hand =HAND
     
   ?manual>
     preparation free
     processor free
     execution free

   =goal>
     isa        phase
     step       check-rule
==>
   =goal>
   -imaginal>
   -retrieval>
   -goal>
   +manual>
     isa punch
     hand =HAND
     finger index
)

;;; --- DONE! -------------------------------------------------------------- ;;;

(p done
   "Detects when the experiment is done"
   =visual>
     text           t
     value          "done"
     color          black

   ?visual>
     state          free
	 
   ?manual>
     preparation    free
     processor      free
     execution      free

   ?goal>
     state          free
==>
   !stop!

)
