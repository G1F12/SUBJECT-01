# Raw Data Manifest — Bird et al. (2026) Dryad Dataset

**Source Title**: *Ultra-wideband radar to measure in vivo muscle forces*  
**Authors**: Christopher S. Bird, Antonio P. L. Bo, Wei Lu, Taylor J. M. Dick  
**Dryad DOI**: [`10.5061/dryad.sbcc2frmh`](https://doi.org/10.5061/dryad.sbcc2frmh)  
**Article DOI**: [`10.1126/scirobotics.aed5865`](https://doi.org/10.1126/scirobotics.aed5865) (*Science Robotics*)  
**ArXiv Preprint**: [`arXiv:2510.20866`](https://arxiv.org/abs/2510.20866)  
**Registered Source ID**: `SRC-0076` | **License**: CC0-1.0 (Public Domain Dedication)  
**Governing Standard**: Evidence Gate V2 Cryptographic Verification  

---

## Official File Manifest & Checksums (Queried from Dryad API v2)

All checksums and byte sizes below are retrieved directly from the official Dryad REST API (`https://datadryad.org/api/v2/versions/450951/files`).

| File Name | Dryad File ID | Exact Size (bytes) | Official SHA-256 Digest | Status in SUBJECT-01 |
| :--- | :---: | :---: | :--- | :---: |
| `CODE_Generate_LSTM_Training_Data.zip` | 4845344 | 1,770,680,319 | `9b28c56c1eead02a3997b0cc2951121c8ad8728f92b5a61d7d401f50eceec7e8` | `PENDING_OWNER_ASSISTED_ACQUISITION` |
| `CODE_LME_Estimate_Torque.m` | 4845345 | 3,306 | `f83dcf36c9226498908d7760655df98f494b1cecc7fd034a66b411e4c672a1d8` | `PENDING_OWNER_ASSISTED_ACQUISITION` |
| `CODE_Train_LSTM_Models.py` | 4845343 | 7,184 | `7252213bc4bed040ff00115bfc5d91cd98defc70f69a99d5aeb41fe22c1ebc5e` | `PENDING_OWNER_ASSISTED_ACQUISITION` |
| `DATA_Dynamic_Knee.mat` | 4845347 | 5,212,093 | `7cb256a8eadf621b9822266c473b620b8121e40fb62ed7615cdfbb32024da7f9` | `PENDING_OWNER_ASSISTED_ACQUISITION` |
| `DATA_Dynamic_Knee.xlsx` | 4845349 | 10,035,204 | `5101bc530624b9d4f604fc8f92143d0c7ee7aced5ea1af1079a83cf11fd82c15` | `PENDING_OWNER_ASSISTED_ACQUISITION` |
| `DATA_Fatiguing_Isometric_Knee.xlsx` | 4845340 | 681,704,952 | `08b104d779845b883701a565fb13f4a9137505d47253caa43491306dbde49c25` | `PENDING_OWNER_ASSISTED_ACQUISITION` |
| `DATA_Isometric_Ankle.xlsx` | 4845338 | 14,591 | `30fd49cd4cdfd6bc301c7a6697408adda0a61dfdff701de3f1cce508c9035cc3` | `PENDING_OWNER_ASSISTED_ACQUISITION` |
| `DATA_Isometric_Knee.xlsx` | 4845339 | 19,879 | `1c415188ba7008586d05e5c4f0a0794c2858fe63e8a4f176d4b653630a7ac37f` | `PENDING_OWNER_ASSISTED_ACQUISITION` |
| `LME_Data_Outputs.mat` | 4845346 | 40,628 | `f532559ce51352342503d776821b13cf78cee81e52d6ba8f2ac48860642199b7` | `PENDING_OWNER_ASSISTED_ACQUISITION` |
| `LME_Trained_Models.mat` | 4845348 | 28,145,117 | `6f729e8b00b862d58eef866ca383eebf069b7ecd9d392094cf0019ad2cba4476` | `PENDING_OWNER_ASSISTED_ACQUISITION` |
| `LSTM_Data_Outputs.zip` | 4845341 | 8,939,260 | `863307becd150259a2bdeb685eceee2be65e5c24d206cceebb4162d7e7e471f0` | `PENDING_OWNER_ASSISTED_ACQUISITION` |
| `LSTM_Trained_Models.zip` | 4845342 | 101,796,528 | `9cf8f31433e0938a3fa64cad86b3083560b39cdfc609a186c23f11e3930f845f` | `PENDING_OWNER_ASSISTED_ACQUISITION` |
| `README.md` | 4845352 | 14,751 | `5a8bf8050f72ebfc8123265ac2101b8eeaa76080c0e452515d5b8ff425f6bc5b` | `PENDING_OWNER_ASSISTED_ACQUISITION` |
| `arxiv_2510_20866.pdf` | N/A (arXiv) | 5,494,859 | `eb1377aecc1df8564e5ac3f99b4afa8b8dc673df1736080de0ab7f598e02176c` | `ACQUIRED_AND_VERIFIED` |

---

## Instructions for Owner-Assisted Download

Automated CLI scripts encounter HTTP 403 (Techaro Anubis BotStopper Proof-of-Work Challenge) on direct web streams and HTTP 401 on REST API downloads. To acquire the data without violating website security gates:

1. Open `https://datadryad.org/dataset/doi:10.5061/dryad.sbcc2frmh` in your web browser.
2. Download the target priority files:
   - **Priority 1**: `DATA_Isometric_Knee.xlsx` (19.88 KB)
   - **Priority 2**: `LME_Data_Outputs.mat` (40.63 KB)
   - **Priority 3**: `DATA_Dynamic_Knee.xlsx` (10.04 MB) *(Note: `DATA_Dynamic_Knee.mat` and `DATA_Dynamic_Knee.xlsx` contain the same observations; `.xlsx` is fully sufficient)*
   - **Priority 4**: `LSTM_Data_Outputs.zip` (8.94 MB)
3. Move downloaded files to: `D:\SUBJECT-01\research\muscle_force_biomechanics_2026_11_10\raw_data\`
4. Once placed, run `python tools/evaluate_bird_biomechanics.py` to cryptographically verify SHA-256 and execute independent validation.
