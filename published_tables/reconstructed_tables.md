# Published aggregate tables

Reconstructed from exported final-paper aggregates. This is not an experiment rerun.

## Table 1: Dataset characteristics. HDFS and BGL differ in scale, vocabulary, prevalence, repetition, and session structure.

| Column 1 | Column 2 | Column 3 |
| --- | --- | --- |
| Characteristic | HDFS | BGL |
| Unit | block session | 100-line window |
| Sessions/windows | 575,061 | 47,479 |
| Anomalies | 16,838 (2.93%) | 4,802 (10.11%) |
| Event vocabulary | 29 | 2,746 |
| Mean length | 19.4 | 100 |
| Distinct count vectors | 589 | 6,280 |
| Repeated-vector share | 99.96% | 88.86% |

## Table 2: Information available before final test scoring, and the resulting access regime.

| Column 1 | Column 2 | Column 3 | Column 4 |
| --- | --- | --- | --- |
| Condition | Labels visible | Template catalog | Access regime |
| Within random/group | own training | full catalog | transductive* |
| BGL chronological | past training | cutoff snapshot | inductive |
| Cross: source corpus, source IDF | source training | source only | inductive |
| Cross: union corpus or target IDF | source training | source + target | transductive |

* Scored labels are hidden; transductive access uses unlabeled scored-data artifacts (Section IV).

## Table 3: Fixed hyperparameters used across protocols and seeds.

| Column 1 | Column 2 |
| --- | --- |
| Model | Configuration |
| LR | inverse regularization; balanced weights; 1,000 iterations; standardized input |
| RF | 200 trees; balanced-subsample class weights |
| XGBoost | 300 trees; depth 6; rate 0.1; histogram method; class-ratio positive weight |
| Word2vec | skip-gram; 100 dimensions; window 5; minimum count 1; 30 epochs |
| LSTM | 32-d embedding; 64 hidden; Adam 10^-3; batch 256; at most five epochs |

## Table 4: HDFS results across five seeds (mean ± SD); random/group access is transductive.

| Column 1 | Column 2 | Column 3 | Column 4 | Column 5 |
| --- | --- | --- | --- | --- |
|  | Random split |  | Group-disjoint |  |
| Configuration | AP | F_1 | AP | F_1 |
| Count/LR | .991±.004 | .989±.006 | .867±.103 | .934±.046 |
| Count/RF | 1.000±.000 | .998±.000 | .743±.227 | .808±.259 |
| Count/XGB | .999±.001 | .998±.000 | .692±.175 | .582±.337 |
| Sequence/LSTM | .999±.001 | .993±.002 | .627±.210 | .502±.324 |
| Semantic/LR | .982±.003 | .981±.003 | .725±.174 | .792±.275 |
| Semantic/XGB | 1.000±.000 | .998±.000 | .624±.235 | .318±.241 |

## Table 5: BGL results across five seeds (mean ± SD); random access is transductive, chronological access is inductive.

| Column 1 | Column 2 | Column 3 | Column 4 | Column 5 |
| --- | --- | --- | --- | --- |
|  | Random split |  | Chronological |  |
| Configuration | AP | F_1 | AP | F_1 |
| Count/LR | .987±.003 | .976±.004 | .277±.000 | .423±.000 |
| Count/RF | .998±.001 | .984±.002 | .388±.005 | .400±.012 |
| Count/XGB | .998±.001 | .989±.004 | .448±.000 | .396±.000 |
| Sequence/LSTM | .946±.012 | .916±.017 | .236±.151 | .282±.091 |
| Semantic/LR | .916±.006 | .870±.007 | .205±.095 | .267±.043 |
| Semantic/XGB | .992±.000 | .955±.006 | .676±.086 | .492±.165 |

## Table 6: BGL chronological sensitivity over five seeds. Parser runs use the 70/30 split; rolling tests cover the next 10% after each cutoff.

