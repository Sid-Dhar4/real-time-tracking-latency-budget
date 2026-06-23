# TrackEval KITTI Results

Native TrackEval KITTI 2D box evaluation was run for class `car` on KITTI tracking sequences `0000` and `0001`.

## Key combined results

- HOTA: `49.412`
- MOTA: `52.312`
- IDF1: `68.385`

## Per-sequence highlights

- Sequence `0000`: HOTA `43.489`, MOTA `25.581`, IDF1 `51.084`
- Sequence `0001`: HOTA `50.009`, MOTA `54.842`, IDF1 `70.177`

## Notes

- Evaluation uses TrackEval native KITTI 2D box support.
- Class evaluated: `car`
- Tracker: `yolov8n_bytetrack`
- Input sequences: `0000`, `0001`
- These are standard TrackEval metrics, not a public KITTI leaderboard submission.

## Raw summary

HOTA DetA AssA DetRe DetPr AssRe AssPr LocA OWTA HOTA(0) LocA(0) HOTALocA(0) MOTA MOTP MODA CLR_Re CLR_Pr MTR PTR MLR CLR_TP CLR_FN CLR_FP IDSW MT PT ML Frag sMOTA IDF1 IDR IDP IDTP IDFN IDFP Dets GT_Dets IDs GT_IDs
49.412 45.955 54.611 51.002 65.551 58.376 76.697 75.473 52.441 70.702 67.717 47.878 52.312 70.984 54.001 65.903 84.703 36.842 45.263 17.895 1639 848 296 42 35 43 17 61 33.19 68.385 60.796 78.14 1512 975 423 1935 2487 135 95
