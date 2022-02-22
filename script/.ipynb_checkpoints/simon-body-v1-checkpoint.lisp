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
;;; Filename    :simon-model.lisp
;;; Version     :v2.0
;;; 
;;; Description :This declarative model simulates gambling task in HCP dataset.
;;; 
;;; Bugs        : 02/17 if not reset, model will give nan responses after 
;;;               running 5 times 
;;;
;;;
;;; To do       : 
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

(chunk-type goal state)

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
        
;;; --------- GOAL --------- 
  (goal isa goal state on-task)
)

;;; ------------------------------------------------------------------
;;; INITIALIZATION
;;; ------------------------------------------------------------------

(p find-screen
   "Look at the screen (if you were not already looking at it)"
    ?visual-location>
       state    free
    ?visual>
      state     free
    ?goal>
      state          free
      buffer         empty
   =visual-location>
==>
   +visual-location>
      kind simon-stimulus 
   +visual>               
      cmd      move-attention
      screen-pos =visual-location
      !eval! (pprint-chunks-fct (list =visual-location)))

    +goal>
      isa      goal
      state    on-task
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
   
   =goal>
      isa      goal
      state    on-task
==>
   +imaginal>
     isa wm
     state process
     checked no
   
   =goal>
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
     isa visual-object
     kind simon-stimulus
     shape =SHAPE
     
   =imaginal>
     state process
     value1 nil

   ?retrieval>
     state free
     buffer empty
   
   =goal>
      isa      goal
      state    on-task

==>
   =visual>
   =imaginal>
     value1 =SHAPE
   =goal>
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
      isa      goal
      state    on-task
==>
   =visual>
   =imaginal>
    value1 =POS
    ;value1 zero
   =goal>
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
      isa      goal
      state    on-task

==>
   =visual>
   =imaginal>
     value2 =POS
   =goal>
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
      isa      goal
      state    on-task

==>
   =visual>     
   =imaginal>
     value2 =SHAPE
   =goal>
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
      isa      goal
      state    on-task
==>
   =visual>   ; Keep visual
   =imaginal> ; Keep WM
   
   +retrieval>
     kind simon-rule
     has-motor-response yes
   
   =goal>
)


;;; ------------------------------------------------------------------
;;; RESPONSE VERIFICATION AND PERFORMANCE MONITORING
;;; ------------------------------------------------------------------
;;; After selecting a response, the model has one chance to check and
;;; correct any eventual mistake. The "one ch

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
      isa      goal
      state    on-task
==>
   =visual>
   =retrieval>
   =imaginal>
     ;value2 nil
     checked yes
   =goal>
 )

(p check-detect-problem
   "If there is a problem, redo the retrieval once"
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
      isa      goal
      state    on-task
 ==>
   =visual>
   -retrieval>
   =imaginal>
     value1 nil
     ;value2 nil
     checked yes
   =goal>
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
      isa      goal
      state    on-task
==>
  
  +manual>
     isa punch
     hand =HAND
     finger index
   -imaginal>
   -retrieval>
   -goal>
   -manual>
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
==>
   !stop!
)