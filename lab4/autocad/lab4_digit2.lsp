;;; ----------------------------------------------------------------------------
;;; lab4_digit2.lsp — ЛР4 АПКС, AutoCAD (2D-орієнтована САПР)
;;; Процак Максим Степанович, КІ-402 -> цифра «2».
;;;
;;; Послідовність (як у методичці):
;;;   1. Тексти ПІБ (TEXT, шрифт Arial Bold) -> TXTEXP (контури) -> REGION
;;;      (внутрішні контури букв віднімаються SUBTRACT, щоб отримати букви з отворами).
;;;   2. 2D-контур цифри PLINE -> REGION -> EXTRUDE на товщину T.
;;;   3. Прізвище: EXTRUDE назовні + UNION (опуклий).
;;;      Ім'я:     EXTRUDE всередину + SUBTRACT (увігнутий).
;;;      По батькові: EXTRUDE на глибину > T + SUBTRACT (наскрізний).
;;;   4. Вид SE Isometric, PNGOUT (скріншот) і STLOUT (STL).
;;; Результати: %USERPROFILE%\lab4_out\
;;; Запуск: SCRIPT -> lab4_run.scr (або вручну: (load "...lab4_digit2.lsp") (lab4-texts),
;;;         TXTEXP з вибором !lab4-ss, потім (lab4-build)).
;;; Потрібні Express Tools (команда TXTEXP), вони входять у повний AutoCAD.
;;; ----------------------------------------------------------------------------
(vl-load-com)

(setq lab4-W 90.0  lab4-H 130.0  lab4-S 24.0     ; ширина, висота цифри, ширина сегмента, мм
      lab4-T 8.0                                 ; товщина цифри
      lab4-RAISE 2.0  lab4-ENGRAVE 2.0)          ; опуклий / увігнутий текст

(setq lab4-out (strcat (getenv "USERPROFILE") "\\lab4_out\\"))

