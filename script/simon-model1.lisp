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
;;; Author      :Andrea Stocco (Modified by Cher Yang)
;;; 
;;; 
;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;
;;; 
;;; Filename    :simon-model1.lisp
;;; Version     :v1.0
;;; 
;;; Description :This declarative model simulates Simon task.
;;; 
;;; Bugs        : DONE 2/17 After 5 times run, the model will give nan responses.
;;;                         
;;;
;;; To do       : DONE 2/17: fix bugs because of retrival failure; add a retrieval failure
;;;                    2/18: 1) 
;;;                          DONE 2) Add a reward delivery mechanism - when check-failed
;;;                             deliver negative rewards, when check passed, positive.
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

(chunk-type (simon-screen (:include visual-object))
      kind 
      value)

(chunk-type (simon-stimulus-location (:include visual-location))
      shape 
      color 
      location)

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


(chunk-type wm       ;; Working Memory. Simple imaginal chunk with 2 slots
      state
      value1
      value2
      checked)

 (chunk-type phase step)


;;; --------- DM ---------
(add-dm (simon-rule isa chunk)
  (simon-stimulus isa chunk)
  (simon-screen isa chunk)
  (stimulus isa chunk)
  (circle isa chunk)
  (square isa chunk)
  (shape isa chunk)
  (yes isa chunk)
  (no isa chunk)
  (proceed isa chunk)
  (process isa chunk)
  (zero isa chunk)
  (done isa chunk)
  (pause isa chunk)
  (screen isa chunk)
  (on-task isa chunk)

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

)



;;; ------------------------------------------------------------------
;;; INITIALIZATION
;;; ------------------------------------------------------------------
    
(p find-screen
   "Look at the screen (if you were not already looking at it)"
    =visual-location>
    ?visual>
     state     free
    ?goal>
     state    free
==>
    +visual>               
      cmd      move-attention
      screen-pos =visual-location

    +goal>
     isa        phase
     step       on-task

)


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
     state    free
==>
   +goal>
     isa        phase
     step       on-task

   +imaginal>
     isa wm
     state process
     checked no
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
     step       on-task
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
     step       on-task
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
     step       on-task
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
     step       on-task
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
     step       on-task
==>
   =goal>
   =visual>   ; Keep visual
   =imaginal> ; Keep WM
   
   +retrieval>
     kind simon-rule
     has-motor-response yes
)


;;; ------------------------------------------------------------------
;;; RESPONSE VERIFICATION AND PERFORMANCE MONITORING
;;; ------------------------------------------------------------------
;;; After selecting a response, the model has ONE chance to check and
;;; correct any eventual mistake. Importantly, it only retrieves once
;;; when check-detect-problem fires. 
;;; When check-pass fires, a positive reward will be given; while when
;;; check-detect-problem fires or retrieval failure, a negative reward 
;;; will be given. 

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
     step       on-task
==>
   =goal>
   =visual>
   =retrieval>
   =imaginal>
     ;value2 nil
     checked yes
 )

(p check-detect-problem
   "If there is a problem, retrieve one more time"
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
     step       on-task
==>
   =goal>
   =visual>
   -retrieval>
   =imaginal>
     value1 nil
     ;value2 nil
     checked yes
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
      step       on-task
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
     step       on-task
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

(spp retrieve-failure :reward -0.1)
(spp check-detect-problem :reward -0.1)
(spp check-pass :reward 0.1)
(spp respond :reward 0.1)