| Column 1 | Column 2 | Column 3 | Column 4 | Column 5 | Column 6 |
| --- | --- | --- | --- | --- | --- |
|  | Test anomaly |  | Count/XGB | LSTM | Semantic/XGB |
| Panel | Setting | rate | AP | AP | AP |
| Parser | Compact s = .3 | 10.1% | .460±.000 | -- | .741±.054 |
| Parser | Compact s = .4 | 10.1% | .448±.000 | -- | .676±.086 |
| Parser | Compact s = .5 | 10.1% | .448±.000 | -- | .631±.109 |
| Parser | Drain3 s = .4 | 10.1% | .432±.000 | -- | .617±.177 |
| Rolling | 50→60% | 1.3% | .902±.000 | .475±.147 | .838±.047 |
| Rolling | 60→70% | 10.8% | .376±.000 | .201±.048 | .663±.077 |
| Rolling | 70→80% | 13.2% | .588±.000 | .373±.248 | .760±.103 |
| Rolling | 80→90% | 5.9% | .332±.000 | .273±.130 | .776±.079 |

## Table 7: Component-level cost over five seeds. Throughput covers classifier-only inference; size covers the serialized classifier.

| Column 1 | Column 2 | Column 3 | Column 4 | Column 5 |
| --- | --- | --- | --- | --- |
| System | Configuration | Fit (s) | Infer. (k/s) | Size (MB) |
| HDFS | Count/LR | 2.6±1.1 | 6771±2151 | .002 |
| HDFS | Count/RF | 17.8±2.1 | 312±91 | 2.234 |
| HDFS | Count/XGB | 3.8±1.8 | 660±94 | .423 |
| HDFS | Sequence/LSTM | 309.3±13.2 | 37±4 | .116 |
| HDFS | Semantic/LR | 31.4±21.3 | 1257±113 | .004 |
| HDFS | Semantic/XGB | 9.4±.8 | 696±189 | .416 |
| BGL | Count/LR | 16.5±4.4 | 70±31 | .069 |
| BGL | Count/RF | 38.9±18.6 | 29±3 | 10.869 |
| BGL | Count/XGB | 10.2±3.2 | 222±74 | .372 |
| BGL | Sequence/LSTM | 37.8±3.9 | 15±2 | .386 |
| BGL | Semantic/LR | 6.1±1.7 | 1812±754 | .004 |
| BGL | Semantic/XGB | 1.6±.3 | 505±28 | .684 |
| Shared Word2vec fit |  | .4±.0 | -- | -- |
| Semantic transform: HDFS/BGL |  | 1.0/1.4 | -- | -- |
| Frozen BGL semantic fit |  | 3.0±.5 | -- | -- |
| BGL parsing, one run |  | 54 | -- | -- |

## Table 8: Cross-system XGBoost target-catalog visibility over five seeds. Union corpus and target IDF are offline transductive; budgets use tie-aware allocation.

| Column 1 | Column 2 | Column 3 | Column 4 | Column 5 | Column 6 | Column 7 |
| --- | --- | --- | --- | --- | --- | --- |
| Word2vec | IDF | AP | P@1% | R@1% | P@5% | R@5% |
| HDFS→BGL |  |  |  |  |  |  |
| Source | Source | .191±.107 | .242±.160 | .024±.016 | .220±.174 | .109±.086 |
| Source | Target | .187±.084 | .259±.163 | .026±.016 | .253±.163 | .125±.081 |
| Union | Source | .297±.136 | .443±.266 | .044±.026 | .293±.021 | .145±.010 |
| Union | Target | .325±.159 | .446±.312 | .044±.031 | .318±.122 | .157±.060 |
| BGL→HDFS |  |  |  |  |  |  |
| Source | Source | .089±.066 | .151±.228 | .051±.078 | .075±.057 | .128±.097 |
| Source | Target | .132±.100 | .248±.297 | .085±.102 | .095±.067 | .162±.114 |
| Union | Source | .039±.017 | .032±.018 | .011±.006 | .025±.007 | .043±.011 |
| Union | Target | .142±.137 | .201±.233 | .068±.080 | .129±.121 | .221±.207 |