(defun lab4-text (str x y h)
  ;; однорядковий TEXT, вирівнювання по центру (72=1, 73=2)
  (entmake (list '(0 . "TEXT") '(100 . "AcDbEntity") '(8 . "0") '(100 . "AcDbText")
                 (list 10 x y 0.0) (cons 40 h) (cons 1 str) '(7 . "LAB4")
                 '(72 . 1) (list 11 x y 0.0) '(100 . "AcDbText") '(73 . 2)))
  (entlast))

(defun lab4-texts ( / )
  (setvar "CMDECHO" 0)
  (setvar "OSMODE" 0)
  (setvar "DELOBJ" 1)
  (vl-mkdir lab4-out)
  (command "_.UCS" "_W")
  (command "_.-VIEW" "_TOP")
  (if (not (tblsearch "STYLE" "LAB4"))
    (entmake '((0 . "STYLE") (100 . "AcDbSymbolTableRecord") (100 . "AcDbTextStyleTableRecord")
               (2 . "LAB4") (70 . 0) (40 . 0.0) (41 . 1.0) (50 . 0.0) (71 . 0) (42 . 2.5)
               (3 . "arialbd.ttf") (4 . ""))))
  (setq lab4-ss (ssadd))
  ;; «Процак» — верхня смуга, «Максим» — середня, «Степанович» — нижня
  (ssadd (lab4-text "\\U+041F\\U+0440\\U+043E\\U+0446\\U+0430\\U+043A"
                    (/ lab4-W 2) (- lab4-H (/ lab4-S 2)) 12.0) lab4-ss)
  (ssadd (lab4-text "\\U+041C\\U+0430\\U+043A\\U+0441\\U+0438\\U+043C"
                    (/ lab4-W 2) (/ lab4-H 2) 12.0) lab4-ss)
  (ssadd (lab4-text "\\U+0421\\U+0442\\U+0435\\U+043F\\U+0430\\U+043D\\U+043E\\U+0432\\U+0438\\U+0447"
                    (/ lab4-W 2) (/ lab4-S 2) 10.0) lab4-ss)
  (command "_.ZOOM" "_W" (list -5.0 -5.0) (list (+ lab4-W 5) (+ lab4-H 5)))
  (princ "\nТексти створено. Далі: TXTEXP, вибір !lab4-ss")
  (princ))

(defun lab4-bbox (e / mn mx)
  (vla-getboundingbox (vlax-ename->vla-object e) 'mn 'mx)
  (list (vlax-safearray->list mn) (vlax-safearray->list mx)))

(defun lab4-inside (a b)                       ; bbox a строго всередині bbox b
  (and (> (car (car a)) (car (car b))) (> (cadr (car a)) (cadr (car b)))
       (< (car (cadr a)) (car (cadr b))) (< (cadr (cadr a)) (cadr (cadr b)))))

(defun lab4-ss->list (ss / i l)
  (setq i 0)
  (if ss (repeat (sslength ss) (setq l (cons (ssname ss i) l) i (1+ i))))
  l)

(defun lab4-after (mark / e l)                 ; усі об'єкти, створені після mark
  (setq e (if mark (entnext mark) (entnext)))
  (while e (setq l (cons e l) e (entnext e)))
  l)

(defun lab4-extrude (lst h / mark)             ; EXTRUDE списку регіонів -> список тіл
  (setq mark (entlast))
  (command "_.EXTRUDE" (lab4-list->ss lst) "" h)
  (lab4-after mark))

(defun lab4-list->ss (l / ss)
  (setq ss (ssadd))
  (foreach e l (ssadd e ss))
  ss)

(defun lab4-build ( / plines regs boxes holes outer r b cy top mid bot base pts)
  (setvar "CMDECHO" 0)
  ;; 1. контури тексту -> регіони
  (setq plines (ssget "_X" '((0 . "LWPOLYLINE,POLYLINE,LINE,ARC,SPLINE"))))
  (command "_.REGION" plines "")
  (setq regs (lab4-ss->list (ssget "_X" '((0 . "REGION")))))
  (setq boxes (mapcar 'lab4-bbox regs))
  ;; внутрішні контури букв (о, а, р, е, в ...) віднімаються від зовнішніх
  (foreach r regs
    (setq b (lab4-bbox r) outer nil)
    (foreach r2 regs
      (if (and (not (eq r r2)) (lab4-inside b (lab4-bbox r2))) (setq outer r2)))
    (if outer (setq holes (cons (cons outer r) holes))))
  (foreach h holes (command "_.SUBTRACT" (car h) "" (cdr h) ""))
  (setq regs (lab4-ss->list (ssget "_X" '((0 . "REGION")))))
  ;; розподіл букв за смугами за координатою Y центру
  (foreach r regs
    (setq b (lab4-bbox r) cy (/ (+ (cadr (car b)) (cadr (cadr b))) 2))
    (cond ((> cy (- lab4-H lab4-S)) (setq top (cons r top)))
          ((> cy lab4-S) (setq mid (cons r mid)))
          (t (setq bot (cons r bot)))))
  ;; прізвище: на верхню грань і назовні
  (command "_.MOVE" (lab4-list->ss top) "" '(0 0 0) (list 0 0 lab4-T))
  (setq top (lab4-extrude top lab4-RAISE))
  ;; ім'я: з верхньої грані всередину
  (command "_.MOVE" (lab4-list->ss mid) "" '(0 0 0) (list 0 0 lab4-T))
  (setq mid (lab4-extrude mid (- lab4-ENGRAVE)))
  ;; по батькові: з-під низу на глибину, більшу за товщину
  (command "_.MOVE" (lab4-list->ss bot) "" '(0 0 0) '(0 0 -1))
  (setq bot (lab4-extrude bot (+ lab4-T 2)))
  ;; 2. контур цифри «2» -> REGION -> EXTRUDE
  (setq pts (list (list 0 0) (list lab4-W 0) (list lab4-W lab4-S) (list lab4-S lab4-S)
                  (list lab4-S (- (/ lab4-H 2) (/ lab4-S 2))) (list lab4-W (- (/ lab4-H 2) (/ lab4-S 2)))
                  (list lab4-W lab4-H) (list 0 lab4-H) (list 0 (- lab4-H lab4-S))
                  (list (- lab4-W lab4-S) (- lab4-H lab4-S)) (list (- lab4-W lab4-S) (+ (/ lab4-H 2) (/ lab4-S 2)))
                  (list 0 (+ (/ lab4-H 2) (/ lab4-S 2)))))
  (command "_.PLINE")
  (foreach p pts (command p))
  (command "_C")
  (command "_.REGION" (entlast) "")
  (command "_.EXTRUDE" (entlast) "" lab4-T)
  (setq base (entlast))
  ;; 3. булеві операції
  (command "_.UNION" base (lab4-list->ss top) "")
  (command "_.SUBTRACT" base "" (lab4-list->ss (append mid bot)) "")
  ;; 4. вид, скріншот, STL
  (command "_.-VIEW" "_SEISO")
  (command "_.VSCURRENT" "_C")
  (command "_.ZOOM" "_E")
  (setvar "FILEDIA" 0)
  (if (findfile (strcat lab4-out "autocad_iso.png")) (vl-file-delete (strcat lab4-out "autocad_iso.png")))
  (command "_.PNGOUT" (strcat lab4-out "autocad_iso.png") "")
  (if (findfile (strcat lab4-out "digit2_autocad.stl")) (vl-file-delete (strcat lab4-out "digit2_autocad.stl")))
  (command "_.STLOUT" (ssget "_X" '((0 . "3DSOLID"))) "" "_Y" (strcat lab4-out "digit2_autocad.stl"))
  (setvar "FILEDIA" 1)
  (princ (strcat "\nГотово. Результати в " lab4-out))
  (princ))

(princ "\nlab4_digit2.lsp завантажено.")
(princ)
