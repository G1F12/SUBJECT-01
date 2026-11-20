Subject: Clarification of duplicate participant files in STS dataset version 2

Dear authors,

We are auditing the provenance of the dataset associated with “Machine Learning Approach for Fatigue Estimation in Sit-to-Stand Exercise” (doi:10.3390/s21155006). Figshare version 2 (doi:10.6084/m9.figshare.15001362.v2) currently provides STS_data.zip with publisher MD5 2f8a8fcb1b8e4fd1361ce938ead90d33; the current version 3 is metadata-only.

In the version 2 archive, we found two pairs of text files that are byte-for-byte identical: Men/P14/S_P14.txt and Men/P6/S_P6.txt (SHA-256 ca3084734a2a49b7253fce38ec5f94ef790070b5e61859ba0e9b6fd4313583ed), and Men/P29/S_P29.txt and Men/P30/S_P30.txt (SHA-256 c2d3468be7ea7b442feffeb959aea7d182e1d14249a04f9f7cd1c8640d10c6ee). The processed CSV has 660 rows and 34 columns, but we do not know its mapping to source recordings.

Could you clarify whether these pairs are intended aliases, duplicated exports, or another issue; whether corrected recordings exist; and how the 660 processed rows map to participant recordings, conditions and Borg measurements? If possible, please share a dictionary, processing code/version, timestamps and instructions for independent participant-level splits and permitted reuse. No identifying information is requested.

Thank you for your help.

Draft only — not sent.
